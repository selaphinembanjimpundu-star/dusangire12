import os
import re

def fix_split_tags(directory):
    # Regex to find tags starting with {% or {{ but not closing on the same line
    # This is a bit tricky, but we can look for unmatched open braces
    
    tag_start = re.compile(r'({%|{{)[^}%]*$')
    tag_end = re.compile(r'^\s*[^%{]*([}%]})')

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                new_lines = []
                skip = 0
                changed = False
                
                i = 0
                while i < len(lines):
                    line = lines[i]
                    # Check if line ends with an unclosed tag
                    # Simple heuristic: ends with {% or {{ and doesn't have closing % } or } }
                    stripped = line.rstrip()
                    if (stripped.endswith('{%') or stripped.endswith('{{') or 
                        (re.search(r'{%[^{%]*$', stripped) and not re.search(r'%}', stripped)) or
                        (re.search(r'{{[^{{]*$', stripped) and not re.search(r'}}', stripped))):
                        
                        if i + 1 < len(lines):
                            next_line = lines[i+1].lstrip()
                            # Combine them
                            combined = stripped + " " + next_line
                            new_lines.append(combined)
                            i += 2
                            changed = True
                            continue
                    
                    new_lines.append(line)
                    i += 1
                
                if changed:
                    print(f"Fixed split tag in {path}")
                    with open(path, 'w', encoding='utf-8') as f:
                        f.writelines(new_lines)

if __name__ == "__main__":
    templates_dir = r"c:\Users\Jean De\Downloads\dusangireog\Dusangire19 (2)\Dusangire19\Dusangire\templates"
    fix_split_tags(templates_dir)
