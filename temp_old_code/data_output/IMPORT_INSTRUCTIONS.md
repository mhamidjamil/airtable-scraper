
# 📥 Airtable Import Instructions

## **Import Order (CRITICAL!)**

Import CSV files in this exact order to maintain relationships:

### **1. Import Lenses Table**
- File: `lenses.csv`
- Records: 5
- Fields: 
  - `lens_name` - Name of the lens
  - `content` - Lens description/summary
  - `patterns` - **Comma-separated list** of patterns using this lens (informational)
- **No dependencies**

### **2. Import Sources Table**
- File: `sources.csv`
- Records: 50
- Fields: 
  - `source_name` - Name of the source
  - `patterns` - **Comma-separated list** of patterns using this source (informational)
- **No dependencies**

### **3. Import METAS Table**
- File: `metas.csv`
- Records: 5
- Fields:
  - `title` - META title
  - `subtitle` - META subtitle
  - `content` - META full content
  - `base_folder` - Organizing folder (BIOME, BULLSHIT, etc.)
  - `linked_patterns` - **Empty for now** - Link manually after Patterns import

### **4. Import Patterns Table**
- File: `patterns.csv`
- Records: 50
- Fields:
  - `pattern_id` - Unique pattern ID (P001, P002, etc.)
  - `pattern_title` - Title of the pattern
  - `base_folder` - Organizing folder
  - `lens` - Links to Lenses table (match by lens_name)
  - `sources` - Links to Sources table (match by source_name)
  - `overview` - Pattern overview/explanation
  - `choice` - The choice/conflict text
  - `drive_doc_url` - Google Drive URL (empty for now)
- **Link these fields during import:**
  - `lens` → Links to Lenses table (single link)
  - `sources` → Links to Sources table (single link for now)

### **5. Import Variations Table**
- File: `variations.csv`
- Records: 49
- Fields:
  - `variation_number` - Variation number (6-10 typically)
  - `variation_title` - Title of the variation
  - `content` - Variation content
  - `linked_pattern` - Links to Patterns table (match by pattern_title)
- **Link this field during import:**
  - `linked_pattern` → Links to Patterns table (single link)

---

## **How to Import in Airtable**

1. **Open your Airtable base**

2. **For each table, click "+ Add or import" → "CSV file"**

3. **Upload the CSV file**

4. **Configure Field Types:**
   - Text fields: Use "Single line text" or "Long text" as appropriate
   - Link fields: Choose "Link to another record" and select target table
   - The "patterns" field in Lenses and Sources is informational (use Long text)

5. **Match Fields:**
   - Airtable will try to auto-match column names
   - Verify the field mapping is correct

6. **Import!**

---

## **After Import**

### **Link METAS to Patterns:**
- Go to METAS table
- Click on a META record  
- In `linked_patterns` field, search for patterns that belong to this META
- ⚠️ **MANUAL STEP:** Client must clarify which patterns belong to which METAS

### **Note on Pattern Lists:**
- Lenses and Sources CSV files include a "patterns" field
- This is **informational only** - shows which patterns use each lens/source
- Not a link field - just comma-separated text for reference

### **Verify Relationships:**
- Check that Patterns show linked Lens
- Check that Patterns show linked Sources
- Check that Variations show linked Pattern
- Check that pattern IDs are unique (P001-P050)

---

## **Data Summary**

- **METAS:** 5 organizing themes
- **Lenses:** 5 interpretive frameworks
- **Sources:** 50 unique attributions
- **Patterns:** 50 main content pieces
- **Variations:** 49 alternative formulations

**Base Folder:** BIOME
**Extraction Time:** 2025-11-26T16:04:20.016592

---

## **Known Issues to Review**

1. **METAS → Patterns mapping:** Currently unmapped (client input needed)
2. **drive_doc_url:** Empty (can be populated later if Google Docs are generated)
3. **Patterns without variations:** Some patterns may have no variations (this is normal)
4. **Pattern lists in Lenses/Sources:** Informational only, not link fields

---

✅ **CSV files are ready for import!**
