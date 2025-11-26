"""
Fix Variation → Pattern Links in Airtable
Updates existing variation records to link them to their patterns
"""

import json
import requests
import time


def update_variation_links(api_token: str, base_id: str):
    """Update variations to link to their patterns"""
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    # Load ID mappings
    with open("id_mappings/variation_id_map.json", 'r', encoding='utf-8') as f:
        variation_id_map = json.load(f)
    
    # Load pattern data to get pattern titles → IDs
    patterns_url = f"https://api.airtable.com/v0/{base_id}/Patterns"
    response = requests.get(patterns_url, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to get patterns: {response.text}")
        return
    
    patterns = response.json().get("records", [])
    pattern_title_to_id = {}
    for p in patterns:
        title = p["fields"].get("pattern_title")
        if title:
            pattern_title_to_id[title] = p["id"]
    
    print(f"✓ Found {len(pattern_title_to_id)} patterns")
    
    # Load patterns JSON to get variation → pattern mapping
    with open("json_data/patterns.json", 'r', encoding='utf-8') as f:
        patterns_data = json.load(f)
    
    # Build variation temp ID → pattern title mapping
    var_to_pattern = {}
    for pattern in patterns_data:
        pattern_title = pattern.get("pattern_title")
        var_temp_ids = pattern.get("variation_temp_ids", [])
        
        for var_temp_id in var_temp_ids:
            var_to_pattern[var_temp_id] = pattern_title
    
    print(f"✓ Built variation → pattern mapping for {len(var_to_pattern)} variations")
    print()
    
    # Update variations
    print("Updating variations...")
    update_count = 0
    failed_count = 0
    
    for var_temp_id, var_airtable_id in variation_id_map.items():
        pattern_title = var_to_pattern.get(var_temp_id)
        
        if not pattern_title:
            print(f"  ⚠️  No pattern found for {var_temp_id}")
            continue
        
        pattern_id = pattern_title_to_id.get(pattern_title)
        
        if not pattern_id:
            print(f"  ⚠️  Pattern '{pattern_title}' not found in Airtable")
            failed_count += 1
            continue
        
        # Update variation
        update_url = f"https://api.airtable.com/v0/{base_id}/Variations/{var_airtable_id}"
        update_data = {
            "fields": {
                "pattern_reference": [pattern_id]
            }
        }
        
        response = requests.patch(update_url, headers=headers, json=update_data)
        
        if response.status_code == 200:
            update_count += 1
            if update_count % 10 == 0:
                print(f"  ✓ Updated {update_count} variations...")
        else:
            failed_count += 1
            print(f"  ✗ Failed to update {var_temp_id}: {response.text}")
        
        # Rate limiting
        time.sleep(0.2)
    
    print()
    print("=" * 80)
    print("UPDATE COMPLETE")
    print("=" * 80)
    print(f"✓ Successfully updated: {update_count} variations")
    print(f"✗ Failed: {failed_count} variations")
    print()
    print("Check Airtable - patterns should now show linked variations!")


def main():
    """Main execution"""
    print("=" * 80)
    print("FIXING VARIATION → PATTERN LINKS")
    print("=" * 80)
    print()
    
    # Load config
    try:
        with open("config.json", 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ config.json not found!")
        return
    
    api_token = config.get("airtable_token")
    base_id = config.get("base_id")
    
    if not api_token or not base_id:
        print("❌ Missing credentials in config.json")
        return
    
    update_variation_links(api_token, base_id)


if __name__ == "__main__":
    main()
