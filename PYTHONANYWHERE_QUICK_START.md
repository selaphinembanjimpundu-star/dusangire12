# PythonAnywhere Quick Start - 12 Steps to Live

> ⏱️ **Estimated Time: 30-45 minutes**

---

## 🎯 Quick Reference Card

### Step 1️⃣: Create Account
```
Website: https://www.pythonanywhere.com
Action: Click "Create a beginner account" (Free)
Result: yourname.pythonanywhere.com
```

### Step 2️⃣: Create Web App
```
Dashboard → Web Tab → "Add a new web app"
Framework: Django
Python Version: 3.11
```

### Step 3️⃣: Clone Repository
```bash
cd ~
git clone https://github.com/selaphinembanjimpundu-star/dusangire12.git
cd dusangire12
```

### Step 4️⃣: Create Virtual Environment
```bash
mkvirtualenv --python=/usr/bin/python3.11 dusangire_env
# Prefix should show: (dusangire_env)
```

### Step 5️⃣: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 6️⃣: Configure Settings
**File:** `dusangire/settings.py`
```python
DEBUG = False
ALLOWED_HOSTS = ['yourname.pythonanywhere.com', 'localhost']
STATIC_ROOT = '/home/yourname/dusangire12/staticfiles/'
MEDIA_ROOT = '/home/yourname/dusangire12/media/'
```

### Step 7️⃣: Prepare Database
```bash
mkdir -p staticfiles media
python manage.py migrate
python manage.py createsuperuser  # Create admin user
python manage.py collectstatic --noinput
```

### Step 8️⃣: Set WSGI Configuration
**File:** `/home/yourname/dusangire12/dusangire/wsgi.py`
```python
import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dusangire.settings')
application = get_wsgi_application()
```

### Step 9️⃣: Configure Static Files
Dashboard → Web Tab → Static Files
```
URL: /static/
Directory: /home/yourname/dusangire12/staticfiles/

URL: /media/
Directory: /home/yourname/dusangire12/media/
```

### Step 🔟: Set Virtual Environment Path
Dashboard → Web Tab → Virtualenv
```
Path: /home/yourname/.virtualenvs/dusangire_env
```

### Step 1️⃣1️⃣: Reload Web App
Click the green **Reload** button at top of Web tab

### Step 1️⃣2️⃣: Verify Deployment
Open: `https://yourname.pythonanywhere.com`
```
✅ Homepage loads
✅ CSS/Images display
✅ No 500 errors
✅ /admin/ accessible
```

---

## ⚡ Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| 404 Static files | Not collected | `python manage.py collectstatic --noinput --clear` |
| ModuleNotFoundError | Wrong virtualenv | Check virtualenv path in Web tab |
| 500 Error | DEBUG=True or missing import | Check error log, set DEBUG=False |
| Database locked | Concurrent access | `rm db.sqlite3-wal db.sqlite3-shm` |
| Import error | Old cache | `rm -rf __pycache__` and reload |

---

## 📋 Checklist

Copy & paste items as you complete:

```
□ PythonAnywhere account created
□ Web app configured in dashboard
□ Repository cloned to /home/yourname/
□ Virtual environment created & activated
□ Dependencies installed (pip install -r requirements.txt)
□ settings.py: DEBUG = False
□ settings.py: ALLOWED_HOSTS configured
□ settings.py: STATIC_ROOT configured
□ staticfiles directory created
□ Database migrated (python manage.py migrate)
□ Superuser created (python manage.py createsuperuser)
□ Static files collected (python manage.py collectstatic)
□ WSGI file verified
□ Static files URL configured
□ Media files URL configured
□ Virtualenv path set
□ Web app reloaded
□ Homepage loads without errors
□ Admin panel accessible
```

---

## 🚨 Emergency Troubleshooting

### Check Error Logs
```bash
# In PythonAnywhere Bash Console
tail -50 /var/log/yourname.pythonanywhere.com.error.log
tail -50 /var/log/yourname.pythonanywhere.com.server.log
```

### Clear Cache & Restart
```bash
cd ~/dusangire12
find . -type d -name __pycache__ -exec rm -r {} +
python manage.py check
# Then reload in Dashboard
```

### Test Database
```bash
python manage.py migrate
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.count()  # Should return a number
>>> exit()
```

### Verify WSGI
```bash
cd ~/dusangire12
python -c "from dusangire.wsgi import application; print('OK')"
```

---

## 💡 After Deployment

### Test Email
```bash
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'This is a test', 'noreply@dusangire.local', ['your@email.com'])
```

### Create Test User
```bash
python manage.py createsuperuser
# Username: testuser
# Email: test@example.com
# Password: TestPass123
```

### Access Admin
```
https://yourname.pythonanywhere.com/admin/
Username: admin
Password: (your superuser password)
```

---

## 📊 Monitor Performance

### Check CPU Usage
Dashboard → Web Tab → "View CPU usage"
```
Beginner limit: 100s CPU time/day
Recommendation: Optimize queries, add caching
```

### Check Bandwidth
Dashboard → Web Tab → "View bandwidth usage"
```
Beginner limit: 100MB/day
Recommendation: Optimize images, compress responses
```

---

## 🔐 Post-Deployment Security

```bash
# Generate new SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(50))"
# Update in settings.py or .env

# Set strong admin password
python manage.py changepassword admin

# Check for debug mode
grep DEBUG dusangire/settings.py  # Should show: False

# Verify SSL redirect
grep SECURE_SSL_REDIRECT dusangire/settings.py  # Should show: True
```

---

## 📞 Support Resources

- **PythonAnywhere Help:** https://help.pythonanywhere.com/
- **Django Docs:** https://docs.djangoproject.com/
- **GitHub:** https://github.com/selaphinembanjimpundu-star/dusangire12
- **Contact:** rukundojeandedieu670@gmail.com

---

## ✨ Success Indicators

When working correctly, you should see:

```
✅ https://yourname.pythonanywhere.com/ loads instantly
✅ Static files (CSS, images) display correctly
✅ /admin/ is accessible
✅ Contact form works
✅ FAQ page displays
✅ Login/signup functions
✅ No 404 or 500 errors
✅ Mobile responsive
✅ HTTPS secure (green lock)
```

---

**Ready? Let's go live! 🚀**

*Follow the 12 steps above, and you'll be deployed to PythonAnywhere in 30-45 minutes!*
