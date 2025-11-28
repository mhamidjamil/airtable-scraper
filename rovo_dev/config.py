import os
from pathlib import Path

# Configuration for Rovo Dev extractor
USE_AI = bool(os.getenv("ROVO_DEV_USE_AI", "").strip())
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Output directory (reuse existing json_data if present)
WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = WORKSPACE_ROOT / "airtable_scraper" / "json_data"
DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Knowledge base file
KB_DIR = Path(__file__).resolve().parent / "knowledge"
KB_DIR.mkdir(parents=True, exist_ok=True)
KB_PATH = KB_DIR / "kb.json"

# Limits
MAX_AI_TOKENS = int(os.getenv("ROVO_DEV_MAX_AI_TOKENS", "2000"))
AI_ENABLED = USE_AI and bool(GEMINI_API_KEY)
