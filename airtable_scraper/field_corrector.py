#!/usr/bin/env python3
"""
Document Field Corrector - Fix and improve document fields in extracted data
This script analyzes documents and suggests/applies corrections to improve data quality
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.data_extractor import DataExtractor


class DocumentFieldCorrector:
    """Corrector that analyzes and fixes document field issues"""
    
    def __init__(self):
        self.extractor = DataExtractor()
        
    def analyze_and_correct(self, folder_path: str, auto_fix: bool = False) -> Dict:
        """
        Analyze document fields and suggest/apply corrections
        
        Args:
            folder_path: Path to folder to analyze
            auto_fix: Whether to automatically apply safe corrections
            
        Returns:
            Dict with analysis and corrections applied
        """
        print(f"🔧 ANALYZING DOCUMENT FIELDS: {folder_path}")
        print("=" * 60)
        
        # Extract data using centralized logic
        extraction_data = self.extractor.process_folder(folder_path)
        
        # Analyze field issues
        field_analysis = self._analyze_field_issues(extraction_data)
        
        # Generate corrections
        corrections = self._generate_corrections(field_analysis, extraction_data)
        
        # Apply corrections if requested
        if auto_fix:
            corrected_data = self._apply_corrections(extraction_data, corrections)
        else:
            corrected_data = extraction_data
            
        # Create report
        report = {
            "analysis_timestamp": datetime.now().isoformat(),
            "folder_path": folder_path,
            "field_analysis": field_analysis,
            "corrections": corrections,
            "auto_fix_applied": auto_fix,
            "original_data": extraction_data,
            "corrected_data": corrected_data if auto_fix else None
        }
        
        # Display results
        self._display_analysis_results(field_analysis, corrections, auto_fix)
        
        return report
    
    def _analyze_field_issues(self, data: Dict) -> Dict:
        """Analyze field quality and identify issues"""
        
        documents = data.get("documents", [])
        issues = {
            "missing_titles": [],
            "missing_overviews": [],
            "missing_variations": [],
            "empty_sources": [],
            "lens_inconsistencies": [],
            "pattern_numbering_issues": [],
            "variation_quality_issues": [],
            "field_format_issues": []
        }
        
        document_stats = []
        
        for doc_idx, doc in enumerate(documents):
            lens = doc.get("lens", "")
            patterns = doc.get("patterns", [])
            sources = doc.get("sources", [])
            
            doc_issues = []
            
            # Check patterns
            for pat_idx, pattern in enumerate(patterns):
                pattern_num = pattern.get("pattern_number", 0)
                title = pattern.get("title", "").strip()
                overview = pattern.get("overview", "").strip()
                variations = pattern.get("variations", [])
                
                # Title issues
                if not title:
                    issues["missing_titles"].append({
                        "document": lens,
                        "pattern_index": pat_idx,
                        "pattern_number": pattern_num
                    })
                    doc_issues.append(f"Pattern {pattern_num}: Missing title")
                
                # Overview issues
                if not overview or len(overview) < 10:
                    issues["missing_overviews"].append({
                        "document": lens,
                        "pattern_index": pat_idx,
                        "pattern_number": pattern_num,
                        "overview_length": len(overview)
                    })
                    doc_issues.append(f"Pattern {pattern_num}: Missing or too short overview")
                
                # Variations issues
                if not variations:
                    issues["missing_variations"].append({
                        "document": lens,
                        "pattern_index": pat_idx,
                        "pattern_number": pattern_num
                    })
                    doc_issues.append(f"Pattern {pattern_num}: No variations found")
                else:
                    # Check variation quality
                    for var_idx, variation in enumerate(variations):
                        var_title = variation.get("title", "").strip()
                        var_content = variation.get("content", "").strip()
                        
                        if not var_title:
                            issues["variation_quality_issues"].append({
                                "document": lens,
                                "pattern_number": pattern_num,
                                "variation_index": var_idx,
                                "issue": "Missing title"
                            })
                        
                        if not var_content or len(var_content) < 20:
                            issues["variation_quality_issues"].append({
                                "document": lens,
                                "pattern_number": pattern_num,
                                "variation_index": var_idx,
                                "issue": f"Content too short ({len(var_content)} chars)"
                            })
                
                # Pattern numbering consistency
                expected_num = pat_idx + 1
                if pattern_num != expected_num:
                    issues["pattern_numbering_issues"].append({
                        "document": lens,
                        "pattern_index": pat_idx,
                        "expected_number": expected_num,
                        "actual_number": pattern_num
                    })
            
            # Check sources
            if not sources:
                issues["empty_sources"].append({
                    "document": lens,
                    "patterns_count": len(patterns)
                })
                doc_issues.append("No sources found")
            
            # Check lens consistency
            filename_lens = Path(doc.get("file_path", "")).stem if doc.get("file_path") else ""
            if lens != filename_lens:
                issues["lens_inconsistencies"].append({
                    "document": lens,
                    "filename_lens": filename_lens,
                    "detected_lens": lens
                })
            
            document_stats.append({
                "document": lens,
                "patterns_count": len(patterns),
                "variations_count": sum(len(p.get("variations", [])) for p in patterns),
                "sources_count": len(sources),
                "issues_count": len(doc_issues),
                "issues": doc_issues
            })
        
        return {
            "issues": issues,
            "document_stats": document_stats,
            "summary": {
                "total_documents": len(documents),
                "documents_with_issues": len([d for d in document_stats if d["issues"]]),
                "total_issues": sum(len(issue_list) for issue_list in issues.values())
            }
        }
    
    def _generate_corrections(self, analysis: Dict, data: Dict) -> Dict:
        """Generate suggested corrections for identified issues"""
        
        corrections = {
            "auto_fixable": [],
            "manual_required": [],
            "suggestions": []
        }
        
        issues = analysis["issues"]
        
        # Auto-fixable corrections
        
        # Pattern numbering fixes
        for issue in issues["pattern_numbering_issues"]:
            corrections["auto_fixable"].append({
                "type": "pattern_numbering",
                "description": f"Fix pattern numbering in {issue['document']}",
                "action": "renumber_patterns",
                "target": issue
            })
        
        # Field format fixes
        for doc in data.get("documents", []):
            for pattern in doc.get("patterns", []):
                # Clean up titles and overviews
                title = pattern.get("title", "").strip()
                overview = pattern.get("overview", "").strip()
                
                if title and (title.startswith("PATTERN") or title.isupper()):
                    corrections["auto_fixable"].append({
                        "type": "title_format",
                        "description": f"Clean title format: '{title[:50]}...'",
                        "action": "clean_title",
                        "target": {"document": doc.get("lens"), "title": title}
                    })
        
        # Manual corrections required
        
        # Missing critical content
        for issue in issues["missing_titles"]:
            corrections["manual_required"].append({
                "type": "missing_title",
                "description": f"Pattern {issue['pattern_number']} in {issue['document']} needs a title",
                "severity": "high",
                "suggestion": "Review document and add descriptive pattern title"
            })
        
        for issue in issues["missing_variations"]:
            corrections["manual_required"].append({
                "type": "missing_variations",
                "description": f"Pattern {issue['pattern_number']} in {issue['document']} has no variations",
                "severity": "critical",
                "suggestion": "Check document structure - variations may not be properly formatted"
            })
        
        # Suggestions for improvement
        
        for issue in issues["missing_overviews"]:
            corrections["suggestions"].append({
                "type": "improve_overview",
                "description": f"Pattern {issue['pattern_number']} overview could be improved",
                "suggestion": f"Current length: {issue['overview_length']} chars. Consider expanding the overview."
            })
        
        for issue in issues["variation_quality_issues"]:
            corrections["suggestions"].append({
                "type": "improve_variation",
                "description": f"Variation quality issue in {issue['document']}",
                "issue": issue["issue"],
                "suggestion": "Review variation content for completeness"
            })
        
        return corrections
    
    def _apply_corrections(self, data: Dict, corrections: Dict) -> Dict:
        """Apply auto-fixable corrections to the data"""
        
        corrected_data = json.loads(json.dumps(data))  # Deep copy
        applied_corrections = []
        
        for correction in corrections["auto_fixable"]:
            try:
                if correction["action"] == "renumber_patterns":
                    # Fix pattern numbering
                    target = correction["target"]
                    doc_name = target["document"]
                    
                    # Find the document
                    for doc in corrected_data.get("documents", []):
                        if doc.get("lens") == doc_name:
                            patterns = doc.get("patterns", [])
                            for i, pattern in enumerate(patterns):
                                pattern["pattern_number"] = i + 1
                            
                            applied_corrections.append(f"Renumbered patterns in {doc_name}")
                            break
                
                elif correction["action"] == "clean_title":
                    # Clean title format
                    target = correction["target"]
                    doc_name = target["document"]
                    old_title = target["title"]
                    
                    # Generate cleaned title
                    new_title = self._clean_title_format(old_title)
                    
                    # Find and update the title
                    for doc in corrected_data.get("documents", []):
                        if doc.get("lens") == doc_name:
                            for pattern in doc.get("patterns", []):
                                if pattern.get("title") == old_title:
                                    pattern["title"] = new_title
                                    applied_corrections.append(f"Cleaned title: '{old_title}' -> '{new_title}'")
                                    break
                            break
                
            except Exception as e:
                print(f"❌ Error applying correction: {e}")
        
        # Add correction metadata
        corrected_data["_corrections_applied"] = {
            "timestamp": datetime.now().isoformat(),
            "applied_corrections": applied_corrections,
            "correction_count": len(applied_corrections)
        }
        
        return corrected_data
    
    def _clean_title_format(self, title: str) -> str:
        """Clean and format a title"""
        import re
        
        # Remove "PATTERN N:" prefix if present
        cleaned = re.sub(r'^PATTERN\s+\d+:\s*', '', title, flags=re.IGNORECASE)
        
        # Convert from ALL CAPS to title case if needed
        if cleaned.isupper() and len(cleaned) > 10:
            cleaned = cleaned.title()
        
        # Clean up extra spaces
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
    
    def _display_analysis_results(self, analysis: Dict, corrections: Dict, auto_fix_applied: bool):
        """Display formatted analysis results"""
        
        print(f"\n📊 FIELD ANALYSIS SUMMARY")
        print("-" * 50)
        
        summary = analysis["summary"]
        print(f"Total Documents: {summary['total_documents']}")
        print(f"Documents with Issues: {summary['documents_with_issues']}")
        print(f"Total Issues Found: {summary['total_issues']}")
        
        print(f"\n🔍 ISSUE BREAKDOWN")
        print("-" * 50)
        
        issues = analysis["issues"]
        for issue_type, issue_list in issues.items():
            if issue_list:
                count = len(issue_list)
                print(f"• {issue_type.replace('_', ' ').title()}: {count}")
        
        print(f"\n📄 DOCUMENT ANALYSIS")
        print("-" * 50)
        
        for doc_stat in analysis["document_stats"]:
            status = "✅ GOOD" if not doc_stat["issues"] else "⚠️ HAS ISSUES"
            print(f"\n📖 {doc_stat['document']} - {status}")
            print(f"   Patterns: {doc_stat['patterns_count']}")
            print(f"   Variations: {doc_stat['variations_count']}")
            print(f"   Sources: {doc_stat['sources_count']}")
            
            if doc_stat["issues"]:
                print(f"   Issues ({doc_stat['issues_count']}):")
                for issue in doc_stat["issues"]:
                    print(f"     • {issue}")
        
        print(f"\n🔧 CORRECTIONS")
        print("-" * 50)
        
        auto_fixable = corrections["auto_fixable"]
        manual_required = corrections["manual_required"]
        suggestions = corrections["suggestions"]
        
        print(f"Auto-fixable: {len(auto_fixable)}")
        print(f"Manual corrections needed: {len(manual_required)}")
        print(f"Suggestions: {len(suggestions)}")
        
        if auto_fix_applied and auto_fixable:
            print(f"\n✅ AUTO-CORRECTIONS APPLIED:")
            for correction in auto_fixable:
                print(f"   • {correction['description']}")
        
        if manual_required:
            print(f"\n⚠️ MANUAL CORRECTIONS NEEDED:")
            for correction in manual_required:
                severity = correction.get("severity", "medium").upper()
                print(f"   [{severity}] {correction['description']}")
                print(f"           → {correction['suggestion']}")
        
        if suggestions:
            print(f"\n💡 SUGGESTIONS FOR IMPROVEMENT:")
            for suggestion in suggestions[:5]:  # Show first 5
                print(f"   • {suggestion['description']}")
                print(f"     → {suggestion['suggestion']}")
    
    def save_correction_report(self, report: Dict, output_path: str = None) -> str:
        """Save correction report to JSON file"""
        
        if not output_path:
            folder_name = Path(report["folder_path"]).name
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"correction_report_{folder_name}_{timestamp}.json"
        
        # Ensure output directory exists
        os.makedirs("correction_reports", exist_ok=True)
        full_path = Path("correction_reports") / output_path
        
        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Correction report saved to: {full_path}")
            return str(full_path)
            
        except Exception as e:
            print(f"❌ Error saving correction report: {e}")
            return ""


def main():
    """CLI interface for the document field corrector"""
    
    parser = argparse.ArgumentParser(description='Document Field Corrector - Fix document field issues')
    parser.add_argument('--folder', required=True, help='Folder path to analyze')
    parser.add_argument('--auto-fix', action='store_true', help='Automatically apply safe corrections')
    parser.add_argument('--save-report', action='store_true', help='Save detailed correction report to file')
    parser.add_argument('--output', help='Output file path for correction report')
    
    args = parser.parse_args()
    
    # Create corrector
    corrector = DocumentFieldCorrector()
    
    # Run analysis and corrections
    report = corrector.analyze_and_correct(args.folder, args.auto_fix)
    
    # Save report if requested
    if args.save_report:
        corrector.save_correction_report(report, args.output)
    
    # Return exit code based on correction success
    return 0


if __name__ == "__main__":
    sys.exit(main())