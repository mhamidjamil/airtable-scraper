# Airtable Scraper Project

A modular Python application to extract data from Word documents and sync it to Airtable.

## Project Structure

```
airtable_scraper/
├── config/
│   └── settings.py          # Configuration (Paths, API Keys)
├── modules/
│   ├── data_extractor.py    # Extracts Patterns, Variations, Metas, Lenses from DOCX
│   └── airtable_uploader.py # Syncs data to Airtable (Read -> Match -> Update)
├── json_data/               # Stores extracted JSON data
├── logs/                    # Execution logs
└── main.py                  # Main entry point
```

## Features

1.  **Data Extraction**:
    *   **Patterns**: Extracts Title, Overview, Choice, Source.
    *   **Variations**: Handles multiple formats (including implicit uppercase titles).
    *   **Metas**: Extracts Title, Subtitle, Content.
    *   **Lenses**: Derived from filenames.
    *   **Sources**: Extracted from pattern details.

2.  **Airtable Sync**:
    *   **Smart Sync**: Reads existing data first to build a map.
    *   **Update Logic**: Matches by unique keys (e.g., Title) and updates existing records instead of creating duplicates.
    *   **Relational Linking**: Automatically links Patterns to Lenses, Sources, and Variations.

## How to Run

1.  **Configure**:
    *   Check `config/settings.py` to ensure your API Token and Base ID are correct.
    *   Verify `SOURCE_DIR` points to your `new_extractions` folder.

2.  **Run**:
    ```bash
    python main.py
    ```

3.  **Check Results**:
    *   Console output will show progress.
    *   Logs are saved in `logs/`.
    *   Extracted data is saved in `json_data/`.
    *   Check Airtable to see the synced records.

## Requirements

*   `python` (3.8+)
*   `python-docx`
*   `requests`
