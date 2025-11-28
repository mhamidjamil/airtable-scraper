#!/usr/bin/env python3
"""
Enhanced Data Inspector - Uses centralized extraction logic to analyze data before syncing to Airtable
This inspector helps you validate extraction results and identify any missing data
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.data_extractor import DataExtractor
from config import settings


class DataInspector:
    """Inspector that uses centralized extraction logic to analyze data"""
    
    def __init__(self):
        self.extractor = DataExtractor()
        
    def find_project_folders(self, start_path_str: str) -> List[Path]:
        """
        Uses same logic as main.py to identify project folders to process.
        Logic:
        1. If start_path has 'STEP 2' (case-insensitive) or .docx files, it's a project.
        2. Else, check immediate subdirectories for the same criteria.
        """
        # Resolve path
        if os.path.isabs(start_path_str):
            start_path = Path(start_path_str)
        else:
            start_path = settings.SOURCE_DIR / start_path_str
            
        if not start_path.exists():
            print(f"❌ Path not found: {start_path}")
            return []

        projects = []
        
        def is_project(p: Path) -> bool:
            # Check for STEP 2 folder
            if (p / "STEP 2").exists() or (p / "Step 2").exists():
                return True
            # Check for docx files (excluding temp files)
            has_files = any(f for f in p.glob("*.docx") if not f.name.startswith("~$"))
            return has_files

        if is_project(start_path):
            projects.append(start_path)
        else:
            # Check subdirectories
            print(f"Checking subdirectories of {start_path} for projects...")
            for child in start_path.iterdir():
                if child.is_dir() and is_project(child):
                    projects.append(child)
                    
        return projects

    def inspect_folder(self, folder_path: str, extract_types: List[str] = None) -> Dict:
        """
        Inspect extraction results from a folder using same logic as main.py
        
        Args:
            folder_path: Path to folder to inspect  
            extract_types: List of data types to extract and inspect
            
        Returns:
            Dict with inspection results and recommendations
        """
        print(f"🔍 INSPECTING FOLDER: {folder_path}")
        print("=" * 60)
        
        # Use same project finding logic as main.py
        project_folders = self.find_project_folders(folder_path)
        
        if not project_folders:
            print(f"❌ No valid project folders found in/at: {folder_path}")
            return {"error": "No valid project folders found", "folders_checked": folder_path}
        
        print(f"📁 Found {len(project_folders)} project(s) to process: {[p.name for p in project_folders]}")
        
        all_results = {}
        
        for project_folder in project_folders:
            print(f"\n🔍 Processing Project: {project_folder.name}")
            
            # Use centralized extractor with same flow as main.py - include all types like main.py does
            if not extract_types:
                extract_types = ['lenses', 'sources', 'metas', 'patterns', 'variations']
            extraction_data = self.extractor.process_folder(str(project_folder), extract_types)
            
            # Analyze extraction results
            inspection_results = self._analyze_extraction(extraction_data, str(project_folder))
            
            # Add short content analysis before removing raw data
            self._add_content_analysis(inspection_results, extraction_data)
            
            # Don't store raw extraction_data in logs - only analysis needed for debugging
            all_results[project_folder.name] = inspection_results
        
        # Generate overall recommendations
        recommendations = self._generate_recommendations(all_results)
        
        # Create full inspection report
        report = {
            "timestamp": datetime.now().isoformat(),
            "folder_path": folder_path,
            "project_folders": [str(p) for p in project_folders],
            "extraction_results": all_results,
            "recommendations": recommendations,
            "ready_for_sync": any(self._check_sync_readiness(result) for result in all_results.values()) if all_results else False
        }
        
        # Display results for all projects
        for project_name, result in all_results.items():
            print(f"\n🔍 Results for {project_name}:")
            self._display_inspection_results(result, recommendations)
        
        return report
    
    def _analyze_extraction(self, data: Dict, folder_path: str) -> Dict:
        """Analyze the extracted data for completeness and quality"""
        
        documents = data.get("documents", [])
        metas = data.get("metas", [])
        
        # Count totals
        total_patterns = sum(len(doc.get("patterns", [])) for doc in documents)
        total_variations = sum(len(pattern.get("variations", [])) 
                             for doc in documents 
                             for pattern in doc.get("patterns", []))
        total_sources = sum(len(doc.get("sources", [])) for doc in documents)
        total_lenses = len([doc.get("lens") for doc in documents if doc.get("lens")])
        
        # Analyze document completeness
        doc_analysis = []
        for doc in documents:
            patterns = doc.get("patterns", [])
            sources = doc.get("sources", [])
            lens = doc.get("lens", "")
            
            # Check for issues
            issues = []
            
            if not patterns:
                issues.append("No patterns found")
            else:
                # Check pattern completeness
                for i, pattern in enumerate(patterns):
                    if not pattern.get("title"):
                        issues.append(f"Pattern {i+1} missing title")
                    if not pattern.get("variations"):
                        issues.append(f"Pattern {i+1} has no variations")
                    if not pattern.get("overview"):
                        issues.append(f"Pattern {i+1} missing overview")
            
            if not sources:
                issues.append("No sources found")
            
            if not lens:
                issues.append("No lens detected")
            
            # Create detailed pattern-variation analysis
            details = self._create_pattern_variation_details(patterns)
            
            doc_analysis.append({
                "filename": doc.get("file_path", "").split("/")[-1] if doc.get("file_path") else "Unknown",
                "lens": lens,
                "patterns_count": len(patterns),
                "variations_count": sum(len(p.get("variations", [])) for p in patterns),
                "sources_count": len(sources),
                "issues": issues,
                "status": "✅ GOOD" if not issues else "⚠️ HAS ISSUES",
                "details": details
            })
        
        # Check folder structure
        folder_path_obj = Path(folder_path)
        has_step2 = (folder_path_obj / "Step 2").exists() or (folder_path_obj / "STEP 2").exists()
        has_metas = (folder_path_obj / "METAS").exists()
        
        return {
            "totals": {
                "documents": len(documents),
                "patterns": total_patterns,
                "variations": total_variations,
                "sources": total_sources,
                "lenses": total_lenses,
                "metas": len(metas)
            },
            "document_analysis": doc_analysis,
            "folder_structure": {
                "has_step2_folder": has_step2,
                "has_metas_folder": has_metas,
                "docx_files_found": len([f for f in folder_path_obj.glob("*.docx") if not f.name.startswith("~$")])
            },
            "data_quality": {
                "documents_with_issues": len([d for d in doc_analysis if d["issues"]]),
                "documents_without_patterns": len([d for d in doc_analysis if d["patterns_count"] == 0]),
                "documents_without_variations": len([d for d in doc_analysis if d["variations_count"] == 0]),
                "documents_without_sources": len([d for d in doc_analysis if d["sources_count"] == 0])
            }
        }
    
    def _generate_recommendations(self, all_results: Dict) -> List[str]:
        """Generate actionable recommendations based on analysis of all projects"""
        recommendations = []
        
        # Aggregate totals from all projects
        total_docs = sum(result.get("totals", {}).get("documents", 0) for result in all_results.values())
        total_patterns = sum(result.get("totals", {}).get("patterns", 0) for result in all_results.values())
        total_variations = sum(result.get("totals", {}).get("variations", 0) for result in all_results.values())
        
        # Count quality issues across all projects
        total_issues = sum(result.get("data_quality", {}).get("documents_with_issues", 0) for result in all_results.values())
        total_missing_sources = sum(result.get("data_quality", {}).get("documents_without_sources", 0) for result in all_results.values())
        
        # Check basic extraction
        if total_docs == 0:
            recommendations.append("🚨 CRITICAL: No documents found. Check folder path and ensure .docx files exist.")
        
        if total_patterns == 0:
            recommendations.append("🚨 CRITICAL: No patterns extracted. Check document format - patterns should start with 'Pattern N:'")
        
        if total_variations == 0:
            recommendations.append("🚨 CRITICAL: No variations extracted. Check variation format in documents.")
        
        # Check data quality issues
        if total_issues > 0:
            recommendations.append(f"⚠️ {total_issues} documents have issues. Check individual document analysis below.")
        
        if total_missing_sources > 0:
            recommendations.append(f"⚠️ {total_missing_sources} documents missing sources. Ensure each pattern has source information.")
        
        # Check folder structure (use first result for structure info)
        first_result = next(iter(all_results.values())) if all_results else {}
        structure = first_result.get("folder_structure", {})
        
        if not structure.get("has_step2_folder", False):
            recommendations.append("💡 No 'Step 2' folder found. Will process main folder documents.")
        
        if not structure.get("has_metas_folder", False):
            recommendations.append("💡 No 'METAS' folder found. Meta extraction will be skipped.")
        
        # Positive feedback
        if not recommendations:
            recommendations.append("✅ All looks good! Data is ready for Airtable sync.")
            
        if total_patterns > 0 and total_variations > 0:
            recommendations.append(f"✅ Successfully extracted {total_patterns} patterns with {total_variations} variations.")
        
        return recommendations
    
    def _check_sync_readiness(self, analysis: Dict) -> bool:
        """Check if data is ready for Airtable sync"""
        totals = analysis["totals"]
        quality = analysis["data_quality"]
        
        # Must have documents, patterns, and variations
        has_core_data = totals["documents"] > 0 and totals["patterns"] > 0 and totals["variations"] > 0
        
        # Must not have critical issues
        no_critical_issues = quality["documents_without_patterns"] == 0
        
        return has_core_data and no_critical_issues
    
    def _display_inspection_results(self, analysis: Dict, recommendations: List[str]):
        """Display formatted inspection results"""
        
        print("\n📊 EXTRACTION SUMMARY")
        print("-" * 40)
        totals = analysis["totals"]
        for key, value in totals.items():
            print(f"{key.capitalize():15}: {value}")
        
        print(f"\n📁 FOLDER STRUCTURE")
        print("-" * 40)
        structure = analysis["folder_structure"]
        for key, value in structure.items():
            status = "✅" if value else "❌"
            print(f"{status} {key.replace('_', ' ').title()}: {value}")
        
        print(f"\n📄 DOCUMENT ANALYSIS") 
        print("-" * 40)
        for doc in analysis["document_analysis"]:
            print(f"\n📖 {doc['filename']}")
            print(f"   Lens: {doc['lens'] or 'Not detected'}")
            print(f"   Patterns: {doc['patterns_count']}")
            print(f"   Variations: {doc['variations_count']}")
            print(f"   Sources: {doc['sources_count']}")
            print(f"   Status: {doc['status']}")
            
            if doc['issues']:
                print(f"   Issues:")
                for issue in doc['issues']:
                    print(f"     • {issue}")
        
        print(f"\n💡 RECOMMENDATIONS")
        print("-" * 40)
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
        
        print(f"\n🔄 SYNC READINESS")
        print("-" * 40)
        ready = self._check_sync_readiness(analysis)
        status = "✅ READY FOR SYNC" if ready else "⚠️ NOT READY - Fix issues above"
        print(f"Status: {status}")
        
        if ready:
            print("\n🚀 You can proceed with:")
            print("   python main.py --folder 'path' --variations --sync")
        else:
            print("\n🔧 Please fix the issues above before syncing to Airtable")
    
    def _create_pattern_variation_details(self, patterns):
        """Create detailed analysis of pattern-variation relationships"""
        def get_short_content(text, word_limit=10):
            """Get first 10 words only"""
            if not text:
                return "No content"
            words = text.split()
            if len(words) <= word_limit:
                return text
            return ' '.join(words[:word_limit]) + "..."
        
        details = {}
        total_variations = sum(len(p.get("variations", [])) for p in patterns)
        total_patterns = len(patterns)
        
        # Determine overall mapping type
        if total_variations == 0:
            mapping_type = "no-variations"
        elif total_variations == total_patterns:
            mapping_type = "1-to-1"
        elif total_variations > total_patterns:
            mapping_type = "mixed"
        else:
            mapping_type = "many-to-1"
        
        details["mapping_type"] = mapping_type
        details["patterns"] = {}
        
        for i, pattern in enumerate(patterns, 1):
            pattern_title = pattern.get("title", f"Pattern {i}")
            pattern_content = get_short_content(pattern.get("content", ""))
            
            variations_list = []
            for variation in pattern.get("variations", []):
                var_title = variation.get("title", "Untitled variation")
                var_content = get_short_content(variation.get("content", ""))
                variations_list.append({
                    "title": var_title,
                    "content": var_content
                })
            
            details["patterns"][f"pattern_{i}"] = {
                "title": pattern_title,
                "content": pattern_content,
                "variations": variations_list,
                "variation_count": len(variations_list)
            }
        
        return details

    def _add_content_analysis(self, inspection_results: Dict, extraction_data: Dict):
        """Add short content previews for metas and lenses to inspection results"""
        def get_word_preview(text, word_limit=15):
            """Get first 15 words maximum"""
            if not text:
                return "No content"
            words = text.split()
            if len(words) <= word_limit:
                return text
            preview_words = words[:word_limit]
            return f"{' '.join(preview_words)}..."
        
        # Create metas analysis
        metas_analysis = {}
        for meta in extraction_data.get('metas', []):
            title = meta.get('title', 'No title')
            content_preview = get_word_preview(meta.get('content', ''))
            metas_analysis[title] = {
                "content": content_preview
            }
        
        # Create lenses analysis
        lenses_analysis = {}
        for doc in extraction_data.get('documents', []):
            lens_name = doc.get('lens', 'Unknown lens')
            summary_preview = get_word_preview(doc.get('summary', ''))
            
            variations_count = len(doc.get('variations', []))
            patterns_count = len(doc.get('patterns', []))
            
            # Determine mapping type
            if variations_count == patterns_count and variations_count > 0:
                mapping_type = "1-to-1"
            elif variations_count > patterns_count:
                mapping_type = "mixed"  
            elif variations_count < patterns_count and variations_count > 0:
                mapping_type = "all-to-1"
            else:
                mapping_type = "none"
            
            lenses_analysis[lens_name] = {
                "summary": summary_preview,
                "total_patterns": patterns_count,
                "total_variations": variations_count,
                "total_sources": len(doc.get('sources', [])),
                "variation_mapping": mapping_type
            }
        
        inspection_results['metas'] = metas_analysis
        inspection_results['lenses'] = lenses_analysis

    def save_inspection_report(self, report: Dict, output_path: str = None) -> str:
        """Save inspection report to JSON file"""
        
        if not output_path:
            folder_name = Path(report["folder_path"]).name
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"inspection_report_{folder_name}_{timestamp}.json"
        
        # Ensure output directory exists
        os.makedirs("inspection_reports", exist_ok=True)
        full_path = Path("inspection_reports") / output_path
        
        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Inspection report saved to: {full_path}")
            return str(full_path)
            
        except Exception as e:
            print(f"❌ Error saving inspection report: {e}")
            return ""


def main():
    """CLI interface for the data inspector"""
    
    parser = argparse.ArgumentParser(description='Data Inspector - Analyze extraction results')
    parser.add_argument('--folder', required=True, help='Folder path to inspect')
    parser.add_argument('--extract-types', nargs='*', 
                       choices=['metas', 'lenses', 'sources', 'patterns', 'variations'],
                       default=['lenses', 'sources', 'metas', 'patterns', 'variations'],
                       help='Types of data to extract and inspect')
    parser.add_argument('--save-report', action='store_true', help='Save detailed inspection report to file')
    parser.add_argument('--output', help='Output file path for inspection report')
    
    args = parser.parse_args()
    
    # Create inspector
    inspector = DataInspector()
    
    # Run inspection
    report = inspector.inspect_folder(args.folder, args.extract_types)
    
    # Always save JSON log to logs folder for perfect readable and foldable format
    log_filename = f"inspection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    log_path = settings.LOG_DIR / log_filename
    
    # Ensure logs directory exists
    os.makedirs(settings.LOG_DIR, exist_ok=True)
    
    # Build the exact analysis structure requested 
    if 'extraction_results' in report:
        for project_name, result in report['extraction_results'].items():
            if 'extraction_data' in result:
                
                def get_word_preview(text, word_limit=15):
                    """Get first 15 words maximum"""
                    if not text:
                        return "No content"
                    words = text.split()
                    if len(words) <= word_limit:
                        return text
                    preview_words = words[:word_limit]
                    return f"{' '.join(preview_words)}..."
                
                # Create metas analysis
                metas_analysis = {}
                for meta in result['extraction_data'].get('metas', []):
                    title = meta.get('title', 'No title')
                    content_preview = get_word_preview(meta.get('content', ''))
                    metas_analysis[title] = {
                        "content": content_preview
                    }
                
                # Create lenses analysis
                lenses_analysis = {}
                for doc in result['extraction_data'].get('documents', []):
                    lens_name = doc.get('lens', 'Unknown Lens')
                    
                    # Count variations and detect mapping type
                    total_variations = sum(len(p.get('variations', [])) for p in doc.get('patterns', []))
                    total_patterns = len(doc.get('patterns', []))
                    
                    # Detect mapping type
                    mapping_type = "all-to-1"  # default
                    if total_patterns > 0 and total_variations > 0:
                        if total_variations == total_patterns:
                            mapping_type = "1-to-1"
                        elif total_variations > total_patterns:
                            # Check if it's mixed mapping
                            patterns_with_variations = sum(1 for p in doc.get('patterns', []) if len(p.get('variations', [])) > 0)
                            if patterns_with_variations == 1:
                                mapping_type = "all-to-1"
                            else:
                                mapping_type = "mixed"
                    
                    # Summary preview
                    summary_preview = get_word_preview(doc.get('summary', ''))
                    
                    lenses_analysis[lens_name] = {
                        "summary": summary_preview,
                        "total_patterns": total_patterns,
                        "total_variations": total_variations,
                        "total_sources": len(doc.get('sources', [])),
                        "variation_mapping": mapping_type
                    }
                
                # Add structured analysis to the result
                result['metas'] = metas_analysis
                result['lenses'] = lenses_analysis
    
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\n📄 Perfect readable JSON log saved to: {log_path}")
    
    # Save additional report if requested
    if args.save_report:
        inspector.save_inspection_report(report, args.output)
    
    # Return exit code based on sync readiness
    return 0 if report.get("ready_for_sync", False) else 1


if __name__ == "__main__":
    sys.exit(main())
