# PythonAnywhere Complete Troubleshooting Guide

## Critical Errors & Solutions

### 1. TemplateSyntaxError: Invalid block tag 'endif'
**Error:**
```
django.template.exceptions.TemplateSyntaxError: Template: /home/dusa2026/dusangire12/templates/orders/checkout.html, 
Invalid block tag on line 197: 'endif', expected 'empty' or 'endfor'.
```

**Cause:** Orphaned or mismatched if/endif tags inside for loops

**Solution:**
- Template has been fixed in checkout.html
- Ensure all `{% if %}` blocks have matching `{% endif %}` 
- Verify `{% for %}` blocks have `{% endfor %}`

---

### 2. FileNotFoundError: activate_this.py
**Error:**
```
FileNotFoundError: [Errno 2] No such file or directory: 
'/home/dusa2026/.virtualenvs/dusangire_env/bin/activate_this.py'
```

**Cause:** PythonAnywhere WSGI file references old activation script (Python 3.6 legacy)

**Solution:**
1. Go to PythonAnywhere Web tab
2. Click your web app
3. Edit the WSGI configuration file
4. Replace `activate_this.py` section with:

```python
import sys
import os

# Add your project directory to the sys.path
project_home = u'/home/dusa2026/dusangire12'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Activate virtualenv
venv_path = u'/home/dusa2026/.virtualenvs/dusangire_env'
os.environ['VIRTUAL_ENV'] = venv_path
sys.path.insert(0, os.path.join(venv_path, 'lib/python3.13/site-packages'))

os.environ['DJANGO_SETTINGS_MODULE'] = 'dusangire.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

5. Save the file
6. Click Reload

---

### 3. OperationalError: no such table: django_session
**Error:**
```
django.db.utils.OperationalError: no such table: django_session
```

**Cause:** Migrations haven't been run after deployment

**Solution:**
```bash
cd ~/dusangire12
python manage.py migrate
```

---

### 4. Error: no such column: orders_order.delivery_address
**Error:**
```
Error loading customer dashboard for user 1: no such column: orders_order.delivery_address
```

**Cause:** Database schema out of sync with models. The column was renamed to `delivery_address_id`

**Solution:**
```bash
cd ~/dusangire12
python manage.py makemigrations
python manage.py migrate
```

---

### 5. ValueError: Unknown format code 'f' for object of type 'SafeString'
**Error:**
```
ValueError: Unknown format code 'f' for object of type 'SafeString'
```

**Cause:** Trying to use float format on a SafeString object in hospital_wards/admin.py

**Solution:**
- Code has been fixed to pre-format string before format_html()
- If still seeing this error, clear browser cache

---

## Complete PythonAnywhere Setup Checklist

### Step 1: Fresh Virtual Environment
```bash
# On PythonAnywhere bash console
cd ~

# Remove old venv if exists
deactivate 2>/dev/null
cd ..
rm -rf dusangire_env

# Create fresh venv
python3.13 -m venv dusangire_env
source dusangire_env/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel --no-cache-dir
```

### Step 2: Install Requirements
```bash
cd ~/dusangire12

# Use minimal requirements (saves disk space)
pip install --no-cache-dir -r requirements-pythonanywhere.txt

# Or use ultra-minimal if quota issues persist
pip install --no-cache-dir -r requirements-pythonanywhere-ultra.txt
```

### Step 3: Fix Database Issues
```bash
# Fix foreign key constraint violations
python fix_pythonanywhere_db.py

# Run migrations
python manage.py migrate

# Create superuser for admin
python manage.py createsuperuser
```

### Step 4: Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### Step 5: Update WSGI Configuration
1. Go to PythonAnywhere Web tab
2. Click your web app
3. Edit WSGI configuration (see section 2 above)
4. Save

### Step 6: Reload Web App
1. Click Reload button in Web tab
2. Wait 30 seconds
3. Visit your site

---

## Post-Deployment Verification

### Check admin panel is accessible
```
https://yoursite.pythonanywhere.com/admin/
```

### Check payment checkout
```
https://yoursite.pythonanywhere.com/payments/checkout/
```

### Check user registration
```
https://yoursite.pythonanywhere.com/accounts/register/
```

### View error logs
1. PythonAnywhere Web tab
2. Scroll down to "Log files"
3. Click "Error log" to see real-time errors
4. Click "Server log" for WSGI errors

---

## Disk Quota Management

### Check disk usage
```bash
du -sh ~/
du -sh ~/dusangire12
df -h
```

### If quota exceeded:
```bash
# Clean cache
pip cache purge

# Remove __pycache__ directories
find ~/dusangire12 -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null

# Remove .pyc files
find ~/dusangire12 -type f -name "*.pyc" -delete

# Use requirements-pythonanywhere-ultra.txt (20 packages, ~25MB)
pip install --no-cache-dir -r requirements-pythonanywhere-ultra.txt
```

---

## Session & Authentication Issues

### If login doesn't work:
1. Run migrations (creates django_session table)
2. Clear browser cookies
3. Try incognito/private window

### If admin page shows error:
1. Check error log for specific error
2. Run: `python manage.py migrate`
3. Reload web app

---

## Quick Recovery Script

Copy this to your terminal to fix most issues:

```bash
#!/bin/bash
cd ~/dusangire12
source ../../../virtualenvs/dusangire_env/bin/activate

echo "1. Running database fix..."
python fix_pythonanywhere_db.py

echo "2. Running migrations..."
python manage.py migrate

echo "3. Collecting static files..."
python manage.py collectstatic --noinput

echo "✓ Done! Reload your web app now."
```

---

## Database Column Reference

**Key changes from updates:**
- `order.delivery_address` → `order.delivery_address_id` (foreign key)
- `order.delivery_address_id` now references `delivery.DeliveryAddress` correctly
- No missing database columns - schema is complete

---

## Support Resources

- Error Log: `/admin/` → check "System Error" entries
- Git Commits: Latest fixes in commits 8e05ffb and earlier
- Documentation: See PYTHONANYWHERE_DISK_FIX.md for deployment steps
