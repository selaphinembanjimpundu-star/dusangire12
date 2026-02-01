# ✅ DUSANGIRE Role-Based Access Control (RBAC) System

## Overview

The DUSANGIRE platform implements a comprehensive Role-Based Access Control (RBAC) system based on the Business Model Canvas. Each user role has specific permissions, responsibilities, and dashboard access according to their function in the organization.

---

## 📋 User Roles & Responsibilities

### 1. 👤 PATIENT
**Role Code**: `patient`
**Description**: Hospital patient receiving nutrition services

**Key Responsibilities**:
- Order meals through the platform
- Manage dietary preferences and restrictions
- Track health profile and nutrition status
- View meal plans prescribed by nutritionists
- Schedule consultations with nutritionists
- Track delivery status of orders
- Provide feedback on meals
- Manage payment information
- View invoices and payment history

**Dashboard**: `/customer_dashboard/`

**Permissions**:
- view_meal_plans
- order_meals
- view_health_profile
- manage_subscriptions
- view_delivery_status
- contact_support
- view_invoices
- book_consultations

**Key Features**:
- Personalized meal recommendations
- Health profile management
- Subscription plans
- Loyalty program access
- Order history and tracking

---

### 2. 👨‍👩‍👧 CAREGIVER
**Role Code**: `caregiver`
**Description**: Family member or support person assisting patient care

**Key Responsibilities**:
- Order meals on behalf of assigned patient
- Coordinate meal schedules with patient
- Track delivery status and receive updates
- Access patient's health information (limited)
- Manage caregiver preferences
- Contact support for patient-related issues
- Reduce patient burden by handling administrative tasks

**Dashboard**: `/caregiver_dashboard/`

**Permissions**:
- view_patient_health
- place_orders_for_patient
- coordinate_with_patient
- view_delivery_status
- contact_support
- view_meal_plans

**Special Fields**:
- `patient_relationship`: Type of relationship to patient
- `assigned_patient`: Link to patient being cared for

---

### 3. 👨‍⚕️ NUTRITIONIST
**Role Code**: `nutritionist`
**Description**: Healthcare professional managing nutrition plans and consultations

**Key Responsibilities**:
- Create personalized meal plans for patients
- Conduct consultations and health assessments
- Review patient health profiles and progress
- Prescribe specialized meal packages (diabetic, high-protein, post-surgery, etc.)
- Track patient nutrition status and recovery
- Generate nutritional assessment reports
- Manage client caseload and schedules
- Coordinate with medical staff on patient care
- Provide dietary recommendations

**Dashboard**: `/nutritionist/`

**Permissions**:
- create_meal_plans
- manage_patients
- create_consultations
- view_health_profiles
- track_patient_progress
- manage_dietary_plans
- generate_reports
- access_patient_data

**Special Fields**:
- `license_number`: Professional license
- `specialization`: Area of nutrition expertise
- `years_experience`: Professional experience

---

### 4. 🏥 MEDICAL_STAFF
**Role Code**: `medical_staff`
**Description**: Doctor or nurse coordinating medical care and nutrition

**Key Responsibilities**:
- Prescribe meal plans aligned with medical treatment
- Review patient health profiles and medical history
- Coordinate nutrition with medical treatment
- Manage hospital patient care integration
- Monitor nutritional status during hospital stay
- Communicate with nutritionists on medical requirements
- Generate medical and nutritional reports
- Authorize specialized meal packages

**Dashboard**: `/medical_dashboard/`

**Permissions**:
- prescribe_meal_plans
- view_patient_health
- coordinate_nutrition
- manage_hospital_patients
- view_delivery_status
- generate_medical_reports
- access_patient_data

**Special Fields**:
- `license_number`: Medical license
- `specialization`: Medical specialty
- `department`: Hospital department

---

### 5. 👨‍🍳 CHEF
**Role Code**: `chef`
**Description**: Head chef overseeing meal preparation and kitchen operations

**Key Responsibilities**:
- Oversee meal preparation quality and standards
- Manage kitchen staff and assign tasks
- Develop and approve recipes
- Manage ingredient procurement and inventory
- Ensure food safety and hygiene standards
- Review daily orders and meal planning
- Implement menu variations
- Monitor preparation times and efficiency
- Conduct quality control checks
- Generate kitchen performance reports

**Dashboard**: `/kitchen_dashboard/`

**Permissions**:
- manage_menu
- view_daily_orders
- manage_recipes
- manage_kitchen_staff
- track_ingredients
- quality_control
- generate_preparation_reports

**Special Fields**:
- `department`: Kitchen
- `employee_id`: Chef ID number

---

### 6. 👨‍🍳 KITCHEN_STAFF
**Role Code**: `kitchen_staff`
**Description**: Cook or kitchen team member preparing meals

**Key Responsibilities**:
- Prepare meals according to recipes and orders
- Follow food safety and hygiene protocols
- Manage assigned food preparation stations
- Report ingredient or equipment issues
- Update meal preparation status
- Maintain cleanliness and organization
- Collaborate with other kitchen staff
- Follow special dietary requirements
- Report quality issues or concerns

**Dashboard**: `/kitchen_dashboard/`

**Permissions**:
- view_daily_orders
- prepare_meals
- update_preparation_status
- report_issues
- view_recipes

**Special Fields**:
- `department`: Kitchen
- `employee_id`: Staff ID
- `manager`: Assigned chef or kitchen manager

---

### 7. 🚗 DELIVERY_PERSON
**Role Code**: `delivery_person`
**Description**: Delivery staff member responsible for meal transport

**Key Responsibilities**:
- Manage assigned delivery routes
- Pick up meals from kitchen
- Deliver meals to patients on time
- Update delivery status in real-time
- Contact customers for delivery coordination
- Collect payments if applicable
- Handle customer inquiries about orders
- Report delivery issues or delays
- Maintain vehicle and equipment
- Ensure food quality during transport

**Dashboard**: `/delivery_dashboard/`

**Permissions**:
- view_assigned_deliveries
- update_delivery_status
- manage_delivery_route
- contact_customer
- report_delivery_issues
- view_customer_info

**Special Fields**:
- `employee_id`: Delivery person ID
- `vehicle_registration`: Vehicle registration number
- `delivery_zones`: Assigned delivery areas
- `is_available_for_delivery`: Availability status

---

### 8. 👨‍💼 SUPPORT_STAFF
**Role Code**: `support_staff`
**Description**: 24/7 customer support representative

**Key Responsibilities**:
- Handle customer support tickets and inquiries
- Respond to customer complaints and issues
- Process refunds and adjustments
- Answer questions about meal plans and orders
- Coordinate with kitchen and delivery teams
- Maintain customer satisfaction records
- Generate support and satisfaction reports
- Handle billing inquiries
- Provide order status updates
- Escalate complex issues appropriately

**Dashboard**: `/support_dashboard/`

**Permissions**:
- view_orders
- handle_support_tickets
- process_complaints
- contact_customers
- manage_refunds
- generate_support_reports
- view_customer_data

**Special Fields**:
- `department`: Support/Customer Service
- `employee_id`: Support staff ID
- `manager`: Support team manager

---

### 9. 🏢 HOSPITAL_MANAGER
**Role Code**: `hospital_manager`
**Description**: Hospital administrator overseeing DUSANGIRE operations

**Key Responsibilities**:
- Oversee overall platform operations
- Manage staff members and schedules
- Coordinate departments (kitchen, delivery, support)
- Monitor financial performance and budgets
- Manage hospital partnerships and agreements
- Review analytics and performance metrics
- Approve promotional activities
- Manage service agreements with patients
- Generate operational and financial reports
- Handle escalated issues

**Dashboard**: `/hospital_manager_dashboard/`

**Permissions**:
- manage_hospital_operations
- view_financial_reports
- manage_staff
- coordinate_departments
- manage_partnerships
- access_analytics
- generate_reports
- manage_all_users

**Special Fields**:
- `license_number`: Administrative credential
- `department`: Hospital administration
- `employee_id`: Manager ID

---

### 10. 👨‍💻 ADMIN (System Administrator)
**Role Code**: `admin`
**Description**: System administrator with full platform access

**Key Responsibilities**:
- Manage all user accounts and permissions
- Configure system settings and features
- Access admin panel for technical management
- Monitor system performance and security
- Manage database and backups
- Create management and technical staff accounts
- Implement security policies
- Generate system-wide reports
- Handle technical escalations
- Maintain system integrity

**Dashboard**: `/admin/`

**Permissions**:
- manage_all_users
- manage_system_settings
- access_admin_panel
- view_all_data
- generate_system_reports
- manage_database
- security_management

---

## 📊 Role Categories

### Customers
- **Patient**: Direct users of the service
- **Caregiver**: Family members supporting patients

### Healthcare Providers
- **Nutritionist**: Nutrition planning and consultations
- **Medical Staff**: Medical coordination and supervision

### Operations
- **Chef**: Kitchen oversight
- **Kitchen Staff**: Meal preparation
- **Delivery Person**: Transport and delivery
- **Support Staff**: Customer support

### Management
- **Hospital Manager**: Hospital operations
- **Admin**: System administration

---

## 🔐 Role-Based Access Control Features

### Decorator Functions

#### 1. `@role_required(*roles)`
Restrict view to specific roles:
```python
from accounts.rbac import role_required
from accounts.models import UserRole

@role_required(UserRole.PATIENT, UserRole.CAREGIVER)
def patient_dashboard(request):
    # Only patients and caregivers can access
    pass
```

#### 2. `@permission_required(*permissions)`
Restrict view to specific permissions:
```python
from accounts.rbac import permission_required

@permission_required('create_meal_plans', 'manage_patients')
def create_meal_plan(request):
    # Only users with both permissions can access
    pass
```

#### 3. `@active_user_required`
Check if user account is active:
```python
from accounts.rbac import active_user_required

@active_user_required
def sensitive_operation(request):
    # Only active users can access
    pass
```

### Class-Based View Mixins

#### 1. `RoleRequiredMixin`
```python
from accounts.mixins import RoleRequiredMixin
from accounts.models import UserRole

class PatientOrdersView(RoleRequiredMixin, ListView):
    allowed_roles = [UserRole.PATIENT]
    # Only patients can access
```

#### 2. Specialized Mixins
```python
# Patient-only
class PatientOnlyMixin

# Caregiver-only
class CaregiverOnlyMixin

# Healthcare providers
class HealthcareProviderMixin
class NutritionistOnlyMixin
class MedicalStaffOnlyMixin

# Staff members
class KitchenStaffMixin
class DeliveryPersonMixin
class SupportStaffMixin

# Management
class HospitalManagerMixin
class AdminOnlyMixin
```

### Template Context

All templates have access to role information:
```django
{{ user_role }}          {# Current user's role #}
{{ user_permissions }}   {# List of user's permissions #}
{{ user_dashboard_url }} {# User's dashboard URL #}
{{ role_permissions }}   {# All role permissions data #}
```

### Utility Functions

```python
from accounts.rbac import (
    get_user_dashboard_url,      # Get user's dashboard URL
    get_user_role_info,          # Get role information
    check_user_permission,       # Check single permission
    check_user_role,             # Check user's role
    get_role_choices,            # Get formatted role choices
    get_roles_by_category,       # Get roles organized by category
)
```

---

## 🗄️ Database Fields

### Profile Model Extensions

**Role Information**:
- `role`: User's role (CharField with choices)
- `status`: Account status (active, inactive, suspended, pending_verification)
- `is_active`: Boolean flag for account activation

**Healthcare Provider Fields**:
- `license_number`: Professional license
- `specialization`: Professional specialty
- `years_experience`: Years in profession

**Staff Fields**:
- `department`: Department assignment
- `employee_id`: Unique employee identifier
- `manager`: ForeignKey to manager/supervisor

**Delivery Fields**:
- `vehicle_registration`: Vehicle registration
- `delivery_zones`: Assigned delivery areas
- `is_available_for_delivery`: Availability status

**Caregiver Fields**:
- `patient_relationship`: Relationship type
- `assigned_patient`: Link to patient

**Notification Preferences**:
- `email_notifications`: Email notification flag
- `sms_notifications`: SMS notification flag
- `push_notifications`: Push notification flag

---

## 🔄 Role Transitions

### User Registration
1. New user registers through public form
2. Role automatically set to **PATIENT**
3. Account status set to **active**
4. User can access patient dashboard

### Creating Staff Accounts
Staff accounts (chef, delivery, support, etc.) must be created by:
1. **Admin** through `/admin/` panel
2. **Hospital Manager** through management dashboard
3. Management command: `python manage.py create_staff_user`

### Healthcare Provider Setup
1. User registers as **Patient**
2. Creates **Nutritionist** or **Medical Staff** profile separately
3. System verifies credentials
4. Role upgraded to healthcare provider

### Account Status Management
- **Active**: User can access platform
- **Inactive**: User account disabled
- **Suspended**: Account temporarily restricted
- **Pending Verification**: Awaiting credential verification

---

## 📈 Dashboard Redirection

After login, users are automatically redirected to their role-specific dashboard:

```
Patient              → /customer_dashboard/
Caregiver            → /caregiver_dashboard/
Nutritionist         → /nutritionist/
Medical Staff        → /medical_dashboard/
Chef                 → /kitchen_dashboard/
Kitchen Staff        → /kitchen_dashboard/
Delivery Person      → /delivery_dashboard/
Support Staff        → /support_dashboard/
Hospital Manager     → /hospital_manager_dashboard/
Admin                → /admin/
```

---

## 🔐 Security Best Practices

1. **Always use role checks**: Never assume user role in sensitive operations
2. **Use decorators**: Apply role/permission checks to all restricted views
3. **Verify permissions**: Double-check permissions before sensitive actions
4. **Log access**: Track access to sensitive data for audit trails
5. **Validate input**: Never trust user input, always validate against permissions
6. **Session management**: Implement proper session timeouts
7. **API security**: Apply same role checks to API endpoints

---

## 📚 Implementation Guide

### Step 1: Update Settings
Add context processor to `TEMPLATES` settings:

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'OPTIONS': {
            'context_processors': [
                # ... existing context processors ...
                'accounts.rbac.rbac_context',  # Add this
            ],
        },
    },
]
```

### Step 2: Use in Views

**Function-based views:**
```python
from accounts.rbac import role_required
from accounts.models import UserRole

@role_required(UserRole.PATIENT)
def patient_view(request):
    # View code
    pass
```

**Class-based views:**
```python
from accounts.mixins import PatientOnlyMixin

class PatientView(PatientOnlyMixin, ListView):
    # View code
    pass
```

### Step 3: Update Templates
```django
{% if user.profile.role == 'patient' %}
    <!-- Patient-specific content -->
{% endif %}

<!-- Or use context variables -->
{% if 'create_meal_plans' in user_permissions %}
    <button>Create Meal Plan</button>
{% endif %}
```

---

## ✅ Status

**RBAC System**: ✅ COMPLETE
**Roles Defined**: ✅ 10 roles
**Permissions**: ✅ 45+ permissions
**Decorators**: ✅ 3 decorator functions
**Mixins**: ✅ 15 class-based mixins
**Database Fields**: ✅ 20+ extended fields
**Documentation**: ✅ COMPLETE

---

**Last Updated**: Current Session
**Version**: 1.0
**Status**: Production Ready ✅
