import os
import json
import re
import docx
from pathlib import Path

# Configuration
STEP2_DIR = r"E:\Work\shoaib\upwork\Step 2"
STEP3_DIR = r"E:\Work\shoaib\upwork\Step 3"
OUTPUT_FILE = r"E:\Work\shoaib\upwork\pattern_to_json\patterns_output.json"

def extract_metadata_from_filename(filename):
    """
    Extract dashboard title and topic name from filename.
    
    Example: "Dashboard - Step 2 - Lens 1 - User vs. Gardener (The Identity Shift)_ The Gardener as Post-Heroic Hero.docx"
    Returns: {
        "dashboard": "Dashboard",
        "step": "Step 2",
        "lens": "Lens 1" (if present),
        "topic_name": "User vs. Gardener (The Identity Shift)_ The Gardener as Post-Heroic Hero"
    }
    """
    basename = os.path.basename(filename)
    name_without_ext = os.path.splitext(basename)[0]
    
    # Pattern: "Dashboard - Step X - [Lens Y -] Topic Name"
    # Try to parse with Lens
    match = re.match(r'^(Dashboard)\s*-\s*(Step\s+\d+)\s*-\s*(Lens\s+\d+)\s*-\s*(.+)$', name_without_ext)
    
    if match:
        return {
            "dashboard": match.group(1),
            "step": match.group(2),
            "lens": match.group(3),
            "topic_name": match.group(4).strip()
        }
    
    # Try without Lens (for Step 3 files)
    match = re.match(r'^(Dashboard)\s*-\s*(Step\s+\d+)\s*-\s*(.+)$', name_without_ext)
    
    if match:
        return {
            "dashboard": match.group(1),
            "step": match.group(2),
            "lens": None,
            "topic_name": match.group(3).strip()
        }
    
    # Fallback
    return {
        "dashboard": "Dashboard",
        "step": "Unknown",
        "lens": None,
        "topic_name": name_without_ext
    }

def clean_label(text):
    """
    Remove common labels from text content.
    Labels: "Explanation:", "Inner war / choice:", "Sources:"
    """
    if not text:
        return ""
    
    # Strip common labels
    labels = [
        "Explanation:",
        "Inner war / choice:",
        "Sources:",
        "Explanation :",
        "Inner war / choice :",
        "Sources :"
    ]
    
    cleaned = text.strip()
    for label in labels:
        if cleaned.startswith(label):
            cleaned = cleaned[len(label):].strip()
            break
    
    return cleaned

def extract_patterns(paragraphs):
    """
    Extract patterns from document paragraphs.
    Returns list of pattern dictionaries.
    """
    patterns = []
    i = 0
    
    while i < len(paragraphs):
        text = paragraphs[i].text.strip()
        
        # Check if this is a pattern header
        pattern_match = re.match(r'^Pattern\s+(\d+):\s*(.+)$', text, re.IGNORECASE)
        
        if pattern_match:
            pattern_number = int(pattern_match.group(1))
            title = pattern_match.group(2).strip()
            
            # Collect next 3 non-empty paragraphs for overview, choice, source
            overview = ""
            choice = ""
            source = ""
            
            j = i + 1
            section_index = 0
            
            while j < len(paragraphs) and section_index < 3:
                para_text = paragraphs[j].text.strip()
                
                # Skip empty paragraphs
                if not para_text:
                    j += 1
                    continue
                
                # Stop if we hit another pattern or variation
                if re.match(r'^(Pattern|Variation)\s+\d+', para_text, re.IGNORECASE):
                    break
                
                # Assign to appropriate section
                cleaned_text = clean_label(para_text)
                
                if section_index == 0:
                    overview = cleaned_text
                elif section_index == 1:
                    choice = cleaned_text
                elif section_index == 2:
                    source = cleaned_text
                
                section_index += 1
                j += 1
            
            patterns.append({
                "pattern_number": pattern_number,
                "title": title,
                "overview": overview,
                "choice": choice,
                "source": source,
                "variations": []
            })
        
        i += 1
    
    return patterns

def extract_variations(paragraphs):
    """
    Extract variations from document paragraphs.
    Returns list of variation dictionaries with pattern references.
    """
    variations = []
    i = 0
    
    while i < len(paragraphs):
        text = paragraphs[i].text.strip()
        
        # Check if this is a variation header
        # Format: "Variation X – Pattern Y: Title"
        variation_match = re.match(
            r'^Variation\s+(\d+)\s*[–-]\s*Pattern\s+(\d+):\s*(.+)$',
            text,
            re.IGNORECASE
        )
        
        if variation_match:
            variation_number = int(variation_match.group(1))
            pattern_ref = int(variation_match.group(2))
            title = variation_match.group(3).strip()
            
            # Get next non-empty paragraph as content
            content = ""
            j = i + 1
            
            while j < len(paragraphs):
                para_text = paragraphs[j].text.strip()
                
                # Skip empty paragraphs
                if not para_text:
                    j += 1
                    continue
                
                # Stop if we hit another variation or pattern
                if re.match(r'^(Pattern|Variation)\s+\d+', para_text, re.IGNORECASE):
                    break
                
                content = para_text
                break
            
            variations.append({
                "variation_number": variation_number,
                "pattern_reference": pattern_ref,
                "title": title,
                "content": content
            })
        
        i += 1
    
    return variations

def build_json_structure(patterns, variations):
    """
    Combine patterns and variations.
    """
    # Create a map of pattern_number to pattern object
    pattern_map = {p["pattern_number"]: p for p in patterns}
    
    # Add variations to their corresponding patterns
    for variation in variations:
        pattern_num = variation["pattern_reference"]
        if pattern_num in pattern_map:
            # Remove pattern_reference from variation (internal use only)
            var_data = {
                "variation_number": variation["variation_number"],
                "title": variation["title"],
                "content": variation["content"]
            }
            pattern_map[pattern_num]["variations"].append(var_data)
    
    return patterns

def process_file(file_path):
    """
    Process a single Docx file and extract patterns.
    Returns document data with metadata.
    """
    print(f"\nProcessing: {os.path.basename(file_path)}")
    
    # Extract metadata from filename
    metadata = extract_metadata_from_filename(file_path)
    
    # Read docx file
    doc = docx.Document(file_path)
    paragraphs = doc.paragraphs
    
    # Extract patterns and variations
    patterns = extract_patterns(paragraphs)
    variations = extract_variations(paragraphs)
    
    # Build structure
    patterns_with_variations = build_json_structure(patterns, variations)
    
    print(f"  - Extracted {len(patterns)} patterns")
    print(f"  - Extracted {len(variations)} variations")
    
    return {
        "dashboard": metadata["dashboard"],
        "step": metadata["step"],
        "lens": metadata["lens"],
        "topic_name": metadata["topic_name"],
        "file_name": os.path.basename(file_path),
        "patterns": patterns_with_variations
    }

def find_dashboard_files(directory):
    """
    Find all Dashboard*.docx files in a directory.
    """
    files = []
    for file in Path(directory).glob("Dashboard*.docx"):
        if not file.name.startswith("~$"):  # Skip temp files
            files.append(str(file))
    return sorted(files)

def main():
    print("=== Pattern Extraction - Batch Processing ===\n")
    
    all_documents = []
    
    # Process Step 2 files
    step2_files = find_dashboard_files(STEP2_DIR)
    print(f"Found {len(step2_files)} files in Step 2")
    
    for file_path in step2_files:
        try:
            doc_data = process_file(file_path)
            all_documents.append(doc_data)
        except Exception as e:
            print(f"  ERROR: {e}")
    
    # Process Step 3 files
    step3_files = find_dashboard_files(STEP3_DIR)
    print(f"\nFound {len(step3_files)} files in Step 3")
    
    for file_path in step3_files:
        try:
            doc_data = process_file(file_path)
            all_documents.append(doc_data)
        except Exception as e:
            print(f"  ERROR: {e}")
    
    # Build final output
    output_data = {
        "total_documents": len(all_documents),
        "documents": all_documents
    }
    
    # Write to JSON file
    print(f"\n=== Writing Output ===")
    print(f"Total documents processed: {len(all_documents)}")
    print(f"Output file: {OUTPUT_FILE}")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print("\n=== Summary ===")
    for doc in all_documents:
        pattern_count = len(doc["patterns"])
        variation_count = sum(len(p["variations"]) for p in doc["patterns"])
        lens_info = f" - {doc['lens']}" if doc['lens'] else ""
        print(f"{doc['step']}{lens_info}: {doc['topic_name']}")
        print(f"  └─ {pattern_count} patterns, {variation_count} variations")
    
    print("\nDone!")

if __name__ == "__main__":
    main()
