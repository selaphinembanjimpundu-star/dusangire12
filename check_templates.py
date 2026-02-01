import os
import django
import re
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dusangire.settings')
django.setup()

from django.template.loader import get_template
from django.template import TemplateDoesNotExist

# Find all render() calls in views
views_files = Path('.').rglob('views.py')
template_refs = set()
view_errors = []

for view_file in views_files:
    try:
        with open(view_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Find render(request, 'template_path', ...) patterns
            matches = re.findall(r"render\(request,\s*['\"]([^'\"]+)['\"]", content)
            for match in matches:
                template_refs.add(match)
    except Exception as e:
        view_errors.append(f"Error reading {view_file}: {e}")

print(f"Found {len(template_refs)} template references in views\n")

# Check each template exists
missing_templates = []
found_templates = []

for template_path in sorted(template_refs):
    try:
        get_template(template_path)
        found_templates.append(template_path)
        print(f"✓ {template_path}")
    except TemplateDoesNotExist:
        missing_templates.append(template_path)
        print(f"✗ {template_path} - NOT FOUND")
    except Exception as e:
        missing_templates.append(template_path)
        print(f"✗ {template_path} - ERROR: {str(e)[:60]}")

print(f"\n{'='*70}")
print(f"✓ Found: {len(found_templates)}")
print(f"✗ Missing: {len(missing_templates)}")
print(f"{'='*70}")

if missing_templates:
    print(f"\nMISSING TEMPLATES ({len(missing_templates)}):")
    for template in missing_templates:
        print(f"  - {template}")
else:
    print("\n✅ All template references are valid!")
