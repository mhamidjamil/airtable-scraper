#!/usr/bin/env python3
"""
Debug pattern matching between extracted data and Airtable
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.airtable_uploader import AirtableUploader
from modules.data_extractor import DataExtractor
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
    logger.info("🔍 Debugging pattern matching...")
    
    try:
        uploader = AirtableUploader()
        
        # Get patterns from extracted data
        logger.info("Reading extracted data...")
        with open('json_data/biome_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        extracted_patterns = []
        for doc_data in data.get('documents', []):
            for pattern in doc_data.get('patterns', []):
                pattern_title = pattern.get('title', '')
                if pattern_title:
                    extracted_patterns.append(pattern_title)
                    
        logger.info(f"Found {len(extracted_patterns)} extracted patterns")
        
        # Get patterns from Airtable
        logger.info("Fetching Airtable patterns...")
        uploader.fetch_existing_records(['patterns'])
        airtable_patterns = uploader.record_map.get('patterns', {})
        
        logger.info(f"Found {len(airtable_patterns)} Airtable patterns")
        
        # Compare normalization
        logger.info("🔍 Pattern matching analysis:")
        logger.info("=" * 80)
        
        matched = 0
        unmatched = []
        
        for extracted_pattern in extracted_patterns:
            normalized_extracted = uploader.normalize_for_matching(extracted_pattern)
            
            if normalized_extracted in airtable_patterns:
                matched += 1
                record_id = airtable_patterns[normalized_extracted]
                logger.info(f"✅ MATCH: '{extracted_pattern}' -> '{normalized_extracted}' -> {record_id}")
            else:
                unmatched.append(extracted_pattern)
                logger.info(f"❌ NO MATCH: '{extracted_pattern}' -> '{normalized_extracted}'")
                
                # Find closest matches
                closest = []
                for airtable_key in airtable_patterns.keys():
                    if extracted_pattern.lower() in airtable_key or airtable_key in extracted_pattern.lower():
                        closest.append(airtable_key)
                        
                if closest:
                    logger.info(f"   🤔 Possible matches: {closest[:3]}")
                    
        logger.info("=" * 80)
        logger.info(f"📊 SUMMARY:")
        logger.info(f"   Matched: {matched}/{len(extracted_patterns)} ({matched/len(extracted_patterns)*100:.1f}%)")
        logger.info(f"   Unmatched: {len(unmatched)}")
        
        if unmatched:
            logger.info(f"📋 First 10 unmatched patterns:")
            for pattern in unmatched[:10]:
                logger.info(f"   - {pattern}")
                
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())