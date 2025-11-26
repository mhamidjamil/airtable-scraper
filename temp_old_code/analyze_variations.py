import json

# Load the extracted data
data = json.load(open(r'airtable_manager\data_output\biome_extracted_20251126_155956.json', encoding='utf-8'))

# Find the Ecological document
eco_doc = [d for d in data['documents'] if 'Ecological' in d['lens']][0]

print("=" * 80)
print("VARIATIONS FOUND IN: Ecological & Microbial Consciousness")
print("=" * 80)
print()

for pattern in eco_doc['patterns']:
    print(f"Pattern {pattern['pattern_number']}: {pattern['title']}")
    print(f"  Variations: {len(pattern['variations'])}")
    for v in pattern['variations']:
        print(f"    {v['variation_number']}: {v['title']}")
    print()

# Count total variations
total = sum(len(p['variations']) for p in eco_doc['patterns'])
print(f"TOTAL VARIATIONS: {total}")
print()

# Expected variations from user
expected_variations = [
    "PLANETARY NERVOUS SYSTEM",
    "YOUR ANXIETY IS EARTH'S FEVER",
    "ONE FIELD, MANY SCALES",
    "COLLECTIVE PSYCHE BLEEDING",
    "THE SOIL REMEMBERS",
    "INNER CLIMATE, OUTER CLIMATE",
    "WATERSHED CONSCIOUSNESS",
    "WE ARE THE CORAL REEF",
    "MYCORRHIZAL EMPATHY",
    "RECIPROCAL RESTORATION"
]

print("EXPECTED VARIATIONS:")
for i, title in enumerate(expected_variations, 1):
    print(f"  {i}: {title}")
print()

# Find all extracted variation titles
extracted_titles = [v['title'].upper() for p in eco_doc['patterns'] for v in p['variations']]

print("MISSING VARIATIONS:")
for title in expected_variations:
    if title not in extracted_titles:
        print(f"  - {title}")
