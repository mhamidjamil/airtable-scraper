#!/usr/bin/env python3
"""Quick script to verify patterns were uploaded successfully"""

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

def count_records(table_name):
    """Count records in a table"""
    url = f"{base_url}/{table_name}"
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        record_count = len(data.get("records", []))
        print(f"{table_name}: {record_count} records")
        
        # Show sample record structure if any exist
        if data.get("records"):
            sample = data["records"][0]
            fields = sample.get("fields", {})
            print(f"  Sample fields: {list(fields.keys())}")
            
    except Exception as e:
        print(f"Error checking {table_name}: {e}")

if __name__ == "__main__":
    print("=== AIRTABLE SYNC VERIFICATION ===")
    count_records("Patterns")
    count_records("Sources")
    count_records("Lenses")
    count_records("Variations")
    count_records("Metas")