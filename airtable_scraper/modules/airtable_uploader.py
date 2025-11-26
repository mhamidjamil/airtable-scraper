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
    
    def normalize_for_matching(self, text: str) -> str:
        """Normalize text for robust duplicate matching"""
        if not text: return ""
        return text.strip().lower()
    
    def _validate_fields(self, fields: Dict, table_key: str) -> Dict:
        """Validate and clean fields before sending to Airtable"""
        clean_fields = {}
        
        for key, value in fields.items():
            if value is None:
                continue
            elif isinstance(value, str):
                # Trim whitespace and limit length
                clean_value = value.strip()
                if len(clean_value) > 100000:  # Airtable limit
                    clean_value = clean_value[:99997] + "..."
                if clean_value:  # Only add non-empty strings
                    clean_fields[key] = clean_value
            elif isinstance(value, list):
                # Remove None values from lists
                clean_list = [v for v in value if v is not None]
                if clean_list:
                    clean_fields[key] = clean_list
            elif isinstance(value, (int, float, bool)):
                clean_fields[key] = value
        
        return clean_fields

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
                # Use normalized key for robust matching
                normalized_key = self.normalize_for_matching(val)
                if normalized_key:  # Only store non-empty keys
                    self.record_map[table_key][normalized_key] = r["id"]
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
        Uploads data. If exists, returns ID and updates; otherwise creates new record.
        Returns: Record ID
        """
        if not unique_val: return None
        
        # Normalize key for consistent matching
        normalized_key = self.normalize_for_matching(unique_val)
        if not normalized_key: return None
        
        table_name = self.tables.get(table_key)
        existing_id = self.record_map[table_key].get(normalized_key)
        
        if existing_id:
            # Update existing record to ensure data is fresh
            url = f"{self.base_url}/{table_name}/{existing_id}"
            try:
                resp = requests.patch(url, headers=self.headers, json={"fields": fields}, timeout=30)
                resp.raise_for_status()
                self.log(f"Updated existing {table_key}: {unique_val}")
                return existing_id
            except Exception as e:
                self.log(f"Failed to update {table_key} ({unique_val}): {str(e)}", "error")
                return existing_id
        else:
            # Create new record
            url = f"{self.base_url}/{table_name}"
            try:
                # Validate fields before sending
                clean_fields = self._validate_fields(fields, table_key)
                resp = requests.post(url, headers=self.headers, json={"fields": clean_fields}, timeout=30)
                resp.raise_for_status()
                new_id = resp.json()["id"]
                # Update cache with normalized key
                self.record_map[table_key][normalized_key] = new_id
                self.log(f"Created new {table_key}: {unique_val}")
                return new_id
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 422:
                    self.log(f"Field validation error for {table_key} ({unique_val}): {e.response.text}", "error")
                else:
                    self.log(f"HTTP error creating {table_key} ({unique_val}): {str(e)}", "error")
                return None
            except Exception as e:
                self.log(f"Failed to create {table_key} ({unique_val}): {str(e)}", "error")
                return None

    # b: Match and update
    def sync_data(self, data: Dict, sync_types: List[str] = None):
        """Sync data with optional filtering by type"""
        if sync_types is None:
            sync_types = ["lenses", "sources", "metas", "patterns", "variations"]
        
        # Save what we're about to sync
        sync_type_str = "_".join(sync_types) if len(sync_types) > 1 else sync_types[0]
        self.save_sync_data(data, sync_type_str)
        
        self.log(f"Starting selective data sync for: {', '.join(sync_types)}...")
        
        # 1. Sync Lenses
        if "lenses" in sync_types:
            self.log("Syncing Lenses...")
            for doc in data.get("documents", []):
                lens_name = doc.get("lens")
                if lens_name:
                    self._create_or_update("lenses", lens_name, {
                        "lens_name": lens_name,
                        "content": doc.get("summary", "")
                    })

        # 2. Sync Sources
        if "sources" in sync_types:
            self.log("Syncing Sources...")
            for doc in data.get("documents", []):
                for p in doc.get("patterns", []):
                    src = p.get("source", "").strip()
                    if src:
                        self._create_or_update("sources", src, {"source_name": src})

        # 3. Sync Metas
        if "metas" in sync_types:
            self.log("Syncing Metas...")
            for m in data.get("metas", []):
                self._create_or_update("metas", m.get("title"), {
                    "title": m.get("title"),
                    "subtitle": m.get("subtitle"),
                    "content": m.get("content"),
                    "base_folder": m.get("base_folder")
                })

        # 4. Sync Patterns (and link to Lens/Source)
        if "patterns" in sync_types or "variations" in sync_types:
            self.log("Syncing Patterns...")
            pattern_id_counter = 1 # In real app, might want to query max ID
            
            for doc in data.get("documents", []):
                lens_id = self.record_map["lenses"].get(self.normalize_for_matching(doc.get("lens")))
                base_folder = doc.get("base_folder")
                
                for p in doc.get("patterns", []):
                    title = p.get("title")
                    src_val = p.get("source", "").strip()
                    src_id = self.record_map["sources"].get(self.normalize_for_matching(src_val))
                
                    p_id = None
                    if "patterns" in sync_types:
                        fields = {
                            "pattern_title": title,
                            "overview": p.get("overview"),
                            "choice": p.get("choice"),
                            "base_folder": base_folder,
                        }
                        
                        if lens_id: fields["lens"] = [lens_id]
                        if src_id: fields["sources"] = [src_id]
                        
                        p_id = self._create_or_update("patterns", title, fields)
                    else:
                        # Get existing pattern ID for variations
                        p_id = self.record_map["patterns"].get(self.normalize_for_matching(title))
                    
                    # 5. Sync Variations (Link to Pattern)
                    if "variations" in sync_types and p_id:
                        variation_count = len(p.get("variations", []))
                        self.log(f"Syncing {variation_count} variations for pattern: {title}")
                        for v in p.get("variations", []):
                            v_title = v.get("title")
                            if v_title:  # Only sync variations with titles
                                v_fields = {
                                    "variation_title": v_title,
                                    "variation_number": v.get("variation_number"),
                                    "content": v.get("content", ""),
                                    "linked_pattern": [p_id]
                                }
                                self._create_or_update("variations", v_title, v_fields)
                
                    pattern_id_counter += 1
        
        # Log sync summary
        total_records = sum(len(cache) for cache in self.record_map.values())
        self.log(f"Sync complete. Total records in cache: {total_records}")
        for table_key, cache in self.record_map.items():
            if cache:
                self.log(f"  {table_key}: {len(cache)} records")
        self.log("Sync complete.")
    
    def save_sync_data(self, data: Dict, sync_type: str = "all"):
        """Save what's being synced to timestamped JSON file"""
        from datetime import datetime
        from pathlib import Path
        import json
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"airtable_sync_{sync_type}_{timestamp}.json"
        filepath = Path("json_data") / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.log(f"Saved sync data to: {filepath}")
        except Exception as e:
            self.log(f"Failed to save sync data: {str(e)}", "error")
