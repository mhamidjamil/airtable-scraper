Rovo Dev End-to-End Workflow, Model Strategy, and Continuation Plan

Purpose
- This document is the authoritative summary of the extraction + mapping workflow so we can resume anytime. It captures: goals, steps, heuristics, GPU semantic mapping, AI fallback, knowledge base behavior, and how to run and diagnose issues.

High-level goals
- Extract Lenses, Patterns, Variations, and Sources from inconsistent DOCX files (with STEP 2 subfolders where present).
- Robustly map variations to the correct patterns using meaning, not just title similarity.
- Avoid recurring manual fixes by learning from prior runs (knowledge base), with optional LLM for hard cases.

Pipeline overview
1) Project discovery
   - A project folder is one that has a STEP 2 folder or contains DOCX files directly.
2) DOCX parsing
   - Extract summary (stop at first Pattern/Task/Part marker)
   - Detect pattern headings (Pattern/Task/Part N: Title) and capture their bodies
   - Detect variation headings (Variation/Var/Option N: Title) and capture their bodies
   - Also accept numbered headings like "1) Title" for variations if explicit labels are missing
3) Mapping (variation -> pattern)
   - Optional index-based mapping (can be disabled with --no-index-map)
   - GPU semantic similarity using SentenceTransformers (CUDA if available) with titles+sections for both patterns and variations
   - Fuzzy title fallback if still unresolved
   - Knowledge-base mapping using kb.json for previously learned cases
   - Optional Gemini mapping for edge cases
   - Final fallback: attach remaining variations to Pattern 1 (logged)
4) Output
   - JSON saved under airtable_scraper/json_data/rovo_dev_{project}_{timestamp}.json
   - Run summaries saved to rovo_dev/run_summaries in both .md and .json form (counts, mapping types, unresolved, file list)

GPU semantic mapping details
- Model: default multi-qa-mpnet-base-dot-v1 (configurable)
- Device: CUDA if available, else CPU
- Threshold: default 0.35 (configurable). Raise to be safer.
- Uses titles + section bodies for patterns and variations for better context matching.

Knowledge base
- File: rovo_dev/knowledge/kb.json
- Stores lens-specific mapping overrides: { lens_name: { variation_number -> pattern_number } }
- Learns from LLM mapping decisions and can be extended manually if needed.

LLM fallback (optional)
- Provider: Google Gemini (via google-generativeai)
- Activation: --use-ai and GEMINI_API_KEY set in environment
- Only used after semantic and KB attempts

How to run
- Requirements:
  - pip install torch --index-url https://download.pytorch.org/whl/cu121
  - pip install sentence-transformers python-docx google-generativeai
- Command (from project root):
  - python -m rovo_dev --folder "E:/Work/shoaib/upwork/new_extractions/PAULA" --no-index-map --semantic-model multi-qa-mpnet-base-dot-v1 --semantic-threshold 0.4 --use-ai
- Output:
  - JSON: airtable_scraper/json_data/rovo_dev_paula_{timestamp}.json
  - Summary: rovo_dev/run_summaries/summary_paula_{timestamp}.md and .json

What to share back for analysis
- The summary Markdown (or JSON) from rovo_dev/run_summaries
- The output JSON if needed for deeper inspection

Resuming after disconnects
- This document + the run summary are sufficient context to continue any time.
- If results are off, increase --semantic-threshold and/or try a stronger model: BAAI/bge-large-en-v1.5 or intfloat/e5-large-v2
- If a specific lens consistently mis-maps, add KB overrides or share the summary so we can extend heuristics.

Planned improvements
- Unique-assignment optimization (Hungarian algorithm) to avoid over-assigning to one pattern
- Post-mapping sanity checks and rebalancing
- Optional integration flag in airtable_scraper/main.py for direct Airtable sync
