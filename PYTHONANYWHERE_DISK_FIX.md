# PythonAnywhere Disk Quota Fix

## Problem
- Disk quota exceeded error when installing requirements.txt
- PythonAnywhere has limited disk space (usually 512MB on free plan)
- Heavy packages like pandas, numpy, scikit-learn consume lots of space

## Solution

### Step 1: Clean Up Virtual Environment
```bash
cd ~/dusangire12
source ../../../virtualenvs/dusangire_env/bin/activate

# Remove and reinstall virtual environment (clean slate)
deactivate
cd ../..
rm -rf dusangire_env  # WARNING: This removes the entire venv

# Create fresh virtual environment
python3.13 -m venv dusangire_env
source dusangire_env/bin/activate

# Upgrade pip, setuptools, wheel
pip install --upgrade pip setuptools wheel

# Install minimal requirements
pip install -r dusangire12/requirements-pythonanywhere.txt
```

### Step 2: If Above Doesn't Work - Clear Pip Cache
```bash
pip cache purge
```

### Step 3: Run Migrations and Collect Static
```bash
cd ~/dusangire12
python manage.py migrate
python manage.py collectstatic --noinput
```

### Step 4: Reload Web App
1. Go to PythonAnywhere Dashboard
2. Click your web app
3. Click **Reload**

## Files Available

- `requirements.txt` - Full development requirements (for local development)
- `requirements-pythonanywhere.txt` - Minimal production requirements (for PythonAnywhere)

### Removed Packages (Not Needed for Web)
These were removed from pythonanywhere.txt as they're heavy and not essential for the web app:
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
- ✅ Django, DRF, Channels (core framework)
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
- **Saves 75%+ space!**

## Troubleshooting

### Still Getting Quota Error?
```bash
# Check disk usage
du -sh ~/
du -sh ~/dusangire12

# Remove old Python caches
find ~/dusangire12 -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find ~/dusangire12 -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null

# Remove .pyc files
find ~/dusangire12 -type f -name "*.pyc" -delete
```

### Check Virtual Environment Size
```bash
du -sh ~/../../virtualenvs/dusangire_env/
```

## Note
After using minimal requirements on PythonAnywhere, if you need data science features locally, use the full `requirements.txt` on your development machine.
