Rovo Dev Robust Extraction Pipeline

Overview
- This module provides a robust, AI-optional pipeline to extract Lenses, Patterns, Variations, and Sources from messy, inconsistent DOCX structures.
- It is designed to handle folder structures like BUSINESS/STEP 2 with variable naming, inconsistent headings, and missing or malformed labels.
- It uses a stack of heuristics and can optionally call an LLM (e.g., Google Gemini) to resolve difficult cases. It also maintains a lightweight knowledge base to "learn" common anomalies and mappings over time.

Key features
- Flexible project discovery: auto-detects projects that contain a STEP 2 folder or DOCX files.
- DOCX parsing with multiple regex patterns to detect patterns and variations even when labels vary (Pattern 1:, Variation 1 -, 1) Title, etc.).
- Captures section bodies for both patterns and variations for richer semantic context.
- Summary extraction that stops at the first pattern/task marker.
- Multi-strategy linking of variations to patterns:
  1) Semantic similarity on GPU via SentenceTransformers (CUDA if available)
  2) Fuzzy matching of titles as a fallback
  3) Knowledge-base mappings learned from previous runs
  4) Optional Gemini-assisted mapping when enabled
  5) Final fallback: attach unresolved variations to Pattern 1
- Knowledge base (JSON) that stores observed anomalies, synonyms, and successful mappings to improve future runs.
- Clean JSON output for integration with existing uploader or further processing.

Structure
- rovo_dev/config.py: Toggle AI usage, API keys (via env), output settings.
- rovo_dev/text_utils.py: Normalization, fuzzy matching helpers.
- rovo_dev/llm_client.py: Optional Gemini client wrapper (safe no-op if not configured).
- rovo_dev/extractor.py: DOCX parsing, summary/pattern/variation/source extraction.
- rovo_dev/linker.py: Variation-to-pattern linking strategies with knowledge base support.
- rovo_dev/semantic_mapper.py: SentenceTransformer + optional trained adapter for semantic mapping.
- rovo_dev/trainer.py: Projection adapter training utilities.
- rovo_dev/train.py: CLI to train an adapter on your folders.
- rovo_dev/main.py: CLI entry point to run extraction on a folder.
- rovo_dev/doc_fixer.py: CLI to generate normalized, corrected Markdown/DOCX using learned mappings.
- rovo_dev/knowledge/kb.json: Lightweight knowledge base persisted across runs.

Usage
- Install (GPU optional but recommended):
  - pip install torch --index-url https://download.pytorch.org/whl/cu121  (choose your CUDA version)
  - pip install sentence-transformers python-docx google-generativeai
- Train an adapter on your folder (self-training with pseudo-labels):
  - python -m rovo_dev.train --folder "E:/Work/shoaib/upwork/new_extractions" --model multi-qa-mpnet-base-dot-v1 --epochs 3 --lr 1e-4 --batch-size 32
  - Trained weights saved to rovo_dev/trained_models/{project}/adapter.pt
- Run extraction with the trained adapter:
  - python -m rovo_dev --folder "E:/Work/shoaib/upwork/new_extractions/PAULA" --no-index-map --semantic-model multi-qa-mpnet-base-dot-v1 --semantic-threshold 0.4 --adapter rovo_dev/trained_models/paula/adapter.pt --use-ai
- Generate normalized, corrected docs (Markdown/DOCX) using learned mappings:
  - python -m rovo_dev.doc_fixer --folder "E:/Work/shoaib/upwork/new_extractions/PAULA" --adapter rovo_dev/trained_models/paula/adapter.pt --no-index-map --semantic-threshold 0.4 --write-docx --use-ai
  - Outputs under rovo_dev/normalized/paula/* with a patch_report JSON
- Output: JSON saved under airtable_scraper/json_data/rovo_dev_{folder}.json

Design notes
- Heuristics are designed to be conservative and deterministic. AI is used only when enabled and only as a suggestion layer.
- The knowledge base records mismatches and label/heading variants. Over time, this reduces the need for AI calls.

Integration
- You can feed the resulting JSON to the existing AirtableUploader (if desired) or keep this extractor standalone.
- If you want me to wire this into airtable_scraper/main.py behind a flag (e.g., --rovo-dev), I can add that after your approval.

