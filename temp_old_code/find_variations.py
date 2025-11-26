import docx
import re

doc = docx.Document(r'new_extractions\BIOME\STEP 2\Ecological & Microbial Consciousness One Wounded Biome.docx')

# Get all paragraphs
paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

with open('variation_analysis.txt', 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("FINDING VARIATION HEADERS IN DOCUMENT\n")
    f.write("=" * 80 + "\n\n")
    
    # Look for lines that might be variations
    for i, para in enumerate(paragraphs):
        # Check if it looks like a variation header
        if (re.match(r'(VARIATION|–|\d+\s*[–—-])', para, re.I) or 
            (para.isupper() and len(para) < 100 and '–' in para)):
            f.write(f"Line {i}:\n")
            f.write(f"  Text: {para}\n")
            f.write(f"  Length: {len(para)}\n\n")
            
            # Print next paragraph (content)
            if i + 1 < len(paragraphs):
                next_para = paragraphs[i + 1][:300]
                f.write(f"  Next: {next_para}...\n\n")

print("Analysis saved to variation_analysis.txt")
