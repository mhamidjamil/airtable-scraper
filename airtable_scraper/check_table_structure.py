#!/usr/bin/env python3
"""
Check Airtable table structure to understand available fields
"""
import requests
import sys
import os
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from config import settings

def check_table_structure():
    """Check the structure of Airtable tables"""
    
    headers = {
        "Authorization": f"Bearer {settings.AIRTABLE_CONFIG['api_token']}",
        "Content-Type": "application/json"
    }
    base_url = f"https://api.airtable.com/v0/{settings.AIRTABLE_CONFIG['base_id']}"
    
    tables_to_check = ["Sources", "Variations", "Patterns"]
    
    for table_name in tables_to_check:
        print(f"=== {table_name.upper()} TABLE STRUCTURE ===")
        
        try:
            resp = requests.get(f"{base_url}/{table_name}?maxRecords=3", headers=headers, timeout=30)
            
            if resp.status_code == 200:
                data = resp.json()
                if data.get("records"):
                    fields = data["records"][0].get("fields", {})
                    print(f"Available fields: {list(fields.keys())}")
                    
                    # Show sample data for debugging
                    print("Sample record:")
                    for key, value in fields.items():
                        if isinstance(value, str) and len(value) > 100:
                            print(f"  {key}: {value[:100]}...")
                        else:
                            print(f"  {key}: {value}")
                else:
                    print("No records found in table")
            else:
                print(f"Error: {resp.status_code} - {resp.text}")
                
        except Exception as e:
            print(f"Exception: {str(e)}")
        
        print()

if __name__ == "__main__":
    check_table_structure()