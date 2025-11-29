import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).parent.parent
LOG_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "json_data"
SOURCE_DIR = Path(r"E:\Work\shoaib\upwork\new_extractions")

# Load .env file manually to avoid external dependencies
env_path = BASE_DIR.parent / ".env"
if env_path.exists():
    with open(env_path, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()

# Airtable Configuration
api_token = os.getenv("AIRTABLE_API_TOKEN")
base_id = os.getenv("AIRTABLE_BASE_ID")

if not api_token or not base_id:
    # Fallback or warning
    print("WARNING: Airtable credentials not found in .env file")

AIRTABLE_CONFIG = {
    "api_token": api_token,
    "base_id": base_id,
    "tables": {
        "lenses": "Lenses",
        "sources": "Sources",
        "metas": "Metas",
        "variations": "Variations",
        "patterns": "Patterns",
        "choices": "Choices"
    }
}

# Ensure directories exist
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
