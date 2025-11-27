"""
Data Extraction Inspector
=========================

This script extracts data from DOCX files and creates detailed JSON logs
for verification BEFORE uploading to Airtable.

Usage:
    python inspector.py --folder "path/to/folder"
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from modules.data_extractor import DataExtractor


def setup_logging():
    """Setup logging configuration"""
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"inspector_{timestamp}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__), log_file


def create_inspection_report(data: dict, folder_name: str, log_dir: Path):
    """
    Create a detailed JSON inspection report
    
    Order: Metas -> Lenses -> Sources -> Patterns -> Variations
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = log_dir / f"inspection_{folder_name}_{timestamp}.json"
    
    report = {
        "folder": folder_name,
        "timestamp": timestamp,
        "summary": {
            "total_metas": len(data.get("metas", [])),
            "total_lenses": 0,
            "total_sources": 0,
            "total_patterns": 0,
            "total_variations": 0
        },
        "details": {
            "metas": [],
            "lenses": [],
            "sources": [],
            "patterns": [],
            "variations": []
        }
    }
    
    # 1. METAS
    for meta in data.get("metas", []):
        report["details"]["metas"].append({
            "title": meta.get("title"),
            "subtitle": meta.get("subtitle", "")[:100] + "..." if len(meta.get("subtitle", "")) > 100 else meta.get("subtitle", ""),
            "content_length": len(meta.get("content", "")),
            "base_folder": meta.get("base_folder")
        })
    
    # 2. LENSES, SOURCES, PATTERNS, VARIATIONS (from documents)
    for doc in data.get("documents", []):
        lens_name = doc.get("lens")
        
        # Count lenses
        if lens_name:
            report["summary"]["total_lenses"] += 1
            report["details"]["lenses"].append({
                "name": lens_name,
                "patterns_count": len(doc.get("patterns", []))
            })
        
        # Process patterns
        for pattern in doc.get("patterns", []):
            report["summary"]["total_patterns"] += 1
            
            pattern_info = {
                "lens": lens_name,
                "pattern_number": pattern.get("pattern_number"),
                "title": pattern.get("title"),
                "summary_length": len(pattern.get("summary", "")),
                "sources_count": len(pattern.get("sources", [])),
                "variations_count": len(pattern.get("variations", []))
            }
            
            # 3. SOURCES
            for source in pattern.get("sources", []):
                report["summary"]["total_sources"] += 1
                report["details"]["sources"].append({
                    "pattern": pattern.get("title"),
                    "source_number": source.get("source_number"),
                    "author": source.get("author"),
                    "title": source.get("title"),
                    "year": source.get("year")
                })
            
            # 5. VARIATIONS
            for variation in pattern.get("variations", []):
                report["summary"]["total_variations"] += 1
                report["details"]["variations"].append({
                    "pattern": pattern.get("title"),
                    "variation_number": variation.get("variation_number"),
                    "title": variation.get("title"),
                    "content_length": len(variation.get("content", ""))
                })
            
            report["details"]["patterns"].append(pattern_info)
    
    # Write report
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    return report_file, report["summary"]


def main():
    """Main inspection function"""
    logger, log_file = setup_logging()
    
    logger.info("="*50)
    logger.info("DATA EXTRACTION INSPECTOR")
    logger.info("="*50)
    
    # Parse arguments
    import argparse
    parser = argparse.ArgumentParser(description='Inspect data extraction from DOCX files')
    parser.add_argument('--folder', '-f', required=True, help='Target folder to inspect')
    args = parser.parse_args()
    
    # Determine folder path
    if os.path.isabs(args.folder):
        folder_path = Path(args.folder)
        folder_name = folder_path.name
    else:
        folder_path = settings.SOURCE_DIR / args.folder
        folder_name = args.folder
    
    logger.info(f"Inspecting folder: {folder_path}")
    logger.info(f"Folder name: {folder_name}")
    
    # Extract data
    extractor = DataExtractor()
    logger.info("Starting data extraction...")
    
    try:
        data = extractor.process_folder(str(folder_path))
        
        if not data:
            logger.error("No data extracted!")
            return
        
        logger.info("Data extraction complete!")
        
        # Create inspection report
        log_dir = Path(__file__).parent / "logs"
        report_file, summary = create_inspection_report(data, folder_name, log_dir)
        
        logger.info("="*50)
        logger.info("EXTRACTION SUMMARY")
        logger.info("="*50)
        logger.info(f"Metas:      {summary['total_metas']}")
        logger.info(f"Lenses:     {summary['total_lenses']}")
        logger.info(f"Sources:    {summary['total_sources']}")
        logger.info(f"Patterns:   {summary['total_patterns']}")
        logger.info(f"Variations: {summary['total_variations']}")
        logger.info("="*50)
        logger.info(f"Inspection report saved to: {report_file}")
        logger.info(f"Log file saved to: {log_file}")
        logger.info("="*50)
        
        # Expected counts
        total_docs = len(data.get("documents", []))
        expected_variations = total_docs * 10
        
        logger.info("\nEXPECTED vs ACTUAL:")
        logger.info(f"Expected Variations: {expected_variations} (10 per document)")
        logger.info(f"Actual Variations:   {summary['total_variations']}")
        
        if summary['total_variations'] < expected_variations:
            logger.warning(f"⚠️  Missing {expected_variations - summary['total_variations']} variations!")
        else:
            logger.info("✅ All variations extracted successfully!")
        
    except Exception as e:
        logger.error(f"Error during extraction: {str(e)}", exc_info=True)
        return


if __name__ == "__main__":
    main()
