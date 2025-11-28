Rovo Dev – Session Summary and Learnings

Problem we set out to solve
- Inconsistent DOCX structures across projects (e.g., BUSINESS/STEP 2) causing unreliable extraction and linking.
- Variations sometimes missing or mis-mapped to patterns due to inconsistent labels, numbering, and formatting.
- Desire for a “brain” that understands documents by meaning, not just string matching, and can learn over time.

What we built
1) New robust extractor and linker (rovo_dev)
   - Extracts titles AND body sections for patterns and variations.
   - Flexible heading detection: Pattern/Task/Part and Variation/Var/Option + generic numbered headings (1) Title, 1. Title, etc.).
   - Multi-stage linking order:
     1) Optional index mapping (can disable)
     2) Semantic GPU mapping (SentenceTransformers)
     3) Fuzzy-title fallback
     4) Knowledge Base (kb.json) mappings
     5) Optional Gemini LLM mapping
     6) Final fallback to Pattern 1 (logged)

2) GPU semantic “brain”
   - rovo_dev/semantic_mapper.py uses SentenceTransformers (CUDA if available).
   - Embeds titles + body content, mapping by meaning (cosine similarity) instead of raw string similarity.
   - Configurable threshold and model; exposes confidence (_semantic_score).

3) Trainable adapter (lightweight model tuning)
   - rovo_dev/train.py and rovo_dev/trainer.py: trains a projection adapter (.pt) on your data using pseudo-labels.
   - Adapters are saved per project under rovo_dev/trained_models/{project}/adapter.pt.
   - Improves alignment for your domain (vocabulary, style, repeated structures).

4) Run summaries and documentation for resumability
   - rovo_dev/run_summaries: per-run .md and .json with counts of semantic/fuzzy/fallback mappings.
   - rovo_dev/WORKFLOW_SUMMARY.md: authoritative workflow design, usage, and continuation plan.

5) Document fixer (normalized outputs)
   - rovo_dev/doc_fixer.py generates normalized, corrected Markdown (and optional DOCX) using the learned mapping.
   - Outputs to rovo_dev/normalized/{project}/ with a patch report JSON.
   - Does not modify originals.

Key files in rovo_dev
- __init__.py, __main__.py (package + CLI entry)
- main.py (extract + link + run summary)
- extractor.py (DOCX parsing with sections)
- linker.py (multi-stage linking pipeline)
- semantic_mapper.py (SentenceTransformer + optional adapter)
- trainer.py, train.py (adapter training)
- doc_fixer.py (normalized outputs from learned mappings)
- knowledge.py (kb.json learnings)
- llm_client.py (optional Gemini)
- text_utils.py (normalization + fuzzy utils)
- config.py (env and paths)
- WORKFLOW_SUMMARY.md (process reference)

How to run (PowerShell examples)
1) Install dependencies
- GPU (CUDA):
  - pip install torch --index-url https://download.pytorch.org/whl/cu121
- CPU (fallback):
  - pip install torch
- Common:
  - pip install sentence-transformers python-docx google-generativeai

2) Train adapter on your data (self-training)
- python -m rovo_dev.train --folder "E:/Work/shoaib/upwork/new_extractions" --model multi-qa-mpnet-base-dot-v1 --epochs 3 --lr 1e-4 --batch-size 32
- Produces adapters: rovo_dev/trained_models/{project}/adapter.pt

3) Run extractor/mapper using trained adapter (example PAULA)
- Optional Gemini fallback:
  - $env:GEMINI_API_KEY="YOUR_KEY"
- Command:
  - python -m rovo_dev --folder "E:/Work/shoaib/upwork/new_extractions/PAULA" --no-index-map --semantic-model multi-qa-mpnet-base-dot-v1 --semantic-threshold 0.4 --adapter rovo_dev/trained_models/paula/adapter.pt --use-ai
- Outputs:
  - JSON data: airtable_scraper/json_data/rovo_dev_paula_{timestamp}.json
  - Run summary: rovo_dev/run_summaries/summary_paula_{timestamp}.md and .json

4) Create normalized “fixed” documents (example PAULA)
- python -m rovo_dev.doc_fixer --folder "E:/Work/shoaib/upwork/new_extractions/PAULA" --adapter rovo_dev/trained_models/paula/adapter.pt --no-index-map --semantic-threshold 0.4 --write-docx --use-ai
- Outputs:
  - rovo_dev/normalized/paula/*_normalized.md (and .docx if --write-docx)
  - rovo_dev/normalized/paula/patch_report_paula_{timestamp}.json

Tuning & troubleshooting
- Threshold: increase --semantic-threshold to reduce loose matches; decrease to accept more matches.
- Model choices: multi-qa-mpnet-base-dot-v1 (default), BAAI/bge-large-en-v1.5, intfloat/e5-large-v2.
- Disable naive 1-to-1 index mapping for messy docs: use --no-index-map.
- CPU fallback works but is slower if CUDA not found.
- If mapping still struggles, share the run summary .md; we can add unique-assignment optimization (Hungarian) and rebalance passes.

Why this addresses prior issues
- Uses section bodies + semantic embeddings for meaning-based mapping, not just title string matching.
- Trained adapter specializes the space for your corpus and recurring patterns.
- Knowledge base remembers fixes; LLM only used for hard cases if enabled.
- Normalized outputs provide consistent structure, so you won’t need to manually point out missing variations or mis-linked patterns repeatedly.

Integration options (future work)
- Wire rovo_dev into airtable_scraper/main.py with a --rovo-dev flag to upload directly to Airtable via existing AirtableUploader.
- Add unique-assignment optimization to avoid over-assigning variations to a single pattern.
- Create Jira items for ongoing enhancements and a Confluence page documenting the pipeline.

Quick checklist (one page)
- Train: python -m rovo_dev.train --folder "E:/Work/shoaib/upwork/new_extractions" --model multi-qa-mpnet-base-dot-v1 --epochs 3 --lr 1e-4 --batch-size 32
- Map: python -m rovo_dev --folder "E:/Work/shoaib/upwork/new_extractions/PAULA" --no-index-map --semantic-model multi-qa-mpnet-base-dot-v1 --semantic-threshold 0.4 --adapter rovo_dev/trained_models/paula/adapter.pt --use-ai
- Fix: python -m rovo_dev.doc_fixer --folder "E:/Work/shoaib/upwork/new_extractions/PAULA" --adapter rovo_dev/trained_models/paula/adapter.pt --no-index-map --semantic-threshold 0.4 --write-docx --use-ai

End of session
- This file plus WORKFLOW_SUMMARY.md and the run summaries are enough to resume quickly at any time.
- If you want a one-click script (PowerShell) to do everything, I can add rovo_dev/run_all.ps1 next session.
