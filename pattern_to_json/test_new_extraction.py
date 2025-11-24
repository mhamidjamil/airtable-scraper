import json

# Test the new extraction output
JSON_FILE = r"E:\Work\shoaib\upwork\pattern_to_json\new_patterns_output.json"

def test_new_extraction():
    """Verify the new JSON structure"""
    
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("=" * 80)
    print("NEW PATTERN EXTRACTION - VERIFICATION")
    print("=" * 80)
    print()
    
    # Test 1: Check structure
    assert "total_documents" in data
    assert "extraction_timestamp" in data
    assert "documents" in data
    print(f"✓ JSON structure valid")
    print(f"✓ Total documents: {data['total_documents']}")
    print(f"✓ Timestamp: {data['extraction_timestamp']}")
    print()
    
    # Test 2: Verify no pattern_number or step
    for doc in data["documents"]:
        assert "pattern_number" not in str(doc), f"Found pattern_number in {doc['lens']}"
        assert "step" not in doc, f"Found step field in {doc['lens']}"
    print(f"✓ No 'pattern_number' in patterns")
    print(f"✓ No 'step' field in documents")
    print()
    
    # Test 3: Verify new fields exist
    required_fields = ["category", "lens", "file_path", "summary", "has_summary", "patterns"]
    for doc in data["documents"]:
        for field in required_fields:
            assert field in doc, f"Missing {field} in {doc.get('lens', 'unknown')}"
    print(f"✓ All documents have required fields: {', '.join(required_fields)}")
    print()
    
    # Test 4: Summary statistics
    docs_with_summary = sum(1 for d in data["documents"] if d["has_summary"])
    docs_without_summary = data["total_documents"] - docs_with_summary
    
    print("=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)
    print(f"Documents with summary: {docs_with_summary}")
    print(f"Documents without summary: {docs_without_summary}")
    print()
    
    # Test 5: Category breakdown
    from collections import Counter
    categories = Counter(d["category"] for d in data["documents"])
    print("Category breakdown:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count} documents")
    print()
    
    # Test 6: Pattern and variation counts
    total_patterns = sum(len(d["patterns"]) for d in data["documents"])
    total_variations = sum(
        sum(len(p["variations"]) for p in d["patterns"])
        for d in data["documents"]
    )
    print(f"Total patterns: {total_patterns}")
    print(f"Total variations: {total_variations}")
    print()
    
    # Test 7: Show sample documents
    print("=" * 80)
    print("SAMPLE DOCUMENTS")
    print("=" * 80)
    for i, doc in enumerate(data["documents"][:5], 1):
        pattern_count = len(doc["patterns"])
        variation_count = sum(len(p["variations"]) for p in doc["patterns"])
        summary_preview = doc["summary"][:100] + "..." if len(doc["summary"]) > 100 else doc["summary"]
        
        print(f"\n{i}. {doc['category']} - {doc['lens']}")
        print(f"   File: {doc['file_path']}")
        print(f"   Summary: {'' if not doc['has_summary'] else summary_preview}")
        print(f"   Patterns: {pattern_count}, Variations: {variation_count}")
    
    print("\n" + "=" * 80)
    print("ALL TESTS PASSED!")
    print("=" * 80)

if __name__ == "__main__":
    try:
        test_new_extraction()
    except AssertionError as e:
        print(f"\n❌ Test Failed: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
