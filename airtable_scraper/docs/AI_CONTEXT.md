# Airtable Scraper - AI Context & Developer Guide

## Project Overview
This tool extracts structured data (Patterns, Variations, Metas, Lenses) from Microsoft Word (`.docx`) files and syncs it to Airtable. It is designed to be idempotent (avoiding duplicates) and robust to various formatting inconsistencies.

## Core Logic Rules

### 1. Variation Extraction & Linking
**CRITICAL UNDERSTANDING**: Each document typically contains **10 patterns** but **only Pattern 1 has variations**. All 10 variations in a document belong to Pattern 1 unless explicitly stated otherwise.

**Document Structure Pattern:**
```
Pattern 1: MAIN PATTERN TITLE
Pattern 2: SECOND PATTERN TITLE  
...
Pattern 10: TENTH PATTERN TITLE

Part II: Ten Variations of Pattern #1
— FIRST VARIATION TITLE
— SECOND VARIATION TITLE
...
0 — TENTH VARIATION TITLE (0 = Variation 10)
```

**Linking Logic:**
*   **Default Rule**: If a variation does not explicitly mention a Pattern number, it **ALWAYS** belongs to **Pattern 1**.
*   **Explicit Rule**: If a variation header contains "PATTERN X", it belongs to **Pattern X**.
*   **Expected Outcome**: Pattern 1 gets 10 variations, Patterns 2-10 get 0 variations each.

**Variation Formats (Must Handle All):**
1.  `– ONE FIELD, MANY SCALES` → **Pattern 1** (Implicit)
2.  `- THE SOIL REMEMBERS` → **Pattern 1** (Implicit, standard dash)
3.  `VARIATION 6 – INNER CLIMATE, OUTER CLIMATE` → **Pattern 1** (Explicit Var Num, Implicit Pattern)
4.  `0 — SUPERLOVE AS COSMIC IMPERATIVE` → **Variation 10** (0 equals 10), **Pattern 1**
5.  `Variation 9 – PATTERN 9: SPEAKING IN SEEDS` → **Pattern 9** (Explicit Pattern Reference)

**Key Regex Requirements:**
*   Must handle different dash types: hyphen (`-`), en-dash (`–`), em-dash (`—`), minus (`−`).
*   Must handle implicit uppercase titles with punctuation (e.g., "EARTH'S FEVER").
*   Must handle "0" as "10".
*   Must handle mixed case variations like "Variation 6 —" or "VARIATION 6 –".

### 2. Airtable Syncing (Idempotency) - CRITICAL SECTION
**NEVER CREATE DUPLICATES** - This is the most common failure point.

**Pre-Sync Process:**
1. **Always** fetch all existing records from all tables before syncing
2. Build a normalized cache mapping `{clean_key: record_id}`
3. Use case-insensitive, whitespace-trimmed matching

**Matching Logic:**
*   **Patterns**: Match by normalized `pattern_title`
*   **Variations**: Match by normalized `variation_title` 
*   **Lenses**: Match by normalized `lens_name`
*   **Sources**: Match by normalized `source_name`
*   **Metas**: Match by normalized `title`

**Normalization Rules:**
```python
def normalize_for_matching(text):
    if not text: return ""
    return text.strip().lower()
```

**Action Logic:**
*   If record exists → **Update** (Patch) to ensure data is fresh
*   If record missing → **Create** (Post)
*   **Always** update the cache after creating new records

### 3. Expected Data Structure
Each document should produce:
- 1 Lens record
- 10 Pattern records (for that document)
- ~10 Variation records (all linked to Pattern 1 typically)
- Variable Meta records 
- Variable Source records

Total per BIOME folder (5 documents): ~50 Patterns, ~50 Variations, 5 Lenses

## Directory Structure
*   `modules/data_extractor.py`: Handles parsing DOCX files.
*   `modules/airtable_uploader.py`: Handles API logic and syncing.
*   `json_data/`: Intermediate storage for extracted data.
*   `logs/`: Execution logs.
*   `config/settings.py`: Configuration and Airtable credentials.

## Common Pitfalls (Do Not Repeat)

### Variation Extraction Issues
*   **Missing Variations**: Often caused by regex not catching titles with punctuation (e.g., "EARTH'S") or different dash styles.
*   **Wrong Pattern Assignment**: Remember most variations go to Pattern 1 unless explicitly stated.
*   **Number Handling**: "0" should be converted to "10".

### Duplicate Upload Issues  
*   **Case Sensitivity**: "BELOVED BANG" vs "beloved bang" should match.
*   **Whitespace**: "PATTERN TITLE " vs "PATTERN TITLE" should match.
*   **Cache Not Updated**: After creating a record, update the local cache.
*   **Incomplete Fetching**: Make sure to fetch ALL pages of existing records.

### Code Structure Issues
*   **Relative Imports**: Always use absolute imports (e.g., `from config import settings`) to avoid execution errors.
*   **Missing Error Handling**: All API calls should have try/catch blocks.
*   **Insufficient Logging**: Log all create/update operations for debugging.

## Debug Commands
```bash
# Test extraction only
python test_variations.py

# Test full sync (requires Airtable credentials)
python main.py

# Analyze extraction results
python analyze_variations.py
```

## Airtable Schema Expected
- **Patterns**: pattern_title, overview, choice, base_folder, lens (link), sources (link)
- **Variations**: variation_title, variation_number, content, linked_pattern (link)  
- **Lenses**: lens_name, content
- **Sources**: source_name
- **Metas**: title, subtitle, content, base_folder
