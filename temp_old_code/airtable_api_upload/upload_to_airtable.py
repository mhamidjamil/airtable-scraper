"""
Airtable API Upload Script
Uploads JSON data to Airtable with proper ID mapping and relationship linking

Upload Order: Lenses → Sources → METAS → Variations → Patterns
"""

import os
import json
import requests
import time
from datetime import datetime
from typing import Dict, List, Any


class AirtableUploader:
    """Handles batch upload to Airtable with ID mapping"""
    
    def __init__(self, api_token: str, base_id: str):
        self.api_token = api_token
        self.base_id = base_id
        self.base_url = f"https://api.airtable.com/v0/{base_id}"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        
        # ID mappings (filled during upload)
        self.lens_id_map = {}
        self.source_id_map = {}
        self.meta_id_map = {}
        self.variation_id_map = {}
        
        # Logging
        self.log_dir = "logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = os.path.join(
            self.log_dir, 
            f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
    
    def log(self, message: str):
        """Log message to file and console"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_msg + "\n")
    
    def batch_upload(self, table_name: str, records: List[Dict], 
                    batch_size: int = 10) -> List[str]:
        """
        Upload records in batches
        Returns list of created record IDs
        """
        url = f"{self.base_url}/{table_name}"
        all_ids = []
        
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            
            try:
                payload = {"records": batch}
                response = requests.post(url, headers=self.headers, json=payload)
                
                if response.status_code == 200:
                    created_records = response.json().get("records", [])
                    batch_ids = [rec["id"] for rec in created_records]
                    all_ids.extend(batch_ids)
                    
                    self.log(f"  ✓ Batch {i//batch_size + 1}: {len(batch_ids)} records created")
                else:
                    self.log(f"  ✗ Batch {i//batch_size + 1} failed: {response.status_code}")
                    self.log(f"    Error: {response.text}")
                
                # Rate limiting (5 requests per second)
                time.sleep(0.2)
                
            except Exception as e:
                self.log(f"  ✗ Batch {i//batch_size + 1} error: {str(e)}")
        
        return all_ids
    
    def upload_lenses(self, lenses_data: List[Dict]) -> Dict[str, str]:
        """
        Upload Lenses table
        Returns: lens_name → airtable_id mapping
        """
        self.log("\n" + "=" * 80)
        self.log("UPLOADING LENSES")
        self.log("=" * 80)
        
        records = []
        lens_names = []
        
        for lens in lenses_data:
            records.append({
                "fields": {
                    "lens_name": lens["lens_name"],
                    "content": lens.get("content", "")
                    # Note: Patterns field is auto-created reverse link
                }
            })
            lens_names.append(lens["lens_name"])
        
        self.log(f"Uploading {len(records)} lenses...")
        ids = self.batch_upload("Lenses", records)
        
        # Create mapping
        for name, airtable_id in zip(lens_names, ids):
            self.lens_id_map[name] = airtable_id
        
        self.log(f"✓ {len(ids)} lenses uploaded\n")
        return self.lens_id_map
    
    def upload_sources(self, sources_data: List[Dict]) -> Dict[str, str]:
        """
        Upload Sources table
        Returns: source_name → airtable_id mapping
        """
        self.log("\n" + "=" * 80)
        self.log("UPLOADING SOURCES")
        self.log("=" * 80)
        
        records = []
        source_names = []
        
        for source in sources_data:
            records.append({
                "fields": {
                    "source_name": source["source_name"]
                    # Note: Patterns field is auto-created reverse link
                }
            })
            source_names.append(source["source_name"])
        
        self.log(f"Uploading {len(records)} sources...")
        ids = self.batch_upload("Sources", records)
        
        # Create mapping
        for name, airtable_id in zip(source_names, ids):
            self.source_id_map[name] = airtable_id
        
        self.log(f"✓ {len(ids)} sources uploaded\n")
        return self.source_id_map
    
    def upload_metas(self, metas_data: List[Dict]) -> Dict[str, str]:
        """
        Upload METAS table
        Returns: meta_title → airtable_id mapping
        """
        self.log("\n" + "=" * 80)
        self.log("UPLOADING METAS")
        self.log("=" * 80)
        
        records = []
        meta_titles = []
        
        for meta in metas_data:
            records.append({
                "fields": {
                    "title": meta["title"],
                    "subtitle": meta.get("subtitle", ""),
                    "content": meta.get("content", ""),
                    "base_folder": meta.get("base_folder", "")
                    # Note: linked_patterns will be filled from Patterns side
                }
            })
            meta_titles.append(meta["title"])
        
        self.log(f"Uploading {len(records)} METAS...")
        ids = self.batch_upload("Metas", records)  # Note: table name is "Metas" not "METAS"
        
        # Create mapping
        for title, airtable_id in zip(meta_titles, ids):
            self.meta_id_map[title] = airtable_id
        
        self.log(f"✓ {len(ids)} METAS uploaded\n")
        return self.meta_id_map
    
    def upload_variations(self, variations_data: List[Dict]) -> Dict[str, str]:
        """
        Upload Variations table
        Returns: variation_temp_id → airtable_id mapping
        """
        self.log("\n" + "=" * 80)
        self.log("UPLOADING VARIATIONS")
        self.log("=" * 80)
        
        records = []
        temp_ids = []
        
        for i, var in enumerate(variations_data):
            # Generate temp ID from pattern_temp_id
            pattern_temp = var.get("pattern_temp_id", "unknown")
            temp_id = f"{pattern_temp}_var{i+1}"
            
            records.append({
                "fields": {
                    "variation_title": var["variation_title"],
                    "content": var.get("content", "")
                    # Note: pattern_reference will be added from Patterns side
                    # variation_number field doesn't exist in your Airtable
                }
            })
            temp_ids.append(temp_id)
        
        self.log(f"Uploading {len(records)} variations...")
        ids = self.batch_upload("Variations", records)
        
        # Create mapping
        for temp_id, airtable_id in zip(temp_ids, ids):
            self.variation_id_map[temp_id] = airtable_id
        
        self.log(f"✓ {len(ids)} variations uploaded\n")
        return self.variation_id_map
    
    def upload_patterns(self, patterns_data: List[Dict]):
        """
        Upload Patterns table with all relationships linked
        Uses ID mappings from previous uploads
        """
        self.log("\n" + "=" * 80)
        self.log("UPLOADING PATTERNS")
        self.log("=" * 80)
        
        records = []
        
        for pattern in patterns_data:
            # Get lens ID
            lens_name = pattern.get("lens", "")
            lens_id = self.lens_id_map.get(lens_name)
            
            # Get source IDs
            source_names = pattern.get("sources", [])
            source_ids = [self.source_id_map.get(s) for s in source_names if s in self.source_id_map]
            
            # Get variation IDs
            variation_temp_ids = pattern.get("variation_temp_ids", [])
            variation_ids = [self.variation_id_map.get(v) for v in variation_temp_ids if v in self.variation_id_map]
            
            # Build fields (only fields that exist in Airtable)
            fields = {
                "pattern_title": pattern["pattern_title"],
                "overview": pattern.get("overview", ""),
                "choice": pattern.get("choice", ""),
                "base_folder": pattern.get("base_folder", "")
                # Note: pattern_id and drive_doc_url don't exist in your Airtable
            }
            
            # Add links (only if IDs exist)
            if lens_id:
                fields["lens"] = [lens_id]
            if source_ids:
                fields["sources"] = source_ids
            if variation_ids:
                fields["variations"] = variation_ids
            
            # Link to all METAS from same base_folder (optional - can enable if needed)
            # base_folder = pattern.get("base_folder", "")
            # meta_ids = [mid for title, mid in self.meta_id_map.items() 
            #            if base_folder in title]  # Basic matching
            # if meta_ids:
            #     fields["Metas"] = meta_ids  # Note: field name is "Metas" not "metas"
            
            records.append({"fields": fields})
        
        self.log(f"Uploading {len(records)} patterns...")
        ids = self.batch_upload("Patterns", records)
        
        self.log(f"✓ {len(ids)} patterns uploaded\n")

    
    def save_id_mappings(self):
        """Save ID mappings to JSON files for audit"""
        mapping_dir = "id_mappings"
        os.makedirs(mapping_dir, exist_ok=True)
        
        mappings = {
            "lens_id_map.json": self.lens_id_map,
            "source_id_map.json": self.source_id_map,
            "meta_id_map.json": self.meta_id_map,
            "variation_id_map.json": self.variation_id_map
        }
        
        for filename, mapping in mappings.items():
            filepath = os.path.join(mapping_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(mapping, f, indent=2, ensure_ascii=False)
            self.log(f"  Saved {filename}")


def main():
    """Main upload flow"""
    print("=" * 80)
    print("AIRTABLE API UPLOAD")
    print("=" * 80)
    print()
    
    # Load configuration
    config_file = "config.json"
    if not os.path.exists(config_file):
        print("❌ config.json not found!")
        print("\nPlease create config.json with:")
        print("""{
  "airtable_token": "your_token_here",
  "base_id": "your_base_id_here"
}""")
        print("\nSee README.md for instructions on getting credentials.")
        return
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    api_token = config.get("airtable_token")
    base_id = config.get("base_id")
    
    if not api_token or not base_id:
        print("❌ Missing credentials in config.json")
        return
    
    # Initialize uploader
    uploader = AirtableUploader(api_token, base_id)
    uploader.log("Starting Airtable upload...")
    
    # Load JSON data
    json_dir = "json_data"
    
    with open(os.path.join(json_dir, "lenses.json"), 'r', encoding='utf-8') as f:
        lenses_data = json.load(f)
    
    with open(os.path.join(json_dir, "sources.json"), 'r', encoding='utf-8') as f:
        sources_data = json.load(f)
    
    with open(os.path.join(json_dir, "metas.json"), 'r', encoding='utf-8') as f:
        metas_data = json.load(f)
    
    with open(os.path.join(json_dir, "variations.json"), 'r', encoding='utf-8') as f:
        variations_data = json.load(f)
    
    with open(os.path.join(json_dir, "patterns.json"), 'r', encoding='utf-8') as f:
        patterns_data = json.load(f)
    
    # Upload in correct order
    uploader.upload_lenses(lenses_data)
    uploader.upload_sources(sources_data)
    uploader.upload_metas(metas_data)
    uploader.upload_variations(variations_data)
    uploader.upload_patterns(patterns_data)
    
    # Save ID mappings
    uploader.log("\n" + "=" * 80)
    uploader.log("SAVING ID MAPPINGS")
    uploader.log("=" * 80)
    uploader.save_id_mappings()
    
    uploader.log("\n" + "=" * 80)
    uploader.log("UPLOAD COMPLETE!")
    uploader.log("=" * 80)
    uploader.log(f"\nLog saved to: {uploader.log_file}")
    uploader.log("Check Airtable to verify all records and links!")


if __name__ == "__main__":
    main()
