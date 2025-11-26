#!/usr/bin/env python3
"""
Test and implement new field structure for proper pattern-variation linking
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.data_extractor import DataExtractor
from modules.airtable_uploader import AirtableUploader
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
    logger.info("🚀 Testing New Field Structure for Pattern-Variation Linking")
    logger.info("=" * 70)
    
    # Extract data from BIOME folder
    extractor = DataExtractor()
    data = extractor.process_folder("BIOME")
    
    # Count patterns and variations from documents
    total_patterns = sum(len(doc.get("patterns", [])) for doc in data.get("documents", []))
    total_variations = sum(len(pattern.get("variations", [])) 
                          for doc in data.get("documents", []) 
                          for pattern in doc.get("patterns", []))
    
    logger.info(f"Extracted: {total_patterns} patterns, {total_variations} variations")
    
    # Test new variation structure
    logger.info("\n📋 TESTING NEW VARIATION STRUCTURE")
    logger.info("=" * 70)
    
    # Get a sample variation and pattern from the first document
    sample_doc = data['documents'][0]
    sample_pattern = sample_doc['patterns'][0]
    sample_variation = sample_pattern['variations'][0]
    
    logger.info(f"Sample Pattern: {sample_pattern['title'][:50]}...")
    logger.info(f"Sample Variation: {sample_variation['title'][:50]}...")
    
    # Create new field structure for variations
    enhanced_variation = {
        'variation_title': sample_variation['title'],
        'content': sample_variation['content'],
        'base_folder': 'BIOME',  # New field
        'lens': ['rec_lens_id_placeholder'],  # New field - will be actual lens ID
        'patterns': ['rec_pattern_id_placeholder']  # New field for pattern linking
    }
    
    logger.info(f"\n✨ Enhanced Variation Structure:")
    for key, value in enhanced_variation.items():
        if isinstance(value, str) and len(value) > 50:
            logger.info(f"  {key}: {value[:50]}...")
        else:
            logger.info(f"  {key}: {value}")
    
    # Create new field structure for sources
    logger.info(f"\n📋 TESTING NEW SOURCE STRUCTURE")
    logger.info("=" * 70)
    
    # Get sample source from pattern
    sample_source = {"source_name": sample_pattern.get('source', 'Sample Source')}
    enhanced_source = {
        'source_name': sample_source['source_name'],
        'base_folder': 'BIOME',  # New field
        'lens': ['rec_lens_id_placeholder'],  # New field
        'Patterns': sample_source.get('Patterns', [])  # Existing field
    }
    
    logger.info(f"\n✨ Enhanced Source Structure:")
    for key, value in enhanced_source.items():
        if isinstance(value, str) and len(value) > 50:
            logger.info(f"  {key}: {value[:50]}...")
        else:
            logger.info(f"  {key}: {value}")
    
    # Test sync order strategy
    logger.info(f"\n🔄 TESTING SYNC ORDER STRATEGY")
    logger.info("=" * 70)
    
    logger.info("Current sync order issue:")
    logger.info("  ❌ Variations created first → No pattern IDs to link to")
    logger.info("")
    logger.info("New sync order solution:")
    logger.info("  1. ✅ Create Lenses first")
    logger.info("  2. ✅ Create Sources") 
    logger.info("  3. ✅ Create Patterns (with lens & source links)")
    logger.info("  4. ✅ Create Variations (with pattern & lens links)")
    logger.info("  5. ✅ Create Metas last")
    
    # Test field validation
    logger.info(f"\n🧪 TESTING FIELD VALIDATION")
    logger.info("=" * 70)
    
    uploader = AirtableUploader()
    
    # Test variation validation
    test_fields = enhanced_variation.copy()
    validated_fields = uploader._validate_fields(test_fields, 'variations')
    
    logger.info(f"Original variation fields: {list(test_fields.keys())}")
    logger.info(f"Validated variation fields: {list(validated_fields.keys())}")
    
    # Since we don't know which fields exist yet, this will show what gets removed
    removed_fields = set(test_fields.keys()) - set(validated_fields.keys())
    if removed_fields:
        logger.info(f"⚠️  Fields that will be removed: {removed_fields}")
        logger.info("   (These fields need to be created in Airtable first)")
    
    # Create sample data structure for testing
    logger.info(f"\n📝 CREATING TEST DATA STRUCTURE")
    logger.info("=" * 70)
    
    test_data = {
        'documents': data['documents'],  # Keep original structure
        'enhanced_variation': enhanced_variation,  # Enhanced with new fields
        'enhanced_source': enhanced_source,  # Enhanced with new fields  
        'metas': data['metas']
    }
    
    # Save test data
    test_file = os.path.join("json_data", "test_enhanced_structure.json")
    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✅ Saved test data to: {test_file}")
    
    # Test linking strategy
    logger.info(f"\n🔗 PATTERN-VARIATION LINKING STRATEGY")
    logger.info("=" * 70)
    
    # Show how linking should work
    doc = data['documents'][0]
    pattern = doc['patterns'][0]
    variations = pattern.get('variations', [])
    
    logger.info(f"Pattern: '{pattern['title'][:50]}...'")
    logger.info(f"Linked variations ({len(variations)}):")
    
    for i, variation in enumerate(variations[:3]):
        logger.info(f"  Variation {i+1}: '{variation['title'][:30]}...'")
        logger.info(f"    → Currently links to Pattern {pattern.get('pattern_number', 'unknown')}")
    
    logger.info(f"\n🎯 NEW LINKING APPROACH:")
    logger.info("  1. Extract all patterns first, get Airtable record IDs")
    logger.info("  2. When creating variations, use actual pattern record IDs")
    logger.info("  3. Add 'patterns' field to variations with array of pattern IDs")
    
    logger.info(f"\n✅ NEW FIELD STRUCTURE TEST COMPLETE!")
    logger.info("Next steps:")
    logger.info("1. Create the new fields in Airtable (base_folder, lens, patterns)")
    logger.info("2. Update the sync order to create patterns first")
    logger.info("3. Implement proper pattern ID linking")
    logger.info("4. Test with --patterns then --variations flags")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())