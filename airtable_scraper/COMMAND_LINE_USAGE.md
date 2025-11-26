# Command Line Usage Guide

## Basic Usage

### Full Sync (Extract and upload everything)
```bash
python main.py
python main.py --folder BIOME
```

### Selective Sync (Case-insensitive)
```bash
# Sync only patterns
python main.py --patterns
python main.py --sync --patterns
python main.py --PATTERNS

# Sync only variations
python main.py --variations
python main.py --sync --variations
python main.py --VARIATIONS

# Sync multiple types
python main.py --patterns --variations
python main.py --patterns --lenses --sources

# Sync specific folder with specific types
python main.py --folder QUANTUM --patterns --variations
```

### Extract Only (No Airtable sync)
```bash
python main.py --extract-only
python main.py --extract-only --folder BIOME
```

## Available Options

- `--sync`: Enable sync mode (optional flag, implied when using specific types)
- `--patterns` / `--pattern` / `--PATTERNS`: Sync only patterns
- `--variations` / `--variation` / `--VARIATIONS`: Sync only variations  
- `--lenses` / `--lens` / `--LENSES`: Sync only lenses
- `--metas` / `--meta` / `--METAS`: Sync only metas
- `--sources` / `--source` / `--SOURCES`: Sync only sources
- `--folder` / `-f`: Specify target folder (default: BIOME)
- `--extract-only`: Only extract data, skip Airtable sync

## Examples

```bash
# Extract and sync only patterns from BIOME folder
python main.py --patterns

# Extract and sync variations from QUANTUM folder
python main.py --folder QUANTUM --variations

# Extract everything but don't sync to Airtable
python main.py --extract-only

# Sync patterns and variations (case-insensitive)
python main.py --PATTERNS --VARIATIONS
```