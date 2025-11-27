#!/usr/bin/env python3
"""
Debug script to see all field names in Airtable records
"""

import requests
import json
from config.settings import AIRTABLE_CONFIG

def debug_schema():
    headers = {
        "Authorization": f"Bearer {AIRTABLE_CONFIG['api_token']}",
        "Content-Type": "application/json"
    }
    base_url = f"https://api.airtable.com/v0/{AIRTABLE_CONFIG['base_id']}"
    
    print("🔍 Debugging Airtable Schema...")
    print("=" * 40)
    
    # Get one variation record to see all fields
    try:
        variations_url = f"{base_url}/Variations"
        params = {"maxRecords": 1}
        
        response = requests.get(variations_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get('records'):
            record = data['records'][0]
            fields = record.get('fields', {})
            
            print("📋 VARIATION FIELDS:")
            print("-" * 20)
            for field_name, field_value in fields.items():
                field_type = type(field_value).__name__
                field_preview = str(field_value)[:50] + ("..." if len(str(field_value)) > 50 else "")
                print(f"  • {field_name} ({field_type}): {field_preview}")
        
        print("\n" + "=" * 40)
        
        # Get one pattern record to see all fields
        patterns_url = f"{base_url}/Patterns"
        response = requests.get(patterns_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get('records'):
            record = data['records'][0]
            fields = record.get('fields', {})
            
            print("📋 PATTERN FIELDS:")
            print("-" * 20)
            for field_name, field_value in fields.items():
                field_type = type(field_value).__name__
                field_preview = str(field_value)[:50] + ("..." if len(str(field_value)) > 50 else "")
                print(f"  • {field_name} ({field_type}): {field_preview}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_schema()