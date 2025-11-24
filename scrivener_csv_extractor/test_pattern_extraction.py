import json

# Test the pattern extraction output
JSON_FILE = r"E:\Work\shoaib\upwork\scrivener_csv_extractor\patterns_output.json"

def test_json_structure():
    """Verify JSON structure and content"""
    
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("=== JSON Structure Verification ===\n")
    
    # Test 1: Check top-level structure
    assert "patterns" in data, "Missing 'patterns' key"
    patterns = data["patterns"]
    print(f"✓ Total patterns: {len(patterns)}")
    assert len(patterns) == 10, f"Expected 10 patterns, got {len(patterns)}"
    
    # Test 2: Verify each pattern has required fields
    required_fields = ["pattern_number", "title", "overview", "choice", "source", "variations"]
    for pattern in patterns:
        for field in required_fields:
            assert field in pattern, f"Pattern {pattern.get('pattern_number')} missing field: {field}"
    print("✓ All patterns have required fields")
    
    # Test 3: Verify pattern numbers are 1-10
    pattern_numbers = [p["pattern_number"] for p in patterns]
    assert sorted(pattern_numbers) == list(range(1, 11)), "Pattern numbers not 1-10"
    print("✓ Pattern numbers are 1-10")
    
    # Test 4: Verify each pattern has content in overview, choice, source
    for pattern in patterns:
        assert len(pattern["overview"]) > 50, f"Pattern {pattern['pattern_number']} has empty/short overview"
        assert len(pattern["choice"]) > 50, f"Pattern {pattern['pattern_number']} has empty/short choice"
        assert len(pattern["source"]) > 10, f"Pattern {pattern['pattern_number']} has empty/short source"
    print("✓ All patterns have substantial content")
    
    # Test 5: Verify variation count
    total_variations = sum(len(p["variations"]) for p in patterns)
    print(f"✓ Total variations: {total_variations}")
    assert total_variations == 10, f"Expected 10 variations, got {total_variations}"
    
    # Test 6: Verify specific content examples
    pattern1 = patterns[0]
    assert "From User to Gardener" in pattern1["title"], "Pattern 1 title mismatch"
    assert "Silicon Valley" in pattern1["overview"], "Pattern 1 overview mismatch"
    assert "Machine Empire" in pattern1["choice"], "Pattern 1 choice mismatch"
    assert "HOME_SPINE" in pattern1["source"], "Pattern 1 source mismatch"
    print("✓ Pattern 1 content verified")
    
    # Test 7: Verify variation structure
    for pattern in patterns:
        for variation in pattern["variations"]:
            assert "variation_number" in variation, f"Variation missing variation_number"
            assert "title" in variation, f"Variation missing title"
            assert "content" in variation, f"Variation missing content"
            assert len(variation["content"]) > 50, f"Variation {variation['variation_number']} has empty/short content"
    print("✓ All variations have required fields and content")
    
    # Test 8: Verify each pattern has exactly 1 variation
    for pattern in patterns:
        assert len(pattern["variations"]) == 1, f"Pattern {pattern['pattern_number']} has {len(pattern['variations'])} variations, expected 1"
    print("✓ Each pattern has exactly 1 variation")
    
    # Test 9: Verify variation numbers match pattern numbers
    for pattern in patterns:
        for variation in pattern["variations"]:
            # Variation number should match pattern number
            assert variation["variation_number"] == pattern["pattern_number"], \
                f"Variation number {variation['variation_number']} doesn't match pattern {pattern['pattern_number']}"
    print("✓ Variation numbers correctly linked to patterns")
    
    print("\n=== All Tests Passed! ===\n")
    
    # Print summary
    print("Summary:")
    for pattern in patterns:
        var_count = len(pattern["variations"])
        print(f"  Pattern {pattern['pattern_number']}: {pattern['title'][:50]}... ({var_count} variation)")

if __name__ == "__main__":
    try:
        test_json_structure()
    except AssertionError as e:
        print(f"\n❌ Test Failed: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
