"""
Extraction Rules Package
========================

This package contains all the extraction rules and logic for parsing variations,
sources, and patterns from documents. This allows for easy maintenance and 
updates by AI or other automated processes.

Modules:
    - variation_rules: Rules for extracting variations from document text
    - source_rules: Rules for extracting sources from pattern text
    - pattern_rules: Rules for extracting patterns (if needed)
"""

from .variation_rules import VariationExtractor
from .source_rules import SourceExtractor

__all__ = ['VariationExtractor', 'SourceExtractor']