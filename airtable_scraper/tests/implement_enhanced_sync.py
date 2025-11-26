#!/usr/bin/env python3
"""
Implementation of enhanced field structure with proper pattern-variation linking
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.data_extractor import DataExtractor
from modules.airtable_uploader import AirtableUploader
import logging
import json
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class EnhancedAirtableSync:
    """Enhanced sync with proper field structure and linking"""
    
    def __init__(self):
        self.extractor = DataExtractor(logger)
        self.uploader = AirtableUploader()
        self.created_records = {
            'lenses': {},  # lens_name -> record_id
            'sources': {},  # source_name -> record_id  
            'patterns': {},  # pattern_number -> record_id
            'variations': {},  # variation_title -> record_id
            'metas': {}  # title -> record_id
        }
    
    def enhance_variation_fields(self, variation, pattern_info, lens_id=None):
        """Add enhanced fields to variation"""
        enhanced = {
            'variation_title': variation['title'],
            'content': variation['content']
        }
        
        # Add new fields (will be filtered out by validation until Airtable fields exist)
        if pattern_info:
            enhanced['base_folder'] = pattern_info.get('base_folder', 'BIOME')
            if lens_id:
                enhanced['lens'] = [lens_id]
            
            # Pattern linking - use pattern record ID if available
            pattern_number = pattern_info.get('pattern_number')
            if pattern_number and pattern_number in self.created_records['patterns']:
                enhanced['patterns'] = [self.created_records['patterns'][pattern_number]]
        
        return enhanced
    
    def enhance_source_fields(self, source, base_folder, lens_id=None):
        """Add enhanced fields to source"""
        enhanced = {
            'source_name': source.get('source_name', source)
        }
        
        # Add new fields
        enhanced['base_folder'] = base_folder
        if lens_id:
            enhanced['lens'] = [lens_id]
            
        # Keep existing pattern links if available
        if isinstance(source, dict) and 'Patterns' in source:
            enhanced['Patterns'] = source['Patterns']
        
        return enhanced
    
    def sync_with_enhanced_order(self, folder_name, sync_types=None):
        """Sync with proper order for pattern-variation linking"""
        if sync_types is None:
            sync_types = ['lenses', 'sources', 'patterns', 'variations', 'metas']
        
        logger.info(f"🚀 Starting Enhanced Sync for {folder_name}")
        logger.info(f"Sync order: {' → '.join(sync_types)}")
        
        # Extract data
        data = self.extractor.process_folder(folder_name)
        if not data:
            logger.error("❌ No data extracted")
            return False
        
        # Flatten data structure for easier processing
        flat_data = self._flatten_extracted_data(data)
        
        success = True
        
        # Sync in proper order
        for sync_type in sync_types:
            logger.info(f"\n📋 Syncing {sync_type.upper()}")
            logger.info("=" * 60)
            
            if sync_type == 'lenses':
                success &= self._sync_lenses(flat_data['lenses'], folder_name)
            elif sync_type == 'sources':
                success &= self._sync_enhanced_sources(flat_data['sources'], folder_name)
            elif sync_type == 'patterns':
                success &= self._sync_enhanced_patterns(flat_data['patterns'], folder_name)
            elif sync_type == 'variations':
                success &= self._sync_enhanced_variations(flat_data['variations'], flat_data['patterns'], folder_name)
            elif sync_type == 'metas':
                success &= self._sync_metas(flat_data['metas'])
        
        if success:
            logger.info(f"✅ Enhanced sync completed successfully!")
            logger.info(f"Created records: {sum(len(records) for records in self.created_records.values())}")
        else:
            logger.error(f"❌ Some sync operations failed")
        
        return success
    
    def _flatten_extracted_data(self, data):
        """Convert extracted data to flat structure for syncing"""
        flat_data = {
            'lenses': [],
            'sources': [],
            'patterns': [],
            'variations': [],
            'metas': data.get('metas', [])
        }
        
        # Process documents to extract lenses, sources, patterns, variations
        for doc in data.get('documents', []):
            lens_name = doc.get('lens')
            base_folder = doc.get('base_folder', 'BIOME')
            
            # Collect lens
            if lens_name:
                lens_entry = {'lens_name': lens_name, 'content': f"Lens: {lens_name}"}
                if lens_entry not in flat_data['lenses']:
                    flat_data['lenses'].append(lens_entry)
            
            # Process patterns
            for pattern in doc.get('patterns', []):
                # Add pattern with enhanced info
                enhanced_pattern = pattern.copy()
                enhanced_pattern['base_folder'] = base_folder
                enhanced_pattern['lens_name'] = lens_name
                flat_data['patterns'].append(enhanced_pattern)
                
                # Collect source
                source = pattern.get('source', 'Unknown Source')
                source_entry = {'source_name': source}
                if source_entry not in flat_data['sources']:
                    flat_data['sources'].append(source_entry)
                
                # Process variations
                for variation in pattern.get('variations', []):
                    enhanced_variation = variation.copy()
                    enhanced_variation['pattern_info'] = {
                        'pattern_number': pattern.get('pattern_number'),
                        'base_folder': base_folder,
                        'lens_name': lens_name
                    }
                    flat_data['variations'].append(enhanced_variation)
        
        return flat_data
    
    def _sync_lenses(self, lenses, base_folder):
        """Sync lenses first"""
        for lens in lenses:
            try:
                record_id = self.uploader._create_or_update('lenses', lens['lens_name'], lens)
                if record_id:
                    lens_name = lens['lens_name']
                    self.created_records['lenses'][lens_name] = record_id
                    logger.info(f"✅ Created lens: {lens_name}")
            except Exception as e:
                logger.error(f"❌ Failed to create lens {lens.get('lens_name', 'unknown')}: {e}")
                return False
        return True
    
    def _sync_enhanced_sources(self, sources, base_folder):
        """Sync sources with enhanced fields"""
        for source in sources:
            # Get lens ID if available
            lens_id = None
            # Note: In real implementation, you'd determine which lens this source belongs to
            
            enhanced_source = self.enhance_source_fields(source, base_folder, lens_id)
            
            try:
                record_id = self.uploader._create_or_update('sources', enhanced_source['source_name'], enhanced_source)
                if record_id:
                    source_name = source['source_name']
                    self.created_records['sources'][source_name] = record_id
                    logger.info(f"✅ Created source: {source_name[:50]}...")
            except Exception as e:
                logger.error(f"❌ Failed to create source: {e}")
                return False
        return True
    
    def _sync_enhanced_patterns(self, patterns, base_folder):
        """Sync patterns and store their IDs for variation linking"""
        for pattern in patterns:
            # Pattern already has base_folder from flattening
            try:
                record_id = self.uploader._create_or_update('patterns', pattern['title'], pattern)
                if record_id:
                    pattern_number = pattern.get('pattern_number')
                    if pattern_number:
                        self.created_records['patterns'][pattern_number] = record_id
                    logger.info(f"✅ Created pattern {pattern_number}: {pattern['title'][:50]}...")
            except Exception as e:
                logger.error(f"❌ Failed to create pattern {pattern.get('pattern_number', 'unknown')}: {e}")
                return False
        return True
    
    def _sync_enhanced_variations(self, variations, patterns, base_folder):
        """Sync variations with proper pattern linking"""
        # Create pattern lookup
        pattern_lookup = {p.get('pattern_number'): p for p in patterns}
        
        for variation in variations:
            pattern_info = variation.get('pattern_info', {})
            pattern_number = pattern_info.get('pattern_number')
            
            # Get lens ID if available
            lens_name = pattern_info.get('lens_name')
            lens_id = self.created_records['lenses'].get(lens_name) if lens_name else None
            
            enhanced_variation = self.enhance_variation_fields(
                variation, pattern_info, lens_id
            )
            
            try:
                record_id = self.uploader._create_or_update('variations', enhanced_variation['variation_title'], enhanced_variation)
                if record_id:
                    variation_title = variation['title']
                    self.created_records['variations'][variation_title] = record_id
                    logger.info(f"✅ Created variation: {variation_title[:50]}...")
                    
                    # Log linking info
                    if pattern_number in self.created_records['patterns']:
                        logger.info(f"  🔗 Linked to pattern {pattern_number}")
            except Exception as e:
                logger.error(f"❌ Failed to create variation: {e}")
                return False
        return True
    
    def _sync_metas(self, metas):
        """Sync metas (unchanged)"""
        for meta in metas:
            try:
                record_id = self.uploader._create_or_update('metas', meta['title'], meta)
                if record_id:
                    meta_title = meta['title']
                    self.created_records['metas'][meta_title] = record_id
                    logger.info(f"✅ Created meta: {meta_title[:50]}...")
            except Exception as e:
                logger.error(f"❌ Failed to create meta: {e}")
                return False
        return True

def main():
    logger.info("🚀 Enhanced Pattern-Variation Linking Implementation")
    logger.info("=" * 70)
    
    if len(sys.argv) < 2:
        logger.error("Usage: python implement_enhanced_sync.py <folder_name> [sync_types]")
        logger.error("Example: python implement_enhanced_sync.py BIOME patterns,variations")
        return 1
    
    folder_name = sys.argv[1]
    
    # Parse sync types
    sync_types = None
    if len(sys.argv) > 2:
        sync_types = sys.argv[2].split(',')
        sync_types = [s.strip() for s in sync_types]
    
    # Create enhanced syncer
    syncer = EnhancedAirtableSync()
    
    # Test with smaller subset first
    test_sync_types = sync_types or ['patterns', 'variations']
    
    logger.info(f"Testing enhanced sync with: {test_sync_types}")
    success = syncer.sync_with_enhanced_order(folder_name, test_sync_types)
    
    if success:
        logger.info("✅ Enhanced sync test successful!")
        logger.info("\nNext steps:")
        logger.info("1. Verify created records in Airtable")
        logger.info("2. Add missing fields (base_folder, lens, patterns) to Airtable tables")
        logger.info("3. Test full sync with all types")
    else:
        logger.error("❌ Enhanced sync test failed")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())