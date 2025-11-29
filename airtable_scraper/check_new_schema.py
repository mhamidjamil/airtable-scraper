#!/usr/bin/env python3
"""
Check Updated Airtable Schema
Verify the new fields and tables structure
"""

import requests
import json
from config.settings import AIRTABLE_CONFIG

def check_table_schema(table_name):
    """Check the schema of a specific table"""
    print(f"\n=== {table_name.upper()} TABLE SCHEMA ===")
    
    headers = {
        "Authorization": f"Bearer {AIRTABLE_CONFIG['api_token']}",
        "Content-Type": "application/json"
    }
    
    base_url = f"https://api.airtable.com/v0/{AIRTABLE_CONFIG['base_id']}"
    
    try:
        # Get a sample record to see available fields
        url = f"{base_url}/{table_name}?maxRecords=1"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('records'):
                fields = data['records'][0]['fields']
                print(f"Available fields: {list(fields.keys())}")
                
                # Show field types and sample data
                for field_name, value in fields.items():
                    field_type = type(value).__name__
                    if isinstance(value, list):
                        if value and isinstance(value[0], str):
                            field_type = "Array of record IDs (linked records)"
                        else:
                            field_type = "Array"
                    sample = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                    print(f"  - {field_name}: {field_type} = {sample}")
            else:
                print("No records found in table")
                
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Error checking {table_name}: {str(e)}")

def main():
    """Check all table schemas"""
    tables = ['Patterns', 'Choices', 'Variations', 'Sources', 'Lenses', 'Metas']
    
    print("AIRTABLE SCHEMA VERIFICATION")
    print("=" * 50)
    
    for table in tables:
        check_table_schema(table)
    
    print(f"\n{'='*50}")
    print("Schema check complete!")

if __name__ == "__main__":
    main()