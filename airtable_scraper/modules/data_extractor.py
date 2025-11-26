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
            pat_ref = None
            title = None
            
            # Check formats
            # 1. VARIATION X – PATTERN Y: Title
            m1 = re.match(r'^VARIATION\s+(\d+)\s*[–—-]\s*PATTERN\s+(\d+):\s*(.+)$', text, re.IGNORECASE)
            # 2. – PATTERN X: Title
            m2 = re.match(r'^\s*[–—-]\s*PATTERN\s+(\d+):\s*(.+)$', text, re.IGNORECASE)
            # 3. Variation X — Title
            m3 = re.match(r'^Variation\s+(\d+)\s*[–—-]\s*(.+)$', text, re.IGNORECASE)
            # 4. X — Title
            m4 = re.match(r'^(\d+)\s*[–—-]\s*(.+)$', text)
            # 5. – UPPERCASE TITLE (Implicit)
            m5 = re.match(r'^\s*[–—-]\s*([A-Z][A-Z\s\',.-]+)$', text)

            if m1:
                var_num, pat_ref, title = int(m1.group(1)), int(m1.group(2)), m1.group(3).strip()
                var_match = True
                current_var_num = var_num
            elif m2:
                pat_ref, title = int(m2.group(1)), m2.group(2).strip()
                var_num = pat_ref
                var_match = True
                current_var_num = var_num
            elif m3:
                var_num, title = int(m3.group(1)), m3.group(2).strip()
                pat_ref = 1
                var_match = True
                current_var_num = var_num
            elif m4:
                num = int(m4.group(1))
                var_num = 10 if num == 0 else num
                title = m4.group(2).strip()
                pat_ref = 1
                var_match = True
                current_var_num = var_num
            elif m5:
                # Additional validation for implicit format
                t_cand = m5.group(1).strip()
                letters = ''.join(c for c in t_cand if c.isalpha())
                if len(letters) > 3 and letters.isupper():
                    current_var_num += 1
                    var_num = current_var_num
                    title = t_cand
                    pat_ref = 1
                    var_match = True

            if var_match:
                content = ""
                j = i + 1
                while j < len(paragraphs):
                    p_text = paragraphs[j].text.strip()
                    if not p_text:
                        j += 1
                        continue
                    
                    # Stop pattern
                    stop = (re.match(r'^(Pattern|Variation|VARIATION|\d+\s*[–—-])\s', p_text, re.IGNORECASE) or
                            re.match(r'^\s*[–—-]\s*([A-Z][A-Z\s\',.-]+)$', p_text))
                    if stop: break
                    
                    content = self.clean_text(p_text)
                    break
                
                if not content:
                    self.log(f"Variation {var_num} in {file_path} has no content", "warning")
                
                variations.append({
                    "variation_number": var_num,
                    "pattern_reference": pat_ref,
                    "title": title,
                    "content": content
                })
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
        return extracted_data
