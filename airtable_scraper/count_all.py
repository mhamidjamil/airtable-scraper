import json
from collections import Counter

with open('logs/inspection_BULLSHIT_20251127_210647.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Count variations per pattern
pattern_counts = Counter([v['pattern'] for v in data['details']['variations']])

print("Variations per pattern:")
print("="*80)
for pattern, count in sorted(pattern_counts.items(), key=lambda x: x[1]):
    print(f"{count:2d} variations: {pattern[:70]}")

print("="*80)
print(f"Total patterns: {len(pattern_counts)}")
print(f"Total variations: {sum(pattern_counts.values())}")
print(f"Expected: {data['summary']['total_patterns'] * 10}")
