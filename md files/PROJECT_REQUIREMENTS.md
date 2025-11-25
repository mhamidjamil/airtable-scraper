# The Garden Project - Migration Requirements Document

## 📋 Project Overview

**Client:** Martin
**Project Name:** The Garden
**Project Type:** Social good project blending mental health and creativity
**Scope:** Migrate ~400 Scrivener files to Google Docs with structured metadata and AI query capabilities

### 🎯 Mission
Create a well-organized, AI-queryable knowledge base exploring the intersection of mental health, technology, and artificial intelligence to meaningfully contribute to humanity's understanding.

---

## 📊 Current State Analysis

### Data Inventory
- **Total Content:** ~300,000 words
- **Organization Tool:** Scrivener
- **Structure:**
  - 15 master folders
  - 300-500 files total
  - Average file size: ~1,000 words per file
  - **Location:** `E:\Work\shoaib\upwork\shoaib53%202025-11-22%2007-11\shoaib53.scriv`

### Content Structure
Each file contains:
- **Headlines** - Main topic identifiers
- **Subheadlines** - Topic subdivisions
- **Sections** - Content blocks
- **Patterns** - Recurring themes and connections

### Major Content Categories (Master Folders)
Based on the Scrivener (.scrivx) file analysis:

1. **GARDEN META** - Project metadata and organization
2. **XBT** - Core content area with subtopics:
   - METAS - Meta-analyses
   - EMOTIONAL SPATIALIZATION
   - INVISIBLE VISIBLE
   - VERBUM VISIBILE
   - METAPHOR MATTER
   - HANDS
   - And more conceptual categories

3. **JUNG** - Jungian psychology content
4. **VISION** - Vision-related materials
5. **XBT WRITINGS** - Extended writings and explorations

---

## 🎯 Project Deliverables

### 1. Data Migration & Structuring
**Objective:** Transform Scrivener files into clean, structured Google Docs

**Requirements:**
- ✅ Parse all ~400 Scrivener files (.rtf format in `Files/Data` directory)
- ✅ Extract content from each UUID-based folder
- ✅ Convert RTF to clean Google Docs format
- ✅ Preserve hierarchy (15 master folders → Google Drive folder structure)
- ✅ Maintain headlines, subheadlines, and section structure
- ✅ Apply consistent formatting across all documents

### 2. Metadata System
**Objective:** Create rich metadata for each document to enable AI queries

**Required Metadata Fields:**
- **Document ID** - Unique identifier
- **Title** - File title from Scrivener
- **Master Folder** - Parent category (e.g., XBT, JUNG, VISION)
- **Subfolder(s)** - Hierarchical path
- **Tags/Keywords** - Topic tags and recurring patterns
- **Word Count** - Document length
- **Creation Date** - From Scrivener metadata
- **Last Modified** - From Scrivener metadata
- **Content Type** - (e.g., meta-analysis, writing, variation)
- **Patterns Identified** - Recurring themes within the document
- **Related Documents** - Cross-references to connected content

### 3. Centralized Airtable Index
**Objective:** Create a master database for content navigation and querying

**Airtable Schema:**

| Field Name | Type | Description |
|------------|------|-------------|
| Document ID | Single line text (Primary) | Unique identifier |
| Title | Single line text | Document title |
| Google Doc URL | URL | Direct link to Google Doc |
| Master Folder | Single select | Top-level category |
| Folder Path | Long text | Full hierarchical path |
| Tags | Multiple select | Topic tags |
| Word Count | Number | Document length |
| Created Date | Date | Original creation |
| Modified Date | Date | Last modification |
| Content Type | Single select | Document classification |
| Patterns | Long text | Identified recurring patterns |
| Related Docs | Linked record | Cross-references |
| Summary | Long text | Brief content summary |
| Status | Single select | Processing status (Pending/In Progress/Complete) |

### 4. Python Automation System
**Objective:** Automate the entire migration process

**Required Components:**

#### A. Scrivener Parser
```
Function: extract_scrivener_content()
- Parse .scrivx XML file to extract document structure
- Map UUID to file paths
- Extract titles, hierarchy, and metadata
- Read .rtf content files
- Convert RTF to plain text/markdown
```

#### B. Content Processor
```
Function: process_content()
- Clean and format text
- Extract headlines and subheadlines
- Identify sections and patterns
- Generate metadata
- Create document summary
```

#### C. Google Drive API Integration
```
Function: upload_to_google_docs()
- Authenticate with Google Drive API
- Create folder structure matching Scrivener hierarchy
- Upload documents with formatting
- Generate shareable links
- Set appropriate permissions
```

#### D. Airtable Integration
```
Function: populate_airtable()
- Connect to Airtable API
- Create/update records for each document
- Populate all metadata fields
- Link related documents
- Update processing status
```

### 5. AI Query Validation
**Objective:** Validate and formulate initial queries with Gemini Pro 3.0

**Tasks:**
- Test data structure with Gemini API
- Formulate 10-15 sample queries demonstrating capabilities:
  - Pattern recognition across documents
  - Thematic connections
  - Conceptual relationships
  - Deep insights extraction
- Document query best practices
- Provide query templates for common use cases

### 6. Claude Projects Integration (Bonus)
**Objective:** Provide tips for importing into Claude 4.0 projects

**Deliverables:**
- Guide for structuring data for Claude ingestion
- Best practices for organizing context
- Sample project setup instructions
- Tips for maximizing Claude's analytical capabilities

---

## 🛠️ Technical Architecture

### Technology Stack

#### Core Technologies
- **Python 3.9+** - Main automation language
- **Google Drive API v3** - Document upload and management
- **Airtable API** - Database management
- **Gemini API** - AI query validation

#### Python Libraries
```
Required Libraries:
- google-auth
- google-auth-oauthlib
- google-api-python-client
- pyairtable
- python-docx
- striprtf
- beautifulsoup4
- lxml
- requests
- python-dotenv
```

### System Workflow

```
┌─────────────────────┐
│  Scrivener Project  │
│   (.scrivx + RTF)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Python Parser      │
│  - Parse XML        │
│  - Extract metadata │
│  - Read RTF content │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Content Processor  │
│  - Clean text       │
│  - Extract patterns │
│  - Generate metadata│
└──────────┬──────────┘
           │
           ├──────────────────────┬──────────────────┐
           ▼                      ▼                  ▼
┌─────────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  Google Drive API   │  │  Airtable API   │  │  Gemini API     │
│  - Create folders   │  │  - Create index │  │  - Validate     │
│  - Upload docs      │  │  - Add metadata │  │  - Test queries │
│  - Get URLs         │  │  - Link docs    │  │  - Optimize     │
└─────────────────────┘  └─────────────────┘  └─────────────────┘
           │                      │                  │
           └──────────────────────┴──────────────────┘
                                  │
                                  ▼
                        ┌─────────────────────┐
                        │  Deliverable        │
                        │  - Structured Docs  │
                        │  - Searchable Index │
                        │  - AI-Ready Data    │
                        └─────────────────────┘
```

---

## 📁 Folder Structure

### Google Drive Target Structure
```
The Garden/
├── GARDEN META/
│   ├── meta meta 11-22.gdoc
│   ├── meta meta 11-21.gdoc
│   └── ACTION.gdoc
├── XBT/
│   ├── xbt home.gdoc
│   ├── taxonomies for cosmos.gdoc
│   ├── METAS/
│   │   ├── meta meta/
│   │   ├── vision meta.gdoc
│   │   └── jung meta.gdoc
│   ├── EMOTIONAL SPATIALIZATION/
│   │   ├── JUNG/
│   │   ├── VISION/
│   │   └── XBT/
│   └── INVISIBLE VISIBLE/
├── JUNG/
├── VISION/
└── XBT WRITINGS/
```

---

## 🚀 Implementation Plan

### Phase 1: Setup & Configuration (Week 1)
- [ ] Set up Python development environment
- [ ] Configure Google Cloud Project
- [ ] Enable Google Drive API
- [ ] Set up OAuth 2.0 credentials
- [ ] Configure Airtable workspace and base
- [ ] Set up Gemini API access
- [ ] Install required libraries

### Phase 2: Parser Development (Week 1-2)
- [ ] Develop Scrivener XML parser
- [ ] Create RTF content extractor
- [ ] Build metadata extraction system
- [ ] Implement pattern recognition logic
- [ ] Test with sample files

### Phase 3: Google Drive Integration (Week 2)
- [ ] Implement folder creation logic
- [ ] Develop document upload system
- [ ] Add formatting preservation
- [ ] Test upload with various content types
- [ ] Implement error handling and retry logic

### Phase 4: Airtable Integration (Week 2-3)
- [ ] Design Airtable schema
- [ ] Implement Airtable API integration
- [ ] Build automated metadata population
- [ ] Create relationship mapping
- [ ] Test data integrity

### Phase 5: Processing & Migration (Week 3)
- [ ] Run full migration on all ~400 files
- [ ] Verify data integrity
- [ ] Check folder structure
- [ ] Validate metadata completeness
- [ ] Generate migration report

### Phase 6: AI Validation (Week 3-4)
- [ ] Formulate test queries
- [ ] Validate with Gemini Pro 3.0
- [ ] Document query patterns
- [ ] Create query templates
- [ ] Optimize for AI performance

### Phase 7: Documentation & Handoff (Week 4)
- [ ] Create user documentation
- [ ] Document codebase
- [ ] Provide Claude integration tips
- [ ] Create maintenance guide
- [ ] Final project handoff

---

## 🔍 Quality Assurance

### Validation Checklist
- [ ] All ~400 files successfully migrated
- [ ] Folder structure matches Scrivener hierarchy
- [ ] All metadata fields populated
- [ ] Google Doc formatting is clean and consistent
- [ ] Airtable index is complete and accurate
- [ ] Document links work correctly
- [ ] Gemini queries return relevant results
- [ ] No data loss or corruption
- [ ] Cross-references correctly linked

---

## 📝 API Credentials Needed

### Google Cloud Platform
- Project ID
- OAuth 2.0 Client ID
- OAuth 2.0 Client Secret
- Service Account (optional for automation)

### Airtable
- API Key or Personal Access Token
- Base ID
- Table Name

### Gemini API
- API Key
- Project ID

---

## 💡 Success Metrics

1. **Completeness:** 100% of source files migrated
2. **Data Integrity:** Zero content loss or corruption
3. **Structure:** Hierarchical organization preserved
4. **Metadata Quality:** All fields populated with accurate data
5. **AI Readiness:** Successful query responses from Gemini
6. **Performance:** Automated process runs reliably
7. **Documentation:** Comprehensive guides for future maintenance

---

## 🚨 Potential Challenges & Solutions

### Challenge 1: RTF Formatting Complexity
**Solution:** Use robust RTF parsers (striprtf, beautifulsoup4) with fallback mechanisms

### Challenge 2: Google Drive API Rate Limits
**Solution:** Implement exponential backoff, batch operations, and progress tracking

### Challenge 3: Metadata Inconsistency
**Solution:** Create standardized extraction rules and validation checks

### Challenge 4: Large File Processing
**Solution:** Use batch processing, progress saving, and resume capability

### Challenge 5: Pattern Recognition Complexity
**Solution:** Use keyword extraction and NLP techniques for initial pass, manual review for refinement

---

## 🎯 Next Steps for Team

### For Developer (You/Your Team)
1. Review this requirements document
2. Set up development environment
3. Start with Phase 1 implementation
4. Create a GitHub repository for code
5. Set up project management board (Trello/Jira/GitHub Projects)

### Questions to Ask Client
1. Do they have Google Workspace account or need one created?
2. Do they have Airtable account or need setup?
3. What level of access do they need to Google Drive?
4. Are there specific patterns/keywords they want tracked?
5. Any formatting preferences for Google Docs?
6. Do they want automated updates or one-time migration?

### For Frontend Developer
- Create a simple dashboard to monitor migration progress
- Build a UI for browsing the Airtable index
- Create query interface for testing Gemini integration
- Design visualization for pattern relationships

---

## 📚 Resources & References

### Documentation
- [Google Drive API - Python Quickstart](https://developers.google.com/drive/api/v3/quickstart/python)
- [Airtable API Documentation](https://airtable.com/developers/web/api/introduction)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [Scrivener File Format Documentation](https://github.com/petermajor/ScrivenerFileFormat)

### Tools
- [striprtf](https://pypi.org/project/striprtf/) - RTF to text conversion
- [pyairtable](https://pypi.org/project/pyairtable/) - Airtable Python client
- [google-api-python-client](https://github.com/googleapis/google-api-python-client)

---

## 📞 Project Contact

**Client:** Martin
**Project:** The Garden
**Developer:** [Your Team]
**Timeline:** 4 weeks
**Budget:** [To be confirmed with client]

---

## ✅ Summary

This project requires building an automated system to:
1. **Extract** ~400 documents from Scrivener (XML + RTF parsing)
2. **Transform** content into structured Google Docs with metadata
3. **Load** into Google Drive with proper folder hierarchy
4. **Index** all documents in Airtable for easy navigation
5. **Validate** with Gemini Pro 3.0 for AI query capabilities
6. **Document** for future maintenance and Claude integration

The result will be a clean, well-organized, AI-queryable knowledge base that serves Martin's mission of exploring mental health, technology, and AI's impact on humanity.
