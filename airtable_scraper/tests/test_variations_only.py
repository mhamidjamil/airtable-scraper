#!/usr/bin/env python3
"""
Test script to verify variations-only syncing works correctly
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from modules.data_extractor import DataExtractor
from modules.airtable_uploader import AirtableUploader

def setup_logging():
    """Setup detailed logging for testing"""
    log_filename = f"test_variations_only_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_path = Path("logs") / log_filename
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_path, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def test_variations_only_sync(logger):
    """Test variations-only syncing"""
    logger.info("=" * 60)
    logger.info("TESTING VARIATIONS-ONLY SYNC")
    logger.info("=" * 60)
    
    # 1. Extract data
    extractor = DataExtractor(log_handler=logger)
    data = extractor.process_folder('BIOME')
    
    # 2. Create uploader and test variations-only sync
    uploader = AirtableUploader(log_handler=logger)
    
    # Simulate existing patterns in Airtable (normally fetched)
    logger.info("Simulating pattern records that would exist in Airtable...")
    uploader.record_map = {
        "lenses": {},
        "sources": {},
        "metas": {},
        "patterns": {
            "children of the beloved bang": "rec_pattern_001",
            "a digital garden of convivencia": "rec_pattern_002", 
            "one wounded biome — inner and outer collapse as single field": "rec_pattern_003",
            "gen g — named by grace, not by trauma": "rec_pattern_004",
            "from spiritual seeking to spiritual hosting": "rec_pattern_005"
        },
        "variations": {
            "the first yes that still echoes": "rec_var_001",
            "neurons in a cosmic heart": "rec_var_002"
        }
    }
    
    # 3. Test variations-only sync
    sync_types = ["variations"]
    logger.info(f"Testing sync with types: {sync_types}")
    
    # Count variations before sync
    total_variations = 0
    patterns_with_variations = 0
    
    for doc in data.get("documents", []):
        for pattern in doc.get("patterns", []):
            variations = pattern.get("variations", [])
            if variations:
                patterns_with_variations += 1
                total_variations += len(variations)
                logger.info(f"Pattern: {pattern.get('title', 'Unknown')[:40]}... has {len(variations)} variations")
    
    logger.info(f"Total patterns with variations: {patterns_with_variations}")
    logger.info(f"Total variations to sync: {total_variations}")
    
    # 4. Test the sync logic (without actual API calls)
    logger.info("Testing variation sync logic...")
    
    variations_processed = 0
    patterns_found = 0
    patterns_missing = 0
    
    for doc in data.get("documents", []):
        for pattern in doc.get("patterns", []):
            pattern_title = pattern.get("title", "")
            normalized_pattern = uploader.normalize_for_matching(pattern_title)
            
            # Check if pattern exists
            pattern_id = uploader.record_map["patterns"].get(normalized_pattern)
            
            if pattern_id:
                patterns_found += 1
                variations = pattern.get("variations", [])
                logger.info(f"✅ Found pattern '{pattern_title}' -> {len(variations)} variations to process")
                
                for variation in variations:
                    v_title = variation.get("title")
                    if v_title:
                        variations_processed += 1
                        # Test field validation
                        v_fields = {
                            "variation_title": v_title,
                            "variation_number": variation.get("variation_number"),
                            "content": variation.get("content", ""),
                            "linked_pattern": [pattern_id]
                        }
                        clean_fields = uploader._validate_fields(v_fields, "variations")
                        logger.info(f"  Variation {variation.get('variation_number', '?')}: {v_title[:40]}... -> Validated ✅")
            else:
                patterns_missing += 1
                variations = pattern.get("variations", [])
                logger.info(f"❌ Pattern '{pattern_title}' not found in Airtable -> {len(variations)} variations skipped")
    
    logger.info(f"📊 SYNC TEST SUMMARY:")
    logger.info(f"  Patterns found in Airtable: {patterns_found}")
    logger.info(f"  Patterns missing from Airtable: {patterns_missing}")
    logger.info(f"  Variations that would be processed: {variations_processed}")
    
    if patterns_missing > 0:
        logger.info(f"⚠️  {patterns_missing} patterns are missing from Airtable!")
        logger.info("   Make sure to run pattern sync first or sync everything together")
        return False
    
    if variations_processed == 0:
        logger.info("❌ No variations would be processed!")
        return False
    
    logger.info("✅ Variations-only sync test passed!")
    return True

def main():
    """Run the variations-only test"""
    logger = setup_logging()
    
    try:
        logger.info("🚀 Starting Variations-Only Sync Test")
        logger.info(f"Timestamp: {datetime.now()}")
        
        # Test variations-only sync
        if not test_variations_only_sync(logger):
            logger.error("❌ Variations-only sync test failed")
            return False
        
        logger.info("✅ VARIATIONS-ONLY SYNC TEST PASSED!")
        logger.info("The system should now properly sync only variations when using --variations flag")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)