import json
import sys

def check_missing_variations(log_file):
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Log file not found: {log_file}")
        return

    print(f"Checking patterns from {len(data['details']['patterns'])} patterns...")
    
    # Group patterns by lens
    lens_variations = {}
    for p in data['details']['patterns']:
        lens = p.get('lens', 'Unknown Lens')
        if lens not in lens_variations:
            lens_variations[lens] = 0
        lens_variations[lens] += p.get('variations_count', 0)
        
    for lens, count in lens_variations.items():
        print(f"Lens: '{lens}' - Variations: {count}")
        if count < 10:
            print(f"  WARNING: Missing variations in '{lens}' (Found {count}, Expected 10)")

if __name__ == "__main__":
    # Find the latest inspection log
    import glob
    import os
    
    logs = glob.glob('logs/inspection_*.json')
    if not logs:
        print("No inspection logs found.")
    else:
        latest_log = max(logs, key=os.path.getctime)
        print(f"Analyzing latest log: {latest_log}")
        check_missing_variations(latest_log)
