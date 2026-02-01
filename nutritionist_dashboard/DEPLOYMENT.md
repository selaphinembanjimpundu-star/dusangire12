# Nutritionist Dashboard - Deployment Guide

## Overview

The Nutritionist Dashboard is a production-ready Django app that manages nutritionist profiles and client assignments for the Dusangire restaurant platform.

## Pre-Deployment Checklist

### 1. Database Migrations
```bash
# Run migrations to create required tables
python manage.py migrate nutritionist_dashboard

# Verify migrations
python manage.py showmigrations nutritionist_dashboard
```

### 2. Static Files
```bash
# Collect static files for production
python manage.py collectstatic --noinput
```

### 3. Testing
```bash
# Run all tests
python manage.py test nutritionist_dashboard

# Run with verbose output
python manage.py test nutritionist_dashboard --verbosity=2

# Run specific test class
python manage.py test nutritionist_dashboard.tests.NutritionistProfileModelTests
```

### 4. Security Check
```bash
# Run Django security checks
python manage.py check --deploy

# Expected: 0 errors
```

## Deployment Steps

### Step 1: Database Setup

Ensure the following database tables exist:
- `nutritionist_dashboard_nutritionistprofile`
- `nutritionist_dashboard_clientassignment`

Run migrations:
```bash
python manage.py migrate nutritionist_dashboard
```

### Step 2: Seed Initial Data

Create demo nutritionists for testing:
```bash
python manage.py seed_nutritionists

# To clear and reseed
python manage.py seed_nutritionists --clear
```

### Step 3: Create Superuser (if not exists)

```bash
python manage.py createsuperuser
```

### Step 4: Configure Admin Access

1. Visit: `https://yourdomain.com/admin/`
2. Login with superuser credentials
3. Navigate to Nutritionist Dashboard sections:
   - Nutritionist Profiles
   - Client Assignments

### Step 5: Environment Variables

Ensure the following settings are configured in `.env`:
```env
# Django settings
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_URL=postgresql://user:password@host:5432/dusangire

# Email (for notifications)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Step 6: Logging Configuration

Ensure logging is configured in `settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'nutritionist_dashboard.log'),
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'nutritionist_dashboard': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

### Step 7: Create Logs Directory

```bash
mkdir -p /var/log/dusangire
mkdir -p /home/dusangire/Dusangire/logs
chmod 755 /var/log/dusangire
```

## Features Overview

### Models

#### NutritionistProfile
- Tracks professional information
- Manages capacity and availability
- Supports status management (active, inactive, on_leave)
- Automatic timestamps and audit trail

#### ClientAssignment
- Links clients to nutritionists
- Tracks assignment lifecycle
- Supports status tracking
- Includes notes and termination capabilities

### Views & Permissions

1. **Dashboard** (`/nutritionist/`)
   - Nutritionist-only access
   - Shows profile and recent client orders
   - Displays capacity statistics

2. **Manage Clients** (`/nutritionist/clients/`)
   - List all assigned clients
   - Filter by status
   - Search functionality
   - Pagination

3. **Client Details** (`/nutritionist/clients/<id>/`)
   - View specific client information
   - View client's order history
   - Assignment details

4. **Profile Management** (`/nutritionist/create-profile/`, `/nutritionist/update-profile/`)
   - Create/update nutritionist profile
   - Form validation and error handling

### Admin Features

- Bulk actions for nutritionists (activate, deactivate, mark on leave)
- Bulk actions for assignments (activate, pause, complete, terminate)
- Advanced filtering and search
- Read-only audit timestamps

## API Integration (Optional - DRF)

If using Django REST Framework:

```python
# In urls.py
from rest_framework.routers import DefaultRouter
from nutritionist_dashboard.views_api import NutritionistProfileViewSet

router = DefaultRouter()
router.register(r'nutritionists', NutritionistProfileViewSet)

urlpatterns += router.urls
```

## Monitoring & Maintenance

### Check Logs

```bash
# View recent logs
tail -f /home/dusangire/Dusangire/logs/nutritionist_dashboard.log

# Search for errors
grep ERROR /home/dusangire/Dusangire/logs/nutritionist_dashboard.log

# Count log entries
wc -l /home/dusangire/Dusangire/logs/nutritionist_dashboard.log
```

### Database Maintenance

```bash
# Check for orphaned profiles
python manage.py shell
>>> from nutritionist_dashboard.models import NutritionistProfile
>>> NutritionistProfile.objects.filter(user__is_active=False).count()

# Review all assignments
>>> from nutritionist_dashboard.models import ClientAssignment
>>> ClientAssignment.objects.all().count()
```

## Troubleshooting

### Issue: "User has no NutritionistProfile"

**Solution**: Direct user to create profile first
```bash
# Or create via shell
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> from nutritionist_dashboard.models import NutritionistProfile
>>> User = get_user_model()
>>> user = User.objects.get(username='nutritionist_name')
>>> NutritionistProfile.objects.create(user=user)
```

### Issue: Assignments not showing

**Solution**: Check assignment status and dates
```bash
python manage.py shell
>>> from nutritionist_dashboard.models import ClientAssignment
>>> assignments = ClientAssignment.objects.filter(status='active')
>>> for a in assignments:
...     print(f"{a.client.email}: {a.is_active}")
```

### Issue: Performance issues with many clients

**Solution**: Add database indexes (already included in model)
```bash
python manage.py migrate
```

## Performance Optimization

1. **Query Optimization**
   - Uses `select_related()` for foreign keys
   - Uses `only()` and `defer()` for large querysets
   - Paginated views (20 items per page)

2. **Caching** (Optional)
   ```python
   from django.views.decorators.cache import cache_page
   
   @cache_page(60 * 5)  # 5 minutes
   def dashboard(request):
       ...
   ```

3. **Database Indexes**
   - Indexed on: user, status, created_at
   - Unique together: (nutritionist, client)

## Backup & Recovery

### Backup Database

```bash
# PostgreSQL backup
pg_dump -U postgres dusangire > /backup/dusangire_$(date +%Y%m%d).sql

# Compress
gzip /backup/dusangire_*.sql
```

### Restore Database

```bash
# Restore from backup
psql -U postgres dusangire < /backup/dusangire_YYYYMMDD.sql
```

## Post-Deployment Verification

1. ✓ Admin interface accessible
2. ✓ Nutritionist can create profile
3. ✓ Nutritionist can view dashboard
4. ✓ Client assignments work
5. ✓ Logs are being written
6. ✓ Email notifications working (if configured)
7. ✓ Security checks passing
8. ✓ Database backups running

## Support & Documentation

- **Admin**: `/admin/nutritionist_dashboard/`
- **Dashboard**: `/nutritionist/`
- **API Docs** (if enabled): `/api/docs/`

For issues, check:
- Application logs
- Django debug toolbar (development only)
- Admin interface for data integrity

---

**Last Updated**: January 2025
**Version**: 1.0 (Production Ready)
