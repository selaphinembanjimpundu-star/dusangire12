# RBAC System - Quick Reference Guide

## 🎯 10 Roles Implementation Based on Business Model Canvas

### Role Hierarchy & Responsibilities

```
┌─────────────────────────────────────────────────────────────┐
│                    ORGANIZATION CHART                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│                    📋 ADMIN (System Admin)                  │
│                                                              │
│              ┌──────────────┬───────────────┐                │
│              │              │               │                │
│    👨‍💼 HOSPITAL_MANAGER   │         API Management           │
│       ├─ Operations      │         Database Access           │
│       ├─ Staff           │         System Configuration      │
│       ├─ Finance         │                                    │
│       └─ Partnerships    │                                    │
│              │              │               │                │
│    ┌─────────┴──────┬───────┴────────┬─────┴──────────┐      │
│    │                │                │                │      │
│  🏥 MEDICAL        👨‍⚕️ HEALTHCARE    👨‍🍳 OPERATIONS   💬 SUPPORT │
│  STAFF             PROVIDERS        LEADS             STAFF  │
│  ├─ Doctors        ├─ Nutritionists ├─ Chef          ├─ 24/7 │
│  ├─ Nurses         ├─ Specialists   ├─ Kitchen Staff │ Support│
│  └─ Coordinators   └─ Consultants   ├─ Delivery      └─ Tickets│
│                                      └─ Personnel             │
│    └─────────────────────────────────────────────────────────┘
│                              ▼
│  👨‍👩‍👦 CUSTOMER SEGMENT
│  ├─ 🏥 PATIENTS (Primary)
│  │  └─ Meal plans, orders, health tracking
│  └─ 👥 CAREGIVERS (Supporting)
│     └─ Coordinate, place orders, track patient
│
└─────────────────────────────────────────────────────────────┘
```

---

## 📱 Role Definitions & Access

### 1️⃣ **PATIENT** (👨‍🦳 Customers - Primary)
```
Role: 'patient'
Dashboard: patient_dashboard/
Permissions:
  ✓ View meal plans
  ✓ Order meals
  ✓ View health profile
  ✓ Manage subscriptions
  ✓ Track delivery
  ✓ Contact support
  ✓ View invoices
  ✓ Book consultations

Profile Fields:
  - dietary_preferences
  - medical_alerts
  - has_light
  - email_notifications
  - sms_notifications

Status: Active/Inactive/Suspended
```

### 2️⃣ **CAREGIVER** (👥 Support Customer)
```
Role: 'caregiver'
Dashboard: caregiver_dashboard/
Permissions:
  ✓ View patient health
  ✓ Place orders for patient
  ✓ Coordinate with patient
  ✓ Track delivery
  ✓ Contact support
  ✓ View meal plans

Profile Fields:
  - patient_relationship (parent/spouse/sibling/etc)
  - assigned_patient (ForeignKey to User)
  - email_notifications
  - sms_notifications
```

### 3️⃣ **NUTRITIONIST** (🥗 Healthcare Provider)
```
Role: 'nutritionist'
Dashboard: nutritionist_dashboard/
Permissions:
  ✓ Create meal plans
  ✓ Manage patients
  ✓ Create consultations
  ✓ View health profiles
  ✓ Track patient progress
  ✓ Manage dietary plans
  ✓ Generate reports
  ✓ Access patient data

Profile Fields:
  - license_number
  - specialization
  - years_experience
  - department (e.g., Nutrition)
```

### 4️⃣ **MEDICAL_STAFF** (👨‍⚕️ Healthcare Provider)
```
Role: 'medical_staff'
Dashboard: medical_staff_dashboard/
Permissions:
  ✓ Prescribe meal plans
  ✓ View patient health
  ✓ Coordinate nutrition
  ✓ Manage hospital patients
  ✓ Track delivery
  ✓ Generate medical reports
  ✓ Access patient data

Profile Fields:
  - license_number
  - specialization
  - years_experience
  - department (e.g., Internal Medicine)
```

### 5️⃣ **CHEF** (👨‍🍳 Operations Lead)
```
Role: 'chef'
Dashboard: chef_dashboard/
Permissions:
  ✓ Manage menu
  ✓ View daily orders
  ✓ Manage recipes
  ✓ Manage kitchen staff
  ✓ Track ingredients
  ✓ Quality control
  ✓ Generate preparation reports

Profile Fields:
  - license_number (optional - culinary certificate)
  - specialization (cuisine type)
  - department = 'Kitchen'
  - manager (Head Chef)
```

### 6️⃣ **KITCHEN_STAFF** (👨‍🍳 Operations)
```
Role: 'kitchen_staff'
Dashboard: kitchen_dashboard/
Permissions:
  ✓ View daily orders
  ✓ Prepare meals
  ✓ Update preparation status
  ✓ Report issues
  ✓ View recipes

Profile Fields:
  - department = 'Kitchen'
  - employee_id
  - manager (Chef)
```

### 7️⃣ **DELIVERY_PERSON** (🚗 Operations)
```
Role: 'delivery_person'
Dashboard: delivery_dashboard/
Permissions:
  ✓ View assigned deliveries
  ✓ Update delivery status
  ✓ Manage delivery route
  ✓ Contact customer
  ✓ Report delivery issues
  ✓ View customer info

Profile Fields:
  - vehicle_registration
  - delivery_zones (comma-separated)
  - is_available_for_delivery (Boolean)
  - department = 'Delivery'
  - employee_id
```

### 8️⃣ **SUPPORT_STAFF** (💬 Operations/Support)
```
Role: 'support_staff'
Dashboard: support_dashboard/
Permissions:
  ✓ View orders
  ✓ Handle support tickets
  ✓ Process complaints
  ✓ Contact customers
  ✓ Manage refunds
  ✓ Generate support reports
  ✓ View customer data

Profile Fields:
  - department = 'Support'
  - employee_id
  - manager (Support Lead)
```

### 9️⃣ **HOSPITAL_MANAGER** (👨‍💼 Management)
```
Role: 'hospital_manager'
Dashboard: manager_dashboard/
Permissions:
  ✓ Manage operations
  ✓ View financial reports
  ✓ Manage staff
  ✓ Coordinate departments
  ✓ Manage partnerships
  ✓ Access analytics
  ✓ Generate reports
  ✓ Manage all users

Profile Fields:
  - department (Administrative)
  - employee_id
  - manager (Optional - CEO)
```

### 🔟 **ADMIN** (🔐 System Admin)
```
Role: 'admin'
Dashboard: admin_dashboard/ (Django Admin)
Permissions:
  ✓ Manage all users
  ✓ Manage system settings
  ✓ Access admin panel
  ✓ View all data
  ✓ Generate system reports
  ✓ Manage database
  ✓ Security management

Profile Fields:
  - Full system access
  - All profile fields visible
```

---

## 🔑 Key Implementation Patterns

### Pattern 1: Function-Based View with Role Decorator

```python
from accounts.rbac import role_required, permission_required
from accounts.models import UserRole

@role_required(UserRole.PATIENT)
def patient_orders(request):
    """Only patients can access this view"""
    orders = request.user.orders.all()
    return render(request, 'patient/orders.html', {'orders': orders})

@permission_required('create_meal_plans', 'manage_patients')
def nutritionist_create_plan(request):
    """Only users with both permissions can access"""
    # ...
    pass
```

### Pattern 2: Class-Based View with Mixin

```python
from accounts.mixins import PatientOnlyMixin, HealthcareProviderMixin

class PatientOrdersView(PatientOnlyMixin, ListView):
    model = Order
    template_name = 'patient/orders.html'
    context_object_name = 'orders'

class NutritionistConsultationsView(HealthcareProviderMixin, ListView):
    model = Consultation
    template_name = 'nutritionist/consultations.html'
```

### Pattern 3: Template-Level Access Control

```django
<!-- dashboard.html -->
<div class="dashboard">
    <!-- Patient section -->
    {% if 'order_meals' in user_permissions %}
    <section class="orders-section">
        <h2>My Orders</h2>
        <a href="{% url 'order_meal' %}" class="btn">Order Meal</a>
    </section>
    {% endif %}
    
    <!-- Nutritionist section -->
    {% if 'create_meal_plans' in user_permissions %}
    <section class="meal-plans-section">
        <h2>Create Meal Plan</h2>
        <a href="{% url 'create_meal_plan' %}" class="btn">New Plan</a>
    </section>
    {% endif %}
    
    <!-- Staff section -->
    {% if user.profile.is_staff_member %}
    <section class="staff-section">
        <h2>Staff Dashboard</h2>
    </section>
    {% endif %}
</div>
```

### Pattern 4: Management Command Usage

```bash
# Create staff user
python manage.py create_staff_user john_doe --role=chef --department=kitchen

# Promote user role
python manage.py promote_user_role john_doe --role=hospital_manager

# Deactivate user
python manage.py deactivate_user john_doe --reason="Left organization"
```

---

## 📊 Role Categories (BMC Alignment)

```
┌─────────────────────────────────────────────────┐
│          BUSINESS MODEL CANVAS MAPPING           │
├─────────────────────────────────────────────────┤
│                                                 │
│ CUSTOMER SEGMENT          →  ROLES              │
│ ├─ Patients              →  PATIENT            │
│ ├─ Caregivers            →  CAREGIVER          │
│ ├─ Hospitals             →  HOSPITAL_MANAGER   │
│ └─ External Customers    →  SUPPORT_STAFF      │
│                                                 │
│ KEY RESOURCES/PARTNERS   →  ROLES              │
│ ├─ Medical Professionals →  NUTRITIONIST,      │
│ │                           MEDICAL_STAFF      │
│ ├─ Delivery Partners     →  DELIVERY_PERSON    │
│ └─ Support Services      →  SUPPORT_STAFF      │
│                                                 │
│ KEY ACTIVITIES            →  ROLES              │
│ ├─ Meal Preparation      →  CHEF,              │
│ │                           KITCHEN_STAFF      │
│ ├─ Meal Delivery         →  DELIVERY_PERSON    │
│ ├─ Consulting            →  NUTRITIONIST       │
│ └─ Support               →  SUPPORT_STAFF      │
│                                                 │
│ ADMINISTRATIVE            →  ROLES              │
│ ├─ Operations            →  HOSPITAL_MANAGER   │
│ └─ System Admin           →  ADMIN             │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## ⚙️ Database Schema Updates

### Profile Model (Extended Fields)

```
Profile
├── user (OneToOneField) ← User
├── phone (CharField)
├── role (CharField) - 10 roles
├── status (CharField) - active/inactive/suspended/pending_verification
├── is_active (BooleanField)
├── created_at (DateTimeField)
├── updated_at (DateTimeField)
│
├─ Healthcare Provider Fields
│  ├── license_number (CharField)
│  ├── specialization (CharField)
│  └── years_experience (IntegerField)
│
├─ Staff Fields
│  ├── department (CharField)
│  ├── employee_id (CharField, unique)
│  └── manager (ForeignKey) ← Profile
│
├─ Delivery Fields
│  ├── vehicle_registration (CharField)
│  ├── delivery_zones (CharField)
│  └── is_available_for_delivery (BooleanField)
│
├─ Caregiver Fields
│  ├── patient_relationship (CharField)
│  └── assigned_patient (ForeignKey) ← User
│
├─ Notification Preferences
│  ├── email_notifications (BooleanField)
│  ├── sms_notifications (BooleanField)
│  └── push_notifications (BooleanField)
│
└─ Existing Patient Fields
   ├── dietary_preferences (TextField)
   ├── medical_alerts (TextField)
   └── has_light (BooleanField)

Indexes:
├── (role, is_active)
└── (user, role)
```

---

## 🧪 Testing Permissions

```python
# Test in Django shell: python manage.py shell

from accounts.rbac import check_user_role, check_user_permission, get_user_role_info
from accounts.models import UserRole
from django.contrib.auth.models import User

# Get user
user = User.objects.first()

# Check role
if check_user_role(user, UserRole.PATIENT):
    print("User is a patient")

# Check permission
if check_user_permission(user, 'order_meals'):
    print("User can order meals")

# Get role info
role_info = get_user_role_info(user)
print(f"Role: {role_info['name']}")
print(f"Permissions: {role_info['permissions']}")
print(f"Dashboard: {role_info['dashboard_url']}")
```

---

## 🚀 Deployment Checklist

- [ ] Models created/migrated
- [ ] rbac.py module exists
- [ ] mixins.py module exists
- [ ] Settings configured with context processor
- [ ] Admin panel customized
- [ ] Views updated with role decorators
- [ ] Class-based views use mixins
- [ ] Templates updated with permissions
- [ ] Management commands created
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] Staff trained on new system
- [ ] Production deployment completed
- [ ] Monitoring in place

---

## 📞 Support & Reference

**Files Created**:
- ✅ `accounts/rbac.py` - Core RBAC system
- ✅ `accounts/mixins.py` - View mixins
- ✅ `RBAC_SYSTEM_DOCUMENTATION.md` - Full documentation
- ✅ `RBAC_IMPLEMENTATION_GUIDE.md` - Step-by-step guide

**Next Steps**:
1. Run migrations
2. Update settings.py
3. Apply decorators to existing views
4. Update templates
5. Test system end-to-end

**Version**: 1.0
**Status**: Ready for Implementation
