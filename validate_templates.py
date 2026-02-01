#!/usr/bin/env python
import os
import sys
import django
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dusangire.settings')
django.setup()

from django.template import Template, TemplateSyntaxError

template_dir = Path('templates')
html_files = list(template_dir.rglob('*.html'))

errors = []
success = 0

print(f"Validating {len(html_files)} templates...\n")

for html_file in sorted(html_files):
    rel_path = html_file.relative_to(Path('.'))
    try:
        with open(html_file, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
            try:
                Template(content)
                success += 1
                print(f"✓ {rel_path}")
            except TemplateSyntaxError as e:
                errors.append((rel_path, f"Syntax Error: {str(e)}"))
                print(f"✗ {rel_path}: {str(e)[:80]}")
    except Exception as e:
        errors.append((rel_path, f"Read Error: {str(e)[:80]}"))
        print(f"✗ {rel_path}: Read error")

print(f"\n{'='*70}")
print(f"Results: ✓ {success} valid, ✗ {len(errors)} errors")
print(f"{'='*70}")

if errors:
    print(f"\nERRORS FOUND ({len(errors)}):\n")
    for file_path, error in errors:
        print(f"❌ {file_path}")
        print(f"   {error}\n")
    sys.exit(1)
else:
    print("\n✅ All templates have valid Django syntax!")
    sys.exit(0)
