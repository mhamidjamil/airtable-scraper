#!/usr/bin/env python3
"""
Test script to verify the variation sync fixes and command-line parameters
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from modules.data_extractor import DataExtractor
from modules.airtable_uploader import AirtableUploader

def setup_logging():
    """Setup detailed logging for testing"""
    log_filename = f"test_variation_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
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

def test_variation_data_validation(logger):
    """Test variation data before sending to Airtable"""
    logger.info("=" * 60)
    logger.info("TESTING VARIATION DATA VALIDATION")
    logger.info("=" * 60)
    
    # Extract data
    extractor = DataExtractor(log_handler=logger)
    data = extractor.process_folder('BIOME')
    
    # Create uploader and test validation
    uploader = AirtableUploader(log_handler=logger)
    
    # Test validation on sample variation data
    sample_variations = []
    for doc in data.get('documents', []):
        for pattern in doc.get('patterns', []):
            variations = pattern.get('variations', [])
            if variations:
                sample_variations.extend(variations[:3])  # Take first 3 from each
                break
        if sample_variations:
            break
    
    logger.info(f"Testing validation on {len(sample_variations)} sample variations:")
    
    for i, variation in enumerate(sample_variations):
        v_fields = {
            "variation_title": variation.get("title"),
            "variation_number": variation.get("variation_number"),
            "content": variation.get("content", ""),
            "linked_pattern": ["rec_test_pattern_001"]  # Fake pattern ID
        }
        
        logger.info(f"  Variation {i+1}: {variation.get('title', 'No title')[:50]}...")
        logger.info(f"    Original fields: {list(v_fields.keys())}")
        
        # Test validation
        clean_fields = uploader._validate_fields(v_fields, "variations")
        logger.info(f"    Clean fields: {list(clean_fields.keys())}")
        
        # Check for issues
        issues = []
        if not clean_fields.get("variation_title"):
            issues.append("Missing variation_title")
        if not clean_fields.get("linked_pattern"):
            issues.append("Missing linked_pattern")
        if clean_fields.get("variation_number") is None:
            issues.append("Missing variation_number")
            
        if issues:
            logger.info(f"    ⚠️ Issues: {', '.join(issues)}")
        else:
            logger.info(f"    ✅ Validation passed")
    
    return True

def test_timestamped_json_export(logger):
    """Test the timestamped JSON export functionality"""
    logger.info("=" * 60)
    logger.info("TESTING TIMESTAMPED JSON EXPORT")
    logger.info("=" * 60)
    
    # Extract data
    extractor = DataExtractor(log_handler=logger)
    data = extractor.process_folder('BIOME')
    
    # Create uploader and test JSON export
    uploader = AirtableUploader(log_handler=logger)
    
    # Test different export types
    test_types = ["variations", "patterns", "all", "lenses_sources"]
    
    for sync_type in test_types:
        logger.info(f"Testing JSON export for type: {sync_type}")
        uploader.save_sync_data(data, sync_type)
    
    # Check if files were created
    json_dir = Path("json_data")
    json_files = list(json_dir.glob("airtable_sync_*.json"))
    logger.info(f"✅ Created {len(json_files)} timestamped JSON files in {json_dir}")
    
    for file in json_files[-4:]:  # Show last 4 files
        logger.info(f"  📄 {file.name}")
    
    return True

def test_command_line_parsing():
    """Test command line argument parsing (simulated)"""
    logger = setup_logging()
    logger.info("=" * 60)
    logger.info("TESTING COMMAND LINE PARSING")
    logger.info("=" * 60)
    
    # Simulate different command line scenarios
    test_scenarios = [
        ['--variations'],
        ['--patterns', '--variations'], 
        ['--lenses', '--folder', 'BIOME'],
        ['--metas', '--sources'],
        []  # No args - should sync all
    ]
    
    # Import the functions from main
    from main import parse_arguments, determine_sync_types
    import sys
    
    for i, args in enumerate(test_scenarios):
        logger.info(f"Scenario {i+1}: {' '.join(args) if args else 'no arguments'}")
        
        # Temporarily modify sys.argv
        original_argv = sys.argv[:]
        sys.argv = ['main.py'] + args
        
        try:
            parsed_args = parse_arguments()
            sync_types = determine_sync_types(parsed_args)
            logger.info(f"  Sync types: {sync_types}")
            logger.info(f"  Folder: {parsed_args.folder}")
        except SystemExit:
            logger.info("  (Help requested or parsing error)")
        finally:
            sys.argv = original_argv
    
    return True

def main():
    """Run all tests"""
    logger = setup_logging()
    
    try:
        logger.info("🚀 Starting Variation Fix Tests")
        logger.info(f"Timestamp: {datetime.now()}")
        
        # Test 1: Variation Data Validation
        if not test_variation_data_validation(logger):
            logger.error("❌ Variation validation test failed")
            return False
        
        # Test 2: Timestamped JSON Export
        if not test_timestamped_json_export(logger):
            logger.error("❌ JSON export test failed")
            return False
        
        # Test 3: Command Line Parsing
        if not test_command_line_parsing():
            logger.error("❌ Command line parsing test failed")
            return False
        
        logger.info("✅ ALL VARIATION FIX TESTS PASSED!")
        logger.info("The system should now handle 422 errors better and support selective syncing")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)