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
        """Sync data with CORRECT order: Metas → Lenses → Sources → Patterns → Variations"""
        if sync_types is None:
            sync_types = ["metas", "lenses", "sources", "patterns", "variations"]
        
        # Save what we're about to sync
        sync_type_str = "_".join(sync_types) if len(sync_types) > 1 else sync_types[0]
        self.save_sync_data(data, sync_type_str)
        
        self.log(f"🚀 CORRECT UPLOAD SEQUENCE: Metas → Lenses → Sources → Patterns → Variations")
        self.log(f"Starting selective data sync for: {', '.join(sync_types)}...")
        
        # 1. METAS FIRST (no dependencies)
        if "metas" in sync_types:
            self.log("📋 [1/5] Syncing Metas...")
            self._sync_metas(data)
        
        # 2. LENSES SECOND (no dependencies)
        if "lenses" in sync_types:
            self.log("🔍 [2/5] Syncing Lenses...")
            self._sync_lenses(data)
        
        # 3. SOURCES THIRD (no dependencies)
        if "sources" in sync_types:
            self.log("📚 [3/5] Syncing Sources...")
            self._sync_sources(data)
        
        # 4. PATTERNS FOURTH (links to metas, lenses, sources)
        if "patterns" in sync_types:
            self.log("🎯 [4/5] Syncing Patterns...")
            self._sync_patterns(data, enable_linking)
        
        # 5. VARIATIONS LAST (requires patterns for linking)
        if "variations" in sync_types:
            self.log("🔄 [5/5] Syncing Variations...")
            self._sync_variations(data, enable_linking)
        
        # Log sync summary
        total_records = sum(len(cache) for cache in self.record_map.values())
        self.log(f"Sync complete. Total records in cache: {total_records}")
        for table_key, cache in self.record_map.items():
            if cache:
                self.log(f"  {table_key}: {len(cache)} records")
        self.log("Sync complete.")

    def _sync_metas(self, data: Dict):
        """Sync Metas with correct field names"""
        metas_synced = 0
        for meta in data.get("metas", []):
            meta_title = meta.get("title")
            
            if meta_title:
                # Clean base_folder value (remove quotes if present)
                base_folder = meta.get("base_folder", "")
                if base_folder and base_folder.startswith('"') and base_folder.endswith('"'):
                    base_folder = base_folder[1:-1]  # Remove quotes
                
                fields = {
                    "title": meta_title,  # PRIMARY FIELD (not meta_title)
                    "subtitle": meta.get("subtitle", ""),
                    "content": meta.get("content", "")
                }
                result = self._create_or_update("metas", meta_title, fields)
                if result:
                    metas_synced += 1
                    self.log(f"Meta '{meta_title}' synced successfully")
        
        self.log(f"✅ Metas sync complete: {metas_synced} records")

    def _sync_lenses(self, data: Dict):
        """Sync Lenses with correct field names"""
        lenses_synced = 0
        for doc in data.get("documents", []):
            lens_name = doc.get("lens")
            
            if lens_name:
                fields = {
                    "lens_name": lens_name,  # PRIMARY FIELD (not lens_title)
                    "content": doc.get("summary", "")  # Use summary as content
                }
                result = self._create_or_update("lenses", lens_name, fields)
                if result:
                    lenses_synced += 1
        
        self.log(f"✅ Lenses sync complete: {lenses_synced} records")

    def _sync_sources(self, data: Dict):
        """Sync Sources with correct field names"""
        sources_synced = 0
        
        # Process sources from patterns within each document
        for doc in data.get("documents", []):
            lens_name = doc.get("lens", "")
            base_folder = doc.get("base_folder", "")
            
            # Sources are nested within patterns
            for pattern in doc.get("patterns", []):
                for source in pattern.get("parsed_sources", []):
                    source_content = source.get("content")  # This is the primary content
                    
                    if source_content:
                        fields = {
                            "content": source_content,  # PRIMARY FIELD
                            "lense": lens_name,  # Note: "lense" not "lens"
                            "base_folder": base_folder
                        }
                        result = self._create_or_update("sources", source_content, fields)
                        if result:
                            sources_synced += 1
                            self.log(f"Source '{source_content[:50]}...' synced")
        
        # Also process standalone sources array if it exists
        for source in data.get("sources", []):
            source_content = source.get("source")  # This is the primary content
            
            if source_content:
                fields = {
                    "content": source_content,  # PRIMARY FIELD
                    "lense": source.get("lens", ""),  # Note: "lense" not "lens" 
                    "base_folder": source.get("base_folder", "")
                }
                result = self._create_or_update("sources", source_content, fields)
                if result:
                    sources_synced += 1
                    self.log(f"Standalone source '{source_content[:50]}...' synced")
        
        self.log(f"✅ Sources sync complete: {sources_synced} records")

    def _sync_variations(self, data: Dict, enable_linking: bool = False):
        """Sync Variations with pattern linking"""
        variations_synced = 0
        
        for doc in data.get("documents", []):
            lens_name = doc.get("lens")
            base_folder = doc.get("base_folder")
            
            for pattern in doc.get("patterns", []):
                pattern_title = pattern.get("title")
                
                # Get pattern ID for linking
                pattern_id = None
                if enable_linking and pattern_title:
                    pattern_id = self.record_map["patterns"].get(self.normalize_for_matching(pattern_title))
                    if not pattern_id:
                        self.log(f"⚠️ Pattern '{pattern_title}' not found for variation linking", "error")
                
                for variation in pattern.get("variations", []):
                    variation_title = variation.get("title")
                    
                    if variation_title:
                        fields = {
                            "variation_title": variation_title,  # PRIMARY FIELD
                            "content": variation.get("content", ""),
                            "lens": lens_name or "",
                            "base_folder": base_folder or ""
                        }
                        
                        # Add pattern linking if enabled and pattern exists
                        if enable_linking and pattern_id:
                            fields["pattern_reference"] = [pattern_id]  # Link field
                        
                        result = self._create_or_update("variations", variation_title, fields)
                        if result:
                            variations_synced += 1
                            link_msg = f" → linked to '{pattern_title}'" if pattern_id else " (no pattern link)"
                            self.log(f"Variation '{variation_title}'{link_msg}")
        
        self.log(f"✅ Variations sync complete: {variations_synced} records")

    def _sync_patterns(self, data: Dict, enable_linking: bool = False):
        """Sync Patterns with links to Metas, Lenses, Sources"""
        patterns_synced = 0
        
        for doc in data.get("documents", []):
            lens_name = doc.get("lens")
            base_folder = doc.get("base_folder")
            
            for pattern in doc.get("patterns", []):
                pattern_title = pattern.get("title")
                
                if pattern_title:
                    fields = {
                        "pattern_title": pattern_title,  # PRIMARY FIELD
                        "overview": pattern.get("overview", ""),
                        "choice": pattern.get("choice", ""), 
                        "base_folder": base_folder or ""
                    }
                    
                    # Add linking if enabled
                    if enable_linking:
                        # Link to Lens
                        if lens_name:
                            lens_id = self.record_map["lenses"].get(self.normalize_for_matching(lens_name))
                            if lens_id:
                                fields["lens"] = [lens_id]  # Link to Lenses table
                        
                        # Link to Sources (pattern sources if available)
                        pattern_sources = pattern.get("parsed_sources", [])
                        if pattern_sources:
                            source_ids = []
                            for source in pattern_sources:
                                # Extract content from source object
                                source_content = source.get("content", "")
                                if source_content:
                                    source_id = self.record_map["sources"].get(self.normalize_for_matching(source_content))
                                    if source_id:
                                        source_ids.append(source_id)
                            if source_ids:
                                fields["sources"] = source_ids  # Link to Sources table
                        
                        # Link to Metas (if pattern belongs to specific metas)
                        # Note: This might need custom logic based on your meta-pattern relationships
                        # For now, we'll link all patterns to all metas from the same base_folder
                        if base_folder:
                            meta_ids = []
                            for meta_key, meta_id in self.record_map["metas"].items():
                                meta_ids.append(meta_id)  # Link all metas for now
                            if meta_ids:
                                fields["Metas"] = meta_ids  # Link to Metas table
                    
                    result = self._create_or_update("patterns", pattern_title, fields)
                    if result:
                        patterns_synced += 1
                        links = []
                        if enable_linking:
                            if "lens" in fields: links.append("lens")
                            if "sources" in fields: links.append(f"{len(fields['sources'])} sources")
                            if "Metas" in fields: links.append(f"{len(fields['Metas'])} metas")
                        link_msg = f" → linked to: {', '.join(links)}" if links else ""
                        self.log(f"Pattern '{pattern_title}'{link_msg}")
        
        self.log(f"✅ Patterns sync complete: {patterns_synced} records")
    
    def get_record_id(self, table_key: str, record_name: str) -> str:
        """Get record ID for linking purposes"""
        if not record_name:
            return None
        normalized_key = self.normalize_for_matching(record_name)
        return self.record_map.get(table_key, {}).get(normalized_key)

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