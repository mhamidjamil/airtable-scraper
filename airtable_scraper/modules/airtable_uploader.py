import requests
import json
import time
from typing import Dict, List, Any
from config import settings

class AirtableUploader:
    def __init__(self, log_handler=None):
        self.logger = log_handler
        self.headers = {
            "Authorization": f"Bearer {settings.AIRTABLE_CONFIG['api_token']}",
            "Content-Type": "application/json"
        }
        self.base_url = f"https://api.airtable.com/v0/{settings.AIRTABLE_CONFIG['base_id']}"
        self.tables = settings.AIRTABLE_CONFIG['tables']
        
        # Cache for existing records to prevent duplicates
        # Format: { "TableName": { "UniqueKey": "RecordID" } }
        self.record_map = {
            "lenses": {},
            "sources": {},
            "metas": {},
            "patterns": {},
            "variations": {}
        }

    def log(self, msg, level="info"):
        if self.logger:
            if level == "error": self.logger.error(msg)
            else: self.logger.info(msg)
        else:
            print(f"[{level.upper()}] {msg}")

    # a: Read already uploaded data
    def fetch_existing_records(self):
        self.log("Fetching existing records from Airtable to build sync map...")
        
        # 1. Lenses (Key: lens_name)
        self._fetch_table_map("lenses", "lens_name")
        
        # 2. Sources (Key: source_name)
        self._fetch_table_map("sources", "source_name")
        
        # 3. Metas (Key: title)
        self._fetch_table_map("metas", "title")
        
        # 4. Patterns (Key: pattern_title) - Assuming titles are unique enough or combined
        self._fetch_table_map("patterns", "pattern_title")
        
        # 5. Variations (Key: variation_title)
        self._fetch_table_map("variations", "variation_title")
        
        self.log("Sync map built successfully.")

    def _fetch_table_map(self, table_key: str, primary_field: str):
        table_name = self.tables.get(table_key)
        if not table_name: return

        records = self._get_all_records(table_name)
        count = 0
        for r in records:
            val = r["fields"].get(primary_field)
            if val:
                self.record_map[table_key][val] = r["id"]
                count += 1
        self.log(f"  - {table_name}: {count} existing records mapped.")

    def _get_all_records(self, table_name: str) -> List[Dict]:
        all_records = []
        offset = None
        
        while True:
            params = {}
            if offset: params["offset"] = offset
            
            try:
                resp = requests.get(f"{self.base_url}/{table_name}", headers=self.headers, params=params, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                all_records.extend(data.get("records", []))
                
                offset = data.get("offset")
                if not offset: break
                time.sleep(0.2) # Rate limit
            except Exception as e:
                self.log(f"Error fetching {table_name}: {str(e)}", "error")
                break
                
        return all_records

    def _create_or_update(self, table_key: str, unique_val: str, fields: Dict) -> str:
        """
        Uploads data. If exists, returns ID (skips update for now to be safe, or could update).
        Returns: Record ID
        """
        if not unique_val: return None
        
        table_name = self.tables.get(table_key)
        existing_id = self.record_map[table_key].get(unique_val)
        
        if existing_id:
            # Logic: Match current extraction -> Update not synced
            # For now, we assume if it exists, we skip or patch. 
            # Let's Patch (Update) to ensure data is fresh.
            url = f"{self.base_url}/{table_name}/{existing_id}"
            try:
                requests.patch(url, headers=self.headers, json={"fields": fields}, timeout=30)
                # self.log(f"Updated {table_key}: {unique_val}")
                return existing_id
            except Exception as e:
                self.log(f"Failed to update {table_key} ({unique_val}): {str(e)}", "error")
                return existing_id
        else:
            # Create new
            url = f"{self.base_url}/{table_name}"
            try:
                resp = requests.post(url, headers=self.headers, json={"fields": fields}, timeout=30)
                resp.raise_for_status()
                new_id = resp.json()["id"]
                self.record_map[table_key][unique_val] = new_id # Update cache
                self.log(f"Created {table_key}: {unique_val}")
                return new_id
            except Exception as e:
                self.log(f"Failed to create {table_key} ({unique_val}): {str(e)}", "error")
                return None

    # b: Match and update
    def sync_data(self, data: Dict):
        self.log("Starting data sync...")
        
        # 1. Sync Lenses
        self.log("Syncing Lenses...")
        for doc in data.get("documents", []):
            lens_name = doc.get("lens")
            if lens_name:
                self._create_or_update("lenses", lens_name, {
                    "lens_name": lens_name,
                    "content": doc.get("summary", "")
                })

        # 2. Sync Sources
        self.log("Syncing Sources...")
        for doc in data.get("documents", []):
            for p in doc.get("patterns", []):
                src = p.get("source", "").strip()
                if src:
                    self._create_or_update("sources", src, {"source_name": src})

        # 3. Sync Metas
        self.log("Syncing Metas...")
        for m in data.get("metas", []):
            self._create_or_update("metas", m.get("title"), {
                "title": m.get("title"),
                "subtitle": m.get("subtitle"),
                "content": m.get("content"),
                "base_folder": m.get("base_folder")
            })

        # 4. Sync Patterns (and link to Lens/Source)
        self.log("Syncing Patterns...")
        pattern_id_counter = 1 # In real app, might want to query max ID
        
        for doc in data.get("documents", []):
            lens_id = self.record_map["lenses"].get(doc.get("lens"))
            base_folder = doc.get("base_folder")
            
            for p in doc.get("patterns", []):
                title = p.get("title")
                src_val = p.get("source", "").strip()
                src_id = self.record_map["sources"].get(src_val)
                
                fields = {
                    "pattern_title": title,
                    "overview": p.get("overview"),
                    "choice": p.get("choice"),
                    "base_folder": base_folder,
                    # "pattern_id": f"P{pattern_id_counter:03d}" # Optional: only if creating new
                }
                
                if lens_id: fields["lens"] = [lens_id]
                if src_id: fields["sources"] = [src_id]
                
                p_id = self._create_or_update("patterns", title, fields)
                
                # 5. Sync Variations (Link to Pattern)
                if p_id:
                    for v in p.get("variations", []):
                        v_title = v.get("title")
                        v_fields = {
                            "variation_title": v_title,
                            "variation_number": v.get("variation_number"),
                            "content": v.get("content"),
                            "linked_pattern": [p_id]
                        }
                        self._create_or_update("variations", v_title, v_fields)
                
                pattern_id_counter += 1
        
        self.log("Sync complete.")
