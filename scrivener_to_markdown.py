import xml.etree.ElementTree as ET
from pathlib import Path
import re
from striprtf.striprtf import rtf_to_text
import os

class ScrivenerToMarkdown:
    def __init__(self, scrivener_path, output_path):
        self.scrivener_path = Path(scrivener_path)
        self.output_path = Path(output_path)
        self.scrivx_file = self.scrivener_path / f"{self.scrivener_path.stem}.scrivx"
        self.data_path = self.scrivener_path / "Files" / "Data"
        self.documents = []
        
    def parse_scrivx(self):
        """Parse the .scrivx XML file to extract document structure"""
        print(f"📖 Parsing {self.scrivx_file.name}...")
        tree = ET.parse(self.scrivx_file)
        root = tree.getroot()
        
        # Find the Binder element
        binder = root.find('Binder')
        if binder is None:
            raise Exception("No Binder found in scrivx file")
        
        # Parse the binder tree
        self._parse_binder_item(binder, [])
        print(f"✅ Found {len(self.documents)} documents")
        return self.documents
    
    def _parse_binder_item(self, item, path):
        """Recursively parse binder items"""
        for child in item:
            if child.tag == 'BinderItem':
                uuid = child.get('UUID')
                item_type = child.get('Type')
                
                # Get title
                title_elem = child.find('Title')
                title = title_elem.text if title_elem is not None and title_elem.text else "Untitled"
                
                # Build path
                current_path = path + [self._sanitize_filename(title)]
                
                if item_type == 'Folder':
                    # Process folder - just add to path
                    children = child.find('Children')
                    if children is not None:
                        self._parse_binder_item(children, current_path)
                
                elif item_type == 'Text':
                    # This is a document
                    created = child.get('Created', '')
                    modified = child.get('Modified', '')
                    
                    self.documents.append({
                        'uuid': uuid,
                        'title': title,
                        'path': current_path,
                        'created': created,
                        'modified': modified,
                        'type': item_type
                    })
                    
                    # Check for children (nested documents)
                    children = child.find('Children')
                    if children is not None:
                        self._parse_binder_item(children, current_path)
    
    def _sanitize_filename(self, name):
        """Remove invalid characters from filename"""
        # Replace invalid characters with underscore
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', name)
        # Remove leading/trailing whitespace and dots
        sanitized = sanitized.strip('. ')
        return sanitized if sanitized else "unnamed"
    
    def extract_rtf_content(self, uuid):
        """Extract text content from RTF file"""
        rtf_path = self.data_path / uuid / "content.rtf"
        
        if not rtf_path.exists():
            return ""
        
        try:
            with open(rtf_path, 'r', encoding='utf-8', errors='ignore') as f:
                rtf_content = f.read()
            
            # Convert RTF to plain text
            text = rtf_to_text(rtf_content)
            return text.strip()
        except Exception as e:
            print(f"⚠️  Error reading {rtf_path}: {e}")
            return ""
    
    def convert_to_markdown(self):
        """Convert all documents to Markdown files"""
        print(f"\n📝 Converting to Markdown...")
        
        # Create output directory
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        converted_count = 0
        skipped_count = 0
        
        for doc in self.documents:
            # Extract content
            content = self.extract_rtf_content(doc['uuid'])
            
            if not content:
                skipped_count += 1
                continue
            
            # Build folder path
            if len(doc['path']) > 1:
                folder_path = self.output_path / Path(*doc['path'][:-1])
                folder_path.mkdir(parents=True, exist_ok=True)
            else:
                folder_path = self.output_path
            
            # Create markdown file
            filename = f"{doc['path'][-1]}.md"
            file_path = folder_path / filename
            
            # Build markdown content with frontmatter
            markdown_content = self._build_markdown(doc, content)
            
            # Write file
            try:
                with open(file_path, 'w', encoding='utf-8', errors='ignore') as f:
                    f.write(markdown_content)
            except Exception as e:
                print(f"⚠️  Error writing {file_path}: {e}")
                continue
            
            converted_count += 1
            if converted_count % 50 == 0:
                print(f"  ✓ Converted {converted_count} documents...")
        
        print(f"\n✅ Conversion complete!")
        print(f"   📄 Converted: {converted_count} documents")
        print(f"   ⏭️  Skipped: {skipped_count} empty documents")
        print(f"   📁 Output: {self.output_path}")
        
        return converted_count
    
    def _build_markdown(self, doc, content):
        """Build markdown content with frontmatter"""
        # Create YAML frontmatter
        frontmatter = "---\n"
        frontmatter += f"title: {doc['title']}\n"
        frontmatter += f"uuid: {doc['uuid']}\n"
        frontmatter += f"path: {'/'.join(doc['path'])}\n"
        if doc['created']:
            frontmatter += f"created: {doc['created']}\n"
        if doc['modified']:
            frontmatter += f"modified: {doc['modified']}\n"
        frontmatter += "---\n\n"
        
        # Add title as H1
        markdown = frontmatter
        markdown += f"# {doc['title']}\n\n"
        markdown += content
        
        return markdown
    
    def generate_index(self):
        """Generate an index.md file with the document tree"""
        print(f"\n📑 Generating index...")
        
        index_content = "# Document Index\n\n"
        index_content += f"Total Documents: {len(self.documents)}\n\n"
        index_content += "## Document Tree\n\n"
        
        # Group by top-level folder
        folders = {}
        for doc in self.documents:
            if len(doc['path']) > 0:
                top_folder = doc['path'][0]
                if top_folder not in folders:
                    folders[top_folder] = []
                folders[top_folder].append(doc)
        
        # Generate tree
        for folder, docs in sorted(folders.items()):
            index_content += f"### {folder}\n\n"
            for doc in docs:
                rel_path = '/'.join(doc['path'])
                index_content += f"- [{doc['title']}]({rel_path}.md)\n"
            index_content += "\n"
        
        # Write index file
        index_path = self.output_path / "INDEX.md"
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        print(f"✅ Index created: {index_path}")

def main():
    # Configuration
    scrivener_project = r"E:\Work\shoaib\upwork\shoaib53%202025-11-22%2007-11\shoaib53.scriv"
    output_folder = r"E:\Work\shoaib\upwork\markdown_export"
    
    print("=" * 60)
    print("🚀 Scrivener to Markdown Converter")
    print("=" * 60)
    print(f"📂 Source: {scrivener_project}")
    print(f"📂 Output: {output_folder}")
    print("=" * 60)
    
    # Create converter
    converter = ScrivenerToMarkdown(scrivener_project, output_folder)
    
    # Parse structure
    converter.parse_scrivx()
    
    # Convert to markdown
    converter.convert_to_markdown()
    
    # Generate index
    converter.generate_index()
    
    print("\n" + "=" * 60)
    print("✨ Conversion Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
