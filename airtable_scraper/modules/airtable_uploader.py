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
    
    def _check_field_exists(self, table_key: str, field_name: str) -> bool:
        """Check if a field exists in the table by attempting a test query"""
        # This is cached after first check to avoid repeated API calls
        cache_key = f"{table_key}_{field_name}"
        if hasattr(self, '_field_existence_cache'):
            if cache_key in self._field_existence_cache:
                return self._field_existence_cache[cache_key]
        else:
            self._field_existence_cache = {}
        
        table_name = self.tables.get(table_key)
        if not table_name:
            self._field_existence_cache[cache_key] = False
            return False
        
        try:
            # Try to get records with just this field to test if it exists
            params = {"maxRecords": 1, "fields": [field_name]}
            resp = requests.get(f"{self.base_url}/{table_name}", headers=self.headers, params=params, timeout=30)
            # Field exists if we don't get a 422 error about unknown field
            exists = resp.status_code != 422
            self._field_existence_cache[cache_key] = exists
            return exists
        except:
            self._field_existence_cache[cache_key] = False
            return False

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
            # Map sources using available fields (now only content + Patterns relationship)
            table_name = self.tables.get("sources")
            if table_name:
                records = self._get_all_records(table_name)
                count = 0
                for r in records:
                    fields = r.get("fields", {})
                    content = fields.get("content", "")
                    
                    # Use content as the primary key since lense and base_folder no longer exist
                    if content:
                        normalized_key = self.normalize_for_matching(content)
                        if normalized_key:
                            self.record_map["sources"][normalized_key] = r["id"]
                            count += 1
                    
                    # Also map by record name for pattern linking
                    record_name = r.get("name", "")
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

    def _create_or_update(self, table_key: str, unique_val: str, fields: Dict, force_update: bool = False) -> str:
        """
        Uploads data. If exists, returns ID and optionally updates; otherwise creates new record.
        Returns: Record ID
        """
        if not unique_val: return None
        
        # Normalize key for consistent matching
        normalized_key = self.normalize_for_matching(unique_val)
        if not normalized_key: return None
        
        table_name = self.tables.get(table_key)
        existing_id = self.record_map[table_key].get(normalized_key)
        
        if existing_id:
            if force_update:
                # Update existing record to ensure data is fresh
                url = f"{self.base_url}/{table_name}/{existing_id}"
                try:
                    # Filter fields to only include those that exist in the table
                    filtered_fields = self._filter_existing_fields(table_key, fields)
                    resp = requests.patch(url, headers=self.headers, json={"fields": filtered_fields}, timeout=30)
                    resp.raise_for_status()
                    self.log(f"Updated existing {table_key}: {unique_val}")
                    return existing_id
                except Exception as e:
                    self.log(f"Failed to update {table_key} ({unique_val}): {str(e)}", "error")
                    return existing_id
            else:
                # Skip existing records by default to prevent duplicates
                self.log(f"Skipped existing {table_key}: {unique_val}")
                return existing_id
        else:
            # Create new record
            url = f"{self.base_url}/{table_name}"
            try:
                # Filter and validate fields before sending
                filtered_fields = self._filter_existing_fields(table_key, fields)
                clean_fields = self._validate_fields(filtered_fields, table_key)
                
                if not clean_fields:
                    self.log(f"No valid fields to create {table_key} ({unique_val})", "error")
                    return None
                
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
                    # Try to create with only the primary field if possible
                    primary_field = self._get_primary_field(table_key)
                    if primary_field and primary_field in fields:
                        try:
                            minimal_fields = {primary_field: fields[primary_field]}
                            resp = requests.post(url, headers=self.headers, json={"fields": minimal_fields}, timeout=30)
                            resp.raise_for_status()
                            new_id = resp.json()["id"]
                            self.record_map[table_key][normalized_key] = new_id
                            self.log(f"Created minimal {table_key}: {unique_val} (only primary field)")
                            return new_id
                        except:
                            pass
                else:
                    self.log(f"HTTP error creating {table_key} ({unique_val}): {str(e)}", "error")
                return None
            except Exception as e:
                self.log(f"Failed to create {table_key} ({unique_val}): {str(e)}", "error")
                return None
    
    def _filter_existing_fields(self, table_key: str, fields: Dict) -> Dict:
        """Filter fields to only include those that exist in the Airtable"""
        filtered = {}
        for field_name, value in fields.items():
            if self._check_field_exists(table_key, field_name):
                filtered[field_name] = value
            else:
                self.log(f"Skipping non-existent field '{field_name}' for {table_key}")
        return filtered
    
    def _get_primary_field(self, table_key: str) -> str:
        """Get the primary field name for each table type"""
        primary_fields = {
            "sources": "content",
            "variations": "variation_title", 
            "patterns": "pattern_title",
            "lenses": "lens_name",
            "metas": "title"
        }
        return primary_fields.get(table_key)

    def _link_source_to_pattern(self, source_id: str, pattern_id: str):
        """Helper method to link a source to a pattern via the Patterns relation field"""
        try:
            # Get current source record to see existing pattern links
            url = f"{self.base_url}/Sources/{source_id}"
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
    
    def _sync_source_pattern_relationships(self, data: Dict):
        """Sync relationships between sources and patterns"""
        self.log("Linking sources to patterns...")
        links_created = 0
        
        for doc in data.get("documents", []):
            for pattern in doc.get("patterns", []):
                pattern_title = pattern.get("title")
                pattern_id = self.record_map["patterns"].get(self.normalize_for_matching(pattern_title)) if pattern_title else None
                
                if pattern_id:
                    # Link all sources in this pattern
                    for source in pattern.get("parsed_sources", []):
                        source_content = source.get("content")
                        if source_content:
                            source_id = self.record_map["sources"].get(self.normalize_for_matching(source_content))
                            if source_id:
                                self._link_source_to_pattern(source_id, pattern_id)
                                links_created += 1
        
        self.log(f"✅ Source-Pattern relationships synced: {links_created} links")
    
    def _sync_variation_pattern_relationships(self, data: Dict):
        """Sync relationships between variations and patterns"""
        self.log("Linking variations to patterns...")
        links_created = 0
        
        for doc in data.get("documents", []):
            for pattern in doc.get("patterns", []):
                pattern_title = pattern.get("title")
                pattern_id = self.record_map["patterns"].get(self.normalize_for_matching(pattern_title)) if pattern_title else None
                
                if pattern_id:
                    # Link all variations in this pattern
                    for variation in pattern.get("variations", []):
                        variation_title = variation.get("title")
                        if variation_title:
                            variation_id = self.record_map["variations"].get(self.normalize_for_matching(variation_title))
                            if variation_id:
                                # Update variation with pattern reference
                                try:
                                    url = f"{self.base_url}/Variations/{variation_id}"
                                    update_fields = {"pattern_reference": [pattern_id]}
                                    resp = requests.patch(url, headers=self.headers, json={"fields": update_fields}, timeout=30)
                                    resp.raise_for_status()
                                    links_created += 1
                                except Exception as e:
                                    self.log(f"Error linking variation {variation_id} to pattern {pattern_id}: {str(e)}", "error")
        
        self.log(f"✅ Variation-Pattern relationships synced: {links_created} links")

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
        
        # Handle relationship syncing for individual table operations with --sync flag
        if enable_linking and len(sync_types) == 1:
            self.log(f"🔗 Syncing relationships for {sync_types[0]} (--sync flag detected)...")
            if "sources" in sync_types:
                self._sync_source_pattern_relationships(data)
            elif "variations" in sync_types:
                self._sync_variation_pattern_relationships(data)
        
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
                    "content": meta.get("content", ""),
                    "base_folder": base_folder  # Add base_folder field as single line string
                }
                result = self._create_or_update("metas", meta_title, fields, force_update=False)
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
                result = self._create_or_update("lenses", lens_name, fields, force_update=False)
                if result:
                    lenses_synced += 1
        
        self.log(f"✅ Lenses sync complete: {lenses_synced} records")

    def _sync_sources(self, data: Dict):
        """Sync Sources with available fields (content only, Patterns relationship handled separately)"""
        sources_synced = 0
        
        # Process sources from patterns within each document
        for doc in data.get("documents", []):
            # Sources are nested within patterns
            for pattern in doc.get("patterns", []):
                for source in pattern.get("parsed_sources", []):
                    source_content = source.get("content")  # This is the primary content
                    
                    if source_content:
                        fields = {
                            "content": source_content  # PRIMARY FIELD (only field available now)
                        }
                        # Note: Patterns relationship will be handled in pattern sync
                        result = self._create_or_update("sources", source_content, fields, force_update=False)
                        if result:
                            sources_synced += 1
                            self.log(f"Source '{source_content[:50]}...' synced")
        
        # Also process standalone sources array if it exists
        for source in data.get("sources", []):
            source_content = source.get("source")  # This is the primary content
            
            if source_content:
                fields = {
                    "content": source_content  # PRIMARY FIELD (only field available now)
                }
                result = self._create_or_update("sources", source_content, fields, force_update=False)
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
                            "content": variation.get("content", "")
                        }
                        
                        # Add pattern linking if enabled and pattern exists
                        pattern_link_msg = ""
                        if enable_linking and pattern_id:
                            fields["pattern_reference"] = [pattern_id]  # Link field
                            pattern_link_msg = f" → pattern: '{pattern_title}'"
                        else:
                            pattern_link_msg = " (no pattern link)"
                        
                        # Note: lens and base_folder fields no longer exist in Variations table
                        link_msg = pattern_link_msg
                        
                        result = self._create_or_update("variations", variation_title, fields, force_update=False)
                        if result:
                            variations_synced += 1
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
                        self.log(f"Debug: Pattern '{pattern_title}' has {len(pattern_sources)} parsed_sources")
                        if pattern_sources:
                            source_ids = []
                            for i, source in enumerate(pattern_sources):
                                # Extract content from source object
                                source_content = source.get("content", "")
                                if source_content:
                                    normalized_content = self.normalize_for_matching(source_content)
                                    source_id = self.record_map["sources"].get(normalized_content)
                                    if source_id:
                                        source_ids.append(source_id)
                                        self.log(f"Debug: Source {i+1} '{source_content[:50]}...' → LINKED")
                                    else:
                                        self.log(f"Debug: Source {i+1} '{source_content[:50]}...' → NOT FOUND in sources table")
                                else:
                                    self.log(f"Debug: Source {i+1} has no content")
                            
                            if source_ids:
                                fields["sources"] = source_ids  # Link to Sources table
                                self.log(f"Pattern '{pattern_title}' linked to {len(source_ids)} sources")
                            else:
                                self.log(f"⚠️ Pattern '{pattern_title}' has NO source links despite {len(pattern_sources)} parsed sources")
                        
                        # Link to Metas (if pattern belongs to specific metas)
                        # Note: This might need custom logic based on your meta-pattern relationships
                        # For now, we'll link all patterns to all metas from the same base_folder
                        if base_folder:
                            meta_ids = []
                            for meta_key, meta_id in self.record_map["metas"].items():
                                meta_ids.append(meta_id)  # Link all metas for now
                            if meta_ids:
                                fields["Metas"] = meta_ids  # Link to Metas table
                    
                    result = self._create_or_update("patterns", pattern_title, fields, force_update=False)
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