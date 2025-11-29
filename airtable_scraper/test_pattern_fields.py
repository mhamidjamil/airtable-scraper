#!/usr/bin/env python3
"""
Manual test to create a single pattern record
"""

import requests
from config.settings import AIRTABLE_CONFIG

def test_pattern_creation():
    """Test creating a single pattern with correct field names"""
    
    url = f"https://api.airtable.com/v0/{AIRTABLE_CONFIG['base_id']}/Patterns"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_CONFIG['api_token']}",
        "Content-Type": "application/json"
    }
    
    # Test data with the exact field names from schema
    test_fields = {
        "pattern_title": "TEST PATTERN - SAMPLE",
        "overview": "This is a test pattern overview to verify field mappings work correctly.",
        "variation_count": "5",
        "base_folder": "TEST"
    }
    
    print("Testing pattern creation with fields:")
    for field, value in test_fields.items():
        print(f"  {field}: {value}")
    
    try:
        response = requests.post(url, 
            headers=headers, 
            json={"records": [{"fields": test_fields}]}
        )
        
        if response.status_code == 200:
            print("✅ SUCCESS! Pattern created successfully")
            created_record = response.json()['records'][0]
            print(f"   Record ID: {created_record['id']}")
            print(f"   Created fields: {list(created_record['fields'].keys())}")
            return created_record['id']
        else:
            print(f"❌ FAILED: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None

def cleanup_test_record(record_id):
    """Clean up the test record"""
    if not record_id:
        return
        
    url = f"https://api.airtable.com/v0/{AIRTABLE_CONFIG['base_id']}/Patterns/{record_id}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_CONFIG['api_token']}"
    }
    
    try:
        response = requests.delete(url, headers=headers)
        if response.status_code == 200:
            print("🧹 Test record cleaned up successfully")
        else:
            print(f"⚠️ Cleanup failed: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Cleanup error: {e}")

if __name__ == "__main__":
    print("PATTERN FIELD TESTING")
    print("=" * 30)
    
    record_id = test_pattern_creation()
    
    if record_id:
        input("\nPress Enter to clean up the test record...")
        cleanup_test_record(record_id)
    
    print("\nTest complete!")