"""
Airtable Data Verifier
Reads data from Airtable to verify upload and check relationships
"""

import json
import requests
from typing import Dict, List


def get_table_records(api_token: str, base_id: str, table_name: str, max_records: int = 100) -> List[Dict]:
    """Get records from a table"""
    url = f"https://api.airtable.com/v0/{base_id}/{table_name}"
    headers = {
        "Authorization": f"Bearer {api_token}"
    }
    
    all_records = []
    offset = None
    
    while True:
        params = {"maxRecords": max_records}
        if offset:
            params["offset"] = offset
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            all_records.extend(data.get("records", []))
            offset = data.get("offset")
            
            if not offset:
                break
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            break
    
    return all_records


def verify_variations_in_patterns(api_token: str, base_id: str):
    """Check if variations are linked to patterns"""
    print("\n" + "=" * 80)
    print("VERIFYING VARIATION → PATTERN LINKS")
    print("=" * 80)
    print()
    
    # Get patterns
    patterns = get_table_records(api_token, base_id, "Patterns")
    print(f"✓ Found {len(patterns)} patterns")
    
    # Get variations
    variations = get_table_records(api_token, base_id, "Variations")
    print(f"✓ Found {len(variations)} variations")
    print()
    
    # Check patterns with variations
    patterns_with_variations = 0
    patterns_without_variations = 0
    
    for pattern in patterns:
        fields = pattern.get("fields", {})
        pattern_title = fields.get("pattern_title", "Unknown")
        variations_field = fields.get("variations", [])
        
        if variations_field:
            patterns_with_variations += 1
            print(f"✓ {pattern_title}: {len(variations_field)} variations")
        else:
            patterns_without_variations += 1
            print(f"❌ {pattern_title}: NO VARIATIONS")
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Patterns WITH variations: {patterns_with_variations}")
    print(f"Patterns WITHOUT variations: {patterns_without_variations}")
    print()
    
    # Check variations with pattern_reference
    print("=" * 80)
    print("CHECKING VARIATIONS")
    print("=" * 80)
    print()
    
    variations_with_pattern = 0
    variations_without_pattern = 0
    
    for var in variations[:10]:  # Check first 10
        fields = var.get("fields", {})
        var_title = fields.get("variation_title", "Unknown")
        pattern_ref = fields.get("pattern_reference", [])
        
        if pattern_ref:
            variations_with_pattern += 1
            print(f"✓ {var_title}: linked to pattern")
        else:
            variations_without_pattern += 1
            print(f"❌ {var_title}: NOT linked to pattern")
    
    print()
    print(f"Total: {variations_with_pattern} linked, {variations_without_pattern} not linked (sample of 10)")
    
    return patterns, variations


def main():
    """Main execution"""
    print("=" * 80)
    print("AIRTABLE DATA VERIFIER")
    print("=" * 80)
    
    # Load config
    try:
        with open("config.json", 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("\n❌ config.json not found!")
        return
    
    api_token = config.get("airtable_token")
    base_id = config.get("base_id")
    
    if not api_token or not base_id:
        print("\n❌ Missing credentials in config.json")
        return
    
    # Verify data
    patterns, variations = verify_variations_in_patterns(api_token, base_id)
    
    # Save sample data for inspection
    sample_data = {
        "sample_patterns": [p for p in patterns[:3]],
        "sample_variations": [v for v in variations[:5]]
    }
    
    with open("airtable_sample_data.json", 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, indent=2, ensure_ascii=False)
    
    print("\n✓ Sample data saved to: airtable_sample_data.json")
    print("\nNext: Check why variations aren't linked to patterns")


if __name__ == "__main__":
    main()
