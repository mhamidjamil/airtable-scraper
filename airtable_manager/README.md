# Airtable Manager - Pattern Data Extraction & Upload System

## 📁 Folder Structure
```
airtable_manager/
├── README.md                          # This file
├── CONTEXT_FOR_AI.md                  # AI-readable project context
├── extract_patterns.py                # Main extraction script
├── prepare_airtable_data.py           # Prepares data for Airtable import
├── upload_to_airtable.py              # Uploads to Airtable (optional)
├── config.yaml                        # Configuration file
├── data_output/                       # Generated CSV/JSON files
│   ├── lenses.csv
│   ├── sources.csv
│   ├── metas.csv
│   ├── patterns.csv
│   └── variations.csv
└── logs/                              # Extraction logs
    └── extraction_YYYYMMDD_HHMMSS.log
```

## 🎯 Purpose
Professional system to extract pattern data from .docx files and prepare for Airtable import with:
- **5 tables**: Patterns, Lenses, Sources, Variations, METAS
- **Clean data**: Properly formatted CSV files
- **Full traceability**: Comprehensive logging
- **AI-friendly documentation**: Context files for future AI assistance

## 🔧 Usage

### Step 1: Extract Patterns from Folder
```bash
python extract_patterns.py --folder "E:\Work\shoaib\upwork\new_extractions\BIOME"
```

### Step 2: Prepare Airtable Data
```bash
python prepare_airtable_data.py
```

### Step 3: Import to Airtable
- Open Airtable
- Import CSV files from `data_output/` folder
- Follow import order: Lenses → Sources → METAS → Patterns → Variations

## 📊 Data Schema

### 1. **Lenses Table**
| Field | Type | Description |
|-------|------|-------------|
| lens_name | Text | Name of the lens (unique) |
| content | Long Text | Lens description |

### 2. **Sources Table**
| Field | Type | Description |
|-------|------|-------------|
| source_name | Text | Name of the source (unique) |

### 3. **METAS Table**
| Field | Type | Description |
|-------|------|-------------|
| title | Text | META title |
| subtitle | Text | META subtitle |
| content | Long Text | META content |
| base_folder | Text | Organizing folder |
| linked_patterns | Link | Links to Patterns table |

### 4. **Patterns Table**
| Field | Type | Description |
|-------|------|-------------|
| pattern_title | Text | Title of the pattern |
| base_folder | Text | Organizing folder (BIOME, BULLSHIT, etc.) |
| lens | Link | Links to Lenses table (single) |
| sources | Link | Links to Sources table (multiple) |
| overview | Long Text | Pattern overview/explanation |
| choice | Long Text | The choice/conflict text |
| drive_doc_url | URL | Google Drive document URL (optional) |
| variations | Link | Links to Variations table (multiple) |

### 5. **Variations Table**
| Field | Type | Description |
|-------|------|-------------|
| variation_title | Text | Title of the variation |
| variation_number | Number | Variation number (6-10 typically) |
| content | Long Text | Variation content |
| linked_pattern | Link | Links back to Patterns table (single) |

## ⚠️ Known Issues & Handling

### Issue 1: Variation Number Mismatch
**Problem:** Some files have variations numbered 6-10 instead of 1-5
**Handling:** Script preserves original variation numbers

### Issue 2: Missing Variation Titles
**Problem:** Some variations lack explicit titles
**Handling:** Script generates title from content or uses "Variation {number}"

### Issue 3: Implicit Variations
**Problem:** Variations marked only with "– TITLE" format
**Handling:** Script detects and auto-numbers sequential variations

### Issue 4: Pattern Reference Errors
**Problem:** Variation may reference wrong pattern number
**Handling:** Script links by document position, logs discrepancies

## 📝 Configuration

Edit `config.yaml` to customize:
```yaml
source_folder: "E:\\Work\\shoaib\\upwork\\new_extractions\\BIOME"
output_folder: "E:\\Work\\shoaib\\upwork\\airtable_manager\\data_output"
log_folder: "E:\\Work\\shoaib\\upwork\\airtable_manager\\logs"

# Which file types to process
process_metas: true
process_step2: true
process_step1: false

# Data validation
require_minimum_patterns: 1
require_summary: true
```

## 🤖 For AI Assistants
See `CONTEXT_FOR_AI.md` for comprehensive project context including:
- Data extraction rules
- Known parsing issues
- METAS mapping strategy
- Airtable schema relationships
