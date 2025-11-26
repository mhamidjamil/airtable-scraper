import logging
import sys
import os
import argparse
from datetime import datetime
from config import settings
from modules.data_extractor import DataExtractor
from modules.airtable_uploader import AirtableUploader

# Setup Logging
log_filename = f"scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
log_path = settings.LOG_DIR / log_filename

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_path, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Airtable Scraper - Extract and sync data from DOCX files')
    
    # Selective sync options
    parser.add_argument('--variations', '--variation', '--Variations', '--Variation', 
                       action='store_true', help='Sync only variations')
    parser.add_argument('--patterns', '--pattern', '--Patterns', '--Pattern', 
                       action='store_true', help='Sync only patterns')
    parser.add_argument('--lenses', '--lens', '--Lenses', '--Lens', 
                       action='store_true', help='Sync only lenses')
    parser.add_argument('--metas', '--meta', '--Metas', '--Meta', 
                       action='store_true', help='Sync only metas')
    parser.add_argument('--sources', '--source', '--Sources', '--Source', 
                       action='store_true', help='Sync only sources')
    
    # Folder option
    parser.add_argument('--folder', '-f', default='BIOME', 
                       help='Target folder to process (default: BIOME)')
    
    return parser.parse_args()

def determine_sync_types(args):
    """Determine which data types to sync based on arguments"""
    sync_types = []
    
    if args.lenses:
        sync_types.append('lenses')
    if args.sources:
        sync_types.append('sources')
    if args.metas:
        sync_types.append('metas')
    if args.patterns:
        sync_types.append('patterns')
    if args.variations:
        sync_types.append('variations')
    
    # If no specific types selected, sync everything
    if not sync_types:
        sync_types = ['lenses', 'sources', 'metas', 'patterns', 'variations']
    
    return sync_types

def main():
    # Parse command line arguments
    args = parse_arguments()
    sync_types = determine_sync_types(args)
    
    logger.info("="*50)
    logger.info("STARTING AIRTABLE SCRAPER PROJECT")
    logger.info("="*50)
    logger.info(f"Sync Types: {', '.join(sync_types)}")
    logger.info(f"Target Folder: {args.folder}")

    # 1. Initialize Modules
    extractor = DataExtractor(log_handler=logger)
    uploader = AirtableUploader(log_handler=logger)

    # 2. Extract Data
    logger.info(f"Extracting data from folder: {args.folder}")
    extracted_data = extractor.process_folder(args.folder)
    
    if not extracted_data or not extracted_data.get("documents"):
        logger.error("No data extracted. Aborting upload.")
        return

    # 3. Upload to Airtable
    logger.info("Initializing Airtable Sync...")
    try:
        # a: Read already uploaded data and sync selectively
        uploader.fetch_existing_records(sync_types)
        uploader.sync_data(extracted_data, sync_types)
        
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

    logger.info("="*50)
    logger.info("PROJECT EXECUTION COMPLETE")
    logger.info(f"Log saved to: {log_path}")
    logger.info("="*50)

if __name__ == "__main__":
    main()
