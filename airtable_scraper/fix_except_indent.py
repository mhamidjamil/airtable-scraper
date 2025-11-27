lines = []
with open('modules/data_extractor.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the except block inside the loop
except_idx = -1
for i, line in enumerate(lines):
    if 'except Exception as e:' in line:
        # Check indentation
        if len(line) - len(line.lstrip()) == 20:
            except_idx = i
            break

if except_idx != -1:
    print(f"Found except at line {except_idx+1}")
    # Indent the next line (self.log)
    if i + 1 < len(lines):
        lines[i+1] = '    ' + lines[i+1]

with open('modules/data_extractor.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
