# PythonAnywhere Disk Space Solutions

## Problem
```
ERROR: Could not install packages due to an OSError: [Errno 122] Disk quota exceeded
```

PythonAnywhere free tier has limited disk space. The full requirements.txt is too large.

## Quick Solution (Recommended)

### Option 1: Clean Cache & Use Minimal Requirements (Best)

```bash
cd ~/dusangire12
source ../../../virtualenvs/dusangire_env/bin/activate

# Step 1: Cleanup
python pythonanywhere_cleanup.py

# Step 2: Install minimal requirements first
pip install -r requirements-minimal.txt

# Step 3: Run migrations
python manage.py migrate

# Step 4: Reload web app from PythonAnywhere dashboard
```

### Option 2: Just Clean Cache

```bash
cd ~/dusangire12
source ../../../virtualenvs/dusangire_env/bin/activate

# Clear pip cache
pip cache purge

# Remove pip cache directory
rm -rf ~/.cache/pip
rm -rf ~/.pip/cache

# Try install again with full requirements
pip install -r requirements.txt
```

### Option 3: Upgrade PythonAnywhere

If you need all packages, upgrade to a paid PythonAnywhere plan:
- Free tier: 512MB disk
- Beginner plan: 5GB disk (recommended)
- More info: pythonanywhere.com/pricing

## What's in requirements-minimal.txt?

**✅ Included (Essential):**
- Django 5.0.1 + DRF
- Channels (WebSocket)
- Authentication (Allauth, JWT)
- Database (PostgreSQL, Redis)
- Images & Documents (Pillow)
- Web framework essentials

**❌ Optional (Can add later):**
- Data analysis (Pandas, NumPy, Scikit-learn)
- Task queue (Celery)
- Advanced caching (Cachalot)
- API documentation (Spectacular)
- Audit logging

## After Installing Minimal

If you need additional packages later:

```bash
# Add one package at a time
pip install django-cachalot==2.8.0

# Or add a group
pip install pandas numpy scipy scikit-learn

# Check what's installed
pip list
```

## File Included

- `pythonanywhere_cleanup.py` - Cleanup script
- `requirements-minimal.txt` - Minimal package set
- `PYTHONANYWHERE_DISK_SPACE.md` - This file

## Troubleshooting

**Still out of space?**
```bash
# See what's using space
du -sh ~/*

# Remove unused Python packages
pip uninstall -y <package_name>

# Check Python cache
find ~ -type d -name __pycache__ -exec rm -rf {} +
```

**Need help?**
- PythonAnywhere Status: https://www.pythonanywhere.com/status
- Contact PythonAnywhere support for disk upgrade options
