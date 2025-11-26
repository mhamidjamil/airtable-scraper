# Pattern Extraction Guide (guid.md)

## Metadata Extraction from Filename

### Filename Pattern
Dashboard files follow this naming convention:
- **With Lens**: `Dashboard - Step X - Lens Y - Topic Name.docx`
- **Without Lens**: `Dashboard - Step X - Topic Name.docx`

### Extracted Metadata
From each filename, we extract:
- **dashboard**: Always "Dashboard"
- **step**: e.g., "Step 2", "Step 3"
- **lens**: e.g., "Lens 1", "Lens 2" (null for Step 3 files)
- **topic_name**: The descriptive title after the lens

## Document Structure Understanding

### Pattern Format
Based on analysis of Step 2 documents, patterns follow this structure:

1. **Pattern Header**: `Pattern X: [Title]`
   - Format: "Pattern" + number + ":" + title text
   - Example: "Pattern 1: From User to Gardener – The Great Identity Shift"

2. **Explanation/Overview**: 
   - Starts immediately after pattern header
   - First paragraph after header
   - May be labeled as "Explanation:" or just be the paragraph itself
   - Contains the core concept description

3. **Choice/Inner War**:
   - Second paragraph after pattern header
   - May be labeled as "Inner war / choice:" or just be the paragraph
   - Describes the decision/conflict the reader faces

4. **Sources**:
   - Third paragraph after pattern header
   - Labeled as "Sources:" 
   - Lists references from the corpus

### Variation Format
Variations appear after all main patterns:

1. **Variation Header**: `Variation X – Pattern Y: [Title]`
   - Format: "Variation" + number + "–" + "Pattern" + number + ":" + title
   - Example: "Variation 1 – Pattern 1: No Longer Used, But Tending"
   - Note: The variation number and pattern number it refers to

2. **Content**: 
   - Single paragraph providing fresh angle on the pattern
   - No separate "choice" or "sources" sections in variations

### Paragraph Style Detection
- **Headings**: Use style "Heading 1", "Heading 2", etc.
- **Normal text**: Use style "normal"
- Pattern headers are in "normal" style, not heading style
- Must detect patterns by text content, not by paragraph style alone

### Key Rules for Parsing

1. **Pattern Detection**:
   - Look for text starting with "Pattern [number]:"
   - Title is the text after the colon on same line
   - Next non-empty paragraph is overview/explanation
   - Next paragraph after that is choice (may have "Inner war / choice:" label)
   - Next paragraph is sources (has "Sources:" label)

2. **Variation Detection**:
   - Look for text starting with "Variation [number]"
   - Contains "Pattern [number]" reference
   - Title after the colon
   - Single content paragraph follows

3. **Label Handling**:
   - Labels like "Explanation:", "Inner war / choice:", "Sources:" should be stripped
   - Keep only the actual content after the label

4. **Edge Cases**:
   - Some patterns might be missing sections
   - Variations are simpler - just one paragraph of content
   - Text before first "Pattern 1:" should be ignored (intro material)

## JSON Output Structure

```json
{
  "patterns": [
    {
      "pattern_number": 1,
      "title": "From User to Gardener – The Great Identity Shift",
      "overview": "Full text of explanation paragraph...",
      "choice": "Full text of inner war/choice paragraph...",
      "source": "Full text of sources...",
      "variations": [
        {
          "variation_number": 1,
          "title": "No Longer Used, But Tending",
          "content": "Full variation text..."
        }
      ]
    }
  ]
}
```

## Implementation Notes

### Parser Strategy
1. Read all paragraphs from docx with their text content
2. Iterate through paragraphs looking for pattern markers
3. When "Pattern X:" found:
   - Extract pattern number and title
   - Next 3 paragraphs are overview, choice, source
   - Strip any labels
4. When "Variation X" found:
   - Extract variation number and pattern reference
   - Extract title
   - Next paragraph is content
   - Associate with correct pattern

### Challenges to Address
1. Paragraph style is mostly "normal" - can't rely on it
2. Labels ("Explanation:", etc.) are optional - must handle both cases
3. Variations link back to patterns - need to match them up
4. Empty paragraphs should be skipped but not break the sequence

## Learning Notes

### What Works Well
- Clear pattern numbering makes detection reliable
- Variations explicitly reference pattern numbers
- Structure is consistent across patterns

### Areas Needing Care
- Must strip labels cleanly without losing content
- Variation to pattern mapping must be accurate
- Handle edge cases where sections might be missing
