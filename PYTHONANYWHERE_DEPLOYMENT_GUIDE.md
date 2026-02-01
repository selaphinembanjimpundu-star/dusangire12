# PythonAnywhere Deployment Guide - Dusangire Platform

## Quick Start for PythonAnywhere Beginner Account

This guide covers deploying the Dusangire Django application to PythonAnywhere with a beginner account.

---

## 📋 Prerequisites

- ✅ GitHub repository: https://github.com/selaphinembanjimpundu-star/dusangire12
- ✅ PythonAnywhere beginner account (free)
- ✅ Python 3.13+ support
- ✅ SQLite database (included)

---

## 🚀 Deployment Steps

### **Step 1: Create PythonAnywhere Account**

1. Go to https://www.pythonanywhere.com
2. Click "Create a beginner account" (Free for 3 months)
3. Username will be your subdomain (e.g., `yourname.pythonanywhere.com`)
4. Verify email

### **Step 2: Set Up Web App on Dashboard**

1. Log in to PythonAnywhere
2. Go to **Web** tab
3. Click **"Add a new web app"**
4. Choose:
   - Domain: `yourname.pythonanywhere.com`
   - Python Framework: **Django**
   - Python Version: **3.11** (closest to 3.13 available)
   - Project Path: Will be set in next step

### **Step 3: Clone Repository to PythonAnywhere**

Open **Bash console** (from Consoles tab):

```bash
# Navigate to home directory
cd ~

# Clone the repository
git clone https://github.com/selaphinembanjimpundu-star/dusangire12.git

# Navigate to project
cd dusangire12

# Check structure
ls -la
```

### **Step 4: Set Up Python Virtual Environment**

```bash
# Create virtual environment (must be in home directory or /tmp)
mkvirtualenv --python=/usr/bin/python3.11 dusangire_env

# Verify activation (you should see (dusangire_env) prefix)
which python
```

### **Step 5: Install Dependencies**

```bash
# Make sure virtual env is activated
pip install --upgrade pip

# Install requirements
pip install django==6.0.1
pip install djangorestframework
pip install django-crispy-forms
pip install crispy-bootstrap5
pip install pillow
pip install python-decouple
pip install django-allauth
pip install requests

# Verify installations
pip list
```

### **Step 6: Configure Settings for Production**

Edit `dusangire/settings.py`:

```python
# Find and update:

# 1. DEBUG (must be False in production)
DEBUG = False

# 2. ALLOWED_HOSTS (add your PythonAnywhere domain)
ALLOWED_HOSTS = ['yourname.pythonanywhere.com', 'localhost', '127.0.0.1']

# 3. DATABASES (SQLite default is OK for beginner)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 4. STATIC FILES (important for PythonAnywhere)
STATIC_URL = '/static/'
STATIC_ROOT = '/home/yourname/dusangire12/staticfiles/'

# 5. MEDIA FILES
MEDIA_URL = '/media/'
MEDIA_ROOT = '/home/yourname/dusangire12/media/'

# 6. EMAIL CONFIGURATION (use console backend for testing)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# Or for production:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-email@gmail.com'
# EMAIL_HOST_PASSWORD = 'your-app-password'

# 7. SECURITY SETTINGS (add these)
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    'default-src': ("'self'",),
}
```

### **Step 7: Prepare Static Files**

```bash
# Navigate to project directory
cd ~/dusangire12

# Create static files directory
mkdir -p staticfiles

# Collect static files
python manage.py collectstatic --noinput

# Verify
ls -la staticfiles/
```

### **Step 8: Initialize Database**

```bash
# Apply migrations
python manage.py migrate

# Create superuser for admin
python manage.py createsuperuser
# Follow prompts:
# Username: admin
# Email: your-email@example.com
# Password: strong-password

# Verify database
ls -lh db.sqlite3
```

### **Step 9: Configure Web App in PythonAnywhere**

1. Go to **Web** tab
2. Click on your web app
3. Under **Code** section, set:
   - Source code: `/home/yourname/dusangire12`
   - Working directory: `/home/yourname/dusangire12`

4. Under **Virtualenv**:
   - Set virtual env to: `/home/yourname/.virtualenvs/dusangire_env`

5. Under **WSGI configuration file**:
   - Click to edit: `/home/yourname/dusangire12/dusangire/wsgi.py`
   - Replace content with:

```python
"""
WSGI config for dusangire project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dusangire.settings')

application = get_wsgi_application()
```

### **Step 10: Set Static and Media Files**

In PythonAnywhere Web app dashboard:

1. Go to **Static files** section
2. Add:
   - URL: `/static/`
   - Directory: `/home/yourname/dusangire12/staticfiles/`

3. Add:
   - URL: `/media/`
   - Directory: `/home/yourname/dusangire12/media/`

### **Step 11: Reload Web App**

Click **Reload** button in Web tab:
- Green button on top right
- Wait 20-30 seconds

### **Step 12: Test Deployment**

Open browser: `https://yourname.pythonanywhere.com`

Expected results:
- ✅ Homepage loads
- ✅ CSS/images display correctly
- ✅ No 500 errors
- ✅ Admin accessible at `/admin/`

---

## 🔧 Troubleshooting

### **Error: Static files not loading (404)**
```bash
# Recollect static files
python manage.py collectstatic --noinput --clear

# Reload web app in PythonAnywhere
```

### **Error: ModuleNotFoundError: No module named 'django'**
```bash
# Verify virtual environment is activated
workon dusangire_env

# Reinstall dependencies
pip install -r requirements.txt
```

### **Error: Database locked**
```bash
# In PythonAnywhere bash:
rm db.sqlite3-wal
rm db.sqlite3-shm

# Recreate migrations
python manage.py migrate
```

### **Error: 500 Internal Server Error**
1. Check error log: **Web** tab → **Error log**
2. Check server log: **Web** tab → **Server log**
3. Most common: Missing virtualenv path or DEBUG=True

### **Check Logs**
```bash
# In PythonAnywhere bash
tail -50 /var/log/yourname.pythonanywhere.com.error.log
tail -50 /var/log/yourname.pythonanywhere.com.server.log
```

---

## 📁 Expected Directory Structure on PythonAnywhere

```
/home/yourname/
├── dusangire12/                    # Project root
│   ├── dusangire/                  # Django settings
│   │   ├── settings.py             # ⚠️ EDIT: DEBUG=False, ALLOWED_HOSTS
│   │   ├── wsgi.py                 # ⚠️ VERIFY: Correct WSGI
│   │   └── urls.py
│   ├── accounts/                   # Apps
│   ├── support/
│   ├── orders/
│   ├── manage.py
│   ├── db.sqlite3                  # Database (auto-created)
│   ├── staticfiles/                # ⚠️ IMPORTANT: Collected static files
│   ├── media/                      # User uploads
│   └── requirements.txt            # All dependencies
├── .virtualenvs/
│   └── dusangire_env/              # Virtual environment
```

---

## 🔐 Security Checklist

- [ ] DEBUG = False in settings.py
- [ ] ALLOWED_HOSTS configured correctly
- [ ] SECRET_KEY rotated (generate new one)
- [ ] SECURE_SSL_REDIRECT = True
- [ ] SESSION_COOKIE_SECURE = True
- [ ] CSRF_COOKIE_SECURE = True
- [ ] Email credentials not in settings.py (use env vars)
- [ ] Superuser created with strong password
- [ ] Static files collected
- [ ] Database migrated

---

## 📊 Beginner Account Limitations

| Feature | Limit | Workaround |
|---------|-------|-----------|
| Bandwidth | 100MB/day | Upgrade to paid |
| CPU time | 100s/day | Optimize queries |
| Web app | 1 app | Upgrade to paid |
| Domains | `yourusername.pythonanywhere.com` | Custom domain on paid |
| Database | SQLite (OK) | PostgreSQL on paid |
| Always-on | ❌ No | Upgrade to paid |
| HTTPS | ✅ Free | Automatic |

---

## 🌐 Environment Variables (Optional)

To use environment variables instead of hardcoding:

1. Create `.env` file in project root:
```
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourname.pythonanywhere.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

2. Install python-decouple (already in requirements):
```bash
pip install python-decouple
```

3. Update settings.py:
```python
from decouple import config
DEBUG = config('DEBUG', default=False, cast=bool)
SECRET_KEY = config('SECRET_KEY', default='unsafe-secret-key')
```

---

## 📱 Mobile & Responsive Testing

After deployment, test on:
- Desktop (Chrome, Firefox)
- Mobile (iPhone, Android)
- Tablet
- Different screen sizes

Use: `https://yourname.pythonanywhere.com/responsive` or similar testing tools

---

## 🚀 Next Steps

1. **Test functionality:**
   - User login/signup
   - Contact form
   - FAQ page
   - Admin panel

2. **Enable HTTPS (already done on PythonAnywhere)**

3. **Set up email:**
   - Test contact form emails
   - Test password reset emails

4. **Monitor performance:**
   - Check error logs daily
   - Monitor CPU usage
   - Check bandwidth

5. **Upgrade when ready:**
   - PythonAnywhere paid plans for production use
   - Additional resources as needed

---

## 📞 Support Resources

- **PythonAnywhere Help:** https://help.pythonanywhere.com/
- **Django Docs:** https://docs.djangoproject.com/
- **GitHub Issues:** https://github.com/selaphinembanjimpundu-star/dusangire12/issues
- **PythonAnywhere Status:** https://www.pythonanywhere.com/status/

---

## ✅ Deployment Checklist

- [ ] PythonAnywhere account created
- [ ] Repository cloned
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Settings.py configured (DEBUG=False, ALLOWED_HOSTS)
- [ ] Static files collected
- [ ] Database migrated
- [ ] Superuser created
- [ ] Web app configured
- [ ] WSGI file updated
- [ ] Static/media URLs configured
- [ ] Web app reloaded
- [ ] Homepage loads without errors
- [ ] Admin panel accessible
- [ ] Contact form works
- [ ] FAQ page loads
- [ ] Mobile responsive

---

## 🎯 Success Criteria

After deployment, verify:

```
✅ https://yourname.pythonanywhere.com/ loads
✅ No 404 or 500 errors
✅ CSS/images display correctly
✅ /admin/ is accessible
✅ Login/signup works
✅ Contact form sends (test email in console)
✅ FAQs display
✅ Responsive on mobile
```

---

## 💡 Pro Tips

1. **Use PythonAnywhere's built-in MySQL:**
   - Free with beginner account
   - Better than SQLite for production

2. **Enable HTTPS:**
   - Already free on PythonAnywhere
   - Automatically enabled

3. **Use error logs aggressively:**
   - Check after every change
   - Error logs are your best friend

4. **Test locally first:**
   - Run `python manage.py runserver` locally
   - Then push to PythonAnywhere

5. **Use GitHub for version control:**
   - Easy rollback if issues occur
   - Track changes

---

**Ready to deploy? Follow the 12 steps above and you'll be live in 30-45 minutes!**
