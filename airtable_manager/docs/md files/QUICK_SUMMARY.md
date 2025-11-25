# The Garden Project - Quick Summary

## 🎯 What You Need to Do

**Migrate 400+ documents from Scrivener to Google Docs + Create AI-queryable database**

---

## 📦 What Client Has Provided

✅ **Scrivener Project** at `E:\Work\shoaib\upwork\shoaib53%202025-11-22%2007-11\shoaib53.scriv`
- 300,000 words across ~400 files
- 15 master folders with hierarchical structure
- Content about mental health, AI, and psychology

---

## 🚀 What You Need to Deliver

### 1. **Google Docs Migration**
   - Upload all files to Google Drive
   - Maintain folder structure
   - Clean formatting

### 2. **Airtable Database**
   - Central index of all documents
   - Rich metadata (tags, categories, word count, dates)
   - Links to Google Docs

### 3. **Python Automation Tool**
   - Parses Scrivener files
   - Uploads to Google Drive
   - Populates Airtable
   - Fully automated process

### 4. **AI Validation**
   - Test with Gemini Pro 3.0
   - Create sample queries
   - Demonstrate AI can query the content

### 5. **Documentation**
   - How to use the system
   - Tips for Claude integration
   - Maintenance guide

---

## 🛠️ Technical Stack

```
Python 3.9+
├── Google Drive API (document upload)
├── Airtable API (database)
├── Gemini API (AI validation)
└── Libraries:
    ├── google-api-python-client
    ├── pyairtable
    ├── striprtf (convert RTF to text)
    └── python-docx
```

---

## 📋 Step-by-Step Process

```
Step 1: Parse Scrivener
   └─> Read XML structure
   └─> Extract RTF content
   └─> Get metadata

Step 2: Process Content
   └─> Clean text
   └─> Extract headings
   └─> Identify patterns
   └─> Generate metadata

Step 3: Upload to Google Drive
   └─> Create folder structure
   └─> Upload documents
   └─> Get shareable links

Step 4: Populate Airtable
   └─> Create records
   └─> Add all metadata
   └─> Link to Google Docs

Step 5: Validate with AI
   └─> Test Gemini queries
   └─> Document best practices
```

---

## ⏱️ Timeline

**4 weeks total**

- Week 1: Setup + Parser Development
- Week 2: Google Drive + Airtable Integration
- Week 3: Full Migration + Testing
- Week 4: AI Validation + Documentation

---

## 💰 What Client Wants

> "A clean, structured, tagged format that enables Gemini Pro 3.0 to perform intelligent queries"

The goal is to make 300,000 words of content:
- ✅ Easily searchable
- ✅ Well organized
- ✅ AI-queryable
- ✅ Properly tagged and categorized

---

## 📁 Sample Airtable Structure

| Document ID | Title | Google Doc Link | Folder | Tags | Word Count | Status |
|-------------|-------|----------------|--------|------|------------|--------|
| DOC-001 | meta meta 11-22 | [link] | GARDEN META | meta, planning | 1,200 | ✅ Complete |
| DOC-002 | xbt home | [link] | XBT | xbt, home | 950 | ✅ Complete |

---

## ❓ Questions to Ask Client

1. ✅ Do they have Google Workspace account?
2. ✅ Do they have Airtable account?
3. ❓ Specific tags/keywords they want tracked?
4. ❓ Any formatting preferences?
5. ❓ One-time migration or ongoing sync?

---

## 📖 Full Details

See **PROJECT_REQUIREMENTS.md** for complete technical specifications, architecture, schemas, and implementation plan.

---

## 🎯 Bottom Line

**Build an automated Python tool that takes messy Scrivener files and turns them into:**
1. Clean Google Docs
2. Searchable Airtable database
3. AI-queryable knowledge base

**For**: A social good project about mental health and AI
**Timeline**: 4 weeks
**Result**: 400 documents perfectly organized and AI-ready
