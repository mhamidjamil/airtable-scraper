#!/usr/bin/env python3
"""
Create a test variation record to see the expected field structure
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

def create_test_variation():
    """Create a minimal test variation to discover field requirements"""
    headers = {
        "Authorization": f"Bearer {AIRTABLE_CONFIG['api_token']}",
        "Content-Type": "application/json"
    }
    
    url = f"https://api.airtable.com/v0/{AIRTABLE_CONFIG['base_id']}/Variations"
    
    # Try different possible field combinations
    test_fields_options = [
        # Option 1: Basic fields
        {
            "variation_title": "TEST VARIATION",
            "content": "This is a test variation"
        },
        # Option 2: With pattern link
        {
            "variation_title": "TEST VARIATION", 
            "content": "This is a test variation",
            "pattern": ["recgmlubmNSVBfL37"]  # Link to "CHILDREN OF THE BELOVED BANG"
        },
        # Option 3: Different field names
        {
            "title": "TEST VARIATION",
            "content": "This is a test variation", 
            "patterns": ["recgmlubmNSVBfL37"]
        }
    ]
    
    for i, test_fields in enumerate(test_fields_options, 1):
        logger.info(f"🧪 Testing field combination {i}: {list(test_fields.keys())}")
        
        payload = {
            "records": [{
                "fields": test_fields
            }]
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            logger.info(f"✅ SUCCESS with field combination {i}!")
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
                
            return test_fields
        else:
            logger.info(f"❌ Failed with combination {i}: {response.status_code}")
            try:
                error_data = response.json()
                if 'error' in error_data:
                    logger.info(f"   Error: {error_data['error']}")
            except:
                logger.info(f"   Raw error: {response.text}")
    
    return None

def main():
    logger.info("🔍 Testing variation field requirements...")
    
    working_fields = create_test_variation()
    
    if working_fields:
        logger.info(f"\n✅ WORKING FIELD STRUCTURE:")
        for field, value in working_fields.items():
            logger.info(f"  - {field}: {type(value).__name__}")
    else:
        logger.info("❌ None of the field combinations worked")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())