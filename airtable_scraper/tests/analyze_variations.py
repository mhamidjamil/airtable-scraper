#!/usr/bin/env python3
from modules.data_extractor import DataExtractor
import json

def main():
    print("Detailed variation analysis...")
    
    extractor = DataExtractor()
    data = extractor.process_folder('BIOME')
    
    docs = data.get('documents', [])
    total_variations = 0
    
    for i, doc in enumerate(docs):
        lens_name = doc.get('lens', 'No lens')
        patterns = doc.get('patterns', [])
        
        print(f"\nDocument {i+1}: {lens_name}")
        
        for j, pattern in enumerate(patterns):
            pattern_title = pattern.get('title', 'No title')
            variations = pattern.get('variations', [])
            pattern_variations_count = len(variations)
            total_variations += pattern_variations_count
            
            print(f"  Pattern {j+1}: {pattern_title}")
            print(f"    Variations count: {pattern_variations_count}")
            
            if pattern_variations_count < 10:
                print(f"    ⚠️  Expected 10 variations, found only {pattern_variations_count}")
                
            # Show all variations for this pattern
            for k, v in enumerate(variations):
                var_num = v.get('variation_number', '?')
                title = v.get('title', 'No title')
                pattern_ref = v.get('pattern_reference', 1)
                print(f"    Var {var_num} (Pattern {pattern_ref}): {title[:80]}...")
                
                # Check if title looks suspicious (too short, empty, etc)
                if len(title) < 5:
                    print(f"      🔴 Short title detected: '{title}'")
    
    print(f"\n📊 Summary:")
    print(f"Total documents: {len(docs)}")
    print(f"Total variations extracted: {total_variations}")
    print(f"Average variations per document: {total_variations/len(docs) if docs else 0:.1f}")
    
    # Check for patterns with unusual variation counts
    unusual_patterns = []
    for doc in docs:
        for pattern in doc.get('patterns', []):
            var_count = len(pattern.get('variations', []))
            if var_count != 10:
                unusual_patterns.append({
                    'doc': doc.get('lens'),
                    'pattern': pattern.get('title'),
                    'count': var_count
                })
    
    if unusual_patterns:
        print(f"\n⚠️  Patterns with unusual variation counts:")
        for p in unusual_patterns:
            print(f"  - {p['doc']}/{p['pattern']}: {p['count']} variations")

if __name__ == "__main__":
    main()