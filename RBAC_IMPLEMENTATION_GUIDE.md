# RBAC Implementation Checklist & Migration Guide

## ✅ Phase 1: Model Updates (COMPLETED)

### Updated Files:
- ✅ `accounts/models.py` - Extended Profile model with role-specific fields
- ✅ `accounts/rbac.py` - Role permissions and decorator functions
- ✅ `accounts/mixins.py` - Class-based view mixins

### Database Migration Needed:
```bash
python manage.py makemigrations
python manage.py migrate
```

**New Database Fields Added:**
```
Profile Model:
├── status (CharField: active, inactive, suspended, pending_verification)
├── is_active (BooleanField)
├── license_number (CharField - for healthcare providers)
├── specialization (CharField - for professionals)
├── years_experience (IntegerField)
├── department (CharField - for staff)
├── employee_id (CharField, unique)
├── manager (ForeignKey to self - for staff hierarchy)
├── vehicle_registration (CharField - for delivery)
├── delivery_zones (CharField)
├── is_available_for_delivery (BooleanField)
├── patient_relationship (CharField - for caregivers)
├── assigned_patient (ForeignKey to User)
├── email_notifications (BooleanField)
├── sms_notifications (BooleanField)
├── push_notifications (BooleanField)
└── Database Indexes:
    ├── role + is_active
    └── user + role
```

---

## ✅ Phase 2: Settings Configuration

### Add to `settings.py`:

```python
# RBAC Configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'accounts.rbac.rbac_context',  # ADD THIS LINE
            ],
        },
    },
]

# Role-based URLs (optional - for role-specific landing pages)
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'accounts:dashboard_redirect'  # Redirects to appropriate dashboard

# Session timeout for active staff (optional)
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_SAVE_EVERY_REQUEST = True
```

---

## ✅ Phase 3: Admin Interface Updates

### Update `accounts/admin.py`:

```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile, UserRole

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('phone', 'status', 'is_active')
        }),
        ('Role & Permissions', {
            'fields': ('role',),
            'description': 'Select user role from Business Model Canvas'
        }),
        ('Healthcare Provider', {
            'fields': ('license_number', 'specialization', 'years_experience'),
            'classes': ('collapse',)
        }),
        ('Staff Information', {
            'fields': ('department', 'employee_id', 'manager'),
            'classes': ('collapse',)
        }),
        ('Delivery Information', {
            'fields': ('vehicle_registration', 'delivery_zones', 'is_available_for_delivery'),
            'classes': ('collapse',)
        }),
        ('Caregiver Information', {
            'fields': ('patient_relationship', 'assigned_patient'),
            'classes': ('collapse',)
        }),
        ('Patient Information', {
            'fields': ('dietary_preferences', 'medical_alerts', 'has_light'),
            'classes': ('collapse',)
        }),
        ('Notification Preferences', {
            'fields': ('email_notifications', 'sms_notifications', 'push_notifications')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing existing object
            return ('created_at', 'updated_at')
        return ()

class CustomUserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'get_full_name', 'get_role', 'get_status', 'is_staff')
    list_select_related = ('profile',)
    list_filter = ('profile__role', 'profile__status', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'profile__employee_id')
    
    def get_role(self, instance):
        return instance.profile.get_role_display() if hasattr(instance, 'profile') else 'N/A'
    get_role.short_description = 'Role'
    get_role.admin_order_field = 'profile__role'
    
    def get_status(self, instance):
        return instance.profile.get_status_display() if hasattr(instance, 'profile') else 'N/A'
    get_status.short_description = 'Status'
    get_status.admin_order_field = 'profile__status'
    
    def get_full_name(self, instance):
        return instance.get_full_name() or instance.username
    get_full_name.short_description = 'Name'
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile)
```

---

## ✅ Phase 4: Update Existing Views

### Step 1: Function-based Views

**Before:**
```python
@login_required
def some_view(request):
    # No role check
    pass
```

**After:**
```python
from accounts.rbac import role_required
from accounts.models import UserRole

@role_required(UserRole.PATIENT, UserRole.CAREGIVER)
def some_view(request):
    # Now requires PATIENT or CAREGIVER role
    pass
```

### Step 2: Class-based Views

**Before:**
```python
from django.contrib.auth.mixins import LoginRequiredMixin

class SomeView(LoginRequiredMixin, ListView):
    pass
```

**After:**
```python
from accounts.mixins import PatientOnlyMixin

class SomeView(PatientOnlyMixin, ListView):
    pass
```

### Step 3: API Views

**Before:**
```python
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_endpoint(request):
    pass
```

**After:**
```python
from rest_framework.decorators import api_view
from accounts.rbac import role_required
from accounts.models import UserRole

@api_view(['GET'])
@role_required(UserRole.NUTRITIONIST)
def api_endpoint(request):
    pass
```

---

## ✅ Phase 5: Update Dashboard Redirects

### Update `accounts/views.py`:

```python
from accounts.rbac import get_user_dashboard_url, ROLE_PERMISSIONS

@login_required
def dashboard_redirect(request):
    """Redirect user to appropriate dashboard based on role"""
    dashboard_url = get_user_dashboard_url(request.user)
    return redirect(dashboard_url)
```

---

## ✅ Phase 6: Management Commands

### Create `accounts/management/commands/create_staff_user.py`:

```python
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserRole

class Command(BaseCommand):
    help = 'Create staff user with specific role'
    
    def add_arguments(self, parser):
        parser.add_argument('username', type=str)
        parser.add_argument('email', type=str)
        parser.add_argument('--role', type=str, default='support_staff')
        parser.add_argument('--department', type=str, default='')
        
    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        role = options['role']
        department = options.get('department', '')
        
        if User.objects.filter(username=username).exists():
            self.stdout.write(f'User {username} already exists')
            return
        
        user = User.objects.create_user(username=username, email=email)
        user.profile.role = role
        user.profile.department = department
        user.profile.save()
        
        self.stdout.write(f'✅ Created {role} user: {username}')
```

**Usage:**
```bash
python manage.py create_staff_user john_chef --role=chef --department=kitchen
python manage.py create_staff_user mary_delivery --role=delivery_person --department=delivery
```

---

## ✅ Phase 7: Template Updates

### Update base template (`templates/base.html`):

```django
<nav class="navbar">
    {% if user.is_authenticated %}
    <div class="user-info">
        <span class="role-badge">{{ user.profile.get_role_display }}</span>
        {% if user.profile.department %}
        <span class="department-badge">{{ user.profile.department }}</span>
        {% endif %}
    </div>
    {% endif %}
</nav>

<footer>
    {% if user.is_authenticated %}
    <p>
        Logged in as: {{ user.get_full_name|default:user.username }}
        ({{ user.profile.get_role_display }})
    </p>
    {% endif %}
</footer>
```

### Update dashboard navigation:

```django
{% if 'create_meal_plans' in user_permissions %}
    <a href="{% url 'create_meal_plan' %}">Create Meal Plan</a>
{% endif %}

{% if user.profile.is_healthcare_provider %}
    <a href="{% url 'health_reports' %}">Health Reports</a>
{% endif %}

{% if user.profile.is_staff_member %}
    <a href="{% url 'staff_dashboard' %}">Staff Dashboard</a>
{% endif %}
```

---

## ✅ Phase 8: Testing

### Create `accounts/tests/test_rbac.py`:

```python
from django.test import TestCase
from django.contrib.auth.models import User
from accounts.models import UserRole, Profile

class RBACTestCase(TestCase):
    def setUp(self):
        # Create test users with different roles
        self.patient_user = User.objects.create_user('patient1', 'patient@test.com', 'pass')
        self.patient_user.profile.role = UserRole.PATIENT
        self.patient_user.profile.save()
        
        self.nutritionist_user = User.objects.create_user('nutritionist1', 'nutri@test.com', 'pass')
        self.nutritionist_user.profile.role = UserRole.NUTRITIONIST
        self.nutritionist_user.profile.save()
    
    def test_patient_permissions(self):
        """Test patient has correct permissions"""
        self.assertTrue(self.patient_user.profile.is_patient_or_caregiver())
        self.assertFalse(self.patient_user.profile.is_healthcare_provider())
    
    def test_nutritionist_permissions(self):
        """Test nutritionist has correct permissions"""
        self.assertTrue(self.nutritionist_user.profile.is_healthcare_provider())
        self.assertFalse(self.nutritionist_user.profile.is_patient_or_caregiver())
    
    def test_role_display(self):
        """Test role display"""
        self.assertEqual(self.patient_user.profile.get_role_display(), 'Patient')
```

---

## 📋 Implementation Checklist

- [ ] Run migrations: `python manage.py makemigrations` && `python manage.py migrate`
- [ ] Update `settings.py` with context processor
- [ ] Update `accounts/admin.py` with new field configurations
- [ ] Update existing views with role decorators
- [ ] Update class-based views with mixins
- [ ] Create staff user management command
- [ ] Update templates with role-based content
- [ ] Run tests: `python manage.py test accounts`
- [ ] Update documentation
- [ ] Deploy to staging for testing
- [ ] Deploy to production

---

## 🔄 Migration Steps

### 1. Backup Database
```bash
python manage.py dumpdata > backup.json
```

### 2. Create Migrations
```bash
python manage.py makemigrations
```

### 3. Review Migration
```bash
python manage.py showmigrations
```

### 4. Apply Migration
```bash
python manage.py migrate
```

### 5. Verify Data
```bash
python manage.py shell
>>> from accounts.models import Profile
>>> Profile.objects.count()  # Should show all profiles
>>> Profile.objects.filter(role='patient').count()  # Check patient count
```

---

## 🚀 Deployment Checklist

- [ ] Database backed up
- [ ] Migrations tested locally
- [ ] Tests passing: `python manage.py test`
- [ ] Settings configured
- [ ] Admin interface reviewed
- [ ] Staging deployment verified
- [ ] User documentation updated
- [ ] Staff trained on new system
- [ ] Production deployment scheduled
- [ ] Rollback plan prepared

---

## ✅ Verification

After implementation, verify with:

```bash
# Check model updates
python manage.py dbshell
> SELECT * FROM accounts_profile LIMIT 1;

# Test decorators
python manage.py shell
>>> from accounts.rbac import check_user_role
>>> from accounts.models import UserRole
>>> # Test with actual users

# Test migrations
python manage.py test accounts

# Check permissions
python manage.py shell
>>> from accounts.rbac import ROLE_PERMISSIONS
>>> list(ROLE_PERMISSIONS.keys())
```

---

**Status**: ✅ Ready for Implementation
**Version**: 1.0
**Last Updated**: Current Session
