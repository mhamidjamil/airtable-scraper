import logging
import sys
import os
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

def main():
    logger.info("="*50)
    logger.info("STARTING AIRTABLE SCRAPER PROJECT")
    logger.info("="*50)

    # 1. Initialize Modules
    extractor = DataExtractor(log_handler=logger)
    uploader = AirtableUploader(log_handler=logger)

    # 2. Extract Data
    # You can loop through folders here. For now, defaulting to BIOME as per previous context.
    target_folder = "BIOME" 
    logger.info(f"Target Folder: {target_folder}")
    
    extracted_data = extractor.process_folder(target_folder)
    
    if not extracted_data or not extracted_data.get("documents"):
        logger.error("No data extracted. Aborting upload.")
        return

    # 3. Upload to Airtable
    logger.info("Initializing Airtable Sync...")
    try:
        # a: Read already uploaded data
        uploader.fetch_existing_records()
        
        # b: Match and update
        uploader.sync_data(extracted_data)
        
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
