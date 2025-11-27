lines = []
with open('modules/data_extractor.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the try block inside the loop
try_idx = -1
for i, line in enumerate(lines):
    if 'try:' in line and 'docx' not in line: # Avoid other try blocks if any
        # Check indentation
        if len(line) - len(line.lstrip()) == 20: # It's at 20 spaces now
            try_idx = i
            break

if try_idx != -1:
    print(f"Found try at line {try_idx+1}")
    # Indent everything from try_idx + 1 until except
    for i in range(try_idx + 1, len(lines)):
        if 'except Exception as e:' in lines[i]:
            break
        if lines[i].strip():
            lines[i] = '    ' + lines[i]

with open('modules/data_extractor.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
