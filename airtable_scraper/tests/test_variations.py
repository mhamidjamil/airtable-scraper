#!/usr/bin/env python3
from modules.data_extractor import DataExtractor
import json

def main():
    print("Testing variation extraction...")
    
    extractor = DataExtractor()
    data = extractor.process_folder('BIOME')
    
    print("Sample variations from first document:")
    docs = data.get('documents', [])
    if docs:
        print('Total documents:', len(docs))
        for i, doc in enumerate(docs[:2]):
            lens_name = doc.get('lens', 'No lens')
            print(f'Document {i+1}: {lens_name}')
            patterns = doc.get('patterns', [])
            if patterns:
                variations = patterns[0].get('variations', [])
                print(f'  Pattern 1 has {len(variations)} variations')
                for v in variations[:5]:
                    var_num = v.get('variation_number', '?')
                    title = v.get('title', 'No title')
                    print(f'    Variation {var_num}: {title[:60]}...')
            else:
                print('  No patterns found')
        
        # Save sample data for inspection
        print("\nSaving sample data to test_output.json...")
        with open('test_output.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("Done!")
    else:
        print('No documents found')

if __name__ == "__main__":
    main()