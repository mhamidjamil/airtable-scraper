# ⚡ QUICK START - Upload to Airtable

## ✅ **JSON Files Ready!**

You already generated:
```
✓ lenses.json (5 records)
✓ sources.json (50 records)
✓ metas.json (5 records)
✓ variations.json (46 records)
✓ patterns.json (50 records)
```

---

## 🚀 **3 Steps to Upload**

### **STEP 1: Get Airtable Credentials** (2 minutes)

**A) Personal Access Token:**
1. Go to: https://airtable.com/create/tokens
2. Click "Create new token"
3. Name: `Pattern Upload`
4. Scopes: ✅ `data.records:read` ✅ `data.records:write`
5. Access: Select your base
6. **Copy token** (starts with `pat...`)

**B) Base ID:**
1. Open your Airtable base
2. URL: `https://airtable.com/appXXXXXXXXXXXXXX/...`
3. **Copy the `appXXXX...` part**

---

### **STEP 2: Create Airtable Tables** (3 minutes)

Create 5 tables in Airtable:

**1. Lenses**
- `lens_name` (Primary, Single line text)
- `content` (Long text)
- `patterns` (Long text)

**2. Sources**
- `source_name` (Primary, Single line text)
- `patterns` (Long text)

**3. METAS**
- `title` (Primary, Single line text)
- `subtitle` (Long text)
- `content` (Long text)
- `base_folder` (Single line text)
- `patterns` (Long text)

**4. Variations**
- `variation_title` (Primary, Single line text)
- `variation_number` (Number)
- `content` (Long text)

**5. Patterns**
- `pattern_id` (Single line text)
- `pattern_title` (Primary, Single line text)
- `overview` (Long text)
- `choice` (Long text)
- `base_folder` (Single line text)
- `drive_doc_url` (URL)
- `lens` (Link to Lenses)
- `sources` (Link to Sources - allow multiple)
- `variations` (Link to Variations - allow multiple)

---

### **STEP 3: Configure & Upload** (1 minute)

**A) Create config file:**
```bash
cp config.json.template config.json
```

**B) Edit config.json:**
```json
{
  "airtable_token": "patABC123YOUR_TOKEN",
  "base_id": "appXYZ456YOUR_BASE_ID"
}
```

**C) Install dependency:**
```bash
pip install requests
```

**D) Upload!**
```bash
python upload_to_airtable.py
```

---

## 🎯 **What Happens**

```
1. Uploading Lenses... ✓ (saves ID mapping)
2. Uploading Sources... ✓ (saves ID mapping)
3. Uploading METAS... ✓ (saves ID mapping)
4. Uploading Variations... ✓ (saves ID mapping)
5. Uploading Patterns... ✓ (links to all above!)
```

**Logs saved to:** `logs/upload_YYYYMMDD_HHMMSS.log`

---

## ✅ **Verify Success**

Open Airtable:

1. **Lenses table** → 5 lenses with pattern lists
2. **Sources table** → 50 sources with pattern lists
3. **METAS table** → 5 METAS with pattern lists
4. **Patterns table** → 50 patterns **linked** to Lenses, Sources, Variations
5. **Variations table** → 46 variations **linked** back to Patterns

**Magic:** Airtable automatically creates reverse link fields showing which patterns use each lens/source!

---

## ❓ **Troubleshooting**

**"config.json not found"**
→ Copy template: `cp config.json.template config.json`

**"Table not found"**
→ Create tables in Airtable with exact names

**"Missing credentials"**
→ Check token starts with `pat` and base ID starts with `app`

---

**Time to complete:** ~5-10 minutes
**Result:** All data in Airtable with proper relationships! 🎉

**See README.md for detailed instructions.**
