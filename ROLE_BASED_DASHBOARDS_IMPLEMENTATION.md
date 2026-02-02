# Role-Based Dashboard System - Implementation Guide

## Overview

The Dusangire application now features a comprehensive role-based dashboard system that provides each user with a personalized interface based on their assigned role. Every user is automatically routed to their appropriate dashboard upon login.

## System Architecture

### Role-to-Dashboard Mapping

```
PATIENT/CAREGIVER → Customer Dashboard
NUTRITIONIST → Nutritionist Dashboard
MEDICAL_STAFF → Medical Staff Dashboard
CHEF/KITCHEN_STAFF → Kitchen Dashboard
DELIVERY_PERSON → Delivery Dashboard
SUPPORT_STAFF → Support Dashboard
HOSPITAL_MANAGER → Hospital Manager Dashboard
ADMIN → Admin Dashboard
```

## Features by Role

### 1. **Customer/Patient Dashboard**
- **Path**: `/customer-dashboard/`
- **Features**:
  - View order history and status
  - Active meal plan information
  - Health profile management
  - Loyalty points tracking
  - Subscription management
  - Nutritionist consultation access

### 2. **Nutritionist Dashboard**
- **Path**: `/nutritionist/`
- **Features**:
  - Create and manage meal plans
  - Track client nutrition
  - Create patient education content
  - View nutrition analytics
  - Manage dietary preferences

### 3. **Medical Staff Dashboard**
- **Path**: `/hospital-wards/medical-staff/dashboard/`
- **Features**:
  - Ward management and bed allocation
  - Patient admission/discharge workflow
  - Patient health data tracking
  - Nutrition program coordination
  - Patient education progress monitoring

- **Sub-dashboards**:
  - Ward Management (`/hospital-wards/medical-staff/ward-management/`)
  - Patient Admission (`/hospital-wards/medical-staff/patient-admission/`)

### 4. **Hospital Manager Dashboard**
- **Path**: `/hospital-wards/manager/dashboard/`
- **Features**:
  - Hospital operations overview
  - Bed occupancy tracking
  - Patient admission/discharge statistics
  - Staff management
  - Nutrition program oversight
  - Revenue and order statistics
  - Hospital analytics and reporting

- **Sub-dashboards**:
  - Staff Management (`/hospital-wards/manager/staff/`)
  - Nutrition Program Management (`/hospital-wards/manager/nutrition/`)
  - Hospital Analytics (`/hospital-wards/manager/analytics/`)

### 5. **Kitchen Staff Dashboard**
- **Path**: `/catering/kitchen/dashboard/`
- **Features**:
  - View pending meal orders
  - Track meal preparation status
  - Update meal completion status
  - View ward-specific meals
  - Kitchen statistics

- **Sub-pages**:
  - Meal Preparation List (`/catering/kitchen/preparation/`)

### 6. **Delivery Person Dashboard**
- **Path**: `/delivery/dashboard/`
- **Features**:
  - View assigned deliveries
  - Real-time delivery tracking
  - Active delivery routes
  - Delivery completion tracking
  - Coverage zone management
  - Location updates

- **Sub-pages**:
  - Active Deliveries (`/delivery/active/`)
  - Delivery Addresses Coverage (`/delivery/addresses-coverage/`)

### 7. **Support Staff Dashboard**
- **Path**: `/support/staff-dashboard/`
- **Features**:
  - Ticket management
  - Open/pending issue tracking
  - Urgent ticket highlighting
  - Unassigned ticket queue
  - Support statistics

### 8. **Admin Dashboard**
- **Path**: `/admin_dashboard/`
- **Features**:
  - System-wide statistics
  - User management
  - All order and payment tracking
  - Popular items analysis
  - Corporate partner management
  - Catering booking management

## Core System Components

### 1. Dashboard Router (`accounts/dashboard_router.py`)

The `dashboard_redirect` view automatically routes authenticated users to their role-specific dashboard.

**Usage**:
```python
# In login flow
return redirect('accounts:dashboard_redirect')
```

**Role Permissions**:
Each role has defined permissions and features accessible through:
```python
get_role_permissions(role)
```

### 2. Role Decorators

Decorators are available to protect role-specific views:

```python
from hospital_wards.medical_staff_views import require_medical_staff
from hospital_wards.hospital_manager_views import require_hospital_manager
from catering.kitchen_views import require_kitchen_staff
from delivery.delivery_person_views import require_delivery_person
from support.support_views import require_support_staff

@require_medical_staff
def medical_staff_only_view(request):
    pass
```

## Real-Time Features

### WebSocket Consumers

The system includes real-time update capabilities using Django Channels for:

#### 1. **Ward Consumer** (`hospital_wards/consumers.py::WardConsumer`)
- Real-time bed status updates
- Patient admission/discharge notifications
- Ward capacity tracking
- Room group: `ward_{ward_id}`

**Client-side usage**:
```javascript
ws = new WebSocket(`ws://${host}/ws/wards/${wardId}/`);
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    if (data.type === 'ward_status') {
        updateWardDisplay(data.data);
    }
};
```

#### 2. **Delivery Consumer** (`hospital_wards/consumers.py::DeliveryConsumer`)
- Real-time delivery tracking
- Location updates
- Status changes
- Room group: `deliveries`

#### 3. **Address Consumer** (`hospital_wards/consumers.py::AddressConsumer`)
- Real-time address updates
- Delivery zone changes
- Room group: `addresses_{user_id}`

## URL Structure

### Main Dashboard Entry Point
```
/accounts/dashboard/ → accounts:dashboard_home (unified dashboard selector)
/accounts/dashboard-redirect/ → accounts:dashboard_redirect (automatic routing)
```

### Role-Specific Dashboards
```
Customer:         /customer-dashboard/
Nutritionist:     /nutritionist/
Medical Staff:    /hospital-wards/medical-staff/dashboard/
Hospital Manager: /hospital-wards/manager/dashboard/
Kitchen Staff:    /catering/kitchen/dashboard/
Delivery Person:  /delivery/dashboard/
Support Staff:    /support/staff-dashboard/
Admin:            /admin_dashboard/
```

## Database Models

### Profile Model (accounts/models.py)
The key to role-based routing:

```python
class Profile(models.Model):
    role = models.CharField(
        max_length=30,
        choices=UserRole.choices,
        default=UserRole.PATIENT
    )
    is_active = models.BooleanField(default=True)
    # ... other fields
```

### Role Choices (accounts/models.py)
```python
class UserRole(models.TextChoices):
    PATIENT = 'patient'
    CAREGIVER = 'caregiver'
    NUTRITIONIST = 'nutritionist'
    MEDICAL_STAFF = 'medical_staff'
    CHEF = 'chef'
    KITCHEN_STAFF = 'kitchen_staff'
    DELIVERY_PERSON = 'delivery_person'
    SUPPORT_STAFF = 'support_staff'
    HOSPITAL_MANAGER = 'hospital_manager'
    ADMIN = 'admin'
```

## Accessing User Role

```python
# In views
user_role = request.user.profile.role

# In templates
{{ request.user.profile.role }}
```

## Implementation Checklist

- [x] Create dashboard router (`accounts/dashboard_router.py`)
- [x] Create medical staff views (`hospital_wards/medical_staff_views.py`)
- [x] Create hospital manager views (`hospital_wards/hospital_manager_views.py`)
- [x] Create kitchen staff views (`catering/kitchen_views.py`)
- [x] Create delivery person views (`delivery/delivery_person_views.py`)
- [x] Create support staff views (`support/support_views.py`)
- [x] Create WebSocket consumers (`hospital_wards/consumers.py`)
- [x] Update URL configurations for all apps
- [x] Add role-based decorators to protect views
- [ ] Create dashboard templates for each role
- [ ] Set up Django Channels configuration (for WebSocket support)
- [ ] Configure ASGI for production
- [ ] Test real-time updates
- [ ] Deploy to production

## Next Steps

### 1. Template Creation
Create role-specific dashboard templates:
```
templates/
├── accounts/
│   └── dashboard_home.html
├── customer_dashboard/
│   └── dashboard.html
├── hospital_wards/
│   ├── medical_staff_dashboard.html
│   ├── ward_management_dashboard.html
│   ├── patient_admission_dashboard.html
│   ├── hospital_manager_dashboard.html
│   ├── staff_management_dashboard.html
│   ├── nutrition_program_dashboard.html
│   └── hospital_analytics.html
├── catering/
│   ├── kitchen_dashboard.html
│   └── meal_preparation_list.html
├── delivery/
│   ├── delivery_dashboard.html
│   ├── active_deliveries.html
│   └── delivery_addresses.html
└── support/
    └── support_dashboard.html
```

### 2. Django Channels Setup
For real-time functionality:

```python
# dusangire/asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
import hospital_wards.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dusangire.settings')

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                hospital_wards.routing.websocket_urlpatterns
            )
        )
    ),
})
```

### 3. Testing
```bash
# Test dashboard routing
python manage.py shell
from accounts.models import UserRole, Profile
from accounts.dashboard_router import get_dashboard_info
for role, _ in UserRole.choices:
    info = get_dashboard_info(role)
    print(f"{role}: {info}")
```

### 4. Production Deployment
- Use Daphne or Uvicorn as ASGI server for WebSocket support
- Configure Redis for channel layers
- Enable SSL/WSS for WebSocket connections
- Set up monitoring for real-time connections

## Troubleshooting

### User Not Redirected to Dashboard
1. Check `Profile.role` is set correctly
2. Verify URL name in `ROLE_DASHBOARD_MAPPING`
3. Ensure view is registered in app URLs

### WebSocket Connection Failed
1. Ensure Django Channels is installed
2. Check ASGI configuration
3. Verify WebSocket URL is correct
4. Check browser console for errors

### 403 Permission Denied
1. Verify user role matches view requirements
2. Check decorator on view function
3. Ensure user.profile.is_active is True

## Support

For issues or questions about the role-based dashboard system:
1. Check the view decorators and role checks
2. Review the `ROLE_DASHBOARD_MAPPING` in `dashboard_router.py`
3. Consult the specific role view files for feature details
4. Check user profile role assignment

---

**Last Updated**: 2026-02-02
**Status**: Implementation Complete - Ready for Template Creation and Testing
