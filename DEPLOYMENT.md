# Deployment Guide for Dusangire

## Hosting Platforms Supported
- **PythonAnywhere** (Recommended - detailed guide below)
- **Linux (Ubuntu/Debian) + systemd + nginx**

---

## PythonAnywhere Deployment (Recommended)

### Step 1: Clone Repository
In PythonAnywhere Web Console:
```bash
cd ~
git clone https://github.com/ocaentity-bot/dusangire.git
cd dusangire
```

### Step 2: Create Virtual Environment
PythonAnywhere provides pre-configured virtualenv. In Web App settings:
- **Python version**: 3.11+
- **Virtualenv path**: `/home/yourUsername/.virtualenvs/dusangire`

Activate and install:
```bash
workon dusangire
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
In **Web app** → **Environment variables** (Advanced tab), add:
```
DJANGO_SETTINGS_MODULE=dusangire.settings_production
DEBUG=False
SECRET_KEY=<generate-50-char-random-string>
ALLOWED_HOSTS=yourapp.pythonanywhere.com,yourdomain.com
DB_NAME=yourUsername$dusangire
DB_USER=yourUsername
DB_PASSWORD=<your-mysql-password>
DB_HOST=yourUsername.mysql.pythonanywhere-services.com
DB_PORT=3306
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=<your-email@gmail.com>
EMAIL_HOST_PASSWORD=<gmail-app-password>
GOOGLE_OAUTH_CLIENT_ID=<your-client-id>
GOOGLE_OAUTH_CLIENT_SECRET=<your-client-secret>
```

### Step 4: Create MySQL Database
In **Databases** tab → Create MySQL database (auto-named as `yourUsername$dusangire`)

### Step 5: Run Migrations
In Web Console:
```bash
cd ~/dusangire
workon dusangire
python manage.py migrate --noinput
python manage.py collectstatic --noinput
```

### Step 6: Configure WSGI
Edit the WSGI configuration file in **Web app** settings. Replace with:
```python
import os
import sys

path = os.path.expanduser('~/dusangire')
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'dusangire.settings_production'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### Step 7: Configure Static Files
In **Web app** → **Static files** section, add:
- URL: `/static/` → Directory: `/home/yourUsername/dusangire/staticfiles/`
- URL: `/media/` → Directory: `/home/yourUsername/dusangire/media/`

### Step 8: Reload Web App
Click the **Reload** button in your Web app page.

### Step 9: Test Deployment
Visit `https://yourapp.pythonanywhere.com` and test:
- User registration at `/accounts/register/` or `/accounts/signup/`
- Login at `/accounts/login/`
- Password reset at `/accounts/password-reset/`
- Google OAuth login (if configured)
- Django admin at `/admin/`

### Troubleshooting
- **Check error logs**: Web app page → **Error log** tab
- **Check server logs**: Web app page → **Server log** tab
- **Test migrations manually**: `python manage.py migrate --verbosity 2`
- **Check deployment status**: `python manage.py check --deploy`

---

## Linux (Ubuntu/Debian) Deployment

### Prerequisites
- Ubuntu 20.04+ or Debian 11+
- PostgreSQL or MySQL installed
- nginx installed

### Installation Steps
```bash
cd /home/www
git clone https://github.com/ocaentity-bot/dusangire.git
cd dusangire
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install psycopg2-binary  # For PostgreSQL
```

### Configuration
```bash
cp .env.example .env
# Edit .env with your production values
python manage.py migrate --noinput
python manage.py collectstatic --noinput
```

### Service & Web Server Setup
1. Copy `deploy_examples/dusangire.service` to `/etc/systemd/system/`
2. Copy `deploy_examples/dusangire.nginx.conf` to `/etc/nginx/sites-available/`
3. Enable and start:
```bash
sudo systemctl enable dusangire
sudo systemctl start dusangire
sudo systemctl restart nginx
```

---

## Pre-Deployment Checklist

Before deploying to production:
- [ ] All tests pass: `python manage.py test`
- [ ] Deployment checks pass: `python manage.py check --deploy`
- [ ] `DEBUG=False` in production
- [ ] `SECRET_KEY` is strong and unique (50+ chars)
- [ ] `ALLOWED_HOSTS` includes your domain
- [ ] Database is configured
- [ ] Email backend is configured for password reset
- [ ] OAuth credentials are set (if using Google login)
- [ ] HTTPS/TLS is enabled
- [ ] Database backups are scheduled
- [ ] Error log monitoring is set up

---

## Post-Deployment Checklist

After deployment:
- [ ] Smoke test all main pages
- [ ] Test user registration flow
- [ ] Test login/logout
- [ ] Test password reset email
- [ ] Test Google OAuth (if configured)
- [ ] Monitor error logs for issues
- [ ] Set up log rotation
- [ ] Schedule regular database backups
- [ ] Monitor performance and uptime

---

## Environment Variables Reference

| Variable | Example | Notes |
|----------|---------|-------|
| `SECRET_KEY` | `abc...xyz` (50+ chars) | Must be strong and random |
| `DEBUG` | `False` | Never True in production |
| `ALLOWED_HOSTS` | `example.com,www.example.com` | Comma-separated domains |
| `DB_NAME` | `dusangire` | Database name |
| `DB_USER` | `dusangire` | Database user |
| `DB_PASSWORD` | `strong_password` | Database password |
| `DB_HOST` | `localhost` or `db.example.com` | Database server |
| `DB_PORT` | `5432` (PostgreSQL) or `3306` (MySQL) | Database port |
| `EMAIL_HOST` | `smtp.gmail.com` | SMTP server |
| `EMAIL_PORT` | `587` | SMTP port |
| `EMAIL_HOST_USER` | `noreply@example.com` | Sender email address |
| `EMAIL_HOST_PASSWORD` | `xxxx` | App-specific password (not account password) |
| `GOOGLE_OAUTH_CLIENT_ID` | `xxx.apps.googleusercontent.com` | From Google Cloud Console |
| `GOOGLE_OAUTH_CLIENT_SECRET` | `xxx` | From Google Cloud Console |

See `.env.example` for complete template.

---

## Additional Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)
- [PythonAnywhere Help](https://help.pythonanywhere.com/)
- [Email Configuration](https://docs.djangoproject.com/en/5.2/topics/email/)
- [Google OAuth Setup](https://django-allauth.readthedocs.io/en/latest/providers/google.html)
