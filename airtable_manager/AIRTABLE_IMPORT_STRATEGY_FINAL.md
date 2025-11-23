# 📋 AIRTABLE IMPORT STRATEGY - FINAL PROFESSIONAL VERSION

## 🎯 **Understanding Airtable Relationships**

### **How Airtable Linked Records Work:**

When you create a link from Table A → Table B:
- Table A has a **Link field** pointing to Table B records
- Table B **automatically** gets a reverse link showing which A records link to it

**Example:**
- If **Pattern 1** links to **Lens "BELOVED BANG"**
- Then **Lens "BELOVED BANG"** automatically shows it's linked from **Pattern 1**
- You DON'T need to manually add Pattern 1 to the Lens record!

### **This Means:**
❌ **We DON'T need `patterns` field in Lenses CSV**
❌ **We DON'T need `patterns` field in Sources CSV**
✅ **Airtable will create these automatically as reverse links!**

---

## 🏗️ **Final Table Structure**

### **Table 1: Lenses**
| Field Name | Type | Description |
|------------|------|-------------|
| `lens_name` | Primary Field | Name of the lens |
| `content` | Long text | Lens description/summary |
| ~~`patterns`~~ | ~~Auto-generated~~ | **REMOVED** - Airtable creates this automatically |

### **Table 2: Sources**
| Field Name | Type | Description |
|------------|------|-------------|
| `source_name` | Primary Field | Name of the source |
| ~~`patterns`~~ | ~~Auto-generated~~ | **REMOVED** - Airtable creates this automatically |

### **Table 3: METAS**
| Field Name | Type | Description |
|------------|------|-------------|
| `title` | Primary Field | META title |
| `subtitle` | Long text | META subtitle |
| `content` | Long text | META full content |
| `base_folder` | Single select | BIOME, BULLSHIT, etc. |
| `linked_patterns` | Link to Patterns | Links to Patterns table (many) |

### **Table 4: Patterns**
| Field Name | Type | Description |
|------------|------|-------------|
| `pattern_id` | Single line text | Unique ID (P001, P002, etc.) |
| `pattern_title` | Primary Field | Title of the pattern |
| `base_folder` | Single select | BIOME, BULLSHIT, etc. |
| `lens` | Link to Lenses | Links to Lenses table (single) |
| `sources` | Link to Sources | Links to Sources table (single/multiple) |
| `overview` | Long text | Pattern overview/explanation |
| `choice` | Long text | The choice/conflict text |
| `drive_doc_url` | URL | Google Drive URL (optional) |
| `metas` | Link to METAS | **Auto-generated** reverse link from METAS |

### **Table 5: Variations**
| Field Name | Type | Description |
|------------|------|-------------|
| `variation_number` | Number | Variation number (6-10) |
| `variation_title` | Primary Field | Title of the variation |
| `content` | Long text | Variation content |
| `linked_pattern` | Link to Patterns | Links to Patterns table (single) |

---

## 📦 **Import Order (CRITICAL!)**

### **Step 1: Import Lenses** ✅
**File:** `lenses.csv`
**Fields:** `lens_name`, `content`

```
1. Create "Lenses" table
2. Import CSV
3. Set field types:
   - lens_name: Primary field (Single line text)
   - content: Long text
```

**Result:** 5 Lens records created

---

### **Step 2: Import Sources** ✅
**File:** `sources.csv`
**Fields:** `source_name`

```
1. Create "Sources" table
2. Import CSV
3. Set field types:
   - source_name: Primary field (Single line text)
```

**Result:** 70 Source records created

---

### **Step 3: Import METAS** ✅
**File:** `metas.csv`
**Fields:** `title`, `subtitle`, `content`, `base_folder`
**Skip:** `linked_patterns` (will link later)

```
1. Create "METAS" table
2. Import CSV
3. Set field types:
   - title: Primary field (Single line text)
   - subtitle: Long text
   - content: Long text
   - base_folder: Single select (or Single line text)
4. IGNORE "linked_patterns" column during import
```

**Result:** 5 META records created (no pattern links yet)

---

### **Step 4: Import Patterns** ⭐ **CRITICAL STEP**
**File:** `patterns.csv`
**Fields:** `pattern_id`, `pattern_title`, `base_folder`, `lens`, `sources`, `overview`, `choice`, `drive_doc_url`

```
1. Create "Patterns" table
2. Import CSV
3. Set field types DURING IMPORT:
   - pattern_id: Single line text
   - pattern_title: Primary field (Single line text)
   - base_folder: Single select (or Single line text)
   - lens: 🔗 Link to another record → SELECT "Lenses" table
   - sources: 🔗 Link to another record → SELECT "Sources" table
   - overview: Long text
   - choice: Long text
   - drive_doc_url: URL

4. When mapping the "lens" field:
   - Choose: "Link to Lenses table"
   - Match by: "lens_name" column

5. When mapping the "sources" field:
   - Choose: "Link to Sources table"
   - Match by: "source_name" column
```

**Result:** 50 Pattern records created, linked to Lenses and Sources

**✅ After this step:**
- Patterns will show their linked Lens
- Patterns will show their linked Source(s)
- **Lenses will automatically show which Patterns link to them**
- **Sources will automatically show which Patterns link to them**

---

### **Step 5: Import Variations** ✅
**File:** `variations.csv`
**Fields:** `variation_number`, `variation_title`, `content`, `linked_pattern`

```
1. Create "Variations" table
2. Import CSV
3. Set field types DURING IMPORT:
   - variation_number: Number
   - variation_title: Primary field (Single line text)
   - content: Long text
   - linked_pattern: 🔗 Link to another record → SELECT "Patterns" table

4. When mapping "linked_pattern":
   - Choose: "Link to Patterns table"
   - Match by: "pattern_title" column
```

**Result:** 46 Variation records created, linked to Patterns

**✅ After this step:**
- Variations will show their linked Pattern
- **Patterns will automatically show their linked Variations**

---

### **Step 6: Link METAS to Patterns** 🖱️ **MANUAL STEP**

Now that Patterns exist, link them to METAS:

```
1. Open METAS table
2. Add a new field: "linked_patterns"
   - Type: Link to another record
   - Link to: Patterns table
   - Allow linking to multiple records: YES

3. For each META record:
   - Click on the "linked_patterns" field
   - Search and select patterns that belong to this META
   - (Ask client which patterns belong to which METAS)

4. After linking:
   - METAS show their linked Patterns
   - Patterns automatically show which METAS they belong to
```

---

## 🎨 **Professional Airtable Setup Tips**

### **Field Types Recommendations:**

1. **Primary Fields:**
   - Lenses: `lens_name`
   - Sources: `source_name`
   - METAS: `title`
   - Patterns: `pattern_title`
   - Variations: `variation_title`

2. **Single Select vs Single Line Text:**
   - `base_folder`: Use **Single select** with options: BIOME, BULLSHIT, BUSINESS, etc.
   - This gives you filtering and grouping capabilities

3. **Link Field Settings:**
   - `lens` in Patterns: Allow linking to **single record** only
   - `sources` in Patterns: Allow linking to **multiple records**
   - `linked_patterns` in METAS: Allow linking to **multiple records**
   - `linked_pattern` in Variations: Allow linking to **single record** only

4. **Reverse Link Field Names:**
   After import, Airtable will create these automatically:
   - In Lenses: "Patterns" (shows which patterns use this lens)
   - In Sources: "Patterns" (shows which patterns use this source)
   - In Patterns: "Variations" (shows variations of this pattern)
   - In Patterns: "METAS" (shows which METAS this pattern belongs to)

### **Views to Create:**

1. **Patterns Table:**
   - View by Lens (group by `lens` field)
   - View by Base Folder (group by `base_folder`)
   - View by META (filter by `METAS` link)

2. **Lenses Table:**
   - Shows count of linked patterns automatically

3. **METAS Table:**
   - Shows count of linked patterns automatically

---

## 📝 **Updated CSV Files Needed**

I will regenerate these CSV files:

1. ✅ `lenses.csv` - **REMOVE** `patterns` field
2. ✅ `sources.csv` - **REMOVE** `patterns` field
3. ✅ `metas.csv` - **REMOVE** `linked_patterns` field (add manually after import)
4. ✅ `patterns.csv` - Keep as is
5. ✅ `variations.csv` - Keep as is

---

## 🔄 **Why This Works**

### **One-Way Links in CSV, Two-Way in Airtable:**

When you import:
```csv
Pattern A → links to → Lens B
```

Airtable automatically creates:
```
Pattern A ←→ Lens B
```

So you only need to specify the link in ONE direction during import!

### **Import Order Matters:**

```
Lenses ✅ (no dependencies)
  ↓
Sources ✅ (no dependencies)
  ↓
METAS ✅ (no dependencies)
  ↓
Patterns ⭐ (links to Lenses + Sources)
  ↓
Variations ✅ (links to Patterns)
  ↓
Manual: Link METAS → Patterns 🖱️
```

---

## ✅ **Final Checklist**

### **Before Import:**
- [ ] Download updated CSV files (without `patterns` field in Lenses/Sources)
- [ ] Have Airtable base ready
- [ ] Understand link field types

### **During Import:**
- [ ] Import in correct order (Lenses → Sources → METAS → Patterns → Variations)
- [ ] Set link fields during Pattern import
- [ ] Match by correct column names

### **After Import:**
- [ ] Verify Patterns show linked Lenses
- [ ] Verify Lenses show reverse links to Patterns
- [ ] Verify Sources show reverse links to Patterns
- [ ] Manually link METAS to Patterns
- [ ] Create useful views

---

## 🚨 **Common Mistakes to Avoid**

1. ❌ **Don't** try to import the `patterns` field in Lenses/Sources
2. ❌ **Don't** try to import `linked_patterns` in METAS
3. ❌ **Don't** forget to set link field types during Pattern import
4. ❌ **Don't** import in wrong order
5. ✅ **DO** let Airtable create reverse links automatically

---

## 📞 **Need Help?**

If import fails:
1. Check you're using updated CSV files (no `patterns` in Lenses/Sources)
2. Verify field type mapping during import
3. Make sure you're matching by correct column names
4. Import one table at a time, verify before moving to next

---

**Status:** ✅ Ready for professional Airtable import
**Last Updated:** 2025-11-25
