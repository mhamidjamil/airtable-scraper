
# 📥 Airtable Import Instructions

## **Import Order (CRITICAL!)**

Import CSV files in this exact order to maintain relationships:

### **1. Import Lenses Table**
- File: `lenses.csv`
- Records: 5
- Fields: lens_name, content
- **No dependencies**

### **2. Import Sources Table**
- File: `sources.csv`
- Records: 50
- Fields: source_name
- **No dependencies**

### **3. Import METAS Table**
- File: `metas.csv`
- Records: 5
- Fields: title, subtitle, content, base_folder
- **Note:** linked_patterns field will be linked manually after Patterns are imported

### **4. Import Patterns Table**
- File: `patterns.csv`
- Records: 50
- Fields: pattern_title, base_folder, lens, sources, overview, choice, drive_doc_url
- **Link these fields during import:**
  - `lens` → Links to Lenses table (match by lens_name)
  - `sources` → Links to Sources table (match by source_name)
  - `_variation_count` is INFO ONLY (don't import this field)

### **5. Import Variations Table**
- File: `variations.csv`
- Records: 46
- Fields: variation_number, variation_title, content, linked_pattern
- **Link this field during import:**
  - `linked_pattern` → Links to Patterns table (match by pattern_title)

---

## **How to Import in Airtable**

1. **Open your Airtable base**

2. **For each table, click "+ Add or import" → "CSV file"**

3. **Upload the CSV file**

4. **Configure Field Types:**
   - Text fields: Use "Single line text" or "Long text" as appropriate
   - Link fields: Choose "Link to another record" and select target table

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

### **Verify Relationships:**
- Check that Patterns show linked Lens
- Check that Patterns show linked Sources
- Check that Variations show linked Pattern
- Check that variation counts match expectations

---

## **Data Summary**

- **METAS:** 5 organizing themes
- **Lenses:** 5 interpretive frameworks
- **Sources:** 50 unique attributions
- **Patterns:** 50 main content pieces
- **Variations:** 46 alternative formulations

**Base Folder:** BIOME
**Extraction Time:** 2025-11-25T17:11:28.572908

---

## **Known Issues to Review**

1. **METAS → Patterns mapping:** Currently unmapped (client input needed)
2. **drive_doc_url:** Empty (can be populated later if Google Docs are generated)
3. **Patterns without variations:** Some patterns may have no variations (this is normal)

---

✅ **CSV files are ready for import!**
