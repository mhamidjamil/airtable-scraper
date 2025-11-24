import os
import json
import re
import docx
from datetime import datetime
from pathlib import Path

# Configuration
ROOT_DIR = r"E:\Work\shoaib\upwork\new_extractions"
OUTPUT_FILE = r"E:\Work\shoaib\upwork\pattern_to_json\new_patterns_output.json"
LOG_FILE = r"E:\Work\shoaib\upwork\pattern_to_json\conversion_log_{timestamp}.txt"

class ConversionLogger:
    """Tracks conversion progress and issues"""
    
    def __init__(self):
        self.successful = []
        self.skipped = []
        self.errors = []
        self.start_time = datetime.now()
    
    def log_success(self, file_path, pattern_count, variation_count, has_summary):
        self.successful.append({
            "file": file_path,
            "patterns": pattern_count,
            "variations": variation_count,
            "summary": "Yes" if has_summary else "No"
        })
    
    def log_skip(self, file_path, reason):
        self.skipped.append({
            "file": file_path,
            "reason": reason
        })
    
    def log_error(self, file_path, error_msg):
        self.errors.append({
            "file": file_path,
            "error": error_msg
        })
    
    def save_log(self, output_path):
        """Write log to file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("CONVERSION LOG\n")
            f.write("=" * 80 + "\n")
            f.write(f"Timestamp: {self.start_time.isoformat()}\n")
            f.write(f"Total files processed: {len(self.successful) + len(self.skipped) + len(self.errors)}\n")
            f.write(f"Successful: {len(self.successful)}\n")
            f.write(f"Skipped: {len(self.skipped)}\n")
            f.write(f"Errors: {len(self.errors)}\n")
            f.write("\n")
            
            # Successful files
            if self.successful:
                f.write("=" * 80 + "\n")
                f.write("SUCCESSFULLY PROCESSED\n")
                f.write("=" * 80 + "\n")
                for item in self.successful:
                    f.write(f"✓ {item['file']}\n")
                    f.write(f"  - Patterns: {item['patterns']}, Variations: {item['variations']}\n")
                    f.write(f"  - Summary: {item['summary']}\n")
                    f.write("\n")
            
            # Skipped files
            if self.skipped:
                f.write("=" * 80 + "\n")
                f.write("SKIPPED (No Patterns)\n")
                f.write("=" * 80 + "\n")
                for item in self.skipped:
                    f.write(f"⊘ {item['file']}\n")
                    f.write(f"  - Reason: {item['reason']}\n")
                    f.write("\n")
            
            # Errors
            if self.errors:
                f.write("=" * 80 + "\n")
                f.write("ERRORS\n")
                f.write("=" * 80 + "\n")
                for item in self.errors:
                    f.write(f"✗ {item['file']}\n")
                    f.write(f"  - Error: {item['error']}\n")
                    f.write("\n")

def clean_label(text):
    """Remove common labels from text content"""
    if not text:
        return ""
    
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

def extract_summary(paragraphs):
    """
    Extract summary - text before Task 1 or first Pattern.
    Returns (summary_text, has_summary)
    """
    summary_lines = []
    
    for para in paragraphs:
        text = para.text.strip()
        
        if not text:
            continue
        
        # Check if we've hit the pattern section
        if re.match(r'^(Task\s+1|TASK\s+1|Pattern\s+1)', text, re.IGNORECASE):
            break
        
        # Skip title-only paragraphs (all caps, short)
        if text.isupper() and len(text) < 100:
            continue
        
        # Skip separator lines
        if re.match(r'^[_\-=]{3,}$', text):
            continue
        
        summary_lines.append(text)
    
    if summary_lines:
        return "\n\n".join(summary_lines), True
    return "", False

def extract_patterns(paragraphs):
    """Extract patterns from document paragraphs (without pattern_number)"""
    patterns = []
    i = 0
    
    while i < len(paragraphs):
        text = paragraphs[i].text.strip()
        
        # Check if this is a pattern header
        pattern_match = re.match(r'^Pattern\s+(\d+):\s*(.+)$', text, re.IGNORECASE)
        
        if pattern_match:
            title = pattern_match.group(2).strip()
            
            # Collect next 3 non-empty paragraphs
            overview = ""
            choice = ""
            source = ""
            
            j = i + 1
            section_index = 0
            
            while j < len(paragraphs) and section_index < 3:
                para_text = paragraphs[j].text.strip()
                
                if not para_text:
                    j += 1
                    continue
                
                # Stop if we hit another pattern or variation
                if re.match(r'^(Pattern|Variation)\s+\d+', para_text, re.IGNORECASE):
                    break
                
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
                "title": title,
                "overview": overview,
                "choice": choice,
                "source": source,
                "variations": []
            })
        
        i += 1
    
    return patterns

def extract_variations(paragraphs):
    """Extract variations from document paragraphs"""
    variations = []
    i = 0
    
    while i < len(paragraphs):
        text = paragraphs[i].text.strip()
        
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
                
                if not para_text:
                    j += 1
                    continue
                
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
    """Combine patterns and variations"""
    pattern_map = {i+1: p for i, p in enumerate(patterns)}
    
    for variation in variations:
        pattern_num = variation["pattern_reference"]
        if pattern_num in pattern_map:
            var_data = {
                "variation_number": variation["variation_number"],
                "title": variation["title"],
                "content": variation["content"]
            }
            pattern_map[pattern_num]["variations"].append(var_data)
    
    return patterns

def extract_category(file_path, root_dir):
    """Extract category from path (parent directory name)"""
    rel_path = os.path.relpath(file_path, root_dir)
    parts = rel_path.split(os.sep)
    if len(parts) > 0:
        return parts[0]  # First directory (WARS, QUANTUM, etc.)
    return "Unknown"

def extract_lens(file_path):
    """Extract lens from filename (without extension)"""
    basename = os.path.basename(file_path)
    name_without_ext = os.path.splitext(basename)[0]
    return name_without_ext

def process_file(file_path, root_dir, logger):
    """Process a single docx file"""
    rel_path = os.path.relpath(file_path, root_dir)
    
    try:
        # Read docx
        doc = docx.Document(file_path)
        paragraphs = doc.paragraphs
        
        # Extract summary
        summary, has_summary = extract_summary(paragraphs)
        
        # Extract patterns and variations
        patterns = extract_patterns(paragraphs)
        variations = extract_variations(paragraphs)
        
        # Skip if no patterns
        if len(patterns) == 0:
            logger.log_skip(rel_path, "No patterns found")
            return None
        
        # Build structure
        patterns_with_variations = build_json_structure(patterns, variations)
        
        # Extract metadata
        category = extract_category(file_path, root_dir)
        lens = extract_lens(file_path)
        
        # Log success
        variation_count = sum(len(p["variations"]) for p in patterns_with_variations)
        logger.log_success(rel_path, len(patterns), variation_count, has_summary)
        
        return {
            "category": category,
            "lens": lens,
            "file_path": rel_path.replace(os.sep, '/'),
            "summary": summary,
            "has_summary": has_summary,
            "patterns": patterns_with_variations
        }
        
    except Exception as e:
        logger.log_error(rel_path, str(e))
        return None

def find_all_docx_files(root_dir):
    """Recursively find all .docx files"""
    files = []
    for root, dirs, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.docx') and not filename.startswith('~$'):
                full_path = os.path.join(root, filename)
                files.append(full_path)
    return sorted(files)

def main():
    print("=" * 80)
    print("NEW PATTERN EXTRACTION - BATCH PROCESSING")
    print("=" * 80)
    print()
    
    logger = ConversionLogger()
    all_documents = []
    
    # Find all docx files
    all_files = find_all_docx_files(ROOT_DIR)
    print(f"Found {len(all_files)} docx files")
    print()
    
    # Process each file
    for file_path in all_files:
        rel_path = os.path.relpath(file_path, ROOT_DIR)
        print(f"Processing: {rel_path}")
        
        doc_data = process_file(file_path, ROOT_DIR, logger)
        if doc_data:
            all_documents.append(doc_data)
    
    # Build final output
    output_data = {
        "total_documents": len(all_documents),
        "extraction_timestamp": datetime.now().isoformat(),
        "documents": all_documents
    }
    
    # Write JSON
    print()
    print("=" * 80)
    print("WRITING OUTPUT")
    print("=" * 80)
    print(f"Total documents: {len(all_documents)}")
    print(f"Output file: {OUTPUT_FILE}")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    # Write log
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = LOG_FILE.format(timestamp=timestamp)
    logger.save_log(log_path)
    print(f"Conversion log: {log_path}")
    
    # Print summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Successfully processed: {len(logger.successful)}")
    print(f"Skipped (no patterns): {len(logger.skipped)}")
    print(f"Errors: {len(logger.errors)}")
    print()
    print("Done!")

if __name__ == "__main__":
    main()
