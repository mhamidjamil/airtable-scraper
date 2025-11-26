"""
Airtable API Upload - Step 1: Generate JSON Files
Converts extracted data to JSON format for API upload

This script creates JSON files with human-readable references
that will be converted to Airtable IDs during upload
"""

import os
import json
from datetime import datetime
from pathlib import Path


def load_extraction_data(data_dir: str) -> dict:
    """Load the latest BIOME extraction JSON"""
    pattern = "biome_extracted_*.json"
    files = list(Path(data_dir).glob(pattern))
    
    if not files:
        raise FileNotFoundError(f"No extraction files found matching {pattern}")
    
    latest_file = max(files, key=lambda p: p.stat().st_mtime)
    
    print(f"Loading: {latest_file.name}")
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_lenses_json(data: dict) -> list:
    """
    Generate lenses.json with pattern references
    
    Structure:
    {
        "lens_name": "BELOVED BANG",
        "content": "Summary text...",
        "patterns": ["Pattern 1", "Pattern 2", ...]  # Human-readable names
    }
    """
    lens_to_data = {}
    
    for doc in data.get("documents", []):
        lens_name = doc.get("lens", "")
        summary = doc.get("summary", "")
        
        if lens_name:
            if lens_name not in lens_to_data:
                lens_to_data[lens_name] = {
                    "lens_name": lens_name,
                    "content": summary,
                    "patterns": []
                }
            
            # Add pattern titles
            for pattern in doc.get("patterns", []):
                pattern_title = pattern.get("title", "").strip()
                if pattern_title:
                    lens_to_data[lens_name]["patterns"].append(pattern_title)
    
    return list(lens_to_data.values())


def generate_sources_json(data: dict) -> list:
    """
    Generate sources.json with pattern references
    
    Structure:
    {
        "source_name": "Source A",
        "patterns": ["Pattern 1", "Pattern 3", ...]
    }
    """
    source_to_patterns = {}
    
    for doc in data.get("documents", []):
        for pattern in doc.get("patterns", []):
            source = pattern.get("source", "").strip()
            pattern_title = pattern.get("title", "").strip()
            
            if source:
                if source not in source_to_patterns:
                    source_to_patterns[source] = {
                        "source_name": source,
                        "patterns": []
                    }
                if pattern_title:
                    source_to_patterns[source]["patterns"].append(pattern_title)
    
    return list(source_to_patterns.values())


def generate_metas_json(data: dict) -> list:
    """
    Generate metas.json with pattern references
    
    Structure:
    {
        "title": "META Title",
        "subtitle": "Subtitle",
        "content": "Full content...",
        "base_folder": "BIOME",
        "patterns": []  # Will be linked manually or by base_folder
    }
    """
    metas = []
    
    # Get all pattern titles from same base_folder for linking
    base_folder = data.get("base_folder", "")
    pattern_titles = []
    
    for doc in data.get("documents", []):
        for pattern in doc.get("patterns", []):
            pattern_title = pattern.get("title", "").strip()
            if pattern_title:
                pattern_titles.append(pattern_title)
    
    for meta in data.get("metas", []):
        metas.append({
            "title": meta.get("title", ""),
            "subtitle": meta.get("subtitle", ""),
            "content": meta.get("content", ""),
            "base_folder": meta.get("base_folder", ""),
            "patterns": pattern_titles  # All patterns from same base_folder
        })
    
    return metas


def generate_variations_json(data: dict) -> list:
    """
    Generate variations.json with temp pattern IDs
    
    Structure:
    {
        "variation_title": "Variation A",
        "variation_number": 6,
        "content": "Content...",
        "pattern_temp_id": "pattern_1"  # Matches patterns.json
    }
    """
    variations = []
    pattern_counter = 1
    pattern_to_temp_id = {}
    
    for doc in data.get("documents", []):
        for pattern in doc.get("patterns", []):
            pattern_title = pattern.get("title", "")
            
            # Assign temp ID
            if pattern_title not in pattern_to_temp_id:
                pattern_to_temp_id[pattern_title] = f"pattern_{pattern_counter}"
                pattern_counter += 1
            
            temp_id = pattern_to_temp_id[pattern_title]
            
            # Add variations
            for var in pattern.get("variations", []):
                variations.append({
                    "variation_title": var.get("title", ""),
                    "variation_number": var.get("variation_number", 0),
                    "content": var.get("content", ""),
                    "pattern_temp_id": temp_id  # Links to pattern
                })
    
    return variations, pattern_to_temp_id


def generate_patterns_json(data: dict, pattern_to_temp_id: dict) -> list:
    """
    Generate patterns.json with human-readable references
    
    Structure:
    {
        "pattern_temp_id": "pattern_1",
        "pattern_id": "P001",
        "pattern_title": "Title",
        "overview": "...",
        "choice": "...",
        "base_folder": "BIOME",
        "lens": "BELOVED BANG",  # Human-readable name
        "sources": ["Source A"],  # Human-readable names
        "variations": ["pattern_1_var1", ...]  # Temp IDs
    }
    """
    patterns = []
    pattern_id_counter = 1
    
    for doc in data.get("documents", []):
        lens_name = doc.get("lens", "")
        base_folder = doc.get("base_folder", "")
        
        for pattern in doc.get("patterns", []):
            pattern_title = pattern.get("title", "")
            temp_id = pattern_to_temp_id.get(pattern_title, f"pattern_{pattern_id_counter}")
            
            # Get variation temp IDs
            variation_temp_ids = []
            for i, var in enumerate(pattern.get("variations", []), 1):
                variation_temp_ids.append(f"{temp_id}_var{i}")
            
            patterns.append({
                "pattern_temp_id": temp_id,
                "pattern_id": f"P{pattern_id_counter:03d}",
                "pattern_title": pattern_title,
                "overview": pattern.get("overview", ""),
                "choice": pattern.get("choice", ""),
                "base_folder": base_folder,
                "lens": lens_name,  # Human-readable name
                "sources": [pattern.get("source", "")],  # List of names
                "variation_temp_ids": variation_temp_ids  # For matching
            })
            
            pattern_id_counter += 1
    
    return patterns


def main():
    """Main execution"""
    # Configuration
    DATA_DIR = r"E:\Work\shoaib\upwork\airtable_manager\data_output"
    OUTPUT_DIR = r"E:\Work\shoaib\upwork\airtable_manager\airtable_api_upload\json_data"
    
    print("=" * 80)
    print("GENERATING JSON FILES FOR AIRTABLE API UPLOAD")
    print("=" * 80)
    print()
    
    # Load data
    data = load_extraction_data(DATA_DIR)
    print(f"Base Folder: {data.get('base_folder', 'Unknown')}\n")
    
    # Generate JSON files
    print("Generating JSON files...")
    
    # 1. Lenses
    lenses = generate_lenses_json(data)
    lenses_file = os.path.join(OUTPUT_DIR, "lenses.json")
    with open(lenses_file, 'w', encoding='utf-8') as f:
        json.dump(lenses, f, indent=2, ensure_ascii=False)
    print(f"  ✓ lenses.json ({len(lenses)} records)")
    
    # 2. Sources
    sources = generate_sources_json(data)
    sources_file = os.path.join(OUTPUT_DIR, "sources.json")
    with open(sources_file, 'w', encoding='utf-8') as f:
        json.dump(sources, f, indent=2, ensure_ascii=False)
    print(f"  ✓ sources.json ({len(sources)} records)")
    
    # 3. METAS
    metas = generate_metas_json(data)
    metas_file = os.path.join(OUTPUT_DIR, "metas.json")
    with open(metas_file, 'w', encoding='utf-8') as f:
        json.dump(metas, f, indent=2, ensure_ascii=False)
    print(f"  ✓ metas.json ({len(metas)} records)")
    
    # 4. Variations (returns temp ID mapping)
    variations, pattern_to_temp_id = generate_variations_json(data)
    variations_file = os.path.join(OUTPUT_DIR, "variations.json")
    with open(variations_file, 'w', encoding='utf-8') as f:
        json.dump(variations, f, indent=2, ensure_ascii=False)
    print(f"  ✓ variations.json ({len(variations)} records)")
    
    # 5. Patterns
    patterns = generate_patterns_json(data, pattern_to_temp_id)
    patterns_file = os.path.join(OUTPUT_DIR, "patterns.json")
    with open(patterns_file, 'w', encoding='utf-8') as f:
        json.dump(patterns, f, indent=2, ensure_ascii=False)
    print(f"  ✓ patterns.json ({len(patterns)} records)")
    
    print()
    print("=" * 80)
    print("JSON GENERATION COMPLETE!")
    print("=" * 80)
    print(f"\nOutput directory: {OUTPUT_DIR}")
    print("\nNext step: Run upload_to_airtable.py")
    print()


if __name__ == "__main__":
    main()
