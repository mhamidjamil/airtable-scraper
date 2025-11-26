"""
Data Inventory Script for new_extractions folder
Analyzes all folders and generates complete manifest
"""

import os
import json
from pathlib import Path
from collections import defaultdict

def analyze_folder_structure(base_path):
    """Analyze the folder structure and count files"""
    base_path = Path(base_path)
    
    inventory = {
        "total_base_folders": 0,
        "base_folders": {},
        "total_docx_files": 0,
        "total_metas_files": 0,
        "summary": {}
    }
    
    # Get all base folders
    for base_folder in sorted(base_path.iterdir()):
        if not base_folder.is_dir():
            continue
            
        inventory["total_base_folders"] += 1
        folder_name = base_folder.name
        
        folder_info = {
            "path": str(base_folder),
            "subfolders": {},
            "total_files": 0,
            "metas_count": 0
        }
        
        # Analyze subfolders
        for subfolder in base_folder.iterdir():
            if not subfolder.is_dir():
                continue
                
            subfolder_name = subfolder.name
            docx_files = list(subfolder.glob("*.docx"))
            
            folder_info["subfolders"][subfolder_name] = {
                "path": str(subfolder),
                "docx_count": len(docx_files),
                "files": [f.name for f in docx_files]
            }
            
            folder_info["total_files"] += len(docx_files)
            inventory["total_docx_files"] += len(docx_files)
            
            # Track METAS specifically
            if "META" in subfolder_name.upper():
                folder_info["metas_count"] = len(docx_files)
                inventory["total_metas_files"] += len(docx_files)
        
        inventory["base_folders"][folder_name] = folder_info
    
    return inventory


def analyze_json_patterns(json_path):
    """Analyze the extracted patterns from JSON"""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    analysis = {
        "total_documents": data.get("total_documents", 0),
        "extraction_timestamp": data.get("extraction_timestamp", ""),
        "patterns_by_folder": defaultdict(int),
        "unique_lenses": set(),
        "unique_sources": set(),
        "total_patterns": 0,
        "total_variations": 0,
        "patterns_with_variations": 0,
        "patterns_without_variations": 0
    }
    
    documents = data.get("documents", {})
    
    for folder, docs in documents.items():
        for doc in docs:
            # Extract base folder from file_path
            file_path = doc.get("file_path", "")
            base_folder = file_path.split("/")[0] if "/" in file_path else folder
            
            # Collect lens
            lens = doc.get("lens", "")
            if lens:
                analysis["unique_lenses"].add(lens)
            
            # Analyze patterns
            patterns = doc.get("patterns", [])
            analysis["patterns_by_folder"][base_folder] += len(patterns)
            analysis["total_patterns"] += len(patterns)
            
            for pattern in patterns:
                # Collect sources
                source = pattern.get("source", "")
                if source:
                    analysis["unique_sources"].add(source)
                
                # Count variations
                variations = pattern.get("variations", [])
                variation_count = len(variations)
                analysis["total_variations"] += variation_count
                
                if variation_count > 0:
                    analysis["patterns_with_variations"] += 1
                else:
                    analysis["patterns_without_variations"] += 1
    
    # Convert sets to sorted lists for JSON serialization
    analysis["unique_lenses"] = sorted(list(analysis["unique_lenses"]))
    analysis["unique_sources"] = sorted(list(analysis["unique_sources"]))
    analysis["patterns_by_folder"] = dict(analysis["patterns_by_folder"])
    
    return analysis


def generate_report(folder_inventory, json_analysis, output_path):
    """Generate a comprehensive report"""
    
    report = []
    report.append("=" * 80)
    report.append("DATA INVENTORY REPORT - new_extractions")
    report.append("=" * 80)
    report.append("")
    
    # Folder Structure Summary
    report.append("📁 FOLDER STRUCTURE SUMMARY")
    report.append("-" * 80)
    report.append(f"Total Base Folders: {folder_inventory['total_base_folders']}")
    report.append(f"Total .docx Files: {folder_inventory['total_docx_files']}")
    report.append(f"Total METAS Files: {folder_inventory['total_metas_files']}")
    report.append("")
    
    # Base Folders Breakdown
    report.append("📂 BASE FOLDERS BREAKDOWN")
    report.append("-" * 80)
    for folder_name, info in folder_inventory["base_folders"].items():
        report.append(f"\n{folder_name}/")
        report.append(f"  Total Files: {info['total_files']}")
        report.append(f"  METAS Files: {info['metas_count']}")
        report.append(f"  Subfolders:")
        for subfolder_name, subfolder_info in info["subfolders"].items():
            report.append(f"    - {subfolder_name}/ ({subfolder_info['docx_count']} files)")
    report.append("")
    
    # JSON Patterns Summary
    report.append("\n📊 EXTRACTED PATTERNS SUMMARY (from new_patterns_output.json)")
    report.append("-" * 80)
    report.append(f"Total Documents Processed: {json_analysis['total_documents']}")
    report.append(f"Extraction Timestamp: {json_analysis['extraction_timestamp']}")
    report.append(f"Total Patterns Extracted: {json_analysis['total_patterns']}")
    report.append(f"Total Variations: {json_analysis['total_variations']}")
    report.append(f"Patterns WITH Variations: {json_analysis['patterns_with_variations']}")
    report.append(f"Patterns WITHOUT Variations: {json_analysis['patterns_without_variations']}")
    report.append("")
    
    # Patterns by Folder
    report.append("📈 PATTERNS BY BASE FOLDER")
    report.append("-" * 80)
    for folder, count in sorted(json_analysis['patterns_by_folder'].items()):
        report.append(f"  {folder}: {count} patterns")
    report.append("")
    
    # Unique Lenses
    report.append(f"\n🔍 UNIQUE LENSES ({len(json_analysis['unique_lenses'])})")
    report.append("-" * 80)
    for lens in json_analysis['unique_lenses']:
        report.append(f"  - {lens}")
    report.append("")
    
    # Unique Sources
    report.append(f"\n📚 UNIQUE SOURCES ({len(json_analysis['unique_sources'])})")
    report.append("-" * 80)
    for source in json_analysis['unique_sources']:
        report.append(f"  - {source}")
    report.append("")
    
    # Critical Gaps
    report.append("\n⚠️  CRITICAL GAPS & ACTION ITEMS")
    report.append("-" * 80)
    report.append(f"1. METAS Files Found: {folder_inventory['total_metas_files']}")
    report.append(f"   STATUS: Need to extract content from these files")
    report.append(f"   ACTION: Run METAS extraction script")
    report.append("")
    report.append(f"2. Patterns in JSON: {json_analysis['total_patterns']}")
    report.append(f"   MISSING: METAS → Patterns mapping")
    report.append(f"   ACTION: Get client clarification on how to link patterns to METAS")
    report.append("")
    report.append(f"3. Google Drive URLs: Not generated")
    report.append(f"   ACTION: Ask client if needed")
    report.append("")
    
    # Airtable Upload Readiness
    report.append("\n✅ AIRTABLE UPLOAD READINESS")
    report.append("-" * 80)
    report.append("READY TO UPLOAD:")
    report.append(f"  ✅ Lenses Table: {len(json_analysis['unique_lenses'])} records")
    report.append(f"  ✅ Sources Table: {len(json_analysis['unique_sources'])} records")
    report.append(f"  ✅ Patterns Table: {json_analysis['total_patterns']} records (partial - missing METAS links)")
    report.append(f"  ✅ Variations Table: {json_analysis['total_variations']} records")
    report.append("")
    report.append("NOT READY:")
    report.append(f"  ❌ METAS Table: {folder_inventory['total_metas_files']} files need extraction")
    report.append(f"  ❌ Pattern → META Links: Mapping strategy unclear")
    report.append("")
    
    # Save report
    report_text = "\n".join(report)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    return report_text


def main():
    """Main execution"""
    base_path = r"E:\Work\shoaib\upwork\new_extractions"
    json_path = r"E:\Work\shoaib\upwork\pattern_to_json\new_patterns_output.json"
    output_path = r"E:\Work\shoaib\upwork\DATA_INVENTORY_REPORT.txt"
    
    print("🔍 Analyzing folder structure...")
    folder_inventory = analyze_folder_structure(base_path)
    
    print("📊 Analyzing extracted patterns...")
    json_analysis = analyze_json_patterns(json_path)
    
    print("📝 Generating report...")
    report_text = generate_report(folder_inventory, json_analysis, output_path)
    
    print("\n" + report_text)
    print(f"\n✅ Report saved to: {output_path}")
    
    # Save JSON data for programmatic use
    json_output_path = output_path.replace(".txt", ".json")
    with open(json_output_path, 'w', encoding='utf-8') as f:
        json.dump({
            "folder_inventory": folder_inventory,
            "json_analysis": json_analysis
        }, f, indent=2, ensure_ascii=False)
    
    print(f"✅ JSON data saved to: {json_output_path}")


if __name__ == "__main__":
    main()
