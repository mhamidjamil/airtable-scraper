#!/usr/bin/env python3
"""
Test pattern linking field names for variations
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

def test_pattern_linking():
    """Test different pattern linking field names"""
    headers = {
        "Authorization": f"Bearer {AIRTABLE_CONFIG['api_token']}",
        "Content-Type": "application/json"
    }
    
    url = f"https://api.airtable.com/v0/{AIRTABLE_CONFIG['base_id']}/Variations"
    
    # Test different possible linking field names
    test_linking_fields = [
        "pattern",
        "patterns", 
        "linked_pattern",
        "linked_patterns",
        "Pattern",
        "Patterns"
    ]
    
    pattern_id = "recgmlubmNSVBfL37"  # "CHILDREN OF THE BELOVED BANG"
    
    for field_name in test_linking_fields:
        logger.info(f"🧪 Testing pattern link field: '{field_name}'")
        
        test_fields = {
            "variation_title": "TEST PATTERN LINK",
            "content": "Testing pattern linking",
            field_name: [pattern_id]
        }
        
        payload = {
            "records": [{
                "fields": test_fields
            }]
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            logger.info(f"✅ SUCCESS with field '{field_name}'!")
            data = response.json()
            if 'records' in data and data['records']:
                record = data['records'][0]
                logger.info(f"Created record ID: {record['id']}")
                logger.info(f"Fields accepted: {list(record['fields'].keys())}")
                
                # Clean up - delete the test record
                delete_url = f"{url}/{record['id']}"
                delete_response = requests.delete(delete_url, headers=headers)
                if delete_response.status_code == 200:
                    logger.info("🧹 Test record cleaned up")
                
            return field_name
        else:
            logger.info(f"❌ Failed with '{field_name}': {response.status_code}")
            try:
                error_data = response.json()
                if 'error' in error_data:
                    logger.info(f"   Error: {error_data['error']['message']}")
            except:
                pass
    
    return None

def main():
    logger.info("🔍 Testing pattern linking field names...")
    
    working_field = test_pattern_linking()
    
    if working_field:
        logger.info(f"\n✅ WORKING PATTERN LINK FIELD: '{working_field}'")
    else:
        logger.info("❌ None of the pattern linking field names worked")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())