import os
import csv
import re
import xml.etree.ElementTree as ET
from striprtf.striprtf import rtf_to_text
import docx

# Configuration


# Regex patterns for headers (handling malformed/SCRIV_PATH = r"E:\Work\shoaib\upwork\shoaib53%202025-11-22%2007-11\shoaib53.scriv"
STEP2_PATH = r"E:\Work\shoaib\upwork\Step 2"
STEP3_PATH = r"E:\Work\shoaib\upwork\Step 3"
OUTPUT_FILE = r"E:\Work\shoaib\upwork\scrivener_csv_extractor\scrivener_data.csv"spaced text)
# "p laning", "planning", "PLANNING", etc.
PLANNING_RE = re.compile(r'(?i)^\s*p\s*l\s*a\s*n\s*n\s*i\s*n\s*g\s*:?\s*$', re.MULTILINE)
REVISION_RE = re.compile(r'(?i)^\s*r\s*e\s*v\s*i\s*s\s*i\s*o\s*n\s*:?\s*$', re.MULTILINE)
METADATA_RE = re.compile(r'(?i)^\s*m\s*e\s*t\s*a\s*d\s*a\s*t\s*a\s*:?\s*$', re.MULTILINE)

def clean_text(text):
    if not text:
        return ""
    # Remove excessive newlines
    return re.sub(r'\n{3,}', '\n\n', text).strip()

def extract_sections(text):
    """
    Splits text into Planning, Revision, and Metadata sections based on headers.
    """
    if not text:
        return {"Planning": "", "Revision": "", "Metadata": ""}

    # Find all matches for headers
    matches = []
    for match in PLANNING_RE.finditer(text):
        matches.append(("Planning", match.start(), match.end()))
    for match in REVISION_RE.finditer(text):
        matches.append(("Revision", match.start(), match.end()))
    for match in METADATA_RE.finditer(text):
        matches.append(("Metadata", match.start(), match.end()))
    
    # Sort matches by position
    matches.sort(key=lambda x: x[1])
    
    sections = {"Planning": "", "Revision": "", "Metadata": ""}
    
    if not matches:
        # No headers found, treat whole text as Planning (or generic content)
        sections["Planning"] = text
        return sections

    # Extract text between matches
    for i, (name, start, end) in enumerate(matches):
        # Text for this section starts after the header
        section_start = end
        
        # Text ends at the start of the next header, or end of string
        if i + 1 < len(matches):
            section_end = matches[i+1][1]
        else:
            section_end = len(text)
            
        content = text[section_start:section_end].strip()
        
        # Append to existing content (in case of duplicate headers, though unlikely to be desired, we append)
        if sections[name]:
            sections[name] += "\n\n" + content
        else:
            sections[name] = content

    # Also capture text *before* the first header if any
    if matches[0][1] > 0:
        pre_text = text[:matches[0][1]].strip()
        if pre_text:
            # Append pre-text to Planning if Planning is the first header? 
            # Or maybe it's "Title" or "Intro". 
            # For now, let's prepend it to the first section found or keep it separate?
            # The user wants "Directory, Planning, Revision, Metadata".
            # If the text starts with "Planning", then pre_text is empty.
            # If it starts with random text then "Planning", maybe that random text is important.
            # I'll add it to "Planning" for now to be safe.
            first_section_name = matches[0][0]
            sections[first_section_name] = pre_text + "\n\n" + sections[first_section_name]

    return sections

def parse_scrivener_project(scriv_path):
    scrivx_path = os.path.join(scriv_path, "shoaib53.scrivx") # Assuming name matches folder
    # Or find any .scrivx
    if not os.path.exists(scrivx_path):
        for f in os.listdir(scriv_path):
            if f.endswith(".scrivx"):
                scrivx_path = os.path.join(scriv_path, f)
                break
    
    print(f"Parsing {scrivx_path}...")
    tree = ET.parse(scrivx_path)
    root = tree.getroot()
    
    data = []

    def traverse(node, path):
        # Get Title
        title_elem = node.find("Title")
        title = title_elem.text if title_elem is not None else "Untitled"
        
        current_path = f"{path}/{title}" if path else title
        
        # Get UUID
        uuid = node.get("UUID")
        
        # Check for content
        content_file = os.path.join(scriv_path, "Files", "Data", uuid, "content.rtf")
        
        if os.path.exists(content_file):
            try:
                with open(content_file, 'r', encoding='utf-8', errors='ignore') as f:
                    rtf_content = f.read()
                    text = rtf_to_text(rtf_content)
                    sections = extract_sections(text)
                    
                    data.append({
                        "Directory": current_path,
                        "Planning": sections["Planning"],
                        "Revision": sections["Revision"],
                        "Metadata": sections["Metadata"]
                    })
            except Exception as e:
                print(f"Error reading {content_file}: {e}")
        
        # Recurse
        children = node.find("Children")
        if children is not None:
            for child in children:
                traverse(child, current_path)

    binder = root.find("Binder")
    if binder is not None:
        for item in binder:
            traverse(item, "")
            
    return data

def parse_docx_folder(folder_path, prefix):
    data = []
    if not os.path.exists(folder_path):
        print(f"Folder not found: {folder_path}")
        return data

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".docx") and not file.startswith("~$"):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, folder_path)
                directory = f"{prefix}/{rel_path}"
                
                try:
                    doc = docx.Document(full_path)
                    text = "\n".join([p.text for p in doc.paragraphs])
                    sections = extract_sections(text)
                    
                    data.append({
                        "Directory": directory,
                        "Planning": sections["Planning"],
                        "Revision": sections["Revision"],
                        "Metadata": sections["Metadata"]
                    })
                except Exception as e:
                    print(f"Error reading {full_path}: {e}")
    return data

def main():
    all_data = []
    
    # 1. Scrivener
    if os.path.exists(SCRIV_PATH):
        all_data.extend(parse_scrivener_project(SCRIV_PATH))
    else:
        print(f"Scrivener path not found: {SCRIV_PATH}")

    # 2. Step 2
    all_data.extend(parse_docx_folder(STEP2_PATH, "Step 2"))

    # 3. Step 3
    all_data.extend(parse_docx_folder(STEP3_PATH, "Step 3"))

    # Write CSV
    print(f"Writing {len(all_data)} records to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["Directory", "Planning", "Revision", "Metadata"])
        writer.writeheader()
        for row in all_data:
            # Clean up fields for CSV (remove excessive newlines/tabs if needed, but CSV handles them)
            # Handle surrogates
            clean_row = {k: v.encode('utf-8', 'replace').decode('utf-8') if isinstance(v, str) else v for k, v in row.items()}
            writer.writerow(clean_row)
    
    print("Done.")

if __name__ == "__main__":
    main()
