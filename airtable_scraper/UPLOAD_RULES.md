# 🚀 AIRTABLE UPLOAD RULES & SEQUENCE

## 📋 **CRITICAL UPLOAD ORDER (MUST BE FOLLOWED)**

### **❗ MANDATORY SEQUENCE:**
1. **METAS first** (no dependencies)
2. **LENSES second** (no dependencies) 
3. **SOURCES third** (no dependencies)
4. **VARIATIONS fourth** (requires patterns for linking)
5. **PATTERNS last** (links to all above tables)

### **🔗 WHY THIS ORDER MATTERS:**
- Patterns link to: Metas, Lenses, Sources, Variations
- If we upload Patterns first, the linked records don't exist yet
- Variations need Patterns for `pattern_reference` linking
- This sequence ensures all dependencies exist before linking

---

## 🗂️ **AIRTABLE SCHEMA (FIELD MAPPING)**

### **Table 1: Metas**
| Field Name in Airtable | Python Data Field | Type |
|------------------------|-------------------|------|
| `title` (Primary) | `meta.title` | Single line text |
| `subtitle` | `meta.subtitle` | Long text |
| `content` | `meta.content` | Long text |
| `base_folder` | `meta.base_folder` | Single line text |
| `linked_patterns` | Auto-generated | Link to Patterns |

### **Table 2: Lenses**
| Field Name in Airtable | Python Data Field | Type |
|------------------------|-------------------|------|
| `lens_name` (Primary) | `doc.lens` | Single line text |
| `content` | `doc.summary` | Long text |
| `Patterns` | Auto-generated | Link to Patterns |

### **Table 3: Sources**
| Field Name in Airtable | Python Data Field | Type |
|------------------------|-------------------|------|
| `content` (Primary) | `source.source` | Long text |
| `lense` | `source.lens` | Single line text |
| `base_folder` | `source.base_folder` | Single select |
| `Patterns` | Auto-generated | Link to Patterns |

### **Table 4: Variations**
| Field Name in Airtable | Python Data Field | Type |
|------------------------|-------------------|------|
| `variation_title` (Primary) | `variation.title` | Single line text |
| `content` | `variation.content` | Long text |
| `pattern_reference` | Link to Pattern | Link to Patterns |
| `lense_link` | Link to Lens | Link to Lenses |
| `base_folder` | `variation.base_folder` | Single select |
| `lens` | `variation.lens` | Single line text |

### **Table 5: Patterns**
| Field Name in Airtable | Python Data Field | Type |
|------------------------|-------------------|------|
| `pattern_title` (Primary) | `pattern.title` | Single line text |
| `base_folder` | `pattern.base_folder` | Single select |
| `lens` | Link to Lens record | Link to Lenses |
| `sources` | Link to Source records | Link to Sources |
| `overview` | `pattern.overview` | Long text |
| `choice` | `pattern.choice` | Long text |
| `variations` | Auto-generated | Link to Variations |
| `Metas` | Link to Meta records | Link to Metas |

---

## 🔄 **LINKING RELATIONSHIPS**

### **Forward Links (We Create These):**
- **Patterns** → **Lenses** (via `lens` field)
- **Patterns** → **Sources** (via `sources` field)  
- **Patterns** → **Metas** (via `Metas` field)
- **Variations** → **Patterns** (via `pattern_reference` field)
- **Variations** → **Lenses** (via `lense_link` field)

### **Reverse Links (Airtable Creates Automatically):**
- **Lenses** → **Patterns** (auto-generated `Patterns` field)
- **Lenses** → **Variations** (auto-generated reverse link from `lense_link`)
- **Sources** → **Patterns** (auto-generated `Patterns` field)
- **Metas** → **Patterns** (auto-generated `linked_patterns` field)
- **Patterns** → **Variations** (auto-generated `variations` field)

---

## ⚠️ **CURRENT ISSUES IDENTIFIED**

### **Problem 1: Wrong Upload Order**
```python
# CURRENT (WRONG):
sync_data() uploads: lenses → metas → patterns+variations → sources

# REQUIRED (CORRECT):
sync_data() uploads: metas → lenses → sources → variations → patterns
```

### **Problem 2: Missing Field Mappings**
```python
# WRONG field names being used:
"lens_title" → should be "lens_name" 
"meta_title" → should be "title"

# Missing critical links:
Patterns missing links to: Metas, Lenses, Sources
```

### **Problem 3: No Dependency Validation**
- Code uploads patterns before their dependencies exist
- No validation that linked records exist before creating links

---

## 🛠️ **REQUIRED FIXES**

### **Fix 1: Correct Upload Sequence**
```python
def sync_data(self, data: Dict, sync_types: List[str] = None, enable_linking: bool = False):
    # 1. METAS first
    if "metas" in sync_types:
        self._sync_metas(data)
    
    # 2. LENSES second  
    if "lenses" in sync_types:
        self._sync_lenses(data)
    
    # 3. SOURCES third
    if "sources" in sync_types:
        self._sync_sources(data)
        
    # 4. VARIATIONS fourth (needs patterns for linking)
    if "variations" in sync_types:
        self._sync_variations(data, enable_linking)
        
    # 5. PATTERNS last (links to all above)
    if "patterns" in sync_types:
        self._sync_patterns(data, enable_linking)
```

### **Fix 2: Correct Field Mappings**
```python
# METAS:
fields = {
    "title": meta.get("title"),           # NOT "meta_title"
    "subtitle": meta.get("subtitle"),
    "content": meta.get("content"),
    "base_folder": meta.get("base_folder")  # Single line text (e.g., "BULLSHIT")
}

# LENSES:
fields = {
    "lens_name": lens_name,               # NOT "lens_title"  
    "content": doc.get("summary")         # NOT missing
}
```

### **Fix 3: Proper Linking**
```python
# PATTERNS must link to:
if enable_linking:
    # Link to Lens
    lens_id = self.get_record_id("lenses", lens_name)
    if lens_id:
        fields["lens"] = [lens_id]
    
    # Link to Sources  
    source_ids = self.get_source_ids_for_pattern(pattern_sources)
    if source_ids:
        fields["sources"] = source_ids
        
    # Link to Metas
    meta_ids = self.get_meta_ids_for_pattern(pattern)
    if meta_ids:
        fields["Metas"] = meta_ids
```

---

## 🎯 **SUCCESS CRITERIA**

After running: `python main.py --folder "BULLSHIT"`

### **Expected Results:**
1. ✅ **Metas table**: All meta records uploaded with correct field names
2. ✅ **Lenses table**: All lens records uploaded with correct field names  
3. ✅ **Sources table**: All source records uploaded with correct field names
4. ✅ **Variations table**: All variations uploaded with `pattern_reference` links
5. ✅ **Patterns table**: All patterns uploaded with links to Metas, Lenses, Sources

### **Verification Commands:**
```bash
# Test individual table uploads:
python main.py --folder "BULLSHIT" --metas --sync
python main.py --folder "BULLSHIT" --lenses --sync  
python main.py --folder "BULLSHIT" --sources --sync
python main.py --folder "BULLSHIT" --variations --sync
python main.py --folder "BULLSHIT" --patterns --sync

# Test full upload:
python main.py --folder "BULLSHIT" --sync
```

---

## 📝 **NOTES FOR AI AGENTS**

- This file contains the definitive upload rules and schema
- Any changes to upload logic MUST update this file
- Always check this file before modifying airtable_uploader.py
- Upload order is CRITICAL - never change the sequence
- Field names MUST match Airtable schema exactly

---

**Last Updated:** 2025-11-28  
**Status:** 🚨 NEEDS IMPLEMENTATION  
**Priority:** HIGH - Upload system currently broken