"""
Complete Variation Link Fixer
Finds ALL variations in Airtable and links them to their patterns
"""

import json
import requests
import time


def get_all_variations(api_token: str, base_id: str):
    """Get all variations from Airtable"""
    headers = {"Authorization": f"Bearer {api_token}"}
    url = f"https://api.airtable.com/v0/{base_id}/Variations"
    
    all_variations = []
    offset = None
    
    while True:
        params = {}
        if offset:
            params["offset"] = offset
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            all_variations.extend(data.get("records", []))
            offset = data.get("offset")
            if not offset:
                break
        else:
            print(f"❌ Error: {response.text}")
            break
    
    return all_variations


def get_all_patterns(api_token: str, base_id: str):
    """Get all patterns from Airtable"""
    headers = {"Authorization": f"Bearer {api_token}"}
    url = f"https://api.airtable.com/v0/{base_id}/Patterns"
    
    all_patterns = []
    offset = None
    
    while True:
        params = {}
        if offset:
            params["offset"] = offset
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            all_patterns.extend(data.get("records", []))
            offset = data.get("offset")
            if not offset:
                break
        else:
            print(f"❌ Error: {response.text}")
            break
    
    return all_patterns


def link_variation_to_pattern(api_token: str, base_id: str, variation_id: str, pattern_id: str):
    """Link a variation to its pattern"""
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    url = f"https://api.airtable.com/v0/{base_id}/Variations/{variation_id}"
    update_data = {
        "fields": {
            "pattern_reference": [pattern_id]
        }
    }
    
    response = requests.patch(url, headers=headers, json=update_data)
    return response.status_code == 200


def main():
    """Main execution"""
    print("=" * 80)
    print("COMPLETE VARIATION LINK FIXER")
    print("=" * 80)
    print()
    
    # Load config
    try:
        with open("config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ config.json not found!")
        return
    
    api_token = config.get("airtable_token")
    base_id = config.get("base_id")
    
    if not api_token or not base_id:
        print("❌ Missing credentials in config.json")
        return
    
    # Get all data from Airtable
    print("Fetching all variations from Airtable...")
    variations = get_all_variations(api_token, base_id)
    print(f"✓ Found {len(variations)} variations\n")
    
    print("Fetching all patterns from Airtable...")
    patterns = get_all_patterns(api_token, base_id)
    print(f"✓ Found {len(patterns)} patterns\n")
    
    # Build pattern title → ID map
    pattern_title_to_id = {}
    pattern_id_to_variations = {}
    
    for pattern in patterns:
        fields = pattern.get("fields", {})
        title = fields.get("pattern_title", "")
        pattern_id = pattern["id"]
        
        if title:
            pattern_title_to_id[title] = pattern_id
            pattern_id_to_variations[pattern_id] = fields.get("variations", [])
    
    # Load patterns JSON to find which variations belong to which patterns
    try:
        with open("json_data/patterns.json", 'r', encoding='utf-8') as f:
            patterns_data = json.load(f)
    except FileNotFoundError:
        print("❌ json_data/patterns.json not found!")
        print("Cannot determine variation → pattern mapping without source data")
        return
    
    # Build variation title → pattern title map from JSON
    variation_to_pattern = {}
    
    for pattern in patterns_data:
        pattern_title = pattern.get("pattern_title", "")
        
        # Get variation temp IDs
        var_temp_ids = pattern.get("variation_temp_ids", [])
        
        # Load variations JSON to get titles
        if var_temp_ids:
            try:
                with open("json_data/variations.json", 'r', encoding='utf-8') as f:
                    variations_data = json.load(f)
                
                # Find variations by temp ID
                for var in variations_data:
                    var_temp_id = var.get("pattern_temp_id", "")
                    var_title = var.get("variation_title", "")
                    pattern_temp_id = pattern.get("pattern_temp_id", "")
                    
                    # Check if this variation belongs to this pattern
                    if var_temp_id == pattern_temp_id and var_title:
                        variation_to_pattern[var_title] = pattern_title
                        
            except Exception as e:
                print(f"⚠️  Error loading variations: {e}")
    
    print(f"Mapped {len(variation_to_pattern)} variations to patterns from JSON\n")
    
    # Now check each variation in Airtable
    print("Checking variations in Airtable...")
    print("=" * 80)
    
    linked_count = 0
    unlinked_count = 0
    updated_count = 0
    not_in_json_count = 0
    
    for var in variations:
        var_id = var["id"]
        fields = var.get("fields", {})
        var_title = fields.get("variation_title", "Unknown")
        pattern_ref = fields.get("pattern_reference", [])
        
        if pattern_ref:
            linked_count += 1
            print(f"✓ {var_title}: Already linked")
        else:
            unlinked_count += 1
            
            # Try to find pattern for this variation
            pattern_title = variation_to_pattern.get(var_title)
            
            if pattern_title:
                pattern_id = pattern_title_to_id.get(pattern_title)
                
                if pattern_id:
                    # Link it!
                    print(f"  Linking: {var_title} → {pattern_title}")
                    success = link_variation_to_pattern(api_token, base_id, var_id, pattern_id)
                    
                    if success:
                        updated_count += 1
                        print(f"  ✓ Linked successfully")
                    else:
                        print(f"  ✗ Failed to link")
                    
                    time.sleep(0.2)  # Rate limiting
                else:
                    print(f"❌ {var_title}: Pattern '{pattern_title}' not found in Airtable")
            else:
                not_in_json_count += 1
                print(f"⚠️  {var_title}: NOT in patterns.json (can't determine which pattern it belongs to)")
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total variations: {len(variations)}")
    print(f"  Already linked: {linked_count}")
    print(f"  Newly linked: {updated_count}")
    print(f"  Still unlinked: {unlinked_count - updated_count}")
    print(f"  Not in JSON (can't link): {not_in_json_count}")
    print()
    
    if not_in_json_count > 0:
        print("⚠️  WARNING: Some variations in Airtable are not in patterns.json")
        print("   These may be from a newer extraction. You need to:")
        print("   1. Re-run generate_json.py with latest extraction data")
        print("   2. Re-run this script to link the new variations")


if __name__ == "__main__":
    main()
