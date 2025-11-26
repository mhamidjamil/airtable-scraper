# The Garden Project - Implementation Plan

## ⏱️ Timeline

**Total Time: 7-10 days of focused development**

### Week 1 (Days 1-5)
- **Days 1-2:** Core parser + extractor (Scrivener XML & RTF)
- **Days 3-4:** Google Drive integration + folder structure
- **Day 5:** Airtable integration + metadata system

### Week 2 (Days 6-10)
- **Day 6:** Main orchestrator + error handling
- **Days 7-8:** Full testing with your ~400 files
- **Days 9-10:** Documentation + final polish

> **Note:** If everything goes smoothly, could finish in ~5-7 days. Adding buffer for testing/issues.

---

## 📋 What I Need From You

### 1. **API Credentials** (You'll provide, I'll make it configurable)

#### Google Cloud Platform
```
- Project ID
- credentials.json file (OAuth 2.0)
  OR
- Service account JSON file (for automation)
```

**How to get:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google Drive API
4. Create credentials (OAuth 2.0 or Service Account)
5. Download the JSON file

#### Airtable
```
- Personal Access Token (or API Key)
- Base ID
- Table Name (e.g., "Documents")
```

**How to get:**
1. Go to [Airtable](https://airtable.com/)
2. Create a base called "The Garden"
3. Go to Account → Developer Hub → Personal Access Token
4. Copy Base ID from the base URL

#### Gemini API (Optional - for validation)
```
- API Key
```

**How to get:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create API key

### 2. **Preferences/Decisions**

Please confirm:
- ✅ Use your own credentials (I'll make it generic/configurable)
- ❓ Should I create the Airtable schema automatically or you want to set it up?
- ❓ For Google Docs - any specific formatting preferences?
- ❓ Should documents be shared publicly or private?
- ❓ Do you want pattern/keyword extraction automated or manual tags?

### 3. **Access to Data**

I have access to: `E:\Work\shoaib\upwork\shoaib53%202025-11-22%2007-11\shoaib53.scriv`

This is perfect - I'll use this for development and testing.

---

## 🛠️ How I'll Build It

### Project Structure
```
garden-migration/
├── config/
│   ├── credentials.json          # Google credentials (gitignored)
│   ├── config.yaml               # Main configuration
│   └── .env                      # API keys (gitignored)
├── src/
│   ├── parsers/
│   │   ├── scrivener_parser.py   # XML + hierarchy parsing
│   │   └── rtf_extractor.py      # RTF to text conversion
│   ├── processors/
│   │   ├── content_processor.py  # Text cleaning + metadata
│   │   └── pattern_extractor.py  # Pattern/keyword extraction
│   ├── integrations/
│   │   ├── google_drive.py       # Google Drive API
│   │   └── airtable_client.py    # Airtable API
│   └── main.py                   # Main orchestrator
├── tests/
│   └── test_*.py                 # Unit tests
├── docs/
│   ├── SETUP.md                  # Setup guide
│   └── USAGE.md                  # Usage instructions
├── requirements.txt              # Python dependencies
├── .gitignore                    # Ignore credentials
└── README.md                     # Project overview
```

### Step-by-Step Approach

#### Step 1: Scrivener Parser
```python
# Parse .scrivx XML → Extract structure
# Read UUIDs → Map to content files
# Extract: titles, hierarchy, dates, metadata
# Read RTF files → Convert to clean text
```

#### Step 2: Content Processor
```python
# Clean text (remove formatting artifacts)
# Extract headlines/subheadlines
# Count words
# Generate summary (first 200 words)
# Extract patterns/keywords (optional AI enhancement)
```

#### Step 3: Google Drive Integration
```python
# Authenticate with credentials
# Create folder structure (matching Scrivener)
# Upload documents as Google Docs
# Get shareable links
# Return document IDs
```

#### Step 4: Airtable Integration
```python
# Connect to Airtable
# Create table schema (if needed)
# Populate records with metadata
# Link to Google Doc URLs
# Mark as complete
```

#### Step 5: Main Orchestrator
```python
# Load configuration
# Parse all Scrivener files
# Process content
# Upload to Google Drive (with progress bar)
# Populate Airtable (with progress bar)
# Generate report
# Handle errors gracefully
```

---

## 🎯 Features I'll Include

### Core Features
✅ **Full automation** - Run one command, everything happens
✅ **Progress tracking** - Live progress bars showing upload status
✅ **Error handling** - Graceful failure + resume capability
✅ **Logging** - Detailed logs for debugging
✅ **Configuration** - Easy config file for credentials/settings
✅ **Generic/reusable** - Works for any Scrivener project

### Bonus Features
✅ **Dry run mode** - Test without uploading
✅ **Selective migration** - Migrate specific folders only
✅ **Report generation** - Summary of what was migrated
✅ **Duplicate detection** - Avoid re-uploading existing files

---

## 📦 Deliverables

When I'm done, you'll get:

1. **Complete Python tool** - Fully working automation
2. **Documentation**:
   - Setup guide (how to configure)
   - Usage guide (how to run)
   - Troubleshooting guide
3. **Configuration templates** - Easy setup for credentials
4. **Sample queries** - Examples for Gemini/Claude
5. **Airtable schema** - Complete field definitions
6. **Migration report** - Summary of processed files

---

## 🚀 How to Start

### Immediate Actions:

1. **I'll start building** the core parser and extractor today
2. **You prepare credentials** (Google Cloud + Airtable)
3. **Answer preference questions** above when you can

### Running the Final Tool:

```bash
# Step 1: Install dependencies
pip install -r requirements.txt

# Step 2: Configure credentials
# (Put your credentials.json in config/)
# (Update config.yaml with Airtable details)

# Step 3: Run migration
python src/main.py --config config/config.yaml

# That's it! ✅
```

---

## 💰 Cost Estimate

**Development Time:** 7-10 days
**Your time needed:** ~1-2 hours (credential setup + testing)
**API Costs:**
- Google Drive API: Free (within quotas)
- Airtable API: Free tier (up to 1,200 records/month)
- Gemini API: Pay-as-you-go (testing ~$1-5)

---

## ❓ Questions Before I Start?

1. Is 7-10 days timeline acceptable?
2. Should I start building the parser now?
3. Any specific requirements I missed?

Let me know and I'll start coding! 🚀
