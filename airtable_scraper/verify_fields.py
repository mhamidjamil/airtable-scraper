#!/usr/bin/env python3
"""
Field verification tool to identify correct Airtable field names
"""

import requests
from config.settings import AIRTABLE_CONFIG

def check_table_structure(table_name):
    """Try to get table structure by attempting to create a minimal test record"""
    
    url = f"https://api.airtable.com/v0/{AIRTABLE_CONFIG['base_id']}/{table_name}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_CONFIG['api_token']}",
        "Content-Type": "application/json"
    }
    
    print(f"\n=== CHECKING {table_name.upper()} TABLE ===")
    
    # First try to get existing records to see field structure
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get('records'):
                print(f"Found {len(data['records'])} existing records")
                first_record = data['records'][0]
                print(f"Field names in {table_name}: {list(first_record['fields'].keys())}")
                return list(first_record['fields'].keys())
            else:
                print(f"Table {table_name} exists but is empty")
        elif response.status_code == 403:
            print(f"❌ 403 Forbidden - Table '{table_name}' does not exist!")
            return None
        elif response.status_code == 404:
            print(f"❌ 404 Not Found - Table '{table_name}' not found!")
            return None
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error checking {table_name}: {e}")
        return None
    
    # Try to create a minimal test record to discover required fields
    test_data = {}
    
    if table_name == "Patterns":
        test_data = {
            "title": "TEST_PATTERN",
            "name": "TEST_PATTERN", 
            "Title": "TEST_PATTERN",
            "Name": "TEST_PATTERN"
        }
    elif table_name == "Variations":
        test_data = {
            "title": "TEST_VARIATION",
            "name": "TEST_VARIATION",
            "Title": "TEST_VARIATION", 
            "Name": "TEST_VARIATION"
        }
    elif table_name == "Choices":
        test_data = {
            "content": "TEST_CHOICE",
            "Content": "TEST_CHOICE",
            "text": "TEST_CHOICE",
            "Text": "TEST_CHOICE"
        }
    
    print(f"Attempting to create test record with fields: {list(test_data.keys())}")
    
    try:
        test_response = requests.post(url, 
            headers=headers, 
            json={"records": [{"fields": test_data}]}
        )
        
        if test_response.status_code == 200:
            print("✅ Test record created successfully!")
            created_record = test_response.json()['records'][0]
            print(f"Confirmed field names: {list(created_record['fields'].keys())}")
            
            # Clean up - delete the test record
            record_id = created_record['id']
            delete_url = f"{url}/{record_id}"
            requests.delete(delete_url, headers=headers)
            print("🧹 Test record cleaned up")
            
            return list(created_record['fields'].keys())
        else:
            print(f"❌ Test record creation failed: {test_response.status_code}")
            print(f"Response: {test_response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating test record: {e}")
        return None

def main():
    """Check all table structures"""
    print("AIRTABLE FIELD VERIFICATION")
    print("=" * 50)
    
    tables_to_check = ["Patterns", "Variations", "Choices", "Sources", "Lenses", "Metas"]
    
    field_mapping = {}
    
    for table in tables_to_check:
        fields = check_table_structure(table)
        if fields:
            field_mapping[table] = fields
    
    print("\n" + "=" * 50)
    print("FIELD MAPPING SUMMARY")
    print("=" * 50)
    
    for table, fields in field_mapping.items():
        print(f"{table}: {fields}")
    
    print("\nField verification complete!")

if __name__ == "__main__":
    main()