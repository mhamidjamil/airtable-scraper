# AI Context Document - Airtable Manager Project

> **Purpose:** This file provides complete context for AI assistants to understand the project, data structure, known issues, and processing rules.

---

## 📚 Project Overview

### **Goal**
Extract pattern data from .docx files in `new_extractions` folder and upload to Airtable with 5 related tables.

### **Data Source**
- **Root folder:** `E:\Work\shoaib\upwork\new_extractions\`
- **11 base folders:** AD FONTES, AI PERSONAS, BIOME, BULLSHIT, BUSINESS, DYNAMITE, FORMULAS + WELLGOS, PAULA, QUANTUM, WARS, WRITINGS
- **157 total .docx files** distributed across:
  - `METAS/` subfolders (54 files)
  - `STEP 2/` subfolders (most pattern files)
  - `STEP 1/` subfolders (some pattern files)

### **Target Schema (Airtable)**
5 interconnected tables:
1. **Lenses** (42 unique) - Interpretive frameworks
2. **Sources** (222 unique) - Source attributions
3. **METAS** (54 from METAS folders) - Organizing themes/topics
4. **Patterns** (420+) - Main content with lens, sources, METAS links
5. **Variations** (351+) - Alternative formulations of patterns

---

## 🔍 Document Structure

### **Typical Pattern Document (.docx)**
```
[TITLE/LENS NAME]

[SUMMARY SECTION - 2-5 paragraphs before "Pattern 1"]

Pattern 1: [Title]
Explanation: [Overview text]
Inner war / choice: [Choice text]
Sources: [Source attribution]

Pattern 2: [Title]
...

[Variations Section - typically after all patterns]

VARIATION 6 – PATTERN 1: [Variation Title]
[Variation content paragraph]

VARIATION 7 – PATTERN 1: [Variation Title]
[Variation content paragraph]
```

### **METAS Document (.docx)**
```
[META TITLE]

[META SUBTITLE or intro paragraph]

[BODY CONTENT - explains the meta-theme]
```

---

## ⚠️ Data Extraction Issues & Solutions

### **Issue 1: Variation Numbering**
**Problem:**
- Patterns are numbered 1-10
- Variations are often numbered 6-10 (not 1-5)
- Sometimes variations numbered 1-10, or 0-10 (0 = typo for 10)

**Regex Patterns Used:**
```python
# Format: "VARIATION 6 – PATTERN 1: Title"
r'^VARIATION\s+(\d+)\s*[–—-]\s*PATTERN\s+(\d+):\s*(.+)$'

# Format: "– PATTERN 5: Title" (missing variation number)
r'^\s*[–—-]\s*PATTERN\s+(\d+):\s*(.+)$'

# Format: "Variation 6 — Title" (no PATTERN)
r'^Variation\s+(\d+)\s*[–—-]\s*(.+)$'

# Format: "6 — Title" (just number)
r'^(\d+)\s*[–—-]\s*(.+)$'

# Format: "– UPPERCASE TITLE" (implicit)
r'^\s*[–—-]\s*([A-Z\s]+)$'
```

**Solution:**
- Preserve original variation numbers (don't renumber)
- Auto-detect format and extract number + title
- Handle special case: `0` → `10`

### **Issue 2: Pattern-Variation Linking**
**Problem:**
- Variation may say "PATTERN 5" but actually belongs to Pattern 3
- Implicit variations don't specify pattern number

**Solution:**
- Primary linking: Document position (sequential assignment)
- Secondary: Pattern reference number (logged but not enforced)
- Create `pattern_reference` field for debugging

### **Issue 3: Missing Summaries**
**Problem:**
- Some files have only title, no summary paragraph
- Some have 1-2 line summaries (too short)

**Validation Rules:**
```python
# Must have 2+ paragraphs OR 50+ characters
if len(summary_lines) >= 2 or len(summary) > 50:
    has_summary = True

# Skip files without valid summary
if not has_summary:
    log_skip(file, "No summary found")
```

### **Issue 4: Source Field Variations**
**Problem:**
- Sources can be: "Inner War / Choice", "HOME_SPINE", "HIGHLIGHTS: ...", etc.
- Some very long (200+ chars)
- Multiple formats in same document

**Solution:**
- Accept any text after "Sources:" label
- Clean and trim whitespace
- Store as-is (don't parse/split)
- Create unique Sources table entries

---

## 🗂️ METAS → Patterns Mapping Strategy

### **Client Guidance**
> "METAS as the main topic, the first column at left in Airtable"  
> "base_folder is for organizing, not querying"

### **Interpretation**
METAS are **cross-cutting themes** that organize patterns across base folders:
- METAS files are in `BIOME/METAS/`, `BULLSHIT/METAS/`, etc.
- Each META describes a thematic lens or organizing principle
- Multiple patterns from different folders can belong to same META

### **Current Status**
⚠️ **MANUAL MAPPING REQUIRED** - client must clarify how patterns link to METAS

**Options Under Consideration:**
1. **Folder-based:** All patterns in BIOME → BIOME's METAS
2. **Semantic:** AI matches pattern content to META content
3. **Client-provided:** Spreadsheet mapping pattern IDs to META IDs
4. **Embedded:** METAS files list pattern titles they cover

**Recommendation:** Extract METAS first, review content, ask client for clarification

---

## 📊 Extraction Rules & Logic

### **File Selection Priority**
```
For each base folder:
1. Check if "STEP 2" subfolder exists
   → YES: Process ONLY files in STEP 2
   → NO: Process files in base folder root
2. Skip: STEP 1, METAS (process separately), temp files (~$)
```

### **Pattern Extraction**
```python
# Start: "Pattern X: [Title]"
# Next 3 non-empty paragraphs:
#   1. Overview (after "Explanation:" label)
#   2. Choice (after "Inner war / choice:" label)
#   3. Source (after "Sources:" label)
# Stop: Next "Pattern X" or "Variation X" detected
```

### **Variation Extraction**
```python
# Detect start with multiple regex patterns (see Issue 1)
# Extract: variation_number, title, pattern_reference
# Next non-empty paragraph = content
# Stop: Next pattern/variation detected
```

### **METAS Extraction**
```python
# Title: Filename (without .docx)
# Subtitle: First paragraph after title
# Content: Remaining paragraphs (full text)
# base_folder: Parent folder name
```

---

## 🔗 Relational Data Structure

### **Import Order (Critical!)**
```
1. Lenses (no dependencies)
2. Sources (no dependencies)
3. METAS (no dependencies)
4. Patterns (links to: Lenses, Sources, METAS)
5. Variations (links to: Patterns)
```

### **Linking Logic**
```python
# Patterns → Lens (1:1)
pattern["lens_id"] = lookup_lens_id(pattern["lens_name"])

# Patterns → Sources (1:Many)
pattern["source_ids"] = [lookup_source_id(s) for s in pattern["sources"]]

# Patterns → METAS (1:Many) ⚠️ TBD
pattern["meta_ids"] = [...] # Strategy unclear

# Variations → Pattern (1:1)
variation["pattern_id"] = lookup_pattern_id(variation["pattern_title"])
```

---

## 📁 File Naming Conventions

### **METAS Files**
Examples from BIOME/METAS/:
- `From Users to Gardeners, From Profiles to Landscapes The Grammatical Shift.docx`
- `The War Is Grammatical Why the Mental Health Crisis Is Really a Linguistic.docx`

**Pattern:** Descriptive titles, often long, no standard prefix

### **Pattern Files (STEP 2)**
Examples from BIOME/STEP 2/:
- `BELOVED BANG.docx`
- `Convivencia, Philoxenia & Emotional Hosting.docx`
- `GEN G Grace, Garden & Generative Generation.docx`

**Pattern:** Title = Lens name (used as lens_name in Lenses table)

---

## 🎯 Quality Validation

### **Must-Have Checks**
```python
✅ Has summary (2+ paragraphs or 50+ chars)
✅ Has at least 1 pattern
✅ Lens name extracted (from filename)
✅ base_folder identified (from path)
✅ No duplicate variation numbers within same pattern
```

### **Should-Have Warnings**
```python
⚠️ Pattern without variations (acceptable but log)
⚠️ Variation referencing non-existent pattern number
⚠️ Summary unusually long (>2000 chars)
⚠️ Pattern missing overview/choice/source fields
```

---

## 🔄 Processing Workflow

### **Phase 1: Extraction (Current)**
```
Input: E:\Work\shoaib\upwork\new_extractions\BIOME\
Process: Extract patterns, variations, lens, sources
Output: biome_extracted.json
```

### **Phase 2: Normalization**
```
Input: biome_extracted.json
Process: Create unique Lenses list, Sources list
Output: lenses.csv, sources.csv
```

### **Phase 3: METAS Processing** ⚠️ Pending
```
Input: E:\Work\shoaib\upwork\new_extractions\BIOME\METAS\
Process: Extract METAS data
Question: How to link to patterns?
Output: metas.csv (with pattern_ids TBD)
```

### **Phase 4: Relational Linking**
```
Input: All CSVs
Process: Replace names with IDs for FK relationships
Output: patterns.csv (with lens_id, source_ids, meta_ids)
        variations.csv (with pattern_id)
```

### **Phase 5: Airtable Import**
```
Order: Lenses → Sources → METAS → Patterns → Variations
Method: CSV import via Airtable UI or API
```

---

## 🛠️ Tools & Scripts

### **Current Scripts**
1. `pattern_to_json/extract_new_patterns.py` - Original batch extractor
2. `airtable_manager/extract_patterns.py` - New focused extractor
3. `airtable_manager/prepare_airtable_data.py` - CSV generator

### **Dependencies**
```python
python-docx  # Read .docx files
pyyaml       # Config files
pandas       # CSV generation (optional)
pyairtable   # API upload (optional, future)
```

---

## 📝 Example Data

### **Lens Record**
```json
{
  "lens_name": "Greek's Overflow Vocabulary vs. Scarcity Capitalism",
  "content": "Summary text from file..."
}
```

### **Pattern Record**
```json
{
  "pattern_title": "Grace Doesn't Fill the Cup, It Floods the Valley",
  "base_folder": "AD FONTES",
  "lens": "Greek's Overflow Vocabulary vs. Scarcity Capitalism",
  "sources": ["Inner War / Choice"],
  "overview": "Greek does not speak in measured portions...",
  "choice": "Scarcity capitalism trains us...",
  "drive_doc_url": "",
  "variations": [6, 7, 8, 9, 10]
}
```

### **Variation Record**
```json
{
  "variation_number": 6,
  "variation_title": "From Cups to Valleys — A Shift in Spiritual Imagination",
  "content": "Most of us were taught to pray for God to fill our cup...",
  "linked_pattern": "Grace Doesn't Fill the Cup, It Floods the Valley"
}
```

---

## 🚨 Critical Unknowns (Client Input Needed)

1. **METAS Mapping:** How do patterns link to METAS?
2. **Google Drive URLs:** Should we generate docs and upload to Drive?
3. **base_folder Usage:** Keep in Patterns table or remove?
4. **Variation Numbering:** Preserve originals (6-10) or renumber (1-5)?
5. **Source Parsing:** Split long source strings or keep as-is?

---

## 💡 AI Assistant Guidelines

When helping with this project:
1. **Check this file first** for context
2. **Preserve variation numbers** as extracted
3. **Log don't fail** - log issues, don't crash extraction
4. **Maintain relationships** - track FK integrity
5. **Document decisions** - update this file with new learnings

---

**Last Updated:** 2025-11-25  
**Version:** 1.0  
**Status:** Active Development - METAS mapping pending client clarification
