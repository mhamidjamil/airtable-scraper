#!/usr/bin/env python3
"""
Check all fields in Variations table to see if there's a pattern linking field
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

def get_all_variation_fields():
    """Get multiple variation records to see all possible fields"""
    headers = {
        "Authorization": f"Bearer {AIRTABLE_CONFIG['api_token']}",
        "Content-Type": "application/json"
    }
    
    table_name = AIRTABLE_CONFIG['tables']['variations']
    url = f"https://api.airtable.com/v0/{AIRTABLE_CONFIG['base_id']}/{table_name}"
    params = {"maxRecords": 10}  # Get 10 records to see all fields
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        return data.get('records', [])
    else:
        logger.error(f"Error fetching variations: {response.status_code} - {response.text}")
        return []

def main():
    logger.info("🔍 Checking all fields in Variations table...")
    
    records = get_all_variation_fields()
    
    if not records:
        logger.error("❌ No variation records found")
        return 1
    
    logger.info(f"Found {len(records)} variation records")
    
    # Collect all unique field names across all records
    all_fields = set()
    for record in records:
        fields = record.get('fields', {})
        all_fields.update(fields.keys())
    
    logger.info(f"\n📋 ALL UNIQUE FIELDS IN VARIATIONS TABLE:")
    logger.info("=" * 60)
    
    for field_name in sorted(all_fields):
        logger.info(f"  ✓ {field_name}")
    
    # Show a sample record with all its fields
    logger.info(f"\n📄 SAMPLE VARIATION RECORD:")
    logger.info("=" * 60)
    
    sample_record = records[0]
    fields = sample_record.get('fields', {})
    
    for field_name, value in fields.items():
        value_type = type(value).__name__
        if isinstance(value, list):
            value_type = f"list[{len(value)}]"
            logger.info(f"  {field_name}: {value_type} = {value}")
        elif isinstance(value, str) and len(value) > 100:
            logger.info(f"  {field_name}: {value_type} = {value[:100]}...")
        else:
            logger.info(f"  {field_name}: {value_type} = {value}")
    
    # Check if any field contains pattern-related data
    logger.info(f"\n🔗 CHECKING FOR PATTERN-RELATED FIELDS:")
    logger.info("=" * 60)
    
    pattern_fields = [f for f in all_fields if 'pattern' in f.lower()]
    if pattern_fields:
        logger.info("Found pattern-related fields:")
        for field in pattern_fields:
            logger.info(f"  ✓ {field}")
    else:
        logger.info("❌ No pattern-related fields found")
    
    # Check for any relationship fields (usually lists of record IDs)
    logger.info(f"\n🔗 RELATIONSHIP FIELDS (lists of record IDs):")
    logger.info("=" * 60)
    
    for record in records[:3]:  # Check first 3 records
        fields = record.get('fields', {})
        for field_name, value in fields.items():
            if isinstance(value, list) and value and isinstance(value[0], str) and value[0].startswith('rec'):
                logger.info(f"  ✓ {field_name}: {value}")
                break
    else:
        logger.info("❌ No relationship fields found")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())