#!/usr/bin/env python3
"""
Enhanced field discovery tool using Airtable Schema API
"""

import requests
from config.settings import AIRTABLE_CONFIG

def get_base_schema():
    """Get the complete base schema from Airtable"""
    
    url = f"https://api.airtable.com/v0/meta/bases/{AIRTABLE_CONFIG['base_id']}/tables"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_CONFIG['api_token']}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Schema API Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error fetching schema: {e}")
        return None

def main():
    """Check base schema and field structure"""
    print("AIRTABLE BASE SCHEMA DISCOVERY")
    print("=" * 50)
    
    schema = get_base_schema()
    if not schema:
        print("Could not fetch schema. Let's try manual field discovery...")
        return
    
    print(f"Found {len(schema.get('tables', []))} tables in base:")
    
    for table in schema.get('tables', []):
        table_name = table.get('name')
        table_id = table.get('id')
        fields = table.get('fields', [])
        
        print(f"\n📋 TABLE: {table_name} (ID: {table_id})")
        print(f"   Fields ({len(fields)}):")
        
        for field in fields:
            field_name = field.get('name')
            field_type = field.get('type')
            field_id = field.get('id')
            print(f"     - {field_name} ({field_type}) [ID: {field_id}]")
    
    print("\n" + "=" * 50)
    print("Schema discovery complete!")

if __name__ == "__main__":
    main()