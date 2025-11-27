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
    def fetch_existing_records(self, sync_types=None):
        """Fetch existing records from Airtable, focusing on needed types"""
        if sync_types is None:
            sync_types = ["lenses", "sources", "metas", "patterns", "variations"]
        
        self.log(f"Fetching existing records from Airtable for: {', '.join(sync_types)}...")
        
        # Always fetch all required tables for pattern relationships
        tables_to_fetch = sync_types[:]
        if "patterns" in sync_types:
            # When syncing patterns, we need ALL related tables for linking
            required_tables = ["lenses", "sources", "metas", "variations"]
            for table in required_tables:
                if table not in tables_to_fetch:
                    tables_to_fetch.append(table)
            self.log("Also fetching all related tables (lenses, sources, metas, variations) for pattern linking")
            
        if "variations" in sync_types and "patterns" not in tables_to_fetch:
            tables_to_fetch.append("patterns")
            self.log("Also fetching patterns (needed for variation linking)")
            
        # Ensure patterns are processed before variations
        if "variations" in sync_types and "patterns" not in sync_types:
            self.log("WARNING: Variations sync requested without patterns. This may cause linking issues.", "warning")

        if "sources" in sync_types and "patterns" not in tables_to_fetch:
            tables_to_fetch.append("patterns")
            self.log("Also fetching patterns (needed for source linking)")
        
        # Fetch each required table
        if "lenses" in tables_to_fetch:
            self._fetch_table_map("lenses", "lens_name")
        
        if "sources" in tables_to_fetch:
            # Map sources using composite keys (content + lense + base_folder)
            table_name = self.tables.get("sources")
            if table_name:
                records = self._get_all_records(table_name)
                count = 0
                for r in records:
                    fields = r.get("fields", {})
                    content = fields.get("content", "")
                    lense = fields.get("lense", "")
                    base_folder = fields.get("base_folder", "")
                    record_name = r.get("name", "")
                    
                    # Create composite key for proper uniqueness detection
                    if content and lense:
                        composite_key = f"{content}|{lense}|{base_folder}"
                        content_hash = str(hash(composite_key))
                        self.record_map["sources"][content_hash] = r["id"]
                        count += 1
                    
                    # Also map by record name for pattern linking
                    if record_name:
                        normalized_key = self.normalize_for_matching(record_name)
                        if normalized_key:
                            self.record_map["sources"][normalized_key] = r["id"]
                            
                self.log(f"  - Sources: {count} existing records mapped.")
        
        if "metas" in tables_to_fetch:
            self._fetch_table_map("metas", "title")
        
        if "patterns" in tables_to_fetch:
            self._fetch_table_map("patterns", "pattern_title")
        
        if "variations" in tables_to_fetch:
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
                    # Provide suggestions for common field name issues
                    if "Unknown field name" in e.response.text and table_key == "variations":
                        self.log("SUGGESTION: Check your Airtable variations table field names. Try: 'Pattern', 'Patterns', 'pattern_title'", "error")
                else:
                    self.log(f"HTTP error creating {table_key} ({unique_val}): {str(e)}", "error")
                return None
            except Exception as e:
                self.log(f"Failed to create {table_key} ({unique_val}): {str(e)}", "error")
                return None

    def _link_source_to_pattern(self, source_id: str, pattern_id: str):
        """Helper method to link a source to a pattern via the Patterns relation field"""
        try:
            # Get current source record to see existing pattern links
            url = f"{self.base_url}/sources/{source_id}"
            resp = requests.get(url, headers=self.headers, timeout=30)
            resp.raise_for_status()
            
            current_patterns = resp.json().get("fields", {}).get("Patterns", [])
            
            # Add the new pattern ID if not already linked
            if pattern_id not in current_patterns:
                current_patterns.append(pattern_id)
                
                # Update the source with the new pattern link
                update_fields = {"Patterns": current_patterns}
                resp = requests.patch(url, headers=self.headers, json={"fields": update_fields}, timeout=30)
                resp.raise_for_status()
                
        except Exception as e:
            self.log(f"Error linking source {source_id} to pattern {pattern_id}: {str(e)}", "error")

    # b: Match and update
    def sync_data(self, data: Dict, sync_types: List[str] = None, enable_linking: bool = False):
        """Sync data with optional filtering by type"""
        if sync_types is None:
            sync_types = ["lenses", "sources", "metas", "patterns", "variations"]
        
        # Save what we're about to sync
        sync_type_str = "_".join(sync_types) if len(sync_types) > 1 else sync_types[0]
        self.save_sync_data(data, sync_type_str)
        
        self.log(f"Starting selective data sync for: {', '.join(sync_types)}...")
        
        # 1. Sync Lenses first (foundational)
        if "lenses" in sync_types:
            self.log("Syncing Lenses...")
            for doc in data.get("documents", []):
                lens_name = doc.get("lens")
                base_folder = doc.get("base_folder")
                
                if lens_name:
                    fields = {
                        "lens_title": lens_name,
                        "base_folder": base_folder,
                    }
                    self._create_or_update("lenses", lens_name, fields)
        
        # 2. Sync Metas 
        if "metas" in sync_types:
            self.log("Syncing Metas...")
            for meta in data.get("metas", []):
                meta_title = meta.get("title")
                base_folder = meta.get("base_folder")
                
                if meta_title:
                    fields = {
                        "meta_title": meta_title,
                        "subtitle": meta.get("subtitle"),
                        "content": meta.get("content"),
                        "base_folder": base_folder,
                    }
                    self._create_or_update("metas", meta_title, fields)
        
        # 3. Sync Patterns and Variations (patterns first, always needed for variations)
        if "patterns" in sync_types or "variations" in sync_types:
            if "patterns" in sync_types:
                self.log("Syncing Patterns...")
            if "variations" in sync_types:
                self.log("Preparing to sync variations...")
            
            for doc in data.get("documents", []):
                lens_name = doc.get("lens")
                base_folder = doc.get("base_folder")
                
                for p in doc.get("patterns", []):
                    title = p.get("title")
                    
                    p_id = None
                    
                    # Handle pattern creation/retrieval
                    if "patterns" in sync_types:
                        # Create or update pattern
                        fields = {
                            "pattern_title": title,
                            "overview": p.get("overview"),
                            "choice": p.get("choice"),
                            "base_folder": base_folder,
                        }
                        
                        p_id = self._create_or_update("patterns", title, fields)
                    else:
                        # For variations-only mode, get existing pattern ID
                        p_id = self.record_map["patterns"].get(self.normalize_for_matching(title))
                        if not p_id:
                            self.log(f"Warning: Pattern '{title}' not found in Airtable for variations linking", "error")
                            continue
                    
                    # 2. Sync Variations (Link to Pattern)
                    if "variations" in sync_types and p_id:
                        variation_count = len(p.get("variations", []))
                        self.log(f"Syncing {variation_count} variations for pattern: {title}")
                        
                        variations_synced = 0
                        for v in p.get("variations", []):
                            v_title = v.get("title")
                            if v_title:  # Only sync variations with titles
                                v_fields = {
                                    "variation_title": v_title,
                                    "content": v.get("content", "")
                                }
                                
                                # Add lens field if lens_name is available
                                if lens_name:
                                    v_fields["lens"] = lens_name
                                
                                # Add base_folder field
                                if base_folder:
                                    v_fields["base_folder"] = base_folder
                                
                                # Add pattern linking if --sync flag is enabled
                                if enable_linking and p_id:
                                    # Use the correct field name from Airtable schema - array format
                                    v_fields["pattern_reference"] = [p_id]
                                    
                                # Debug: Log what fields we're trying to send
                                self.log(f"Creating variation '{v_title}' with fields: {list(v_fields.keys())}")
                                result = self._create_or_update("variations", v_title, v_fields)
                                if result:
                                    variations_synced += 1
                                    link_status = "with pattern link" if enable_linking else "without pattern link"
                                    self.log(f"Successfully synced variation '{v_title}' to pattern '{title}' ({link_status})")
                        
                        self.log(f"Successfully synced {variations_synced}/{variation_count} variations for pattern: {title}")
        
        # 4. Sync Sources (if requested)  
        if "sources" in sync_types:
            self.log("Syncing Sources...")
            for source in data.get("sources", []):
                source_content = source.get("source")  # This is the content
                base_folder = source.get("base_folder")
                lens_name = source.get("lens")
                
                if source_content:
                    fields = {
                        "content": source_content,  # Primary field
                        "base_folder": base_folder,
                    }
                    
                    # Add lens field if available
                    if lens_name:
                        fields["lense"] = lens_name  # Note: correct field name is "lense" not "lens"
                    
                    # Add pattern linking if enabled and patterns exist
                    if enable_linking and source.get("patterns"):
                        pattern_ids = []
                        for pattern_title in source.get("patterns", []):
                            pattern_id = self.get_record_id("patterns", pattern_title)
                            if pattern_id:
                                pattern_ids.append(pattern_id)
                        if pattern_ids:
                            fields["Patterns"] = pattern_ids  # Correct field name with capital P
                    
                    self._create_or_update("sources", source_content, fields)
        
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