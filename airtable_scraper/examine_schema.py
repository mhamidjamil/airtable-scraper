#!/usr/bin/env python3
"""
Script to examine Airtable schema and identify linking field names
"""

import requests
import json
from config.settings import AIRTABLE_CONFIG

def fetch_table_schema(table_name):
    """Fetch the schema for a specific table"""
    url = f"https://api.airtable.com/v0/meta/bases/{AIRTABLE_CONFIG['base_id']}/tables"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_CONFIG['api_token']}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Find the specific table
        for table in data.get('tables', []):
            if table['name'] == table_name:
                return table
        
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching schema for {table_name}: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def analyze_linking_fields(table_schema):
    """Analyze fields to identify linking relationships"""
    if not table_schema:
        return {}
    
    linking_fields = {}
    
    for field in table_schema.get('fields', []):
        field_type = field.get('type')
        field_name = field.get('name')
        
        # Check for linking fields
        if field_type == 'multipleRecordLinks':
            options = field.get('options', {})
            linked_table_id = options.get('linkedTableId')
            is_reversed = options.get('isReversed', False)
            
            linking_fields[field_name] = {
                'type': field_type,
                'linked_table_id': linked_table_id,
                'is_reversed': is_reversed,
                'options': options
            }
    
    return linking_fields

def main():
    print("Examining Airtable Schema for Patterns and Variations tables...")
    print("=" * 60)
    
    # Fetch schemas for both tables
    patterns_schema = fetch_table_schema("Patterns")
    variations_schema = fetch_table_schema("Variations")
    
    if not patterns_schema:
        print("❌ Could not fetch Patterns table schema")
        return
    
    if not variations_schema:
        print("❌ Could not fetch Variations table schema")
        return
    
    print("✅ Successfully fetched both table schemas")
    print()
    
    # Analyze Patterns table
    print("🔍 PATTERNS TABLE ANALYSIS")
    print("-" * 30)
    print(f"Table ID: {patterns_schema.get('id')}")
    print(f"Table Name: {patterns_schema.get('name')}")
    print()
    
    patterns_links = analyze_linking_fields(patterns_schema)
    if patterns_links:
        print("Linking fields in Patterns table:")
        for field_name, field_info in patterns_links.items():
            print(f"  📎 {field_name}")
            print(f"     Type: {field_info['type']}")
            print(f"     Linked Table ID: {field_info['linked_table_id']}")
            print(f"     Is Reversed: {field_info['is_reversed']}")
            print()
    else:
        print("No linking fields found in Patterns table")
    
    print()
    
    # Analyze Variations table
    print("🔍 VARIATIONS TABLE ANALYSIS")
    print("-" * 30)
    print(f"Table ID: {variations_schema.get('id')}")
    print(f"Table Name: {variations_schema.get('name')}")
    print()
    
    variations_links = analyze_linking_fields(variations_schema)
    if variations_links:
        print("Linking fields in Variations table:")
        for field_name, field_info in variations_links.items():
            print(f"  📎 {field_name}")
            print(f"     Type: {field_info['type']}")
            print(f"     Linked Table ID: {field_info['linked_table_id']}")
            print(f"     Is Reversed: {field_info['is_reversed']}")
            print()
    else:
        print("No linking fields found in Variations table")
    
    # Cross-reference the tables
    print("🔗 CROSS-REFERENCE ANALYSIS")
    print("-" * 30)
    
    patterns_table_id = patterns_schema.get('id')
    variations_table_id = variations_schema.get('id')
    
    print(f"Patterns table ID: {patterns_table_id}")
    print(f"Variations table ID: {variations_table_id}")
    print()
    
    # Find fields that link between these tables
    pattern_to_variation_fields = []
    variation_to_pattern_fields = []
    
    for field_name, field_info in patterns_links.items():
        if field_info['linked_table_id'] == variations_table_id:
            pattern_to_variation_fields.append(field_name)
    
    for field_name, field_info in variations_links.items():
        if field_info['linked_table_id'] == patterns_table_id:
            variation_to_pattern_fields.append(field_name)
    
    print("Fields linking Patterns → Variations:")
    for field in pattern_to_variation_fields:
        print(f"  ✅ {field}")
    
    print("Fields linking Variations → Patterns:")
    for field in variation_to_pattern_fields:
        print(f"  ✅ {field}")
    
    print()
    
    # Save detailed schemas to files
    with open("patterns_schema.json", "w", encoding="utf-8") as f:
        json.dump(patterns_schema, f, indent=2, ensure_ascii=False)
    
    with open("variations_schema.json", "w", encoding="utf-8") as f:
        json.dump(variations_schema, f, indent=2, ensure_ascii=False)
    
    print("💾 Detailed schemas saved to:")
    print("  - patterns_schema.json")
    print("  - variations_schema.json")
    
    # Summary
    print()
    print("📋 SUMMARY FOR CODE FIXES")
    print("-" * 30)
    print("Use these exact field names in your linking code:")
    print()
    if pattern_to_variation_fields:
        print(f"When creating/updating Patterns, link to Variations using field: '{pattern_to_variation_fields[0]}'")
    if variation_to_pattern_fields:
        print(f"When creating/updating Variations, link to Patterns using field: '{variation_to_pattern_fields[0]}'")

if __name__ == "__main__":
    main()