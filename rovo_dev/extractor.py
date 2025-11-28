from __future__ import annotations
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
import docx
from .text_utils import normalize_text, looks_like_heading, extract_number_prefix


PATTERN_HEADING_RE = re.compile(r"^(?:pattern|task|part)\s*(\d+)[:\-\).\s]+(.+)$", re.IGNORECASE)
VARIATION_HEADING_RE = re.compile(r"^(?:variation|var|option)\s*(\d+)[:\-\).\s]+(.+)$", re.IGNORECASE)


class RovoExtractor:
    def __init__(self, logger=None):
        self.logger = logger

    def log(self, msg, level="info"):
        if self.logger:
            getattr(self.logger, level if hasattr(self.logger, level) else "info")(msg)
        else:
            print(f"[{level.upper()}] {msg}")

    def _iter_docx(self, file_path: Path):
        doc = docx.Document(str(file_path))
        for p in doc.paragraphs:
            txt = normalize_text(p.text)
            if txt:
                yield txt

    def extract_summary(self, lines: List[str]) -> Tuple[str, bool]:
        out = []
        first_skipped = False
        for line in lines:
            if re.match(r"^(task\s*1|pattern\s*1|part\s*i)\b", line, re.IGNORECASE):
                break
            if (line.isupper() and len(line) < 100) or re.match(r'^[_\-=]{3,}$', line):
                continue
            if not first_skipped:
                first_skipped = True
                continue
            out.append(line)
        summary = "\n\n".join(out).strip()
        has_valid = len(out) >= 2 or len(summary) > 50
        return (summary, has_valid)

    def _find_headings(self, lines: List[str], regex) -> List[Tuple[int, int, str]]:
        # returns list of (index, number, title)
        hits: List[Tuple[int, int, str]] = []
        for i, line in enumerate(lines):
            m = regex.match(line)
            if m:
                try:
                    num = int(m.group(1))
                except Exception:
                    continue
                title = m.group(2).strip()
                hits.append((i, num, title))
                continue
            # also accept plain numbered headings like "1) Title" as patterns if pattern regex absent
        return hits

    def _capture_sections(self, lines: List[str], headings: List[Tuple[int, int, str]]) -> Dict[int, Dict[str, Any]]:
        # Given heading indices, capture text until next heading
        sections: Dict[int, Dict[str, Any]] = {}
        for idx, (start_i, num, title) in enumerate(headings):
            end_i = headings[idx + 1][0] if idx + 1 < len(headings) else len(lines)
            body = []
            for j in range(start_i + 1, end_i):
                # stop if a hard rule line
                if re.match(r"^(?:pattern|task|part|variation|var|option)\s*\d+[\).:\-\s]+", lines[j], re.IGNORECASE):
                    break
                body.append(lines[j])
            sections[num] = {
                "title": title,
                "content": "\n".join(body).strip()
            }
        return sections

    def parse_document(self, file_path: Path) -> Dict[str, Any] | None:
        try:
            lines = list(self._iter_docx(file_path))
            if not lines:
                return None
            summary, has_summary = self.extract_summary(lines)
            # find pattern and variation headings
            pattern_heads = self._find_headings(lines, PATTERN_HEADING_RE)
            variation_heads = self._find_headings(lines, VARIATION_HEADING_RE)

            # also augment variations with generic numbered headings that look like titles
            for i, line in enumerate(lines):
                if VARIATION_HEADING_RE.match(line) or PATTERN_HEADING_RE.match(line):
                    continue
                num = extract_number_prefix(line)
                if num is not None and looks_like_heading(line):
                    title = re.sub(r"^.*?\b\d+[\).:\-\s]+", "", line).strip()
                    if title and not any(n == num for _, n, _ in variation_heads):
                        variation_heads.append((i, num, title))
            # sort by index
            pattern_heads.sort(key=lambda x: x[0])
            variation_heads.sort(key=lambda x: x[0])

            pattern_sections = self._capture_sections(lines, pattern_heads) if pattern_heads else {}
            variation_sections = self._capture_sections(lines, variation_heads) if variation_heads else {}

            patterns: List[Dict[str, Any]] = []
            for _, num, title in pattern_heads:
                sec = pattern_sections.get(num, {"content": ""})
                patterns.append({
                    "pattern_number": num,
                    "title": title,
                    "overview": sec.get("content", ""),
                    "choice": "",
                    "source": "",
                    "variations": []
                })

            variations: List[Dict[str, Any]] = []
            for _, num, title in variation_heads:
                sec = variation_sections.get(num, {"content": ""})
                variations.append({
                    "variation_number": num,
                    "title": title,
                    "content": sec.get("content", ""),
                })

            if not patterns or not has_summary:
                self.log(f"Skipping {file_path.name}: Missing patterns or summary", "warning")
                return None
            return {
                "lens": file_path.stem,
                "file_path": str(file_path),
                "summary": summary,
                "patterns": patterns,
                "variations": variations,
            }
        except Exception as e:
            self.log(f"Error parsing {file_path.name}: {e}", "error")
            return None
