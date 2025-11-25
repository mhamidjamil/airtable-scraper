# 🚀 Airtable API Upload Guide

## 📋 **What This Does**

Uploads your extracted pattern data to Airtable using the API with proper relationship linking.

**Upload Order:**
```
Lenses → Sources → METAS → Variations → Patterns
```

---

## 🔑 **Step 1: Get Airtable Credentials**

### **A) Get Your Personal Access Token**

1. Go to https://airtable.com/create/tokens
2. Click **"Create new token"**
3. Name it: `Pattern Upload`
4. Under **Scopes**, select:
   - ✅ `data.records:read`
   - ✅ `data.records:write`
5. Under **Access**, select your base
6. Click **"Create token"**
7. **Copy the token** (starts with `pat...`)

### **B) Get Your Base ID**

1. Open your Airtable base
2. Look at the URL: `https://airtable.com/appXXXXXXXXXXXXXX/...`
3. Copy the part that starts with `app` (e.g., `appABC123DEF456`)

---

## ⚙️ **Step 2: Create Your Airtable Tables**

Create 5 tables in your Airtable base with these **exact names**:

### **1. Lenses**
Fields:
- `lens_name` (Single line text) - Primary field
- `content` (Long text)
- `patterns` (Long text) - For pattern list

### **2. Sources**
Fields:
- `source_name` (Single line text) - Primary field
- `patterns` (Long text) - For pattern list

### **3. METAS**
Fields:
- `title` (Single line text) - Primary field
- `subtitle` (Long text)
- `content` (Long text)
- `base_folder` (Single line text)
- `patterns` (Long text) - For pattern list

### **4. Variations**
Fields:
- `variation_title` (Single line text) - Primary field
- `variation_number` (Number)
- `content` (Long text)
- `linked_pattern` (Link to Patterns) - **Will be created automatically**

### **5. Patterns**
Fields:
- `pattern_id` (Single line text)
- `pattern_title` (Single line text) - Primary field
- `overview` (Long text)
- `choice` (Long text)
- `base_folder` (Single line text)
- `drive_doc_url` (URL)
- `lens` (Link to Lenses)
- `sources` (Link to Sources) - Allow linking to multiple
- `variations` (Link to Variations) - Allow linking to multiple

---

## 🔧 **Step 3: Configure Upload Script**

1. **Copy config template:**
   ```bash
   cp config.json.template config.json
   ```

2. **Edit `config.json`:**
   ```json
   {
     "airtable_token": "patABC123...",
     "base_id": "appXYZ456..."
   }
   ```

3. **Install dependencies:**
   ```bash
   pip install requests
   ```

---

## ▶️ **Step 4: Run Upload**

Upload to Airtable:
```bash
python upload_to_airtable.py
```

**What Happens:**

1. ✅ Uploads 5 Lenses → Saves ID mapping
2. ✅ Uploads 50 Sources → Saves ID mapping
3. ✅ Uploads 5 METAS → Saves ID mapping
4. ✅ Uploads 46 Variations → Saves ID mapping
5. ✅ Uploads 50 Patterns → Links to all above using IDs

**Output:**
- Logs saved to `logs/upload_YYYYMMDD_HHMMSS.log`
- ID mappings saved to `id_mappings/` folder

---

## ✅ **Step 5: Verify in Airtable**

1. **Open Lenses table**
   - Should see 5 lenses
   - `patterns` field shows pattern titles (text)
   - After Patterns upload: **automatic reverse link field** created showing actual pattern records

2. **Open Sources table**
   - Should see 50 sources
   - `patterns` field shows pattern titles (text)
   - Automatic reverse links to Patterns

3. **Open METAS table**
   - Should see 5 METAS
   - `patterns` field shows pattern titles (text)

4. **Open Patterns table**
   - Should see 50 patterns
   - Each has linked Lens (clickable)
   - Each has linked Sources (clickable)
   - Each has linked Variations (clickable)

5. **Open Variations table**
   - Should see 46 variations
   - Each has linked_pattern (automatic reverse link)

---

## 🔍 **Troubleshooting**

### **"config.json not found"**
- Copy `config.json.template` to `config.json`
- Add your credentials

### **"Missing credentials"**
- Make sure token starts with `pat`
- Make sure base ID starts with `app`

### **"Table not found"**
- Create tables in Airtable first
- Use exact names: `Lenses`, `Sources`, `METAS`, `Variations`, `Patterns`

### **"Rate limit exceeded"**
- Script automatically waits 0.2s between requests
- If still fails, Airtable has 5 req/sec limit
- Script will log which batch failed

### **"Field not found"**
- Make sure all fields exist in Airtable tables
- Field names are case-sensitive

---

## 📊 **What Gets Created**

### **ID Mappings** (in `id_mappings/` folder):

After upload, these JSON files show the mapping:

**lens_id_map.json:**
```json
{
  "BELOVED BANG": "recABC123",
  "PHILOXENIA": "recDEF456"
}
```

**source_id_map.json:**
```json
{
  "Source A": "recGHI789"
}
```

These are used to create proper links in Patterns table.

---

## 🎯 **After Upload**

1. **Check logs** - Review `logs/` folder for any errors
2. **Verify data** - Click through Airtable to verify links
3. **Test queries** - Try filtering by Lens, Source, etc.
4. **Airtable magic** - Automatic reverse link fields created!

---

## 🔄 **Re-upload (if needed)**

To re-upload:
1. Delete all records from Airtable tables
2. Run `python upload_to_airtable.py` again
3. Fresh upload with new ID mappings

---

## 📞 **Need Help?**

Check the log file in `logs/` folder for detailed error messages.

**Common issues:**
- Wrong credentials → Update config.json
- Missing tables → Create in Airtable first
- Missing fields → Add fields to tables
- Rate limit → Script handles automatically

---

**Ready to upload!** 🚀
