#!/usr/bin/env python3
"""
Check what patterns are currently in Airtable
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.airtable_uploader import AirtableUploader
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

def main():
    logger.info("🔍 Checking patterns currently in Airtable...")
    
    try:
        uploader = AirtableUploader(logger)
        
        # Fetch existing patterns
        logger.info("Fetching existing patterns from Airtable...")
        result = uploader.fetch_existing_records(['patterns'])
        
        # The method returns None but builds the internal record_map
        patterns_map = uploader.record_map.get('patterns', {})
        logger.info(f"📋 Found {len(patterns_map)} patterns in Airtable:")
        
        if patterns_map:
            for i, (normalized_key, record_id) in enumerate(patterns_map.items(), 1):
                logger.info(f"  {i}. {normalized_key}")
                logger.info(f"     ID: {record_id}")
        else:
            logger.info("❌ No patterns found in Airtable")
            
    except Exception as e:
        logger.error(f"❌ Error checking Airtable patterns: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())