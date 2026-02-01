# Dusangire Health Platform - GitHub Deployment Guide

## Overview

This guide covers deploying the Dusangire Health Platform with the complete Health Check Auto-Assignment System to GitHub and production environments.

## Pre-Deployment Checklist

- [ ] All code changes committed locally
- [ ] No sensitive information in code (check `.env`, database credentials)
- [ ] Database migrations created and tested
- [ ] Static files collected
- [ ] Tests passing locally
- [ ] `.gitignore` properly configured (venv, __pycache__, *.pyc, .env, db.sqlite3)
- [ ] Requirements.txt up-to-date with all dependencies

## GitHub Setup

### 1. Create GitHub Repository

```bash
# Initialize git (if not already done)
git init

# Add GitHub remote
git remote add origin https://github.com/YOUR_USERNAME/dusangire.git

# Set default branch
git branch -M main

# Push code to GitHub
git push -u origin main
```

### 2. Verify .gitignore

The following files/folders should be ignored and NOT committed:

```
venv/
env/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.egg-info/
dist/
build/
.env
.env.local
.DS_Store
db.sqlite3
*.db
media/
staticfiles/
.vscode/
.idea/
*.log
```

Your `.gitignore` is already properly configured. Verify with:

```bash
git status
```

## Installation & Setup

### 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/dusangire.git
cd dusangire
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the project root:

```env
# Django Settings
DEBUG=False
SECRET_KEY=your-secret-key-here-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=dusangire_db
DB_USER=dusangire_user
DB_PASSWORD=secure-password-here
DB_HOST=localhost
DB_PORT=5432

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@dusangire.com
CONTACT_EMAIL=support@dusangire.com

# OAuth (if using Google)
GOOGLE_OAUTH_CLIENT_ID=your-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret

# Site Configuration
SITE_NAME=Dusangire Health Platform
SITE_ID=1
```

### 5. Database Setup

```bash
# Create database migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load initial data (if available)
python manage.py loaddata initial_data.json
```

## Health Check Auto-Assignment System Setup

### Database Models

The system includes 3 main models:

1. **HealthCheck** - Patient health check requests
2. **ConsultantAvailability** - Consultant availability and workload tracking
3. **AutoAssignmentLog** - Audit trail of all assignments

### Initialize Consultant Availability

```bash
python manage.py shell

# Create availability records for consultants
from accounts.models import User
from health_profiles.models import ConsultantAvailability

for consultant in User.objects.filter(profile__role__in=['medical_staff', 'nutritionist']):
    availability, created = ConsultantAvailability.objects.get_or_create(
        user=consultant,
        defaults={
            'status': 'available',
            'max_concurrent_checks': 5,
            'specialization': 'General Consultation'
        }
    )
    if created:
        print(f"Created availability for {consultant.email}")
```

### Batch Assignment

Run batch assignment for pending health checks:

```bash
python manage.py assign_health_checks_batch
```

## Testing

### Run Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test health_profiles

# Run with verbose output
python manage.py test --verbosity=2

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Manual Testing URLs

After setup, test these URLs:

- Dashboard: `http://localhost:8000/`
- Health Checks: `http://localhost:8000/health-checks/`
- Admin: `http://localhost:8000/admin/`
- Health Profiles: `http://localhost:8000/customer-dashboard/reports/health/`

## Email Configuration

### For Development (Console Backend)

Emails print to console. Already configured in `settings.py`.

### For Production (Gmail SMTP)

1. Enable 2-factor authentication on Gmail
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Add to `.env`:
   ```
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   ```

### For Production (SendGrid)

```python
# In settings.py
EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
```

## Static Files & Media

### Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### Configure Media Upload Directory

Ensure `MEDIA_ROOT` and `MEDIA_URL` are configured in `settings.py`:

```python
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

## Production Deployment

### Using Gunicorn

```bash
# Install gunicorn (in requirements.txt)
pip install gunicorn

# Run server
gunicorn dusangire.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### Using Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "dusangire.wsgi:application", "--bind", "0.0.0.0:8000"]
```

Build and run:

```bash
docker build -t dusangire .
docker run -p 8000:8000 -e DEBUG=False dusangire
```

### Using Heroku

```bash
# Install Heroku CLI
# Login
heroku login

# Create app
heroku create dusangire

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate

# Create superuser
heroku run python manage.py createsuperuser
```

### Using PythonAnywhere

1. Create account at https://www.pythonanywhere.com
2. Upload code
3. Configure web app with Python 3.11
4. Set WSGI file
5. Configure environment variables
6. Reload web app

## Performance Optimization

### Database Optimization

- Health Check views use `select_related()` and `prefetch_related()` for efficiency
- Indexes on `status`, `assigned_consultant`, `patient` fields
- Pagination set to 20-50 items per page

### Caching

Add Redis caching for consultant availability:

```python
# In settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### Query Optimization

Monitor slow queries:

```bash
python manage.py shell_plus
from django.test.utils import override_settings
from django.db import connection
from django.test.utils import CaptureQueriesContext

with CaptureQueriesContext(connection) as context:
    # Run queries
    pass
print(f"Queries: {len(context)}")
```

## Admin Interface Management

### Health Check Admin

- View all health checks with filtering
- Filter by status, priority, consultant assignment
- Read-only assignment logs
- Bulk actions for status updates

### Consultant Availability Admin

- Monitor current workload percentages
- Update max concurrent checks
- View average ratings
- Sort by performance metrics

### Auto-Assignment Logs

- View all assignment attempts
- Filter by success/failure
- Prevent manual log creation/deletion (read-only)
- Track assignment reasons and messages

## Monitoring & Troubleshooting

### Check Health Check Status

```bash
python manage.py shell

from health_profiles.models import HealthCheck
pending = HealthCheck.objects.filter(status='pending').count()
assigned = HealthCheck.objects.filter(status='assigned').count()
print(f"Pending: {pending}, Assigned: {assigned}")
```

### View Assignment Logs

```bash
from health_profiles.models import AutoAssignmentLog
logs = AutoAssignmentLog.objects.order_by('-timestamp')[:10]
for log in logs:
    print(f"{log.timestamp}: {log.result} - {log.message}")
```

### Monitor Email Queue

Check console output or email logs:

```bash
# Monitor logs
tail -f logs/django.log | grep -i email
```

## Backup & Recovery

### Backup Database

```bash
# PostgreSQL
pg_dump dusangire_db > backup_$(date +%Y%m%d_%H%M%S).sql

# SQLite
cp db.sqlite3 backup_db_$(date +%Y%m%d_%H%M%S).sqlite3
```

### Restore Database

```bash
# PostgreSQL
psql dusangire_db < backup_20240101_120000.sql

# SQLite
cp backup_db_20240101_120000.sqlite3 db.sqlite3
```

## Troubleshooting

### Common Issues

**Issue: Import errors for health_profiles**
```
Solution: Ensure health_profiles is in INSTALLED_APPS in settings.py
```

**Issue: Template not found errors**
```
Solution: Check TEMPLATES settings, ensure app templates are in templates/ directory
```

**Issue: Signals not firing**
```
Solution: Verify signals registered in apps.py ready() method
```

**Issue: Auto-assignment not happening**
```
Solution: Check ConsultantAvailability.status is 'available'
Check consultant current_assignments < max_concurrent_checks
```

## Support

For issues or questions:

1. Check the Django logs: `logs/django.log`
2. Run tests: `python manage.py test`
3. Check admin interface for data integrity
4. Review health check signals in `health_profiles/signals.py`

## Additional Resources

- Django Documentation: https://docs.djangoproject.com/
- Django Health Check: https://django-health-check.readthedocs.io/
- Gunicorn: https://gunicorn.org/
- PostgreSQL: https://www.postgresql.org/docs/

---

**Last Updated**: February 2025
**Version**: 1.0
**Status**: Production Ready
