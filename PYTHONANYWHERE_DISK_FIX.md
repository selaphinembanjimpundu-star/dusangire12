# PythonAnywhere Disk Quota Fix

## Problem
- Disk quota exceeded error when installing requirements.txt
- PythonAnywhere has limited disk space (usually 512MB on free plan)
- Heavy packages like pandas, numpy, scikit-learn consume lots of space

## Solution

### URGENT: Aggressive Cleanup (Do This First!)
```bash
# 1. Check current disk usage
du -sh ~/ 
du -sh ~/dusangire12
df -h

# 2. Remove pip cache BEFORE anything else
pip cache purge

# 3. Remove old venv and build artifacts
deactivate 2>/dev/null
cd ~/..
rm -rf dusangire_env  # CRITICAL: This saves 50-100 MB
cd ~

# 4. Clean project cache files
find ~/dusangire12 -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find ~/dusangire12 -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null
find ~/dusangire12 -type f -name "*.pyc" -delete 2>/dev/null
find ~/dusangire12 -type d -name .tox -exec rm -rf {} + 2>/dev/null
find ~/dusangire12 -type d -name build -exec rm -rf {} + 2>/dev/null
find ~/dusangire12 -type d -name dist -exec rm -rf {} + 2>/dev/null
find ~/dusangire12 -type d -name .eggs -exec rm -rf {} + 2>/dev/null

# 5. Check disk again (should have freed 50-100 MB)
du -sh ~/
```

### Step 1: Create Fresh Virtual Environment
```bash
# From your PythonAnywhere bash console
cd ~/..
python3.13 -m venv dusangire_env
source dusangire_env/bin/activate

# Upgrade pip, setuptools, wheel (use --no-cache to save space)
pip install --no-cache-dir --upgrade pip setuptools wheel
```

### Step 2: Install Minimal Requirements with Space Optimization
```bash
cd ~/dusangire12

# Install with NO cache to save disk space
pip install --no-cache-dir -r requirements-pythonanywhere.txt
```

### Step 3: If Still Getting Quota Error - Use Ultra-Minimal
```bash
# Remove optional packages not critical for payment system
pip install --no-cache-dir \
  Django==5.0.1 \
  djangorestframework==3.14.0 \
  gunicorn==21.2.0 \
  whitenoise==6.6.0 \
  django-crispy-forms==2.5 \
  crispy-bootstrap5==2025.6 \
  django-allauth==65.14.0 \
  django-environ==0.12.0 \
  djangorestframework-simplejwt==5.5.1 \
  psycopg2-binary==2.9.11 \
  redis==5.0.1 \
  Pillow==12.0.0 \
  python-docx==1.2.0 \
  lxml==6.0.2 \
  requests==2.32.5 \
  python-decouple==3.8 \
  PyJWT==2.10.1 \
  cryptography==46.0.4 \
  pyOpenSSL==25.3.0
```

### Step 4: Run Migrations and Collect Static
```bash
cd ~/dusangire12

# If you get foreign key constraint error during migrate:
# This fixes orders with invalid delivery addresses
python fix_pythonanywhere_db.py

# Then run migrations
python manage.py migrate
python manage.py collectstatic --noinput
```

### Step 5: Reload Web App
1. Go to PythonAnywhere Dashboard
2. Click your web app
3. Click **Reload**

## Files Available

- `requirements.txt` - Full development requirements (for local development)
- `requirements-pythonanywhere.txt` - Minimal production requirements (48 packages, for PythonAnywhere)
- `requirements-pythonanywhere-ultra.txt` - Ultra-minimal (20 core packages only, if disk quota still exceeded)

### Removed Packages (Not Needed for Web)
These were removed from pythonanywhere.txt as they're heavy and not essential for the web app:
- ❌ daphne (ASGI server - not needed for WSGI only)
- ❌ pandas (12.3 MB)
- ❌ numpy (16.4 MB)
- ❌ scipy (data science)
- ❌ scikit-learn (data science)
- ❌ recordlinkage (redundant)
- ❌ fhir.resources (3.1 MB)
- ❌ mysql-connector-python (34.1 MB)
- ❌ click, colorama, and other dev utilities

### Kept Packages (Essential)
These are required for the web app to function:
- ✅ Django, DRF, Gunicorn (core framework & web server)
- ✅ Crispy Forms, Bootstrap (UI)
- ✅ Allauth (authentication)
- ✅ JWT, cryptography (security)
- ✅ PostgreSQL driver (database)
- ✅ Redis (caching/sessions)
- ✅ Pillow, docx (file handling)
- ✅ Requests, YAML (API/config)

### Result
- Original: 88 packages (~200+ MB)
- Minimal: 48 packages (~50 MB)
- **Ultra-minimal: 20 packages (~30 MB)**
- **Saves 85%+ space with ultra-minimal!**

## Troubleshooting

### Still Getting Quota Error After Installing Minimal?

**The venv directory is taking too much space.** Follow the aggressive cleanup:

```bash
# 1. Completely remove the old venv (critical!)
deactivate
cd ~/..
rm -rf dusangire_env

# 2. Create completely fresh venv
python3.13 -m venv dusangire_env
source dusangire_env/bin/activate

# 3. Upgrade core tools with NO cache
pip install --no-cache-dir --upgrade pip setuptools wheel

# 4. Try ultra-minimal requirements first (20 packages only)
pip install --no-cache-dir -r dusangire12/requirements-pythonanywhere-ultra.txt

# 5. If that works, try adding back more packages one at a time
pip install --no-cache-dir django-redis==6.0.0
pip install --no-cache-dir channels==4.3.2
```

### Check Actual Disk Usage
```bash
# Show all large directories
du -sh ~/* | sort -rh

# Check just venv
du -sh ~/../../virtualenvs/dusangire_env/

# Check project
du -sh ~/dusangire12

# Check pip cache
du -sh ~/.cache/pip/

# Total available
df -h /
```

### Clear Everything If Needed
```bash
# Remove ALL Python cache
find ~ -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find ~ -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null
find ~ -type f -name "*.pyc" -delete 2>/dev/null

# Remove pip cache completely
rm -rf ~/.cache/pip/

# Remove unused venv
deactivate
cd ~/..
rm -rf dusangire_env
```

### Package-by-Package Installation (Last Resort)
If you still get quota errors, install packages one by one:
```bash
pip install --no-cache-dir Django==5.0.1
pip install --no-cache-dir djangorestframework==3.14.0
pip install --no-cache-dir gunicorn==21.2.0
# ... continue with other packages
```

### Still Getting Quota Error?
Check if PythonAnywhere quota is the issue:
```bash
# On PythonAnywhere bash console
quota -u
# Look for "dusangire_env" in the output - it's likely too large
```

If venv is repeatedly too large:
1. Use ultra-minimal requirements ONLY
2. Don't install extras like dev tools
3. Consider removing optional packages:
   - channels (WebSocket support - not needed without Daphne ASGI)
   - django-cachalot (caching)
   - auditlog (audit logging)
   - oauth-toolkit (OAuth)
   - cors-headers (if not needed)
   - drf-spectacular (API docs)
   - twisted (async/event loop - not needed for WSGI)

## Note
After using minimal requirements on PythonAnywhere, if you need data science features locally, use the full `requirements.txt` on your development machine.
