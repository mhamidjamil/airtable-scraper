import json

# Test the multi-file pattern extraction output
JSON_FILE = r"E:\Work\shoaib\upwork\pattern_to_json\patterns_output.json"

def test_multi_file_extraction():
    """Verify JSON structure for multi-file processing"""
    
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("=== Multi-File Extraction Verification ===\n")
    
    # Test 1: Check top-level structure
    assert "total_documents" in data, "Missing 'total_documents' key"
    assert "documents" in data, "Missing 'documents' key"
    print(f"✓ Total documents: {data['total_documents']}")
    
    
    # Test 2: Verify document count
    documents = data["documents"]
    assert len(documents) == data["total_documents"], "Document count mismatch"
    print(f"✓ Document count matches: {len(documents)}")
    
    # Test 3: Verify each document has metadata
    required_metadata = ["dashboard", "step", "lens", "topic_name", "file_name", "patterns"]
    for doc in documents:
        for field in required_metadata:
            assert field in doc, f"Document missing field: {field}"
    print("✓ All documents have required metadata fields")
    
    # Test 4: Verify Step 2 documents have lens
    step2_docs = [d for d in documents if d["step"] == "Step 2"]
    for doc in step2_docs:
        assert doc["lens"] is not None, f"Step 2 document missing lens: {doc['file_name']}"
    print(f"✓ All {len(step2_docs)} Step 2 documents have lens information")
    
    # Test 5: Verify Step 3 documents have null lens
    step3_docs = [d for d in documents if d["step"] == "Step 3"]
    for doc in step3_docs:
        assert doc["lens"] is None, f"Step 3 document should have null lens: {doc['file_name']}"
    print(f"✓ All {len(step3_docs)} Step 3 documents have null lens (as expected)")
    
    # Test 6: Count total patterns across all documents
    total_patterns = sum(len(d["patterns"]) for d in documents)
    print(f"✓ Total patterns across all documents: {total_patterns}")
    
    # Test 7: Count total variations
    total_variations = sum(
        sum(len(p["variations"]) for p in d["patterns"])
        for d in documents
    )
    print(f"✓ Total variations across all documents: {total_variations}")
    
    print("\n=== Document Summary ===")
    for doc in documents:
        pattern_count = len(doc["patterns"])
        variation_count = sum(len(p["variations"]) for p in doc["patterns"])
        lens_info = f" - {doc['lens']}" if doc['lens'] else ""
        print(f"\n{doc['step']}{lens_info}")
        print(f"  Topic: {doc['topic_name']}")
        print(f"  Patterns: {pattern_count}, Variations: {variation_count}")
        
        # Show first pattern title if available
        if pattern_count > 0:
            print(f"  First Pattern: {doc['patterns'][0]['title']}")
        else:
            print(f"  ⚠️ WARNING: No patterns found in this document!")
    
    print("\n=== All Tests Passed! ===")

if __name__ == "__main__":
    try:
        test_multi_file_extraction()
    except AssertionError as e:
        print(f"\n❌ Test Failed: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
