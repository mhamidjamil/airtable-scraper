# Comprehensive AI Guide for Airtable Scraper System

## Project Mission
Extract structured data (Patterns, Variations, Metas, Lenses, Sources) from Microsoft Word documents and sync to Airtable with zero duplicates and complete variation coverage.

## Core Data Structure
- **Patterns**: Main content blocks with pattern_number, title, overview, choice, source
- **Variations**: Alternative formulations of patterns (usually 10 per file)
- **Metas**: Metadata documents from METAS folder
- **Lenses**: Document concepts (derived from filename)
- **Sources**: Referenced materials within patterns

## Critical Rules for Variations

### 1. Variation Linking Logic
- **Default Rule**: If variation has NO explicit pattern reference → ALWAYS belongs to Pattern 1
- **Explicit Rule**: If variation contains "PATTERN X" → belongs to Pattern X

### 2. Variation Format Support (MUST handle ALL)
```
1. – ONE FIELD, MANY SCALES                          → Pattern 1, Implicit title
2. - THE SOIL REMEMBERS                              → Pattern 1, Different dash
3. VARIATION 6 – INNER CLIMATE, OUTER CLIMATE       → Pattern 1, Explicit var num
4. 0 — SUPERLOVE AS COSMIC IMPERATIVE               → Pattern 1, Var 10 (0=10)
5. Variation 9 – PATTERN 9: SPEAKING IN SEEDS       → Pattern 9, Explicit pattern ref
```

### 3. Regex Requirements
- Handle dash types: `-` (hyphen), `–` (en-dash), `—` (em-dash), `−` (minus)
- Support uppercase titles with punctuation: "EARTH'S FEVER", "ONE FIELD, MANY SCALES"
- Convert "0" to "10" for variation numbering
- Validate implicit titles are mostly uppercase letters

## File Processing Flow

### 1. Directory Structure Expected
```
new_extractions/
  FOLDER_NAME/
    METAS/          # Meta documents
      *.docx
    STEP 2/         # Main content (preferred)
      *.docx
    *.docx          # Fallback if no STEP 2
```

### 2. Document Processing Order
1. Extract summary (first content before patterns)
2. Extract patterns (numbered: Pattern 1:, Pattern 2:, etc.)
3. Extract variations (various formats, link to patterns)
4. Link variations to patterns based on rules
5. Create lens from filename
6. Extract sources from patterns

## Airtable Sync Logic (IDEMPOTENT)

### 1. Duplicate Prevention System
- **ALWAYS** fetch existing records before sync
- **Match by unique fields**:
  - Patterns: `pattern_title`
  - Variations: `variation_title` 
  - Lenses: `lens_name`
  - Sources: `source_name`
  - Metas: `title`

### 2. Sync Actions
- **If record exists**: UPDATE (patch) to ensure fresh data
- **If record missing**: CREATE (post) new record
- **NEVER create duplicates**

### 3. Relationship Linking
- Link variations to their parent patterns
- Link patterns to lenses and sources
- Maintain referential integrity

## Code Architecture

### modules/data_extractor.py
- `extract_variations()`: Core variation parsing logic
- `extract_patterns()`: Pattern extraction
- `process_folder()`: Main orchestration
- **Key methods**: Clean text, handle multiple file formats

### modules/airtable_uploader.py
- `fetch_existing_records()`: Build duplicate prevention cache
- `_create_or_update()`: Smart upsert logic
- `sync_data()`: Main sync orchestration
- **Key feature**: Record mapping for duplicate prevention

### config/settings.py
- Airtable credentials and table mapping
- Directory paths
- Environment configuration

## Debugging Checklist

### When Variations Are Missing:
1. Check regex patterns in `extract_variations()`
2. Verify dash character handling
3. Confirm uppercase title validation
4. Check pattern reference logic
5. Verify file path in logs

### When Duplicates Occur:
1. Verify `fetch_existing_records()` is called
2. Check field matching logic in `_create_or_update()`
3. Confirm record cache is populated
4. Check for whitespace/case sensitivity in matches

### When Sync Fails:
1. Verify Airtable credentials in .env
2. Check table names in settings
3. Review field mappings
4. Check rate limiting (0.2s delays)

## Expected File Counts
- **Each file should have**: ~10 variations minimum
- **Empty variations arrays**: Indicates extraction failure
- **Missing variations in sync**: Check uploader logic

## Environment Setup
```
.env file required with:
AIRTABLE_API_TOKEN=your_token
AIRTABLE_BASE_ID=your_base_id
```

## Testing Strategy
1. Run extraction on single folder first
2. Check JSON output for variation counts
3. Verify no empty variation arrays (unless truly no variations)
4. Test sync with small dataset
5. Confirm no duplicates created
6. Validate all relationships linked correctly

## Performance Considerations
- Rate limiting: 0.2s between Airtable calls
- Batch operations where possible
- Log verbosely for debugging
- Handle network timeouts gracefully

## Success Metrics
- ✅ 10 variations per file (typical)
- ✅ Zero duplicates in Airtable
- ✅ All variations linked to correct patterns
- ✅ Complete relationship mapping
- ✅ Robust error handling

## Emergency Fixes
- If variations missing: Check regex patterns first
- If duplicates occurring: Verify fetch_existing_records()
- If sync failing: Check Airtable credentials
- If patterns wrong: Review linking logic

This guide ensures any AI can understand, debug, and maintain the system without context loss.