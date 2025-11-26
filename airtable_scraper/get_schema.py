#!/usr/bin/env python3
"""Script to get the actual table schema from Airtable Metadata API"""

import requests
import sys
import os
sys.path.append(os.path.dirname(__file__))

from config.settings import AIRTABLE_CONFIG

# Setup API connection
base_id = AIRTABLE_CONFIG['base_id']
api_token = AIRTABLE_CONFIG['api_token']
headers = {"Authorization": f"Bearer {api_token}"}

def get_table_schema():
    """Get the table schema using the metadata API"""
    url = f"https://api.airtable.com/v0/meta/bases/{base_id}/tables"
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        print("=== BASE SCHEMA ===")
        
        for table in data.get("tables", []):
            table_name = table.get("name")
            if table_name in ["Patterns", "Sources"]:
                print(f"\n--- {table_name} Table ---")
                print(f"ID: {table.get('id')}")
                print(f"Primary Field: {table.get('primaryFieldId')}")
                
                fields = table.get("fields", [])
                print(f"Fields ({len(fields)}):")
                
                for field in fields:
                    field_name = field.get("name")
                    field_type = field.get("type")
                    field_id = field.get("id")
                    print(f"  - {field_name} ({field_type}) [ID: {field_id}]")
                    
                    # If it's a linked record field, show details
                    if field_type == "multipleRecordLinks":
                        options = field.get("options", {})
                        linked_table_id = options.get("linkedTableId")
                        print(f"    → Links to table ID: {linked_table_id}")
                        
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"Error getting schema: {e}")

if __name__ == "__main__":
    get_table_schema()