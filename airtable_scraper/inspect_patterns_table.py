#!/usr/bin/env python3
"""Quick script to inspect the Patterns table schema in Airtable"""

import requests
import sys
import os
sys.path.append(os.path.dirname(__file__))

from config.settings import AIRTABLE_CONFIG

# Setup API connection
base_id = AIRTABLE_CONFIG['base_id']
api_token = AIRTABLE_CONFIG['api_token']
headers = {"Authorization": f"Bearer {api_token}"}
base_url = f"https://api.airtable.com/v0/{base_id}"

def inspect_table(table_name):
    """Get a few records from the table to see the field structure"""
    url = f"{base_url}/{table_name}?maxRecords=1"
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        print(f"\n=== {table_name} Table Structure ===")
        print(f"URL: {url}")
        print(f"Response Status: {response.status_code}")
        
        if "records" in data and data["records"]:
            record = data["records"][0]
            fields = record.get("fields", {})
            print(f"Available fields in {table_name}:")
            for field_name, field_value in fields.items():
                field_type = type(field_value).__name__
                if isinstance(field_value, list):
                    list_content = f"[{len(field_value)} items]" if field_value else "[]"
                    print(f"  - {field_name} ({field_type}): {list_content}")
                else:
                    preview = str(field_value)[:50] + "..." if len(str(field_value)) > 50 else str(field_value)
                    print(f"  - {field_name} ({field_type}): {preview}")
        else:
            print(f"No records found in {table_name} table")
            
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error for {table_name}: {e}")
        print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"Error inspecting {table_name}: {e}")

if __name__ == "__main__":
    # Check both Patterns and Sources tables
    inspect_table("Patterns")
    inspect_table("Sources")