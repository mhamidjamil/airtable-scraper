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
    # Currently the body is at 12 spaces (from previous indentation).
    
    for i in range(start_idx + 1, len(lines)):
        if lines[i].strip() and not lines[i].startswith(' ' * 16):
            # Check if it's the end of the method
            if lines[i].strip() and not lines[i].startswith(' ' * 8):
                break # End of method
            
            # Add 4 spaces
            lines[i] = '    ' + lines[i]

with open('modules/data_extractor.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
