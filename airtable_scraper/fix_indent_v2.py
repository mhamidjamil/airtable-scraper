lines = []
with open('modules/data_extractor.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the start of the loop
start_idx = -1
for i, line in enumerate(lines):
    if 'for f in target_dir.glob("*.docx"):' in line:
        start_idx = i
        break

if start_idx != -1:
    # Indent everything from start_idx + 1 until the end of the method
    # The method ends when indentation drops back to class level (4 spaces)
    # But process_folder is at 4 spaces. The loop is at 12 spaces now.
    # The body should be at 16 spaces.
    
    # We want to add 4 spaces to every line in the body.
    
    for i in range(start_idx + 1, len(lines)):
        if lines[i].strip(): # Skip empty lines
            # Check if it's the end of the method
            # The loop is at 12 spaces. If we see something at 8 spaces or less, it's outside.
            current_indent = len(lines[i]) - len(lines[i].lstrip())
            if current_indent <= 8:
                break # End of method/loop scope
            
            # Add 4 spaces
            lines[i] = '    ' + lines[i]

with open('modules/data_extractor.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
