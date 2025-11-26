# The Garden Project - Complete Analysis & Development Plan

## 📊 What We Now Understand (Complete Picture)

### Client's Actual Workflow

**Their Process:**
```
3 Million Words → 4 AI Engines (Claude 4.1, 4.5, GPT, Gemini)
      ↓
5 Interpretive Lenses (TOPS)
      ↓
10 Patterns per Document (~1,000 words each)
      ↓
Pattern Variations (1:1 correspondence)
      ↓
Meta-Analyses (~1,000 words each)
```

### The 3-Step Structure

#### **Step 1: AI Analysis** (DONE by client)
- Used 4 AI engines to analyze content
- Created 5 "lenses" (TOPS) for interpretation
- Outputs stored in Google Docs (e.g., Quantum folder)
- Each folder has: Claude 4.1, Claude 4.5, GPT, Gemini analyses
- **→ This data already exists in the markdown export**

#### **Step 2: Pattern Extraction** (OUR WORK)
Each document contains:
- **Headline** - Main theme
- **Text** - Full content
- **10 Patterns** - Each has:
  - Pattern number (1-10)
  - Overview
  - Conflict/Choice
  - Question
  - Sources (linked documents)
  - Tags
  - Interpretive summary
- **Overall Summary** (~1,000 words)
- **Pattern Variations** - Alternative versions (Pattern 1 has 11 variations!)

#### **Step 3: Organization & Querying** (OUR WORK)
- Structured in Airtable (4 tables)
- Queryable by Gemini Pro
- Filterable in Airtable interface

---

## 🎯 Dual Query System

### Query Method A: Gemini AI (Natural Language)
**Examples:**
- "Show me all Pattern 7s across entire corpus"
- "Compare Pattern 3 across all documents"
- "Find all patterns with Emotional Spatialization lens"
- "Map relationships between lenses, patterns, conflicts"

### Query Method B: Airtable Filtering (Database-Style)
**Examples:**
- Filter by: lens, pattern #, theme, conflict type, tags
- Explore relationships between tables
- Manual insight discovery
- Find patterns, anomalies, gaps

**Important:** Both systems work together - Gemini queries BOTH Airtable metadata AND Google Docs content

---

## 🗄️ Revised Airtable Schema

### Table 1: Documents (~566 rows)

| Field | Type | Description |
|-------|------|-------------|
| Document ID | Primary | AUTO-001, AUTO-002... |
| Title | Text | Document title |
| Folder Path | Text | AD FONTES/STEP 2/... |
| Master Folder | Select | AD FONTES, XBT, BIOME... |
| Step | Select | Step 1, Step 2, Step 3 |
| Total Word Count | Number | Document length |
| Google Doc URL | URL | Link to master doc |
| Has Patterns | Checkbox | True if Step 2 doc |
| Created Date | Date | From Scrivener |
| Modified Date | Date | From Scrivener |
| Summary | Text | Document summary |
| Status | Select | Processed/Pending |

### Table 2: Patterns (~5,660 rows)

| Field | Type | Description |
|-------|------|-------------|
| Pattern ID | Primary | PAT-001, PAT-002... |
| Document | Link | → Documents table |
| Pattern Number | Select | 1, 2, 3...10 |
| Pattern Title | Text | Main theme |
| Pattern Text | Long Text | Full pattern content (~1,000 words) |
| Overview | Long Text | Pattern overview |
| Conflict/Choice | Long Text | Core conflict described |
| Question | Text | Associated question |
| Interpretive Summary | Long Text | Key insights |
| Sources | Long Text | Source document references |
| Tags | Multi-Select | agency, boundary, spatial... |
| Lens | Link | → Lenses table |
| Theme | Link | → Themes table |
| Has Variation | Checkbox | True if variations exist |
| Variation Count | Number | # of variations |
| Google Doc URL | URL | Link to pattern doc (optional) |
| Word Count | Number | Pattern length |

### Table 3: Pattern Variations (~6,000+ rows)

| Field | Type | Description |
|-------|------|-------------|
| Variation ID | Primary | VAR-001, VAR-002... |
| Parent Pattern | Link | → Patterns table |
| Variation Number | Number | 1, 2, 3...11 (Pattern 1 has 11!) |
| Variation Text | Long Text | Alternative version |
| Differences | Text | What changed from original |
| Google Doc URL | URL | Link if created |

### Table 4: Lenses (~5-15 rows)

| Field | Type | Description |
|-------|------|-------------|
| Lens ID | Primary | LENS-001... |
| Lens Name | Text | Emotional Spatialization, Temporal Compression... |
| Description | Long Text | What this lens interprets |
| Pattern Count | Rollup | # patterns using this lens |
| Documents | Link | → Documents |

### Table 5: Themes (Variable, AI-generated later)

| Field | Type | Description |
|-------|------|-------------|
| Theme ID | Primary | THEME-001... |
| Theme Name | Text | Boundary Dissolution, Agency... |
| Description | Long Text | Theme definition |
| Pattern Count | Rollup | # patterns with this theme |
| Patterns | Link | → Patterns table |
| AI Generated | Checkbox | True if from Gemini |

---

## 🛠️ Development Phases

### **Phase 1: Data Analysis & Schema Design** (Days 1-2)

#### Tasks:
- [x] Convert Scrivener to Markdown (DONE - 566 files)
- [ ] Analyze pattern structure in markdown files
- [ ] Identify pattern markers and formatting
- [ ] Map out 5 lenses (TOPS) from Step 1 data
- [ ] Design final Airtable schema (5 tables)
- [ ] Create schema documentation

#### Deliverables:
- Pattern structure documentation
- Airtable schema design
- Field definitions
- Relationship mappings

---

### **Phase 2: Pattern Parser Development** (Days 3-5)

#### Tasks:
- [ ] Build markdown parser for Step 2 documents
- [ ] Extract pattern sections (1-10)
- [ ] Parse pattern fields:
  - Overview
  - Conflict/Choice
  - Question
  - Sources
  - Tags
  - Interpretive summary
- [ ] Handle pattern variations
- [ ] Extract document metadata
- [ ] Test with 10 sample documents

#### Technical Approach:

```python
def parse_step2_document(markdown_content):
    """
    Parse Step 2 document structure:
    - Headline
    - Text
    - 10 Patterns (each with sub-fields)
    - Overall Summary
    """
    patterns = []
    
    # Detect pattern markers
    # Extract for each pattern:
    #   - Pattern number
    #   - Overview
    #   - Conflict/Choice
    #   - Question
    #   - Sources
    #   - Interpretive summary
    
    return {
        'headline': headline,
        'text': text,
        'patterns': patterns,  # List of 10
        'summary': summary,
        'variations': variations
    }
```

#### Deliverables:
- Pattern parsing script
- Test results (10 documents)
- Pattern extraction report

---

### **Phase 3: Airtable Setup** (Days 5-7)

#### Tasks:
- [ ] Create Airtable base "The Garden"
- [ ] Set up 5 tables with full schema
- [ ] Configure relationships and links
- [ ] Set up views:
  - By Lens
  - By Pattern Number
  - By Theme
  - By Master Folder
  - By Conflict Type
- [ ] Create filters and groups
- [ ] Test with sample data

#### Deliverables:
- Configured Airtable base
- View templates
- Relationship validation

---

### **Phase 4: Data Migration** (Days 7-10)

#### Tasks:
- [ ] Build Airtable population script
- [ ] Process all 566 documents
- [ ] Extract ~5,660 patterns
- [ ] Extract ~6,000+ variations
- [ ] Populate Documents table
- [ ] Populate Patterns table
- [ ] Populate Variations table
- [ ] Populate Lenses table
- [ ] Link all relationships
- [ ] Validate data integrity

#### Technical Approach:

```python
# Main migration pipeline
for markdown_file in markdown_files:
    # 1. Parse document
    doc_data = parse_document(markdown_file)
    
    # 2. Create document record in Airtable
    doc_record = airtable.create_document(doc_data)
    
    # 3. Extract and create pattern records
    for pattern in doc_data['patterns']:
        pattern_record = airtable.create_pattern(
            pattern,
            document_id=doc_record['id']
        )
        
        # 4. Link to lens
        airtable.link_to_lens(pattern_record, pattern['lens'])
        
        # 5. Create variation records
        for variation in pattern['variations']:
            airtable.create_variation(
                variation,
                pattern_id=pattern_record['id']
            )
```

#### Deliverables:
- Populated Airtable (all 5 tables)
- Migration report
- Data validation results

---

### **Phase 5: Google Docs Integration** (Days 10-12) - OPTIONAL

**Decision Point:** Ask client if they want pattern-level Google Docs

If YES:
- [ ] Generate ~5,660 pattern docs
- [ ] Link back to Airtable
- [ ] Store URLs in Airtable

If NO:
- [ ] Keep only master documents
- [ ] Work entirely from Airtable

---

### **Phase 6: Gemini Integration & Testing** (Days 12-14)

#### Tasks:
- [ ] Set up Gemini API access
- [ ] Configure Airtable API for Gemini
- [ ] Test sample queries from client's list:
  - "Show me all Pattern 7s"
  - "Compare Pattern 3 across all documents"
  - "Which patterns use Emotional Spatialization lens?"
  - "Find patterns about agency"
- [ ] Validate hybrid queries (Airtable + Google Docs)
- [ ] Document query patterns
- [ ] Create query templates

#### Sample Queries to Test:

1. **Pattern-Level Retrieval:**
   - Show all Pattern 7s
   - List Conflict/Choice tagged 'agency'
   
2. **Cross-Document Reasoning:**
   - Compare Pattern 3 across docs
   - Track motif evolution
   
3. **Thematic Maps:**
   - Generate transformation taxonomy
   - Map lens-pattern-conflict relationships

4. **Hybrid Queries:**
   - Filter by Airtable metadata + analyze Google Docs content

#### Deliverables:
- Gemini query templates
- Test results
- Query documentation
- Best practices guide

---

### **Phase 7: Sync Automation** (Days 14-15)

#### Option A: Automated Sync Script

```python
# Keep Airtable synced to Google Drive
def sync_airtable_to_drive():
    """
    Export Airtable tables as CSV/JSON
    Upload to fixed Google Drive folder
    Gemini reads from there
    """
    tables = ['Documents', 'Patterns', 'Variations', 'Lenses', 'Themes']
    
    for table in tables:
        data = airtable.export(table)
        drive.upload(data, folder='Airtable_Sync')
```

#### Option B: Direct Gemini Actions
- Configure Gemini to query Airtable API directly
- No manual sync needed
- Always latest data

#### Deliverables:
- Sync automation script (if Option A)
- Gemini action configuration (if Option B)

---

### **Phase 8: Documentation & Handoff** (Days 15-16)

#### Tasks:
- [ ] Create user guide
- [ ] Document schema
- [ ] Write query cookbook
- [ ] Create maintenance guide
- [ ] Record demo video
- [ ] Provide training

#### Deliverables:
- Complete documentation
- Query cookbook
- Training materials
- Handoff package

---

## 📋 Critical Decisions Needed from Client

### Decision 1: Pattern Structure
**Q:** Can you share 2-3 sample Step 2 documents showing:
- How patterns are marked (Pattern 1, Pattern 2...?)
- How fields are formatted (Overview, Conflict/Choice, etc.)
- How variations are indicated

**Why:** Need to see actual structure to build parser

---

### Decision 2: Lenses (TOPS)
**Q:** What are the 5 lenses?
- Names?
- Descriptions?
- How to identify which lens each pattern uses?

**Why:** Need to populate Lenses table and link patterns

---

### Decision 3: Pattern Variations
**Q:** Do you want variations:
- As separate Airtable records (our recommendation)
- Stored in a single field
- Skip entirely and just use main patterns

**Why:** Pattern 1 has 11 variations - need clear structure

---

### Decision 4: Google Docs
**Q:** Generate pattern-level Google Docs?
- Option A: Yes, create ~5,660 docs (time-intensive)
- Option B: No, just master docs + Airtable
- Option C: Only for specific categories

**Why:** Significant work to generate thousands of docs

---

### Decision 5: Sync Method
**Q:** How should Gemini access Airtable?
- Option A: Automated sync script (CSV/JSON to Drive)
- Option B: Direct API actions (Gemini → Airtable)

**Why:** Affects architecture and maintenance

---

## ⏱️ Revised Timeline

**Total: 14-16 days**

| Phase | Days | Status |
|-------|------|--------|
| 1. Schema Design | 1-2 | Waiting on sample docs |
| 2. Parser Development | 3-5 | After Decision 1 |
| 3. Airtable Setup | 5-7 | After Decision 2, 3 |
| 4. Data Migration | 7-10 | - |
| 5. Google Docs (optional) | 10-12 | After Decision 4 |
| 6. Gemini Integration | 12-14 | After Decision 5 |
| 7. Sync Automation | 14-15 | After Decision 5 |
| 8. Documentation | 15-16 | - |

---

## 💡 Key Insights

### What's Different from Original Plan:

1. **More Complex Pattern Structure**
   - Not just 10 patterns per doc
   - Each pattern has 6+ sub-fields
   - Pattern variations add ~1,000+ extra records

2. **5 Tables Instead of 4**
   - Added Pattern Variations table
   - Critical for 1:1 correspondence tracking

3. **Dual Query System**
   - Gemini for natural language
   - Airtable for database filtering
   - Both work together

4. **Step 1 Data Already Exists**
   - Claude 4.1, 4.5, GPT, Gemini analyses in markdown
   - These become reference docs
   - Stored in Google Docs

5. **~1,000 Words per Pattern**
   - Much larger than expected
   - Each pattern is substantial content
   - Meta-analyses are full documents

---

## 🚀 Next Steps

### Immediate (Your Actions):
1. ✅ Send CLIENT_QUESTIONS.md to client
2. ✅ Request 2-3 sample Step 2 documents
3. ✅ Get list of 5 lenses (TOPS)
4. ✅ Confirm decisions 1-5 above

### After Client Response:
1. Build pattern parser for their specific structure
2. Set up Airtable with actual lens names
3. Test with sample data
4. Get client approval
5. Run full migration

---

## 📊 Scope Summary

**Input:** 566 markdown documents (3 million words)  
**Output:** 
- ~566 document records
- ~5,660 pattern records
- ~6,000+ variation records
- ~5-15 lens records
- ~Variable theme records (AI-generated)

**Total Airtable Records:** ~12,000+  
**Query Capabilities:** Gemini AI + Airtable filtering  
**Infrastructure:** Dual system (structured metadata + full text)

**This is a complex, substantial project requiring precision and careful architecture!**
