# Client Communication - Questions & Understanding

## ✅ What We Understand

Based on your `google-plan.docx`, we understand you want:

1. **Airtable-First Architecture** (not Google Docs first)
   - Airtable = main database for AI queries
   - Google Docs = optional human viewing only

2. **Pattern-Based Structure**
   - Each document has ~10 patterns
   - Each pattern = 1 Airtable record
   - ~566 documents = ~5,660 pattern records

3. **4-Table Relational Database**
   - Documents table (~566 rows)
   - Patterns table (~5,660 rows)
   - Lenses table (~15-20 rows)
   - Themes table (AI-generated)

4. **Workflow:**
   ```
   Markdown files → Parse patterns → Airtable → AI queries (Gemini)
   ```

---

## ❓ Critical Questions

### 1. Pattern Structure
**Q:** How are patterns marked in your documents?
- Are they numbered? (Pattern 1, Pattern 2...Pattern 10)
- Any specific headings or markers we should look for?
- Can you share 1-2 example documents showing pattern structure?

### 2. Markdown Export
**Q:** We've converted your Scrivener to Markdown (566 files ready).
- Should we proceed with this, or do you prefer to export yourself?
- Files are at: `E:\Work\shoaib\upwork\markdown_export`

### 3. Pattern Fields
**Q:** For each pattern, you want these fields extracted:
- Pattern Title ✅
- Pattern Text ✅
- Conflict/Choice ✅
- Interpretive Key Summary ✅
- Question ✅
- Sources ✅
- Tags ✅

Are these marked in documents or should we use AI to extract them?

### 4. Google Docs
**Q:** Do you want pattern-level Google Docs created?
- Option A: Yes, create ~5,660 mini docs (one per pattern)
- Option B: No, keep master docs only, work from Airtable
- Option C: Only for specific categories?

### 5. API Credentials
**Q:** When ready for testing, you'll provide:
- Google Cloud credentials ✅
- Airtable token + Base ID ✅
- Gemini API key ✅

Correct?

### 6. Timeline
**Q:** Is 10-14 days acceptable for:
- Pattern parsing logic
- Airtable 4-table setup
- Full migration (~5,660 records)
- Gemini query validation

---

## 🚀 Next Steps (After Your Answers)

1. Build pattern parser based on your structure
2. Design Airtable schema (4 tables)
3. Test with 10-20 sample patterns
4. Get your approval
5. Run full migration
6. Validate with Gemini

---

**Please answer the 6 questions above so we can proceed correctly! 🙏**
