#!/usr/bin/env python3
"""
Test variation extraction from BELOVED BANG.docx to see if we get all 10 variations
"""

from modules.data_extractor import DataExtractor
import os
import sys

def test_beloved_bang():
    extractor = DataExtractor()
    
    # Test by processing just the BIOME folder and finding BELOVED BANG specifically
    try:
        print("Processing BIOME folder to find BELOVED BANG variations...")
        result = extractor.process_folder('BIOME')
        
        # Find the BELOVED BANG file data
        beloved_bang_data = None
        for file_data in result.get('files', []):
            if 'BELOVED BANG' in file_data.get('file_path', ''):
                beloved_bang_data = file_data
                break
        
        if not beloved_bang_data:
            print("❌ BELOVED BANG.docx not found in processing results")
            return False
            
        print(f"Found BELOVED BANG.docx in results")
        
        variations = beloved_bang_data.get('variations', [])
        print(f"Total variations extracted: {len(variations)}")
        
        print("\nVariation details:")
        for i, var in enumerate(variations, 1):
            print(f"{i:2d}. Variation {var['variation_number']:2d}: {var['title']}")
        
        if len(variations) == 10:
            print("\n✅ SUCCESS: All 10 variations extracted!")
            return True
        else:
            print(f"\n❌ ISSUE: Only {len(variations)} variations extracted instead of 10")
            
            # Show what we expected
            expected_titles = [
                "THE FIRST YES THAT STILL ECHOES",
                "NEURONS IN A COSMIC HEART", 
                "THE UNIVERSE PRACTICING COMPOSITION",
                "MATTER LEARNING TO RISK INTIMACY",
                "THE GARDEN GENERATION AS COSMIC REMEMBERERS",
                "FROM COSMIC ORPHANHOOD TO COSMIC BELONGING",
                "WELLGORITHMS AS LITURGIES OF THE BELOVED BANG",
                "THE COSMOS AS A LOVE-BIASED FIELD",
                "YOUR EXISTENCE AS COSMIC VICTORY",
                "SUPERLOVE AS COSMIC IMPERATIVE"
            ]
            
            print("\nExpected variations:")
            for i, title in enumerate(expected_titles, 1):
                print(f"{i:2d}. {title}")
            
            print("\nMissing variations:")
            extracted_titles = [var['title'] for var in variations]
            for i, title in enumerate(expected_titles, 1):
                if title not in extracted_titles:
                    print(f"{i:2d}. {title}")
            
            return False
            
    except Exception as e:
        print(f"❌ Error during extraction: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_all_biome_files():
    """Test all BIOME files to get total variation count"""
    extractor = DataExtractor()
    
    try:
        print("Processing all BIOME files...")
        result = extractor.process_folder('BIOME')
        
        total_variations = 0
        files_processed = 0
        
        print("\nFile breakdown:")
        for file_data in result.get('files', []):
            file_name = os.path.basename(file_data.get('file_path', ''))
            variations = file_data.get('variations', [])
            total_variations += len(variations)
            files_processed += 1
            print(f"{file_name}: {len(variations)} variations")
        
        print(f"\n📊 SUMMARY:")
        print(f"Files processed: {files_processed}")
        print(f"Total variations: {total_variations}")
        print(f"Expected total: {files_processed * 10}")
        
        if total_variations == files_processed * 10:
            print("✅ SUCCESS: All variations extracted correctly!")
        else:
            print(f"❌ ISSUE: Missing {files_processed * 10 - total_variations} variations")
            
    except Exception as e:
        print(f"❌ Error during processing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 80)
    print("TESTING BELOVED BANG VARIATION EXTRACTION")
    print("=" * 80)
    
    success = test_beloved_bang()
    
    print("\n" + "=" * 80)
    print("TESTING ALL BIOME FILES")
    print("=" * 80)
    
    test_all_biome_files()