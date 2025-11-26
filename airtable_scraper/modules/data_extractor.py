import os
import re
import docx
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from config import settings

class DataExtractor:
    def __init__(self, log_handler=None):
        self.logger = log_handler
        
    def log(self, msg, level="info"):
        if self.logger:
            if level == "error":
                self.logger.error(msg)
            elif level == "warning":
                self.logger.warning(msg)
            else:
                self.logger.info(msg)
        else:
            print(f"[{level.upper()}] {msg}")

    def clean_text(self, text: str) -> str:
        if not text: return ""
        text = text.replace('\\n', ' ').replace('\n', ' ')
        return re.sub(r'\s+', ' ', text).strip()

    def clean_label(self, text: str) -> str:
        if not text: return ""
        labels = ["Explanation:", "Inner war / choice:", "Sources:", "Explanation :", "Inner war / choice :", "Sources :"]
        cleaned = text.strip()
        for label in labels:
            if cleaned.lower().startswith(label.lower()):
                cleaned = cleaned[len(label):].strip()
                break
        return cleaned

    def extract_summary(self, paragraphs: List) -> Tuple[str, bool]:
        summary_lines = []
        first_line_skipped = False
        
        for para in paragraphs:
            text = para.text.strip()
            if not text: continue
            
            # Stop at pattern start
            if re.match(r'^(Task\s+1|TASK\s+1|Pattern\s+1|Part\s+I)', text, re.IGNORECASE):
                break
            
            # Skip title/separators
            if (text.isupper() and len(text) < 100) or re.match(r'^[_\-=]{3,}$', text):
                continue
                
            if not first_line_skipped:
                first_line_skipped = True
                continue
                
            summary_lines.append(text)
        
        summary = "\n\n".join(summary_lines)
        has_valid = len(summary_lines) >= 2 or len(summary) > 50
        return (self.clean_text(summary), True) if has_valid else ("", False)

    # a: Pattern Extractor
    def extract_patterns(self, paragraphs: List) -> List[Dict]:
        patterns = []
        i = 0
        while i < len(paragraphs):
            text = paragraphs[i].text.strip()
            match = re.match(r'^Pattern\s+(\d+):\s*(.+)$', text, re.IGNORECASE)
            
            if match:
                p_num = int(match.group(1))
                title = match.group(2).strip()
                overview, choice, source = "", "", ""
                
                # Collect next 3 sections
                j = i + 1
                section_idx = 0
                while j < len(paragraphs) and section_idx < 3:
                    p_text = paragraphs[j].text.strip()
                    if not p_text:
                        j += 1
                        continue
                    
                    if re.match(r'^(Pattern|Variation)\s+\d+', p_text, re.IGNORECASE):
                        break
                        
                    cleaned = self.clean_text(self.clean_label(p_text))
                    if section_idx == 0: overview = cleaned
                    elif section_idx == 1: choice = cleaned
                    elif section_idx == 2: source = cleaned
                    
                    section_idx += 1
                    j += 1
                
                patterns.append({
                    "pattern_number": p_num,
                    "title": title,
                    "overview": overview,
                    "choice": choice,
                    "source": source,
                    "variations": []
                })
            i += 1
        return patterns

    # c: Variation Extractor
    def extract_variations(self, paragraphs: List, file_path: str) -> List[Dict]:
        variations = []
        i = 0
        current_var_num = 0
        
        while i < len(paragraphs):
            text = paragraphs[i].text.strip()
            var_match = False
            var_num = None
            pat_ref = 1 # Default to Pattern 1
            title = None
            
            # Regex Patterns for different formats
            # Enhanced patterns to handle more edge cases
            # Note: [–—-−] handles various dash types (en-dash, em-dash, hyphen, minus)
            
            # Format 1: Explicit Pattern Ref -> "Variation 9 – PATTERN 9: Title"
            m_explicit = re.match(r'^Variation\s+(\d+)\s*[–—-−]\s*PATTERN\s+(\d+):\s*(.+)$', text, re.IGNORECASE)
            
            # Format 2: Explicit Var Num -> "VARIATION 6 – Title" or "Variation 6 — Title"
            m_var_num = re.match(r'^VARIATION\s+(\d+)\s*[–—-−]\s*(?!PATTERN)(.+)$', text, re.IGNORECASE)
            
            # Format 3: Number only -> "0 — Title" or "6 — Title"
            m_num_only = re.match(r'^(\d+)\s*[–—-−]\s*(.+)$', text)
            
            # Format 4: Implicit -> "– ONE FIELD, MANY SCALES" or "- THE SOIL REMEMBERS"
            # Enhanced to handle more punctuation and formats
            m_implicit = re.match(r'^\s*[–—-−]\s*([A-Z0-9][A-Z0-9\s\',.:;!?&()-]+)$', text)

            if m_explicit:
                var_num = int(m_explicit.group(1))
                pat_ref = int(m_explicit.group(2))
                title = m_explicit.group(3).strip()
                current_var_num = var_num
                var_match = True
                
            elif m_var_num:
                var_num = int(m_var_num.group(1))
                title = m_var_num.group(2).strip()
                # pat_ref stays 1
                current_var_num = var_num
                var_match = True
                
            elif m_num_only:
                raw_num = int(m_num_only.group(1))
                var_num = 10 if raw_num == 0 else raw_num
                title = m_num_only.group(2).strip()
                # pat_ref stays 1
                current_var_num = var_num
                var_match = True
                
            elif m_implicit:
                # Validation: Ensure it looks like a title (mostly uppercase letters)
                candidate = m_implicit.group(1).strip()
                letters = ''.join(c for c in candidate if c.isalpha())
                if len(letters) > 3 and letters.isupper():
                    current_var_num += 1
                    var_num = current_var_num
                    title = candidate
                    # pat_ref stays 1
                    var_match = True

            if var_match:
                content = ""
                j = i + 1
                while j < len(paragraphs):
                    p_text = paragraphs[j].text.strip()
                    if not p_text:
                        j += 1
                        continue
                    
                    # Stop pattern: Check for next header
                    # Matches: "Pattern X", "Variation X", "X - Title", "- TITLE"
                    stop = (
                        re.match(r'^(Pattern|Variation|VARIATION)\s+\d+', p_text, re.IGNORECASE) or
                        re.match(r'^\d+\s*[–—-−]', p_text) or
                        re.match(r'^\s*[–—-−]\s*[A-Z]', p_text)
                    )
                    if stop: break
                    
                    content = self.clean_text(p_text)
                    break # Take only the first paragraph as content (usually)
                
                if not content:
                    self.log(f"Variation {var_num} in {file_path} has no content", "warning")
                
                variations.append({
                    "variation_number": var_num,
                    "pattern_reference": pat_ref,
                    "title": title,
                    "content": content
                })
                
                self.log(f"Extracted variation {var_num} for pattern {pat_ref}: {title[:50]}...")
            i += 1
        return variations

    # e: Metas Extractor
    def extract_metas(self, file_path: str, base_folder: str) -> Optional[Dict]:
        try:
            doc = docx.Document(file_path)
            paras = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
            if not paras: return None
            
            return {
                "title": Path(file_path).stem,
                "subtitle": paras[0],
                "content": self.clean_text("\n\n".join(paras)),
                "base_folder": base_folder
            }
        except Exception as e:
            self.log(f"Error extracting META {file_path}: {str(e)}", "error")
            return None

    # Main Processing Method
    def process_folder(self, folder_name: str) -> Dict:
        folder_path = settings.SOURCE_DIR / folder_name
        if not folder_path.exists():
            self.log(f"Folder not found: {folder_path}", "error")
            return {}

        self.log(f"Processing folder: {folder_name}")
        
        extracted_data = {
            "base_folder": folder_name,
            "timestamp": datetime.now().isoformat(),
            "metas": [],
            "documents": []
        }

        # 1. Extract METAS
        metas_dir = folder_path / "METAS"
        if metas_dir.exists():
            for f in metas_dir.glob("*.docx"):
                if f.name.startswith("~$"): continue
                meta = self.extract_metas(str(f), folder_name)
                if meta: extracted_data["metas"].append(meta)

        # 2. Extract Documents (Patterns, Sources, Lenses, Variations)
        step2_dir = folder_path / "STEP 2"
        target_dir = step2_dir if step2_dir.exists() else folder_path
        
        for f in target_dir.glob("*.docx"):
            if f.name.startswith("~$"): continue
            
            try:
                doc = docx.Document(str(f))
                paras = doc.paragraphs
                
                # Extract components
                summary, has_summary = self.extract_summary(paras)
                patterns = self.extract_patterns(paras)
                variations = self.extract_variations(paras, f.name)
                
                if not patterns or not has_summary:
                    self.log(f"Skipping {f.name}: Missing patterns or summary", "warning")
                    continue

                # Link variations to patterns
                p_map = {p["pattern_number"]: p for p in patterns}
                for v in variations:
                    # Logic: Try pattern ref, else fallback to first pattern (common in single-pattern docs)
                    target = p_map.get(v["pattern_reference"], patterns[0])
                    target["variations"].append({
                        "variation_number": v["variation_number"],
                        "title": v["title"],
                        "content": v["content"]
                    })
                    self.log(f"Linked variation {v['variation_number']} to pattern {target['pattern_number']}: {target['title'][:30]}...")

                # d: Lens Extractor (Lens is the document concept/filename)
                lens_name = f.stem
                
                # b: Source Extractor (Sources are inside patterns)
                # (Implicitly handled as they are part of the pattern dict)

                extracted_data["documents"].append({
                    "lens": lens_name,
                    "base_folder": folder_name,
                    "file_path": str(f),
                    "summary": summary,
                    "patterns": patterns
                })
                
            except Exception as e:
                self.log(f"Error processing {f.name}: {str(e)}", "error")

        # Save to JSON
        out_file = settings.DATA_DIR / f"{folder_name.lower()}_data.json"
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(extracted_data, f, indent=2, ensure_ascii=False)
            
        self.log(f"Extraction complete. Saved to {out_file}")
        # Log extraction summary
        doc_count = len(extracted_data.get("documents", []))
        meta_count = len(extracted_data.get("metas", []))
        total_patterns = sum(len(doc.get("patterns", [])) for doc in extracted_data.get("documents", []))
        total_variations = sum(len(pattern.get("variations", [])) 
                              for doc in extracted_data.get("documents", []) 
                              for pattern in doc.get("patterns", []))
        
        self.log(f"Extraction Summary - Documents: {doc_count}, Patterns: {total_patterns}, Variations: {total_variations}, Metas: {meta_count}")
        
        return extracted_data
