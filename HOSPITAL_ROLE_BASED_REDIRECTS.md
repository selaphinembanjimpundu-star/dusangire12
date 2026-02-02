# 🏥 Hospital Ward System - Role-Based Dashboard Redirects

## Overview

The Hospital Ward Management System now features intelligent role-based redirects that automatically route users to their appropriate dashboard templates upon login. Users are seamlessly directed to the correct dashboard based on their assigned role.

---

## 🎯 How It Works

### Login Flow

```
User Logs In
    ↓
login_view() validates credentials
    ↓
dashboard_redirect() checks user role
    ↓
Route to appropriate hospital dashboard
    ↓
Display role-specific template
```

### Entry Points

#### 1. **Main Dashboard Redirect** (General System)
- **URL**: `/accounts/dashboard-redirect/`
- **View**: `accounts.views.dashboard_redirect()`
- **Use**: Main application login endpoint
- **Behavior**: Routes to hospital ward OR main system dashboards

#### 2. **Hospital-Specific Entry** (Hospital System Only)
- **URL**: `/accounts/hospital-dashboard/`
- **View**: `accounts.views.hospital_ward_login_redirect()`
- **Use**: Direct hospital ward system login
- **Behavior**: Routes ONLY to hospital ward dashboards
- **Feature**: Better error handling for non-hospital users

---

## 👥 Role Mappings

### 10 Hospital Ward Roles

| Role | Dashboard URL | Template | Audience |
|------|---------------|----------|----------|
| **patient** | `/hospital/dashboards/patient/` | `patient_dashboard.html` | Hospitalized Patients |
| **caregiver** | `/hospital/dashboards/caregiver/` | `caregiver_dashboard.html` | Assigned Patient Caregivers |
| **nutritionist** | `/hospital/dashboards/nutritionist/` | `nutritionist_dashboard.html` | Hospital Nutritionists |
| **medical_staff** | `/hospital/dashboards/medical-staff/` | `medical_staff_dashboard.html` | Doctors & Nurses |
| **chef** | `/hospital/dashboards/chef/` | `chef_dashboard.html` | Head Chef |
| **kitchen_staff** | `/hospital/dashboards/kitchen-staff/` | `kitchen_staff_dashboard.html` | Kitchen Employees |
| **delivery_person** | `/hospital/dashboards/delivery-person/` | `delivery_person_dashboard.html` | Meal Delivery Staff |
| **support_staff** | `/hospital/dashboards/support-staff/` | `support_staff_dashboard.html` | Bed Management & Maintenance |
| **hospital_manager** | `/hospital/dashboards/hospital-manager/` | `hospital_manager_dashboard.html` | Hospital Administrator |
| **admin** | `/hospital/dashboards/admin/` | `admin_dashboard.html` | System Administrator |

---

## 🔒 Authentication & Authorization

### Two-Level Security

1. **Authentication** (Login)
   - User credentials validated via Django's `AuthenticationForm`
   - Session created on successful login

2. **Authorization** (Dashboard Access)
   - Role checked in `hospital_wards.views._require_role()` decorator
   - Decorator restricts access to specific role(s)
   - Unauthorized users redirected with error message

### Example: Medical Staff Dashboard

```python
@login_required
@_require_role('medical_staff')
def medical_staff_dashboard(request):
    """Only users with 'medical_staff' role can access"""
    # Dashboard logic here
    return render(request, 'hospital_wards/dashboards/medical_staff_dashboard.html', context)
```

---

## 📋 User Roles & Access

### Patient Role
- **Access**: Personal dashboard, education content, meal info
- **Restrictions**: Cannot access staff dashboards
- **Template**: `patient_dashboard.html`
- **Features**: 
  - View current bed & ward
  - Check pending orders
  - Access education materials
  - View notifications

### Caregiver Role
- **Access**: Monitor assigned patients, notifications
- **Restrictions**: Cannot modify hospital configuration
- **Template**: `caregiver_dashboard.html`
- **Features**:
  - Track assigned patients
  - Receive notifications
  - View patient orders

### Medical Staff Role
- **Access**: Patient admission/discharge/transfer, medical records
- **Restrictions**: Cannot manage kitchen or delivery
- **Template**: `medical_staff_dashboard.html`
- **Features**:
  - Admit/discharge patients
  - Transfer patients between wards
  - View medical information

### Nutritionist Role
- **Access**: Nutrition information, patient meal plans
- **Restrictions**: Cannot modify bed assignments
- **Template**: `nutritionist_dashboard.html`
- **Features**:
  - Manage nutrition information
  - View meal plans
  - Track nutrition progress

### Chef & Kitchen Staff Roles
- **Access**: Kitchen dashboard, meal preparation info
- **Restrictions**: Cannot access patient medical info
- **Templates**: `chef_dashboard.html`, `kitchen_staff_dashboard.html`
- **Features**:
  - View meal orders
  - Track preparation
  - Manage kitchen inventory

### Delivery Person Role
- **Access**: Delivery schedule, meal delivery tracking
- **Restrictions**: Cannot modify hospital operations
- **Template**: `delivery_person_dashboard.html`
- **Features**:
  - View delivery schedule
  - Track deliveries
  - Manage delivery slots

### Support Staff Role
- **Access**: Bed management, maintenance scheduling
- **Restrictions**: Cannot access medical records
- **Template**: `support_staff_dashboard.html`
- **Features**:
  - Manage bed availability
  - Schedule maintenance
  - Track bed assignments

### Hospital Manager Role
- **Access**: Analytics, reporting, all hospital data
- **Restrictions**: Limited admin functions
- **Template**: `hospital_manager_dashboard.html`
- **Features**:
  - Hospital analytics
  - Generate reports
  - Monitor operations

### Admin Role
- **Access**: Full system access including Django admin
- **Restrictions**: None (full administrative privileges)
- **Template**: `admin_dashboard.html`
- **Features**:
  - System configuration
  - User management
  - Data administration

---

## 🔧 Configuration Files

### 1. **accounts/views.py**
Contains the redirect logic:

```python
def dashboard_redirect(request):
    """Routes user to appropriate dashboard based on role"""
    hospital_ward_roles = {
        'patient': 'hospital_wards:patient_dashboard',
        'caregiver': 'hospital_wards:caregiver_dashboard',
        'nutritionist': 'hospital_wards:nutritionist_dashboard',
        # ... all 10 roles
    }
    
    if profile.role in hospital_ward_roles:
        return redirect(hospital_ward_roles[profile.role])
```

### 2. **accounts/urls.py**
Exposes the redirect endpoints:

```python
path('dashboard-redirect/', views.dashboard_redirect, name='dashboard_redirect'),
path('hospital-dashboard/', views.hospital_ward_login_redirect, name='hospital_dashboard_redirect'),
```

### 3. **hospital_wards/urls.py**
Defines dashboard routes:

```python
path('', views.hospital_dashboard, name='dashboard'),
path('dashboards/patient/', views.patient_dashboard, name='patient_dashboard'),
path('dashboards/medical-staff/', views.medical_staff_dashboard, name='medical_staff_dashboard'),
# ... all dashboard routes
```

### 4. **hospital_wards/views.py**
Contains dashboard view functions with role decorators:

```python
@login_required
@_require_role('medical_staff')
def medical_staff_dashboard(request):
    """Medical staff dashboard"""
    return render(request, 'hospital_wards/dashboards/medical_staff_dashboard.html', context)
```

### 5. **hospital_wards/templates/dashboards/**
Dashboard template files (one per role):
- `patient_dashboard.html`
- `caregiver_dashboard.html`
- `nutritionist_dashboard.html`
- `medical_staff_dashboard.html`
- `chef_dashboard.html`
- `kitchen_staff_dashboard.html`
- `delivery_person_dashboard.html`
- `support_staff_dashboard.html`
- `hospital_manager_dashboard.html`
- `admin_dashboard.html`

---

## 🚀 Usage

### For End Users

#### Login to Hospital System
1. Visit `/accounts/login/`
2. Enter username and password
3. System automatically redirects to role-based dashboard
4. Dashboard template displays based on user role

#### Direct Hospital Entry
Users can also navigate directly to:
- `/accounts/hospital-dashboard/` - Redirects to role dashboard
- `/hospital/` - Main hospital dashboard (routes by role)

### For Developers

#### Check User Role
```python
user_role = request.user.profile.role
if user_role == 'medical_staff':
    # Medical staff specific logic
```

#### Protect Dashboard Access
```python
@_require_role('medical_staff', 'hospital_manager')  # Multiple roles
def restricted_view(request):
    return render(request, 'template.html')
```

#### Add New Role
1. Create new dashboard view with `@_require_role()` decorator
2. Add role to `hospital_ward_roles` dict in `dashboard_redirect()`
3. Create corresponding template
4. Add URL pattern to `hospital_wards/urls.py`

---

## 🛡️ Error Handling

### Scenario: User Without Profile
```
User logs in → dashboard_redirect() checks profile
→ Profile missing → Redirected to profile setup page
→ Message: "Please complete your profile setup first."
```

### Scenario: Invalid Role
```
User with unrecognized role logs in
→ dashboard_redirect() doesn't match hospital roles
→ Falls through to main system role checks
→ If still unmatched → Redirected to home with warning
```

### Scenario: Unauthorized Access
```
Patient tries to access medical_staff dashboard directly
→ _require_role() decorator blocks access
→ User redirected to general hospital dashboard
→ Message: "You do not have access to this dashboard."
```

---

## 📊 Flow Diagrams

### Complete Login → Dashboard Flow

```
┌─────────────────────────────────────────────────┐
│            User Login Page                       │
│  (GET /accounts/login/)                         │
└────────────────┬────────────────────────────────┘
                 │ User submits credentials
                 ↓
┌─────────────────────────────────────────────────┐
│      login_view() - Validate Credentials       │
│  (POST /accounts/login/)                       │
└────────────────┬────────────────────────────────┘
                 │ Credentials valid?
        ┌────────┴────────┐
        │ YES             │ NO
        ↓                 ↓
   ┌─────────┐    ┌──────────────────┐
   │ Log In  │    │ Show Error Page  │
   │ User    │    │ (Redirect to     │
   │         │    │  login with      │
   └────┬────┘    │  error message)  │
        │         └──────────────────┘
        │
        ↓
┌──────────────────────────────────────────────────┐
│  dashboard_redirect() - Route by Role           │
│  (GET /accounts/dashboard-redirect/)            │
│                                                  │
│  Check: request.user.profile.role               │
└────────┬─────────────────────────────────────────┘
         │
    ┌────┴──────────────┐
    │ Hospital Role?    │
    └────┬──────────────┘
         │ YES
         ↓
┌──────────────────────────────────────────────────┐
│   hospital_ward_roles Dictionary Lookup          │
│                                                  │
│   {                                              │
│     'patient': 'hospital_wards:patient_...',    │
│     'medical_staff': 'hospital_wards:medical_..',│
│     ...                                          │
│   }                                              │
└────────┬─────────────────────────────────────────┘
         │ Get target view name
         ↓
┌──────────────────────────────────────────────────┐
│    Redirect to Role-Specific Dashboard View      │
│    (e.g., /hospital/dashboards/patient/)        │
└────────┬─────────────────────────────────────────┘
         │
         ↓
┌──────────────────────────────────────────────────┐
│   View Function (with @login_required +          │
│   @_require_role decorators)                    │
│                                                  │
│   1. Check: User authenticated? ✓               │
│   2. Check: User has required role? ✓           │
│   3. Render template with context               │
└────────┬─────────────────────────────────────────┘
         │
         ↓
┌──────────────────────────────────────────────────┐
│   Display Role-Specific Dashboard Template      │
│   (e.g., patient_dashboard.html)               │
│                                                  │
│   Features:                                      │
│   - Patient-specific widgets                    │
│   - Relevant navigation options                 │
│   - Personalized data views                     │
└──────────────────────────────────────────────────┘
```

---

## 🔄 Backward Compatibility

The redirect system maintains backward compatibility with existing main system roles:

| Main System Role | Redirect Target |
|------------------|-----------------|
| `ADMIN` | `/dashboard/` (Main admin dashboard) |
| `NUTRITIONIST` | `/nutritionist/` (Main nutritionist dashboard) |
| `KITCHEN_STAFF` | `/dashboard/kitchen/` (Main kitchen dashboard) |
| `DELIVERY_PERSON` | `/dashboard/orders/` (Main delivery dashboard) |
| `CUSTOMER` | `/customer_dashboard/` (Main customer dashboard) |

Hospital roles always redirect to hospital ward dashboards.

---

## 🧪 Testing the Redirects

### Test Patient Login
```bash
# 1. Create test patient user
python manage.py shell
>>> from django.contrib.auth.models import User
>>> from accounts.models import UserRole
>>> user = User.objects.create_user('patient1', password='testpass')
>>> user.profile.role = 'patient'
>>> user.profile.save()

# 2. Login and verify redirect
# Visit /accounts/login/
# Enter: patient1 / testpass
# Should redirect to /hospital/dashboards/patient/
```

### Test Medical Staff Login
```bash
>>> user = User.objects.create_user('doctor1', password='testpass')
>>> user.profile.role = 'medical_staff'
>>> user.profile.save()

# Should redirect to /hospital/dashboards/medical-staff/
```

### Test Unauthorized Access
```bash
# 1. Login as patient
# 2. Try to access /hospital/dashboards/medical-staff/
# Should get 403 or redirect with error message
```

---

## 📝 Summary

- ✅ **10 Hospital Roles** - Each with dedicated dashboard
- ✅ **Role-Based Redirects** - Automatic routing post-login
- ✅ **Template Integration** - Proper HTML template display
- ✅ **Access Control** - Two-level security (auth + authz)
- ✅ **Error Handling** - Graceful fallbacks and messages
- ✅ **Backward Compatible** - Existing system roles still work
- ✅ **Developer-Friendly** - Easy to extend with new roles

The system is production-ready and fully integrated! 🎉
