# 🚀 PythonAnywhere Deployment - Step-by-Step Guide (Free Tier)

**Date**: February 3, 2026  
**Target**: PythonAnywhere Free Tier  
**Application**: Dusangire Hospital Management System  
**Status**: Ready for deployment

---

## 📋 Complete Deployment Steps

### **STEP 1: Create PythonAnywhere Free Account**

1. Go to https://www.pythonanywhere.com
2. Click **"Pricing"** → **"Free Account"**
3. Fill in:
   - Username: `yourname` (becomes yourname.pythonanywhere.com)
   - Email: Your email
   - Password: Strong password
4. Click **"Create account"**
5. **Verify your email** (check spam folder)
6. Log in to PythonAnywhere dashboard

---

### **STEP 2: Open Bash Console**

1. In PythonAnywhere dashboard, go to **"Consoles"** tab
2. Click **"Bash"** to open a new bash console
3. You'll see a terminal prompt

---

### **STEP 3: Clone GitHub Repository**

```bash
# Go to home directory
cd ~

# Clone the repository
git clone https://github.com/selaphinembanjimpundu-star/dusangire12.git dusangire

# Navigate into project
cd dusangire

# List contents to verify
ls -la
```

**Expected output**: You should see `manage.py`, `requirements.txt`, `dusangire/`, etc.

---

### **STEP 4: Create Python Virtual Environment**

```bash
# Create virtual environment (Python 3.10 is safe for PythonAnywhere free)
mkvirtualenv --python=/usr/bin/python3.10 dusangire_env

# You should see (dusangire_env) prefix in terminal
# If not, activate manually:
source /home/yourusername/.virtualenvs/dusangire_env/bin/activate
```

**Note**: The prefix should show `(dusangire_env)` before your username

---

### **STEP 5: Install Dependencies**

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt

# Verify key packages installed
pip list
```

**If installation fails:**
```bash
# Try installing without cache
pip install --no-cache-dir -r requirements.txt

# Or install packages individually if errors occur
pip install Django==5.0.0
pip install Pillow==10.0.0
pip install django-crispy-forms==2.0
# ... etc
```

---

### **STEP 6: Collect Static Files**

```bash
# Make sure you're in project directory
cd ~/dusangire

# Activate virtual environment if needed
source /home/yourusername/.virtualenvs/dusangire_env/bin/activate

# Collect static files
python manage.py collectstatic --noinput
```

**Expected**: Should create/populate `static/` folder with CSS, JS, images

---

### **STEP 7: Set Up Database**

```bash
# Run migrations to create database
python manage.py migrate

# Create superuser for admin panel
python manage.py createsuperuser
# Follow prompts:
# Username: admin
# Email: your@email.com
# Password: (strong password)
```

**Note**: You can skip this and create superuser later via web interface

---

### **STEP 8: Configure Web App on PythonAnywhere**

1. Go to **"Web"** tab in PythonAnywhere
2. Click **"Add a new web app"**
3. Choose:
   - Domain: `yourusername.pythonanywhere.com`
   - Web framework: **"Manual configuration"** (NOT "Django")
   - Python version: **3.10**
4. Click **"Next"**

---

### **STEP 9: Configure WSGI File**

1. In the Web tab, you'll see a **WSGI configuration file** path
2. Click on it to edit (usually `/var/www/yourusername_pythonanywhere_com_wsgi.py`)
3. **Replace entire contents** with:

```python
import os
import sys

# Add your project to the path
path = '/home/yourusername/dusangire'
if path not in sys.path:
    sys.path.append(path)

# Set Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'dusangire.settings'

# Import Django application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**IMPORTANT**: Replace `yourusername` with your actual PythonAnywhere username

4. Click **"Save"**

---

### **STEP 10: Update Django Settings for Production**

1. Go back to Bash console
2. Edit `dusangire/settings.py`:

```bash
nano ~/dusangire/dusangire/settings.py
```

3. Find and update:

```python
# Change DEBUG
DEBUG = False

# Add your PythonAnywhere domain
ALLOWED_HOSTS = ['yourusername.pythonanywhere.com', 'localhost', '127.0.0.1']

# Add CSRF trusted origins
CSRF_TRUSTED_ORIGINS = [
    'https://yourusername.pythonanywhere.com',
]

# Static files configuration
STATIC_ROOT = '/home/yourusername/dusangire/static'
STATIC_URL = '/static/'

# Media files configuration
MEDIA_ROOT = '/home/yourusername/dusangire/media'
MEDIA_URL = '/media/'

# Database (SQLite is fine for free tier)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/home/yourusername/dusangire/db.sqlite3',
    }
}
```

4. Save: Press `Ctrl+X`, then `Y`, then `Enter`

---

### **STEP 11: Configure Static & Media Files (Web Tab)**

1. In **Web** tab, scroll down to **"Static files"** section
2. Click **"Add a new static files mapping"**
3. Set up TWO mappings:

**Mapping 1 - Static Files:**
- URL: `/static/`
- Directory: `/home/yourusername/dusangire/static`

**Mapping 2 - Media Files:**
- URL: `/media/`
- Directory: `/home/yourusername/dusangire/media`

---

### **STEP 12: Configure Virtual Environment in Web App**

1. In **Web** tab, find **"Virtualenv"** section
2. Click on the virtualenv field
3. Enter the path: `/home/yourusername/.virtualenvs/dusangire_env`
4. It should validate and show the path

---

### **STEP 13: Reload Web App**

1. In **Web** tab, find the green **"Reload"** button
2. Click it to reload your web application
3. Wait a few seconds

---

### **STEP 14: Test Your Application**

1. Visit `https://yourusername.pythonanywhere.com/`
2. **You should see the Dusangire application!**

**Common issues:**
- **Error 500**: Check error log in Web tab
- **Static files not loading**: Verify static files mapping
- **Page blank/white**: Check `ALLOWED_HOSTS` setting

---

### **STEP 15: Create Admin User (If Needed)**

```bash
# In bash console
cd ~/dusangire
source /home/yourusername/.virtualenvs/dusangire_env/bin/activate

# Create superuser
python manage.py createsuperuser
```

Then visit: `https://yourusername.pythonanywhere.com/admin/`

---

## 🔧 Important Settings Update

Update your `dusangire/settings.py` with these critical settings:

```python
# ===== PRODUCTION SETTINGS =====

# Debug mode MUST be False for production
DEBUG = False

# Add your domain
ALLOWED_HOSTS = [
    'yourusername.pythonanywhere.com',
    'localhost',
    '127.0.0.1'
]

# CSRF and security
CSRF_TRUSTED_ORIGINS = [
    'https://yourusername.pythonanywhere.com',
]

# Use secure cookies (HTTPS only)
SESSION_COOKIE_SECURE = False  # Set to True if you have HTTPS
CSRF_COOKIE_SECURE = False     # Set to True if you have HTTPS

# Static files
STATIC_ROOT = '/home/yourusername/dusangire/static'
STATIC_URL = '/static/'

# Media files
MEDIA_ROOT = '/home/yourusername/dusangire/media'
MEDIA_URL = '/media/'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/home/yourusername/dusangire/db.sqlite3',
    }
}
```

---

## 📊 Deployment Checklist

- [ ] PythonAnywhere account created
- [ ] Repository cloned to PythonAnywhere
- [ ] Virtual environment created
- [ ] Dependencies installed from `requirements.txt`
- [ ] Static files collected
- [ ] Database migrations run
- [ ] Superuser created (optional at this stage)
- [ ] WSGI file configured
- [ ] Django settings updated for production
- [ ] Static files mapping configured
- [ ] Media files mapping configured
- [ ] Virtual environment path set
- [ ] Web app reloaded
- [ ] Application accessible via domain
- [ ] Admin panel working

---

## 🚨 Troubleshooting

### **Issue: 500 Error / Blank Page**

1. Go to **Web** tab → **"Error log"**
2. Read the error message carefully
3. Common causes:
   - `ALLOWED_HOSTS` not configured
   - Import errors in `settings.py`
   - Virtual environment not activated

### **Issue: Static Files Not Loading**

1. Verify static files mapping in Web tab
2. Run: `python manage.py collectstatic --noinput`
3. Check directory path exists: `ls -la ~/dusangire/static/`

### **Issue: Can't Access Admin**

1. Create superuser: `python manage.py createsuperuser`
2. Visit: `https://yourusername.pythonanywhere.com/admin/`
3. Use credentials you created

### **Issue: Module Import Error**

```bash
# Reinstall all packages
pip install --upgrade --force-reinstall -r requirements.txt

# Or install individually
pip install Django==5.0.0
pip install Pillow==10.0.0
# ... etc
```

---

## 🔄 After Deployment - Common Updates

### **Push New Code Changes**

```bash
cd ~/dusangire
git pull origin main
source /home/yourusername/.virtualenvs/dusangire_env/bin/activate
pip install -r requirements.txt  # if new packages
python manage.py migrate         # if new migrations
python manage.py collectstatic   # if new static files
```

Then click **"Reload"** in Web tab.

### **Restart Virtual Environment**

```bash
# Kill all processes
pkill -9 python
```

Then click **"Reload"** in Web tab.

---

## 📱 Features Ready on PythonAnywhere

✅ **Role-Based Dashboards**
- Medical Staff Dashboard
- Hospital Manager Dashboard  
- Ward Management Dashboard
- Kitchen Dashboard
- Delivery Dashboard
- Support Dashboard

✅ **Ordering System**
- Browse menu by category
- Add items to shopping cart
- Select delivery address from saved addresses
- Add special requests (allergies, customizations)
- Multiple payment methods

✅ **User Management**
- Login/Register
- User profiles
- Address management
- Order history

✅ **Admin Panel**
- Manage users
- Manage menu items
- View orders
- Manage categories

---

## ⚠️ PythonAnywhere Free Tier Limitations

- **CPU**: Limited
- **Memory**: 512MB
- **Disk**: 512MB
- **Web Apps**: 1 app
- **Workers**: None (no background tasks)
- **Database**: SQLite only
- **Uptime**: Not guaranteed
- **Custom Domain**: Not available

**Recommendation**: Upgrade to Beginner or Hacker plan for production use.

---

## 🎯 Next Steps

1. **Test all features** on deployed site
2. **Monitor error logs** for any issues
3. **Create admin account** for management
4. **Set up backup** for database regularly
5. **Plan upgrade** to paid tier for production

---

## 📞 Support Resources

- **PythonAnywhere Help**: https://help.pythonanywhere.com
- **Django Docs**: https://docs.djangoproject.com
- **GitHub Issues**: https://github.com/selaphinembanjimpundu-star/dusangire12/issues

---

**Status**: ✅ Ready to Deploy  
**Estimated Time**: 30-45 minutes  
**Difficulty**: Beginner-friendly with step-by-step guide

Good luck with your deployment! 🚀
