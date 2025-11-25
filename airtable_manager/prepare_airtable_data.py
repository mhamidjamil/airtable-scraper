"""
Airtable Manager - CSV Preparation Script
Converts extracted JSON data into CSV files ready for Airtable import

Input: biome_extracted_XXXXXX.json
Output: 5 CSV files (lenses, sources, metas, patterns, variations)

For AI Context: See CONTEXT_FOR_AI.md for schema and relationships
"""

import os
import json
import csv
from datetime import datetime
from pathlib import Path
from collections import Counter


def load_latest_extraction(data_dir: str, base_folder: str = "biome") -> dict:
    """Load the most recent extraction JSON file for a base folder"""
    pattern = f"{base_folder.lower()}_extracted_*.json"
    files = list(Path(data_dir).glob(pattern))
    
    if not files:
        raise FileNotFoundError(f"No extraction files found matching {pattern}")
    
    # Get most recent file
    latest_file = max(files, key=lambda p: p.stat().st_mtime)
    
    print(f"Loading: {latest_file.name}")
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data, latest_file.name


def extract_unique_lenses(data: dict) -> list:
    """
    Extract unique lenses from pattern documents
    
    Returns: List of dicts with lens_name and content (summary)
    """
    lenses = {}
    
    for doc in data.get("documents", []):
        lens_name = doc.get("lens", "")
        summary = doc.get("summary", "")
        
        if lens_name and lens_name not in lenses:
            lenses[lens_name] = {
                "lens_name": lens_name,
                "content": summary  # Use document summary as lens content
            }
    
    return list(lenses.values())


def extract_unique_sources(data: dict) -> list:
    """
    Extract unique sources from all patterns
    
    Returns: List of dicts with source_name
    """
    sources = set()
    
    for doc in data.get("documents", []):
        for pattern in doc.get("patterns", []):
            source = pattern.get("source", "").strip()
            if source:
                sources.add(source)
    
    return [{"source_name": s} for s in sorted(sources)]


def prepare_metas(data: dict) -> list:
    """
    Prepare METAS for CSV export
    
    Schema: title, subtitle, content, base_folder
    linked_patterns: Will be added in Airtable UI
    
    Returns: List of METAS dicts
    """
    metas = []
    
    for meta in data.get("metas", []):
        metas.append({
            "title": meta.get("title", ""),
            "subtitle": meta.get("subtitle", ""),
            "content": meta.get("content", ""),
            "base_folder": meta.get("base_folder", "")
        })
    
    return metas


def prepare_patterns(data: dict) -> list:
    """
    Prepare patterns for CSV export
    
    Schema: pattern_title, base_folder, lens, sources, overview, choice, drive_doc_url
    variations: Will be linked in Airtable automatically
    
    Returns: List of pattern dicts
    """
    patterns = []
    pattern_id = 1
    
    for doc in data.get("documents", []):
        lens_name = doc.get("lens", "")
        base_folder = doc.get("base_folder", "")
        
        for pattern in doc.get("patterns", []):
            patterns.append({
                "pattern_id": f"P{pattern_id:03d}",  # P001, P002, etc.
                "pattern_title": pattern.get("title", ""),
                "base_folder": base_folder,
                "lens": lens_name,
                "sources": pattern.get("source", ""),  # Keep as single value for now
                "overview": pattern.get("overview", ""),
                "choice": pattern.get("choice", ""),
                "drive_doc_url": "",  # Empty for now
                "_variation_count": len(pattern.get("variations", []))  # Info only
            })
            pattern_id += 1
    
    return patterns


def prepare_variations(data: dict) -> list:
    """
    Prepare variations for CSV export
    
    Schema: variation_title, variation_number, content, linked_pattern
    
    Returns: List of variation dicts
    """
    variations = []
    
    for doc in data.get("documents", []):
        for pattern in doc.get("patterns", []):
            pattern_title = pattern.get("title", "")
            
            for variation in pattern.get("variations", []):
                variations.append({
                    "variation_number": variation.get("variation_number", 0),
                    "variation_title": variation.get("title", ""),
                    "content": variation.get("content", ""),
                    "linked_pattern": pattern_title  # Will match pattern_title in Patterns table
                })
    
    return variations


def write_csv(filename: str, data: list, fieldnames: list):
    """Write data to CSV file"""
    if not data:
        print(f"  ⚠️  No data to write for {filename}")
        return
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(data)
    
    print(f"  ✓ {filename} ({len(data)} records)")


def generate_import_instructions(output_dir: str, stats: dict):
    """Generate instructions for importing to Airtable"""
    instructions = """
# 📥 Airtable Import Instructions

## **Import Order (CRITICAL!)**

Import CSV files in this exact order to maintain relationships:

### **1. Import Lenses Table**
- File: `lenses.csv`
- Records: {lenses_count}
- Fields: lens_name, content
- **No dependencies**

### **2. Import Sources Table**
- File: `sources.csv`
- Records: {sources_count}
- Fields: source_name
- **No dependencies**

### **3. Import METAS Table**
- File: `metas.csv`
- Records: {metas_count}
- Fields: title, subtitle, content, base_folder
- **Note:** linked_patterns field will be linked manually after Patterns are imported

### **4. Import Patterns Table**
- File: `patterns.csv`
- Records: {patterns_count}
- Fields: pattern_title, base_folder, lens, sources, overview, choice, drive_doc_url
- **Link these fields during import:**
  - `lens` → Links to Lenses table (match by lens_name)
  - `sources` → Links to Sources table (match by source_name)
  - `_variation_count` is INFO ONLY (don't import this field)

### **5. Import Variations Table**
- File: `variations.csv`
- Records: {variations_count}
- Fields: variation_number, variation_title, content, linked_pattern
- **Link this field during import:**
  - `linked_pattern` → Links to Patterns table (match by pattern_title)

---

## **How to Import in Airtable**

1. **Open your Airtable base**

2. **For each table, click "+ Add or import" → "CSV file"**

3. **Upload the CSV file**

4. **Configure Field Types:**
   - Text fields: Use "Single line text" or "Long text" as appropriate
   - Link fields: Choose "Link to another record" and select target table

5. **Match Fields:**
   - Airtable will try to auto-match column names
   - Verify the field mapping is correct

6. **Import!**

---

## **After Import**

### **Link METAS to Patterns:**
- Go to METAS table
- Click on a META record
- In `linked_patterns` field, search for patterns that belong to this META
- ⚠️ **MANUAL STEP:** Client must clarify which patterns belong to which METAS

### **Verify Relationships:**
- Check that Patterns show linked Lens
- Check that Patterns show linked Sources
- Check that Variations show linked Pattern
- Check that variation counts match expectations

---

## **Data Summary**

- **METAS:** {metas_count} organizing themes
- **Lenses:** {lenses_count} interpretive frameworks
- **Sources:** {sources_count} unique attributions
- **Patterns:** {patterns_count} main content pieces
- **Variations:** {variations_count} alternative formulations

**Base Folder:** {base_folder}
**Extraction Time:** {timestamp}

---

## **Known Issues to Review**

1. **METAS → Patterns mapping:** Currently unmapped (client input needed)
2. **drive_doc_url:** Empty (can be populated later if Google Docs are generated)
3. **Patterns without variations:** Some patterns may have no variations (this is normal)

---

✅ **CSV files are ready for import!**
""".format(**stats)
    
    instructions_file = os.path.join(output_dir, "IMPORT_INSTRUCTIONS.md")
    with open(instructions_file, 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print(f"\n📄 Import instructions saved to: IMPORT_INSTRUCTIONS.md")


def main():
    """Main execution"""
    # Configuration
    DATA_DIR = r"E:\Work\shoaib\upwork\airtable_manager\data_output"
    OUTPUT_DIR = DATA_DIR
    BASE_FOLDER = "BIOME"
    
    print("=" * 80)
    print("PREPARING AIRTABLE CSV FILES")
    print("=" * 80)
    print()
    
    # Load extraction data
    data, source_file = load_latest_extraction(DATA_DIR, BASE_FOLDER)
    
    print(f"Base Folder: {data.get('base_folder', 'Unknown')}")
    print(f"Extraction Time: {data.get('extraction_timestamp', 'Unknown')}")
    print()
    
    # Extract unique data
    print("Extracting unique data...")
    lenses = extract_unique_lenses(data)
    sources = extract_unique_sources(data)
    metas = prepare_metas(data)
    patterns = prepare_patterns(data)
    variations = prepare_variations(data)
    
    print(f"  - {len(lenses)} unique lenses")
    print(f"  - {len(sources)} unique sources")
    print(f"  - {len(metas)} METAS")
    print(f"  - {len(patterns)} patterns")
    print(f"  - {len(variations)} variations")
    print()
    
    # Write CSV files
    print("Writing CSV files...")
    
    write_csv(
        os.path.join(OUTPUT_DIR, "lenses.csv"),
        lenses,
        ["lens_name", "content"]
    )
    
    write_csv(
        os.path.join(OUTPUT_DIR, "sources.csv"),
        sources,
        ["source_name"]
    )
    
    write_csv(
        os.path.join(OUTPUT_DIR, "metas.csv"),
        metas,
        ["title", "subtitle", "content", "base_folder"]
    )
    
    write_csv(
        os.path.join(OUTPUT_DIR, "patterns.csv"),
        patterns,
        ["pattern_id", "pattern_title", "base_folder", "lens", "sources", 
         "overview", "choice", "drive_doc_url", "_variation_count"]
    )
    
    write_csv(
        os.path.join(OUTPUT_DIR, "variations.csv"),
        variations,
        ["variation_number", "variation_title", "content", "linked_pattern"]
    )
    
    print()
    
    # Generate import instructions
    stats = {
        "lenses_count": len(lenses),
        "sources_count": len(sources),
        "metas_count": len(metas),
        "patterns_count": len(patterns),
        "variations_count": len(variations),
        "base_folder": data.get("base_folder", "Unknown"),
        "timestamp": data.get("extraction_timestamp", "Unknown")
    }
    
    generate_import_instructions(OUTPUT_DIR, stats)
    
    # Summary
    print("\n" + "=" * 80)
    print("CSV PREPARATION COMPLETE!")
    print("=" * 80)
    print()
    print(f"📁 Output directory: {OUTPUT_DIR}")
    print()
    print("CSV Files Created:")
    print(f"  ✓ lenses.csv ({len(lenses)} records)")
    print(f"  ✓ sources.csv ({len(sources)} records)")
    print(f"  ✓ metas.csv ({len(metas)} records)")
    print(f"  ✓ patterns.csv ({len(patterns)} records)")
    print(f"  ✓ variations.csv ({len(variations)} records)")
    print()
    print("Next Step:")
    print("1. Open IMPORT_INSTRUCTIONS.md for detailed import steps")
    print("2. Import CSV files to Airtable in the specified order")
    print()


if __name__ == "__main__":
    main()
