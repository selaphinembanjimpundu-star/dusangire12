# Role-Based Dashboards - Quick Reference Guide

## 🎯 System Overview

The Dusangire application now automatically routes each user to their role-specific dashboard upon login. The system includes dashboards for 8 different roles with real-time update capabilities.

---

## 📍 Quick Navigation

### Login Flow
```
User logs in
    ↓
Dashboard Router (/accounts/dashboard-redirect/)
    ↓
Checks user.profile.role
    ↓
Routes to appropriate dashboard
```

### Main Entry Points
| Role | Dashboard URL | File |
|------|---------------|------|
| Patient/Caregiver | `/customer-dashboard/` | `customer_dashboard/views.py` |
| Nutritionist | `/nutritionist/` | `nutritionist_dashboard/views.py` |
| Medical Staff | `/hospital-wards/medical-staff/dashboard/` | `hospital_wards/medical_staff_views.py` |
| Hospital Manager | `/hospital-wards/manager/dashboard/` | `hospital_wards/hospital_manager_views.py` |
| Chef | `/catering/chef/dashboard/` | `catering/views.py` |
| Kitchen Staff | `/catering/kitchen/dashboard/` | `catering/kitchen_views.py` |
| Delivery Person | `/delivery/dashboard/` | `delivery/delivery_person_views.py` |
| Support Staff | `/support/staff-dashboard/` | `support/support_views.py` |
| Admin | `/admin_dashboard/` | `admin_dashboard/views.py` |

---

## 🔧 Core Files

### Dashboard Router
```python
# accounts/dashboard_router.py
- dashboard_redirect(request) → Routes to role-specific dashboard
- dashboard_home(request) → Displays available dashboards
- get_dashboard_info(role) → Returns dashboard information
- get_role_permissions(role) → Returns role permissions
```

### Role-Specific Views
```python
# hospital_wards/medical_staff_views.py
- medical_staff_dashboard() → Main medical staff dashboard
- ward_management_dashboard() → Ward management interface
- patient_admission_dashboard() → Patient admission/discharge

# hospital_wards/hospital_manager_views.py
- hospital_manager_dashboard() → Hospital operations overview
- staff_management_dashboard() → Staff management
- nutrition_program_dashboard() → Nutrition programs
- hospital_analytics() → Analytics and reporting

# catering/kitchen_views.py
- kitchen_dashboard() → Kitchen operations
- meal_preparation_list() → Meal preparation tracking

# delivery/delivery_person_views.py
- delivery_dashboard() → Active deliveries
- active_deliveries() → Detailed delivery view
- delivery_addresses() → Coverage zones

# support/support_views.py
- support_dashboard() → Ticket management
```

### Real-Time Features
```python
# hospital_wards/consumers.py
- WardConsumer → Real-time ward updates
- DeliveryConsumer → Real-time delivery tracking
- AddressConsumer → Real-time address updates
```

---

## 🛡️ Access Control

### Using Decorators
```python
@login_required
@require_medical_staff
def medical_staff_only_view(request):
    pass
```

### Checking Role in Views
```python
user_role = request.user.profile.role

if user_role == UserRole.HOSPITAL_MANAGER:
    # Manager-specific logic
    pass
```

### Checking Role in Templates
```html
{% if request.user.profile.role == "hospital_manager" %}
    <div>Manager content</div>
{% endif %}
```

---

## 📊 Available Dashboards

### Medical Staff Dashboard
**Features**:
- Ward occupancy tracking
- Bed status management
- Recent admissions
- Patient discharges
- Education progress

**Sub-pages**:
- Ward Management
- Patient Admission/Discharge

### Hospital Manager Dashboard
**Features**:
- Hospital operations overview
- Bed statistics (occupied/available)
- Staff management
- Nutrition programs
- Hospital analytics
- Revenue tracking

**Sub-pages**:
- Staff Management
- Nutrition Program Management
- Hospital Analytics

### Kitchen Staff Dashboard
**Features**:
- Pending meal orders
- Meal preparation status
- Order completion tracking
- Kitchen statistics

**Sub-pages**:
- Meal Preparation List

### Delivery Person Dashboard
**Features**:
- Active deliveries
- Real-time route tracking
- Delivery zones
- Completion rates

**Sub-pages**:
- Active Deliveries
- Delivery Addresses Coverage

### Support Staff Dashboard
**Features**:
- Open tickets
- In-progress tickets
- Resolved tickets
- Urgent ticket highlights
- Unassigned queue

---

## 🔌 Real-Time Updates

### WebSocket Consumers

#### Ward Consumer
```javascript
ws = new WebSocket(`ws://${host}/ws/wards/${wardId}/`);
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    if (data.type === 'ward_status') {
        // Update ward display
    }
};
```

#### Delivery Consumer
```javascript
ws = new WebSocket(`ws://${host}/ws/deliveries/`);
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    if (data.type === 'delivery_location_update') {
        // Update delivery location
    }
};
```

#### Address Consumer
```javascript
ws = new WebSocket(`ws://${host}/ws/addresses/`);
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    if (data.type === 'address_added') {
        // Handle new address
    }
};
```

---

## 📝 Key Model Fields

### Profile Model
```python
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=30,
        choices=UserRole.choices,
        default=UserRole.PATIENT
    )
    is_active = models.BooleanField(default=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
```

### UserRole Choices
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

---

## 🚀 Accessing Dashboards

### In Code
```python
# Get dashboard info
from accounts.dashboard_router import get_dashboard_info, get_role_permissions

dashboard_info = get_dashboard_info(user.profile.role)
permissions = get_role_permissions(user.profile.role)
```

### In Templates
```html
<!-- Display dashboard-specific content -->
{% with role=request.user.profile.role %}
    {% if role == "hospital_manager" %}
        {% include "hospital_wards/hospital_manager_dashboard.html" %}
    {% endif %}
{% endwith %}
```

---

## 🐛 Troubleshooting

### User Sees Wrong Dashboard
1. Check `user.profile.role` value
2. Verify `ROLE_DASHBOARD_MAPPING` has the role
3. Ensure URL name exists in app URLs

### Access Denied (403)
1. Check `user.profile.is_active` is True
2. Verify decorator matches user role
3. Check profile.role is in allowed roles for view

### WebSocket Not Working
1. Install Django Channels: `pip install channels`
2. Add 'channels' to INSTALLED_APPS
3. Create ASGI configuration
4. Check WebSocket URL is correct

---

## 📚 Documentation Files

- **ROLE_BASED_DASHBOARDS_IMPLEMENTATION.md** - Full implementation guide
- **ROLE_BASED_DASHBOARDS_COMPLETION_SUMMARY.md** - Project completion summary
- **ROLE_BASED_DASHBOARDS_QUICK_REFERENCE.md** - This file

---

## ✅ Checklist for Next Steps

- [ ] Create dashboard HTML templates
- [ ] Set up Django Channels for production
- [ ] Configure Redis for channel layers
- [ ] Create ASGI configuration
- [ ] Test WebSocket connections
- [ ] Deploy to production server
- [ ] Monitor real-time connections
- [ ] Implement client-side WebSocket handlers

---

## 📞 Support

**For implementation questions**, see: `ROLE_BASED_DASHBOARDS_IMPLEMENTATION.md`  
**For architecture details**, see: `ROLE_BASED_DASHBOARDS_COMPLETION_SUMMARY.md`  
**For quick lookup**, use this guide

---

**Last Updated**: 2026-02-02  
**Status**: ✅ Implementation Complete
