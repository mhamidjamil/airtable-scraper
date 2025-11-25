# Airtable Pattern Upload - Complete Project

## 📂 **Project Structure**

```
airtable_manager/
├── biome_extractor.py         # Extracts patterns from BIOME folder
├── pattern_document_processor.py  # Processes Google Docs
├── prepare_airtable_data.py   # CSV generation (deprecated)
│
├── airtable_api_upload/       # ✅ ACTIVE: API upload system
│   ├── generate_json.py        # Generate JSON from extraction
│   ├── upload_to_airtable.py   # Main upload script
│   ├── fix_variation_links.py  # Fix variation → pattern links
│   ├── verify_data.py          # Verify Airtable data
│   ├── inspect_schema.py       # Read Airtable schema
│   ├── config.json             # API credentials (gitignored)
│   ├── json_data/              # Generated JSON files
│   ├── logs/                   # Upload logs  
│   └── id_mappings/            # ID mapping files
│
├── docs/                       # All documentation
│   ├── API_UPLOAD_COMPLETE.md  # API system overview
│   ├── QUICK_START.md          # Fast setup guide
│   ├── README.md               # Detailed API setup
│   ├── AIRTABLE_IMPORT_STRATEGY_FINAL.md  # CSV strategy
│   ├── QUICK_START_IMPORT_GUIDE.md        # CSV guide
│   └── (other analysis docs)
│
├── data_output/                # Extraction outputs
└── csv_output/                 # CSV files (deprecated)
```

---

## 🚀 **Quick Start**

### **1. Extract Data from Google Docs**
```bash
cd airtable_manager
python biome_extractor.py
```
**Output:** `data_output/biome_extracted_YYYYMMDD_HHMMSS.json`

### **2. Generate API Upload JSONs**
```bash
cd airtable_api_upload
python generate_json.py
```
**Output:** 5 JSON files in `json_data/`
- lenses.json (5 records)
- sources.json (50 records)
- metas.json (5 records)
- variations.json (46 records)
- patterns.json (50 records)

### **3. Upload to Airtable**
```bash
# Setup config
cp config.json.template config.json
# Edit config.json with your API token and base ID

# Upload
python upload_to_airtable.py
```

### **4. Fix Variation Links (if needed)**
```bash
python fix_variation_links.py
```

### **5. Verify Upload**
```bash
python verify_data.py
```

---

## ✅ **What Was Uploaded**

### **Current Airtable State:**
- ✅ 5 Lenses (all linked)
- ✅ 50 Sources (all linked)
- ✅ 5 METAS
- ✅ 46 Variations (all linked to 10 patterns)
- ✅ 50 Patterns (with links to lenses, sources, variations)

**Note:** Only 10 of 50 patterns have variations:
- Pattern 1: 10 variations
- Pattern 11: 10 variations
- Pattern 21: 8 variations
- Pattern 31: 8 variations
- Pattern 41: 10 variations
- **Other 40 patterns:** No variations

---

## 📖 **Documentation**

### **For API Upload:**
- `docs/QUICK_START.md` - Fast 3-step setup
- `docs/README.md` - Detailed setup with troubleshooting
- `docs/API_UPLOAD_COMPLETE.md` - Complete system overview

### **For CSV Upload (Deprecated):**
- `docs/AIRTABLE_IMPORT_STRATEGY_FINAL.md` - CSV strategy
- `docs/QUICK_START_IMPORT_GUIDE.md` - CSV quick guide

---

## 🔑 **Configuration**

### **Required Credentials** (`config.json`):
```json
{
  "airtable_token": "patXXXXX...",
  "base_id": "appXXXXX..."
}
```

**Get credentials:** See `docs/QUICK_START.md`

---

## 🛠️ **Utilities**

### **Inspect Airtable Schema:**
```bash
python inspect_schema.py
```
Shows all tables and fields in your Airtable base.

### **Verify Upload:**
```bash
python verify_data.py
```
Checks if variations are linked to patterns.

### **Fix Variation Links:**
```bash
python fix_variation_links.py
```
Updates variations with pattern_reference links.

---

## 📝 **Workflow**

1. **Extract** → Run `biome_extractor.py`
2. **Generate JSON** → Run `generate_json.py`
3. **Upload** → Run `upload_to_airtable.py`
4. **Fix Links** → Run `fix_variation_links.py`
5. **Verify** → Run `verify_data.py`

---

## 🎯 **Key Features**

- ✅ Batch upload (10 records per batch)
- ✅ ID mapping system for relationships
- ✅ Automatic schema detection
- ✅ Comprehensive logging
- ✅ Error handling & retry logic
- ✅ Rate limiting (5 req/sec)
- ✅ UTF-8 encoding support

---

## 📊 **Data Flow**

```
Google Docs (BIOME folder)
    ↓
biome_extractor.py
    ↓
biome_extracted_*.json
    ↓
generate_json.py
    ↓
5 JSON files (lenses, sources, metas, variations, patterns)
    ↓
upload_to_airtable.py
    ↓
Airtable (Lenses → Sources → Metas → Variations → Patterns)
    ↓
fix_variation_links.py
    ↓
Verified in Airtable ✅
```

---

## 🐛 **Troubleshooting**

**"Unknown field name" error:**
→ Run `inspect_schema.py` to see actual Airtable fields
→ Upload script auto-adapts to your schema

**Variations not linked:**
→ Run `fix_variation_links.py`

**Unicode errors:**
→ All scripts use UTF-8 encoding

**Rate limit errors:**
→ Script auto-waits 0.2s between requests

---

## 📦 **Dependencies**

```bash
pip install requests
```

---

## 🙌 **Current Status**

✅ **Complete and Production-Ready!**
- All 5 tables uploaded
- All relationships linked
- Documentation complete
- Project organized

**Last Upload:** Check `logs/` folder for timestamp

---

For detailed setup instructions, see **`docs/QUICK_START.md`**
