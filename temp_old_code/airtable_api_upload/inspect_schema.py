"""
Airtable Schema Inspector
Reads your Airtable base and shows what fields exist in each table
"""

import json
import requests
from typing import Dict, List


def get_base_schema(api_token: str, base_id: str) -> Dict:
    """Get schema for all tables in the base"""
    url = f"https://api.airtable.com/v0/meta/bases/{base_id}/tables"
    headers = {
        "Authorization": f"Bearer {api_token}"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Error {response.status_code}: {response.text}")
        return {}


def display_schema(schema: Dict):
    """Display schema in readable format"""
    tables = schema.get("tables", [])
    
    print("\n" + "=" * 80)
    print("AIRTABLE SCHEMA")
    print("=" * 80)
    print(f"\nFound {len(tables)} tables:\n")
    
    for table in tables:
        table_name = table.get("name", "Unknown")
        table_id = table.get("id", "")
        fields = table.get("fields", [])
        
        print(f"📋 Table: {table_name}")
        print(f"   ID: {table_id}")
        print(f"   Fields ({len(fields)}):")
        
        for field in fields:
            field_name = field.get("name", "")
            field_type = field.get("type", "")
            field_id = field.get("id", "")
            
            # Show if it's a link field
            if field_type == "multipleRecordLinks":
                linked_table = field.get("options", {}).get("linkedTableId", "")
                print(f"      • {field_name} ({field_type} → {linked_table})")
            else:
                print(f"      • {field_name} ({field_type})")
        
        print()


def compare_with_expected(schema: Dict):
    """Compare actual schema with expected fields"""
    expected_fields = {
        "Lenses": ["lens_name", "content", "patterns"],
        "Sources": ["source_name", "patterns"],
        "METAS": ["title", "subtitle", "content", "base_folder", "patterns"],
        "Variations": ["variation_title", "variation_number", "content", "linked_pattern"],
        "Patterns": ["pattern_id", "pattern_title", "overview", "choice", 
                    "base_folder", "drive_doc_url", "lens", "sources", "variations"]
    }
    
    tables = schema.get("tables", [])
    
    print("=" * 80)
    print("FIELD COMPARISON (Expected vs Actual)")
    print("=" * 80)
    print()
    
    for table in tables:
        table_name = table.get("name", "")
        
        if table_name not in expected_fields:
            continue
        
        actual_fields = [f.get("name") for f in table.get("fields", [])]
        expected = expected_fields[table_name]
        
        print(f"📋 {table_name}:")
        print(f"   Expected fields: {', '.join(expected)}")
        print(f"   Actual fields: {', '.join(actual_fields)}")
        
        # Missing fields
        missing = [f for f in expected if f not in actual_fields]
        if missing:
            print(f"   ❌ MISSING: {', '.join(missing)}")
        else:
            print(f"   ✅ All expected fields present")
        
        # Extra fields
        extra = [f for f in actual_fields if f not in expected]
        if extra:
            print(f"   ℹ️  Extra fields: {', '.join(extra)}")
        
        print()


def generate_field_mapping(schema: Dict) -> Dict:
    """
    Generate mapping for upload script
    Maps our expected field names to actual Airtable field names
    """
    tables = schema.get("tables", [])
    mapping = {}
    
    for table in tables:
        table_name = table.get("name", "")
        fields = table.get("fields", [])
        
        field_map = {}
        for field in fields:
            field_name = field.get("name", "")
            field_type = field.get("type", "")
            field_id = field.get("id", "")
            
            field_map[field_name] = {
                "id": field_id,
                "type": field_type
            }
        
        mapping[table_name] = field_map
    
    return mapping


def main():
    """Main execution"""
    print("=" * 80)
    print("AIRTABLE SCHEMA INSPECTOR")
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
    
    print(f"\nReading schema from base: {base_id}...")
    
    # Get schema
    schema = get_base_schema(api_token, base_id)
    
    if not schema:
        return
    
    # Display schema
    display_schema(schema)
    
    # Compare with expected
    compare_with_expected(schema)
    
    # Generate mapping
    mapping = generate_field_mapping(schema)
    
    # Save mapping
    with open("field_mapping.json", 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)
    
    print("=" * 80)
    print("FIELD MAPPING SAVED")
    print("=" * 80)
    print("\nSaved field mapping to: field_mapping.json")
    print("\nNext steps:")
    print("1. Review the field comparison above")
    print("2. Either:")
    print("   A) Add missing fields to Airtable tables, OR")
    print("   B) I'll update upload script to match your current schema")
    print()


if __name__ == "__main__":
    main()
