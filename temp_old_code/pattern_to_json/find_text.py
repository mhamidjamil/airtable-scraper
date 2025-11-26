import os
from docx import Document

def search_docx(directory, search_term):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".docx"):
                path = os.path.join(root, file)
                try:
                    doc = Document(path)
                    for para in doc.paragraphs:
                        if search_term.lower() in para.text.lower():
                            print(f"Found in: {path}")
                            return
                except Exception as e:
                    print(f"Error reading {path}: {e}")

search_docx(r"E:\Work\shoaib\upwork\pattern_to_json", "HOME_SPINE")
