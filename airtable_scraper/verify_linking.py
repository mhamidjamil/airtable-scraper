#!/usr/bin/env python3
"""
Quick verification script to check if pattern-variation linking is working in Airtable
"""

import requests
import json
import time
from config.settings import AIRTABLE_CONFIG

def check_linking():
    headers = {
        "Authorization": f"Bearer {AIRTABLE_CONFIG['api_token']}",
        "Content-Type": "application/json"
    }
    base_url = f"https://api.airtable.com/v0/{AIRTABLE_CONFIG['base_id']}"
    
    print("🔍 Checking Pattern-Variation Linking in Airtable...")
    print("=" * 50)
    
    # Get a few variations to check their Pattern Reference field
    try:
        variations_url = f"{base_url}/Variations"
        params = {
            "maxRecords": 5
        }
        
        response = requests.get(variations_url, headers=headers, params=params)
        response.raise_for_status()
        variations_data = response.json()
        
        print(f"📊 Found {len(variations_data.get('records', []))} variations")
        print()
        
        for record in variations_data.get('records', []):
            fields = record.get('fields', {})
            variation_title = fields.get('variation_title', 'Unknown')[:50] + "..."
            pattern_ref = fields.get('Pattern Reference', 'NOT LINKED')
            base_folder = fields.get('base_folder', 'Unknown')
            
            status = "✅ LINKED" if pattern_ref and pattern_ref != 'NOT LINKED' else "❌ NOT LINKED"
            print(f"{status} | {base_folder} | {variation_title}")
            if pattern_ref and pattern_ref != 'NOT LINKED':
                print(f"         Pattern ID: {pattern_ref}")
            print()
    
    except Exception as e:
        print(f"❌ Error checking variations: {e}")
        
    # Now check patterns to see if they have variations
    try:
        patterns_url = f"{base_url}/Patterns"
        params = {
            "maxRecords": 5,
            "fields[]": ["pattern_title", "variations", "base_folder"]
        }
        
        response = requests.get(patterns_url, headers=headers, params=params)
        response.raise_for_status()
        patterns_data = response.json()
        
        print("📋 PATTERN VARIATIONS CHECK:")
        print("-" * 30)
        
        for record in patterns_data.get('records', []):
            fields = record.get('fields', {})
            pattern_title = fields.get('pattern_title', 'Unknown')[:50] + "..."
            variations = fields.get('variations', [])
            base_folder = fields.get('base_folder', 'Unknown')
            
            count = len(variations) if variations else 0
            status = "✅" if count > 0 else "❌"
            
            print(f"{status} | {base_folder} | {pattern_title}")
            print(f"         Variations: {count}")
            print()
            
    except Exception as e:
        print(f"❌ Error checking patterns: {e}")

if __name__ == "__main__":
    check_linking()