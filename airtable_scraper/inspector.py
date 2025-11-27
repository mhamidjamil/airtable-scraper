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


class DataInspector:
    """Inspector that uses centralized extraction logic to analyze data"""
    
    def __init__(self):
        self.extractor = DataExtractor()
        
    def inspect_folder(self, folder_path: str, extract_types: List[str] = None) -> Dict:
        """
        Inspect extraction results from a folder using centralized logic
        
        Args:
            folder_path: Path to folder to inspect  
            extract_types: List of data types to extract and inspect
            
        Returns:
            Dict with inspection results and recommendations
        """
        print(f"🔍 INSPECTING FOLDER: {folder_path}")
        print("=" * 60)
        
        # Use centralized extractor
        extraction_data = self.extractor.process_folder(folder_path, extract_types)
        
        # Analyze extraction results
        inspection_results = self._analyze_extraction(extraction_data, folder_path)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(inspection_results)
        
        # Create full inspection report
        report = {
            "inspection_timestamp": datetime.now().isoformat(),
            "folder_path": folder_path,
            "extraction_data": extraction_data,
            "analysis": inspection_results,
            "recommendations": recommendations,
            "ready_for_sync": self._check_sync_readiness(inspection_results)
        }
        
        # Display results
        self._display_inspection_results(inspection_results, recommendations)
        
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
            
            doc_analysis.append({
                "filename": doc.get("file_path", "").split("/")[-1] if doc.get("file_path") else "Unknown",
                "lens": lens,
                "patterns_count": len(patterns),
                "variations_count": sum(len(p.get("variations", [])) for p in patterns),
                "sources_count": len(sources),
                "issues": issues,
                "status": "✅ GOOD" if not issues else "⚠️ HAS ISSUES"
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
    
    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        totals = analysis["totals"]
        quality = analysis["data_quality"]
        structure = analysis["folder_structure"]
        
        # Check basic extraction
        if totals["documents"] == 0:
            recommendations.append("🚨 CRITICAL: No documents found. Check folder path and ensure .docx files exist.")
        
        if totals["patterns"] == 0:
            recommendations.append("🚨 CRITICAL: No patterns extracted. Check document format - patterns should start with 'Pattern N:'")
        
        if totals["variations"] == 0:
            recommendations.append("🚨 CRITICAL: No variations extracted. Check variation format in documents.")
        
        # Check data quality issues
        if quality["documents_with_issues"] > 0:
            recommendations.append(f"⚠️ {quality['documents_with_issues']} documents have issues. Check individual document analysis below.")
        
        if quality["documents_without_sources"] > 0:
            recommendations.append(f"⚠️ {quality['documents_without_sources']} documents missing sources. Ensure each pattern has source information.")
        
        # Check folder structure
        if not structure["has_step2_folder"]:
            recommendations.append("💡 No 'Step 2' folder found. Will process main folder documents.")
        
        if not structure["has_metas_folder"] and "metas" in analysis.get("extract_types", []):
            recommendations.append("💡 No 'METAS' folder found. Meta extraction will be skipped.")
        
        # Positive feedback
        if not recommendations:
            recommendations.append("✅ All looks good! Data is ready for Airtable sync.")
            
        if totals["patterns"] > 0 and totals["variations"] > 0:
            recommendations.append(f"✅ Successfully extracted {totals['patterns']} patterns with {totals['variations']} variations.")
        
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
                       default=['lenses', 'sources', 'patterns', 'variations'],
                       help='Types of data to extract and inspect')
    parser.add_argument('--save-report', action='store_true', help='Save detailed inspection report to file')
    parser.add_argument('--output', help='Output file path for inspection report')
    
    args = parser.parse_args()
    
    # Create inspector
    inspector = DataInspector()
    
    # Run inspection
    report = inspector.inspect_folder(args.folder, args.extract_types)
    
    # Save report if requested
    if args.save_report:
        inspector.save_inspection_report(report, args.output)
    
    # Return exit code based on sync readiness
    return 0 if report["ready_for_sync"] else 1


if __name__ == "__main__":
    sys.exit(main())
