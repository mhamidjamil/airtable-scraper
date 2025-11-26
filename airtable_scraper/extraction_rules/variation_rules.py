"""
Variation Extraction Rules
=========================

This file contains all the regex patterns and validation logic for extracting variations
from document paragraphs. These rules can be easily updated or modified by AI or other 
automated processes.

Usage:
    from extraction_rules.variation_rules import VariationExtractor
    extractor = VariationExtractor()
    variations = extractor.extract_variations(paragraphs, file_path)
"""

import re
from typing import List, Dict, Optional, Tuple


class VariationExtractor:
    """Handles variation extraction from document paragraphs using configurable rules."""
    
    def __init__(self):
        # Configuration for variation extraction
        self.max_title_length = 200
        self.min_title_length = 3
        self.default_pattern_ref = 1
        
        # Words that commonly start content rather than titles
        self.content_start_words = [
            'the ', 'this ', 'it ', 'a ', 'an ', 'in ', 'on ', 'at ', 
            'to ', 'for ', 'with ', 'by ', 'and ', 'or ', 'but '
        ]
        
        # Section headers to exclude
        self.section_headers = ['pattern ', 'part ', 'section ', 'task ', 'chapter ']
        
        # Stop patterns for content extraction
        self.stop_patterns = [
            r'^(Pattern|Variation|VARIATION)\s+\d+',
            r'^\d+\s*[–—-−]',
            r'^\s*[–—-−]\s*[A-Z]'
        ]
    
    def get_variation_patterns(self) -> List[Tuple[str, str]]:
        """
        Returns list of (pattern_name, regex) tuples for variation detection.
        
        These patterns are checked in order. The first match wins.
        """
        return [
            # Format 1: Explicit Pattern Reference
            # Example: "Variation 9 – PATTERN 9: Title"
            ("explicit_pattern", r'^Variation\s+(\d+)\s*[–—-−]\s*PATTERN\s+(\d+):\s*(.+)$'),
            
            # Format 2: Explicit Variation Number
            # Example: "VARIATION 6 – Title" or "Variation 6 — Title"
            ("explicit_number", r'^Variation\s+(\d+)\s*[–—-−]\s*(?!PATTERN)(.+)$'),
            
            # Format 3: Number Only
            # Example: "0 — Title" or "6 — Title" (handles "0" as "10")
            ("number_only", r'^(\d+)\s*[–—-−]\s*(.+)$'),
            
            # Format 4: Dash Title (All Caps)
            # Example: "— THE FIRST YES THAT STILL ECHOES"
            ("dash_title", r'^[–—-−]\s*([A-Z\s]+)$'),
            
            # Format 5: General Implicit
            # Example: "– ONE FIELD, MANY SCALES" or "- THE SOIL REMEMBERS"
            ("implicit_dash", r'^\s*[–—-−]\s*(.+)$')
        ]
    
    def validate_dash_title(self, candidate: str) -> bool:
        """
        Validates if a dash-title candidate should be treated as a variation.
        
        Args:
            candidate: The text after the dash
            
        Returns:
            bool: True if this should be treated as a variation title
        """
        candidate = candidate.strip()
        
        # Length check
        if len(candidate) <= self.min_title_length or len(candidate) >= self.max_title_length:
            return False
        
        # Must be all uppercase
        if not candidate.isupper():
            return False
        
        # Should not start with section headers
        for header in self.section_headers:
            if candidate.lower().startswith(header):
                return False
        
        return True
    
    def validate_implicit_title(self, candidate: str) -> bool:
        """
        Validates if an implicit candidate should be treated as a variation.
        
        Args:
            candidate: The text after the dash
            
        Returns:
            bool: True if this should be treated as a variation title
        """
        candidate = candidate.strip()
        
        # Length check
        if len(candidate) >= self.max_title_length:
            return False
        
        # Should not start with common content words
        candidate_lower = candidate.lower()
        for word in self.content_start_words:
            if candidate_lower.startswith(word):
                return False
        
        # Should have some uppercase content (indicating it's a title)
        if not (candidate.isupper() or 
                any(c.isupper() for c in candidate[:10]) or 
                re.search(r'[A-Z]{2,}', candidate)):
            return False
        
        return True
    
    def check_stop_condition(self, text: str) -> bool:
        """
        Checks if the given text matches any stop pattern for content extraction.
        
        Args:
            text: Text to check
            
        Returns:
            bool: True if this text indicates the end of variation content
        """
        for pattern in self.stop_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def clean_text(self, text: str) -> str:
        """
        Cleans extracted text by removing newlines and extra spaces.
        
        Args:
            text: Raw text to clean
            
        Returns:
            str: Cleaned text
        """
        if not text:
            return ""
        
        # Replace literal \n with space
        text = text.replace('\\n', ' ')
        # Replace actual newlines with space
        text = text.replace('\n', ' ')
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def extract_variations(self, paragraphs: List, file_path: str, logger=None) -> List[Dict]:
        """
        Extract variations from document paragraphs using the configured rules.
        
        Args:
            paragraphs: List of document paragraphs
            file_path: Path to the source file (for logging)
            logger: Optional logger instance
            
        Returns:
            List[Dict]: List of extracted variation dictionaries
        """
        variations = []
        i = 0
        current_var_num = 0
        patterns = self.get_variation_patterns()
        
        def log(message: str, level: str = "info"):
            if logger:
                getattr(logger, level, logger.info)(message)
        
        while i < len(paragraphs):
            text = paragraphs[i].text.strip()
            var_match = False
            var_num = None
            pat_ref = self.default_pattern_ref
            title = None
            
            # Try each pattern in order
            for pattern_name, pattern_regex in patterns:
                match = re.match(pattern_regex, text, re.IGNORECASE if pattern_name != "dash_title" else 0)
                
                if match:
                    if pattern_name == "explicit_pattern":
                        var_num = int(match.group(1))
                        pat_ref = int(match.group(2))
                        title = match.group(3).strip()
                        current_var_num = var_num
                        var_match = True
                        
                    elif pattern_name == "explicit_number":
                        var_num = int(match.group(1))
                        title = match.group(2).strip()
                        current_var_num = var_num
                        var_match = True
                        
                    elif pattern_name == "number_only":
                        raw_num = int(match.group(1))
                        var_num = 10 if raw_num == 0 else raw_num
                        title = match.group(2).strip()
                        current_var_num = var_num
                        var_match = True
                        
                    elif pattern_name == "dash_title":
                        candidate = match.group(1).strip()
                        if self.validate_dash_title(candidate):
                            current_var_num += 1
                            var_num = current_var_num
                            title = candidate
                            var_match = True
                            
                    elif pattern_name == "implicit_dash":
                        candidate = match.group(1).strip()
                        if self.validate_implicit_title(candidate):
                            current_var_num += 1
                            var_num = current_var_num
                            title = candidate
                            var_match = True
                    
                    # If we found a match, stop trying other patterns
                    if var_match:
                        break
            
            # If we found a variation, extract its content
            if var_match:
                content = ""
                j = i + 1
                while j < len(paragraphs):
                    p_text = paragraphs[j].text.strip()
                    if not p_text:
                        j += 1
                        continue
                    
                    # Check for stop condition
                    if self.check_stop_condition(p_text):
                        break
                    
                    content = self.clean_text(p_text)
                    break  # Take only the first paragraph as content
                
                if not content:
                    log(f"Variation {var_num} in {file_path} has no content", "warning")
                
                variations.append({
                    "variation_number": var_num,
                    "pattern_reference": pat_ref,
                    "title": title,
                    "content": content
                })
                
                log(f"Extracted variation {var_num} for pattern {pat_ref}: {title[:50]}...")
            
            i += 1
        
        return variations