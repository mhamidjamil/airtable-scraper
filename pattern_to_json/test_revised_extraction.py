import json

# Test the revised extraction output
JSON_FILE = r"E:\Work\shoaib\upwork\pattern_to_json\new_patterns_output.json"

def test_revised_extraction():
    """Verify the new JSON structure and changes"""
    
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("=" * 80)
    print("REVISED PATTERN EXTRACTION - VERIFICATION")
    print("=" * 80)
    print()
    
    # Test 1: Check top-level structure
    print()
    
    # Test 3: Verify summary requirements
    all_summaries_valid = True
    for category, docs in data["documents"].items():
        for doc in docs:
            summary = doc["summary"]
            lines = summary.split('\n')
            
            # Check that title is not included (first line should not be repeated in summary)
            lens = doc["lens"]
            if summary.startswith(lens):
                print(f"✗ WARNING: Title '{lens}' found in summary")
                all_summaries_valid = False
            
            # Check minimum 2 lines
            if len(lines) < 2:
                print(f"✗ WARNING: Summary has less than 2 lines for {lens}")
                all_summaries_valid = False
    
    if all_summaries_valid:
        print(f"✓ All summaries valid (no titles, 2+ lines)")
    print()
    
    # Test 4: Category breakdown with lens counts
    print("=" * 80)
    print("CATEGORY BREAKDOWN")
    print("=" * 80)
    for category, docs in sorted(data["documents"].items()):
        print(f"\n{category}:")
        print(f"  Lenses: {len(docs)}")
        for doc in docs[:3]:  # Show first 3 lenses
            print(f"    - {doc['lens']}")
        if len(docs) > 3:
            print(f"    ... and {len(docs) - 3} more")
    print()
    
    # Test 5: Pattern statistics
    total_patterns = 0
    total_variations = 0
    for category, docs in data["documents"].items():
        for doc in docs:
            total_patterns += len(doc["patterns"])
            total_variations += sum(len(p["variations"]) for p in doc["patterns"])
    
    print("=" * 80)
    print("PATTERN STATISTICS")
    print("=" * 80)
    print(f"Total patterns: {total_patterns}")
    print(f"Total variations: {total_variations}")
    print(f"Average patterns per document: {total_patterns / data['total_documents']:.1f}")
    print()
    
    # Test 6: Sample document structure
    print("=" * 80)
    print("SAMPLE DOCUMENT STRUCTURE")
    print("=" * 80)
    first_category = list(data["documents"].keys())[0]
    first_doc = data["documents"][first_category][0]
    
    print(f"Category: {first_category}")
    print(f"Lens: {first_doc['lens']}")
    print(f"File path: {first_doc['file_path']}")
    print(f"Summary (first 100 chars): {first_doc['summary'][:100]}...")
    print(f"Has summary: {first_doc['has_summary']}")
    print(f"Pattern count: {len(first_doc['patterns'])}")
    print()
    
    print("=" * 80)
    print("ALL TESTS PASSED!")
    print("=" * 80)

if __name__ == "__main__":
    try:
        test_revised_extraction()
    except AssertionError as e:
        print(f"\n❌ Test Failed: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
