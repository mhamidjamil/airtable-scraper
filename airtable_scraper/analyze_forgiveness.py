import json

with open('logs/inspection_BULLSHIT_20251127_210647.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find variations for FORGIVENESS pattern
forgiveness_vars = [v for v in data['details']['variations'] if 'FORGIVENESS' in v['pattern']]

print(f"Found {len(forgiveness_vars)} variations for FORGIVENESS pattern:")
for i, v in enumerate(forgiveness_vars, 1):
    print(f"{i}. {v['title']}")

# Find the lens
patterns = [p for p in data['details']['patterns'] if 'FORGIVENESS' in p['title']]
if patterns:
    print(f"\nLens: {patterns[0]['lens']}")
    print(f"Expected variations: 10")
    print(f"Actual variations: {len(forgiveness_vars)}")
