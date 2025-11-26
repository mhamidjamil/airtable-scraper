#!/usr/bin/env python3
"""
Inspect Airtable table schema to see what fields exist
"""

import sys
import os
import requests
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import AIRTABLE_CONFIG
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def inspect_table_schema(table_name):
    """Get a few records to see the field structure"""
    headers = {
        "Authorization": f"Bearer {AIRTABLE_CONFIG['api_token']}",
        "Content-Type": "application/json"
    }
    
    url = f"https://api.airtable.com/v0/{AIRTABLE_CONFIG['base_id']}/{table_name}"
    params = {"maxRecords": 1}  # Just get 1 record to see fields
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        return data.get('records', [])
    else:
        logger.error(f"Error fetching {table_name}: {response.status_code} - {response.text}")
        return []

def main():
    logger.info("🔍 Inspecting Airtable table schemas...")
    
    for table_key, table_name in AIRTABLE_CONFIG['tables'].items():
        logger.info(f"\n📋 Table: {table_name} ({table_key})")
        logger.info("=" * 60)
        
        records = inspect_table_schema(table_name)
        
        if records:
            # Get field names from the first record
            fields = records[0].get('fields', {})
            logger.info(f"Available fields:")
            
            for field_name, value in fields.items():
                value_type = type(value).__name__
                if isinstance(value, list):
                    value_type = f"list[{len(value)}]"
                elif isinstance(value, str) and len(value) > 50:
                    value = value[:50] + "..."
                
                logger.info(f"  - {field_name}: {value_type}")
                
                # Show sample value for reference
                if isinstance(value, (str, int, float, bool)):
                    logger.info(f"    Sample: {value}")
                elif isinstance(value, list) and value:
                    logger.info(f"    Sample: {value[0] if len(value) == 1 else value[:2]}")
                    
        else:
            logger.info("❌ No records found or unable to fetch")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())