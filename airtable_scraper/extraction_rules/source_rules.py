"""
Source Extraction Rules
=======================

This file contains all the regex patterns and validation logic for extracting sources
from pattern text. These rules can be easily updated or modified by AI or other 
automated processes.

Usage:
    from extraction_rules.source_rules import SourceExtractor
    extractor = SourceExtractor()
    sources = extractor.parse_sources(source_text, lens_name, base_folder)
"""

import re
from typing import List, Dict, Optional


class SourceExtractor:
    """Handles source extraction from text using configurable rules."""
    
    def __init__(self):
        # Configuration for source extraction
        self.fallback_prefix = "SOURCE_"
        
        # Known source name patterns (all caps names that commonly appear)
        self.known_sources = [
            "HOME_SPINE", "HIGHLIGHTS", "GITHUB_MOMENT", "BELOVED_BANG",
            "GEN_G", "INNER", "LOVE", "MICROBIAL_THEOLOGY", "SOURCE_1",
            "SOURCE_2", "SOURCE_3", "BIOME", "QUANTUM", "WARS", "DYNAMITE"
        ]
        
        # Separators that can split multiple sources
        self.source_separators = [';', '|', '&', ' and ', ' AND ']
        
        # Characters that indicate parenthetical content (to avoid splitting inside)
        self.paren_chars = {'(': ')', '[': ']', '{': '}'}
    
    def get_source_pattern(self) -> str:
        """
        Returns the regex pattern for identifying source names and content.
        
        Pattern matches: SOURCE_NAME [separator] content
        Where separator can be: –, —, -, −, :
        """
        return r'^([A-Z_\s]+?)\s*[–—-−:]\s*(.+)$'
    
    def split_sources(self, source_text: str) -> List[str]:
        """
        Split source text into individual sources, handling nested parentheses.
        
        Args:
            source_text: Raw source text that may contain multiple sources
            
        Returns:
            List[str]: Individual source strings
        """
        if not source_text:
            return []
        
        raw_sources = []
        current = ""
        paren_stack = []
        
        i = 0
        while i < len(source_text):
            char = source_text[i]
            
            # Handle opening parentheses/brackets
            if char in self.paren_chars:
                paren_stack.append(self.paren_chars[char])
                current += char
                
            # Handle closing parentheses/brackets
            elif paren_stack and char == paren_stack[-1]:
                paren_stack.pop()
                current += char
                
            # Handle separators (only if not inside parentheses)
            elif not paren_stack and char == ';':
                if current.strip():
                    raw_sources.append(current.strip())
                current = ""
                
            # Handle multi-character separators
            elif not paren_stack:
                found_separator = False
                for sep in [' and ', ' AND ']:
                    if source_text[i:i+len(sep)] == sep:
                        if current.strip():
                            raw_sources.append(current.strip())
                        current = ""
                        i += len(sep) - 1  # Skip ahead
                        found_separator = True
                        break
                
                if not found_separator:
                    current += char
            else:
                current += char
            
            i += 1
        
        # Add the last part
        if current.strip():
            raw_sources.append(current.strip())
        
        return raw_sources
    
    def extract_source_info(self, raw_source: str, index: int = 0) -> Dict[str, str]:
        """
        Extract source name and content from a raw source string.
        
        Args:
            raw_source: Raw source string to parse
            index: Index for fallback naming
            
        Returns:
            Dict with 'source_name' and 'content' keys
        """
        raw_source = raw_source.strip()
        if not raw_source:
            return {"source_name": f"{self.fallback_prefix}{index+1}", "content": ""}
        
        # Try to match the source pattern
        pattern = self.get_source_pattern()
        source_match = re.match(pattern, raw_source)
        
        if source_match:
            source_name = source_match.group(1).strip()
            source_content = source_match.group(2).strip()
            
            # Validate that the source name looks legitimate
            if self.is_valid_source_name(source_name):
                return {
                    "source_name": source_name,
                    "content": source_content
                }
        
        # Fallback: use position-based naming
        return {
            "source_name": f"{self.fallback_prefix}{index+1}",
            "content": raw_source
        }
    
    def is_valid_source_name(self, name: str) -> bool:
        """
        Validates if a string looks like a legitimate source name.
        
        Args:
            name: Potential source name
            
        Returns:
            bool: True if this looks like a valid source name
        """
        name = name.strip()
        
        # Must have some content
        if not name:
            return False
        
        # Should be mostly uppercase with underscores/spaces
        if not re.match(r'^[A-Z_\s]+$', name):
            return False
        
        # Should not be too long (likely content, not a name)
        if len(name) > 50:
            return False
        
        # Should not be too short (likely not a real source name)
        if len(name) < 2:
            return False
        
        return True
    
    def clean_content(self, content: str) -> str:
        """
        Clean source content by removing extra whitespace and formatting.
        
        Args:
            content: Raw content string
            
        Returns:
            str: Cleaned content
        """
        if not content:
            return ""
        
        # Replace literal \n with space
        content = content.replace('\\n', ' ')
        # Replace actual newlines with space
        content = content.replace('\n', ' ')
        # Remove multiple spaces
        content = re.sub(r'\s+', ' ', content)
        # Remove leading/trailing whitespace
        content = content.strip()
        
        return content
    
    def parse_sources(self, source_text: str, lens_name: str, base_folder: str, logger=None) -> List[Dict]:
        """
        Parse multiple sources from source text using the configured rules.
        
        Args:
            source_text: Raw text containing source information
            lens_name: Name of the lens this source belongs to
            base_folder: Base folder name for organization
            logger: Optional logger instance
            
        Returns:
            List[Dict]: List of source dictionaries
        """
        def log(message: str, level: str = "info"):
            if logger:
                getattr(logger, level, logger.info)(message)
        
        if not source_text:
            return []
        
        # Split into individual sources
        raw_sources = self.split_sources(source_text)
        
        sources = []
        for i, raw_source in enumerate(raw_sources):
            if not raw_source:
                continue
            
            # Extract source info
            source_info = self.extract_source_info(raw_source, i)
            
            # Clean the content
            source_info["content"] = self.clean_content(source_info["content"])
            
            # Add metadata
            source_info.update({
                "lens": lens_name,
                "base_folder": base_folder
            })
            
            sources.append(source_info)
            
            log(f"Extracted source: {source_info['source_name']} from {lens_name}")
        
        return sources
    
    def get_common_labels(self) -> List[str]:
        """
        Get list of common labels that should be removed from pattern content.
        
        Returns:
            List[str]: Common labels to remove
        """
        return [
            "Explanation:", "Inner war / choice:", "Sources:", 
            "Explanation :", "Inner war / choice :", "Sources :"
        ]
    
    def clean_label(self, text: str) -> str:
        """
        Remove common labels from text content.
        
        Args:
            text: Text that may contain labels
            
        Returns:
            str: Text with labels removed
        """
        if not text:
            return ""
        
        cleaned = text.strip()
        labels = self.get_common_labels()
        
        for label in labels:
            if cleaned.startswith(label):
                cleaned = cleaned[len(label):].strip()
                break
        
        return cleaned