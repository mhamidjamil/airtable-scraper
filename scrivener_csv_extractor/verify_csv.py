import csv
import os

CSV_FILE = r"E:\Work\shoaib\upwork\scrivener_csv_extractor\scrivener_data.csv"

def analyze_csv(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    total_rows = 0
    planning_count = 0
    revision_count = 0
    metadata_count = 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_rows += 1
            if row.get("Planning", "").strip():
                planning_count += 1
            if row.get("Revision", "").strip():
                revision_count += 1
            if row.get("Metadata", "").strip():
                metadata_count += 1
                
    print(f"Total Records: {total_rows}")
    print(f"Records with Planning: {planning_count}")
    print(f"Records with Revision: {revision_count}")
    print(f"Records with Metadata: {metadata_count}")

if __name__ == "__main__":
    analyze_csv(CSV_FILE)
