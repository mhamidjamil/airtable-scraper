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
                # Debug logging removed
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

        # 2. Sync Sources (Updated to handle multiple sources with new fields)
        if "sources" in sync_types:
            self.log("Syncing Sources...")
            sources_synced = 0
            
            for doc in data.get("documents", []):
                lens_name = doc.get("lens", "")
                base_folder = doc.get("base_folder", "")
                pattern_count = 0
                
                # Process patterns to extract their parsed sources
                for pattern in doc.get("patterns", []):
                    pattern_count += 1
                    source_count_for_pattern = 0
                    
                    for parsed_source in pattern.get("parsed_sources", []):
                        source_name = parsed_source.get("source_name")
                        source_content = parsed_source.get("content", "")
                        
                        if source_name and source_content:
                            # Create composite key for uniqueness check (same as mapping logic)
                            composite_key = f"{source_content}|{lens_name}|{base_folder}"
                            content_hash = str(hash(composite_key))
                            
                            # Check if this exact source already exists in Airtable
                            if content_hash not in self.record_map.get("sources", {}):
                                
                                # Create unique record name for each source
                                record_name = f"{source_name}_P{pattern_count}_{lens_name}_{content_hash[:4]}"
                                
                                fields = {
                                    "content": source_content,  # The actual source text goes in content field
                                    "lense": lens_name,        # Note: 'lense' as per your table structure  
                                    "base_folder": base_folder
                                }
                                
                                # Try to link to pattern if it exists
                                pattern_title = pattern.get("title")
                                if pattern_title:
                                    p_id = self.record_map["patterns"].get(self.normalize_for_matching(pattern_title))
                                    if p_id:
                                        fields["Patterns"] = [p_id]
                                
                                # Use unique record name to ensure separate records
                                result = self._create_or_update("sources", record_name, fields)
                                
                                # Update cache with content hash so pattern linking can find this new source
                                if result:
                                    self.record_map["sources"][content_hash] = result
                                    
                                sources_synced += 1
                                source_count_for_pattern += 1
                                self.log(f"Created source #{sources_synced}: {source_name} for pattern {pattern_count} (lense: {lens_name})")
                            else:
                                self.log(f"Skipped duplicate source: {source_name} (already exists)")
                    
                    if source_count_for_pattern > 0:
                        self.log(f"Pattern {pattern_count}: Created {source_count_for_pattern} source records")
            
            self.log(f"Total unique sources created: {sources_synced}")

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
            if "patterns" in sync_types:
                self.log("Syncing Patterns...")
            if "variations" in sync_types:
                self.log("Preparing to sync variations...")
            
            pattern_id_counter = 1
            
            for doc in data.get("documents", []):
                lens_name = doc.get("lens")  # Get lens name as string
                base_folder = doc.get("base_folder")
                
                for p in doc.get("patterns", []):
                    title = p.get("title")
                    
                    # Get source IDs from parsed sources using composite keys
                    source_ids = []
                    
                    for parsed_source in p.get("parsed_sources", []):
                        source_name = parsed_source.get("source_name")
                        source_content = parsed_source.get("content", "")
                        
                        if source_name and source_content:
                            # Use the same composite key as during source creation
                            composite_key = f"{source_content}|{lens_name}|{base_folder}"
                            content_hash = str(hash(composite_key))
                            
                            source_id = self.record_map["sources"].get(content_hash)
                            if source_id:
                                source_ids.append(source_id)
                                self.log(f"Linked pattern '{title}' to source: {source_name}")
                            else:
                                self.log(f"Warning: Source '{source_name}' not found for pattern '{title}'", "warning")
                    
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
                        
                        # Link to Lens
                        if lens_name: 
                            lens_id = self.record_map["lenses"].get(self.normalize_for_matching(lens_name))
                            if lens_id:
                                fields["lens"] = [lens_id]  # Must be array of record IDs
                                self.log(f"Linked pattern '{title}' to lens: {lens_name}")
                            else:
                                self.log(f"Warning: Lens '{lens_name}' not found for pattern '{title}'", "warning")
                        
                        # Link to Sources
                        if source_ids: 
                            fields["sources"] = source_ids
                            self.log(f"Linked pattern '{title}' to {len(source_ids)} sources")
                        
                        # Link to Meta (find meta record that matches the base_folder)
                        # The meta records are stored with normalized title as key
                        # We need to find the meta that has the same base_folder as this pattern
                        meta_ids = []
                        for doc_meta in data.get("metas", []):
                            if doc_meta.get("base_folder") == base_folder:
                                meta_title = doc_meta.get("title")
                                if meta_title:
                                    meta_id = self.record_map["metas"].get(self.normalize_for_matching(meta_title))
                                    if meta_id:
                                        meta_ids.append(meta_id)
                        
                        if meta_ids:
                            fields["Metas"] = meta_ids
                            self.log(f"Linked pattern '{title}' to {len(meta_ids)} meta(s) (base_folder: {base_folder})")
                        else:
                            self.log(f"Warning: No meta found for pattern '{title}' with base_folder '{base_folder}'", "warning")
                        
                        # Get variation IDs for this pattern
                        pattern_variation_ids = []
                        for v in p.get("variations", []):
                            v_title = v.get("title")
                            if v_title:
                                v_id = self.record_map["variations"].get(self.normalize_for_matching(v_title))
                                if v_id:
                                    pattern_variation_ids.append(v_id)
                        
                        if pattern_variation_ids:
                            fields["variations"] = pattern_variation_ids
                            self.log(f"Linked pattern '{title}' to {len(pattern_variation_ids)} variations")
                        
                        p_id = self._create_or_update("patterns", title, fields)
                        
                        # Update sources to link back to this pattern (bidirectional linking)
                        if p_id and source_ids:
                            for source_id in source_ids:
                                self._link_source_to_pattern(source_id, p_id)
                        
                        # Note: Variations table does not have a pattern field, so no bidirectional linking needed
                        # The pattern -> variations relationship is one-way only
                    else:
                        # For variations-only mode, get existing pattern ID
                        p_id = self.record_map["patterns"].get(self.normalize_for_matching(title))
                        if not p_id:
                            self.log(f"Warning: Pattern '{title}' not found in Airtable for variations linking", "error")
                            continue
                    
                    # 5. Sync Variations (Link to Pattern)
                    if "variations" in sync_types and p_id:
                        variation_count = len(p.get("variations", []))
                        self.log(f"Syncing {variation_count} variations for pattern: {title}")
                        
                        variations_synced = 0
                        for v in p.get("variations", []):
                            v_title = v.get("title")
                            if v_title:  # Only sync variations with titles
                                v_fields = {
                                    "variation_title": v_title,
                                    "content": v.get("content", ""),
                                    "base_folder": base_folder
                                }
                                
                                # Add lens field if lens_name is available
                                if lens_name:
                                    v_fields["lens"] = lens_name
                                
                                result = self._create_or_update("variations", v_title, v_fields)
                                if result:
                                    variations_synced += 1
                        
                        self.log(f"Successfully synced {variations_synced}/{variation_count} variations for pattern: {title}")
                    
                    pattern_id_counter += 1        # Log sync summary
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
