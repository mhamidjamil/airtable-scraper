#!/usr/bin/env python3
import requests
import json
from config.settings import AIRTABLE_CONFIG

url = f"https://api.airtable.com/v0/meta/bases/{AIRTABLE_CONFIG['base_id']}/tables"
headers = {
    "Authorization": f"Bearer {AIRTABLE_CONFIG['api_token']}",
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)
data = response.json()

for table in data.get('tables', []):
    if table['name'] == 'Sources':
        with open('sources_schema.json', 'w', encoding='utf-8') as f:
            json.dump(table, f, indent=2, ensure_ascii=False)
        print('Sources schema saved to sources_schema.json')
        
        # Print linking fields
        print(f'\n📋 SOURCES TABLE LINKING FIELDS:')
        for field in table.get('fields', []):
            if field.get('type') == 'multipleRecordLinks':
                print(f"  🔗 {field['name']}: links to table {field['options']['linkedTableId']}")
        break
else:
    print('❌ Sources table not found')