# AI Context & Generic Extraction Rules

This document defines the generic rules and project structure for the Airtable Scraper. It serves as the source of truth for AI agents and automated processes working on this codebase.

## 1. Project Structure
The project is designed to be modular and scalable.
- **`main.py`**: Entry point. Handles argument parsing and orchestrates the extraction and sync process. Supports recursive folder discovery.
- **`modules/`**: Contains core logic.
    - `data_extractor.py`: Orchestrates data extraction from files.
    - `airtable_uploader.py`: Handles data synchronization with Airtable.
- **`extraction_rules/`**: Contains specific regex and parsing logic.
    - `variation_rules.py`: Rules for extracting Variations.
    - `source_rules.py`: Rules for extracting Sources.
- **`config/`**: Configuration settings.

## 2. Extraction Logic

### A. Variations
**Goal**: Extract exactly 10 variations per file.
**Linking Logic**:
1.  **Explicit Mode**: If *any* variation in a file explicitly references a pattern (e.g., "Variation 9 – PATTERN 9..."), we assume a **1-to-1 mapping** for the entire file.
    -   Variation 1 -> Pattern 1
    -   Variation 2 -> Pattern 2
    -   ...
    -   Variation 10 -> Pattern 10
2.  **Implicit Mode**: If *no* variations in a file reference a pattern, **ALL** variations are linked to **Pattern 1**.

**Regex Formats Supported**:
-   `Variation X – PATTERN Y: Title` (Explicit)
-   `– PATTERN Y: Title` (Implicit Variation, Explicit Pattern)
-   `Variation X – Title`
-   `X – Title` (where 0 = 10)
-   `– TITLE IN CAPS` (Implicit Dash Title)

### B. Metas
**Goal**: Extract metadata from the `METAS` folder.
**Linking Logic**:
-   **All-to-All**: All Meta files found in the `METAS` folder of a project are linked to **EVERY** Pattern found in that same project.
-   Example: If `PAULA` has 5 Metas and 10 Patterns, each of the 10 Patterns will be linked to all 5 Metas.

### C. Sources
**Goal**: Extract sources from Pattern descriptions.
-   Sources are parsed using `SourceExtractor`.
-   They are linked to the Pattern they were found in.
-   They are stored in the `Sources` table with a composite key to prevent duplicates.

## 3. Airtable Sync
-   **Selective Sync**: Can sync specific tables (`--patterns`, `--variations`, etc.) or all.
-   **Relationships**:
    -   Patterns -> Lenses (Many-to-One)
    -   Patterns -> Sources (Many-to-Many)
    -   Patterns -> Metas (Many-to-Many)
    -   Patterns -> Variations (One-to-Many)

## 4. Future Improvements
-   Always prefer generic regex patterns over hardcoded logic.
-   Maintain separation of concerns: `extraction_rules` for parsing, `modules` for flow.
