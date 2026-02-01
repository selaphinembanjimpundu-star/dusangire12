# Multi-Role Customer Ordering System

## Overview

The Dusangire platform supports **cross-role customer functionality**, allowing multiple user roles to act as customers and place orders. This document explains how different roles can participate in the ordering system.

## Roles and Customer Capabilities

### 1. **Patient** (Primary Customer)
**Status:** Full Customer
**Can Order:** ✅ YES
**Can Order For:** Self

**Features:**
- Place meal orders for personal delivery
- Subscribe to meal plans
- Track delivery status
- Manage dietary preferences
- Access meal plan recommendations from nutritionists
- View order history and invoices

**Order Types:**
- Personal meal orders
- Subscription-based meals
- Custom meal requests

**Permissions:**
- `place_order` - Create new meal orders
- `view_own_orders` - View personal orders
- `manage_subscriptions` - Subscribe/unsubscribe from meal plans
- `rate_meals` - Rate delivered meals

---

### 2. **Medical Staff** (Provider + Customer)
**Status:** Healthcare Provider who can also order
**Can Order:** ✅ YES
**Can Order For:** Self + Assigned Patients

**Features:**
- Place personal meal orders for self
- Prescribe meal orders for patients
- Order meals for patient dietary requirements
- Approve patient meal plans
- Track meals delivered to patients
- Generate meal compliance reports

**Order Types:**
- Personal orders (for themselves)
- Patient orders (medical prescription)
- Bulk orders for patient groups
- Hospital meal distribution orders

**Permissions:**
- `place_order` - Create orders for self
- `order_for_patient` - Prescribe/order for patients
- `view_patient_orders` - Track patient meals
- `manage_medical_meals` - Manage medically-prescribed meals

**Example Workflow:**
```
Doctor places order:
1. Logs into system
2. Selects "My Orders" for personal meals
3. Can also select "Patient Orders" tab
4. Prescribes meal plans for patient recovery
5. System tracks patient dietary compliance
```

---

### 3. **Nutritionist** (Provider + Customer)
**Status:** Health Professional who can order
**Can Order:** ✅ YES
**Can Order For:** Self + Client Patients

**Features:**
- Place personal meal orders
- Design and order meals for nutritionist clients
- Track nutrition compliance
- Recommend specific meal combinations
- Monitor patient nutrition levels

**Order Types:**
- Personal nutritionist meals
- Client dietary requirement orders
- Nutrition-specific meal combinations

**Permissions:**
- `place_order` - Order meals for self
- `order_for_client` - Order for nutrition clients
- `design_meal_plans` - Create customized meal plans

---

### 4. **Chef** (Staff + Customer)
**Status:** Kitchen Staff who can order
**Can Order:** ✅ YES (Personal Use)
**Can Order For:** Self

**Features:**
- Place personal meal orders during break times
- Employee meal benefit access
- Order from own menu
- Test new dishes
- Staff meals during shifts

**Order Types:**
- Personal meal orders
- Staff meal benefits
- Employee discount orders

**Permissions:**
- `place_order` - Order meals for personal use
- `use_employee_discount` - Apply staff discounts
- `access_all_meals` - Choose from entire menu

---

### 5. **Kitchen Staff** (Staff + Customer)
**Status:** Kitchen Support who can order
**Can Order:** ✅ YES (Personal Use)
**Can Order For:** Self

**Features:**
- Order meals during shifts
- Access staff meal programs
- Employee benefit meals
- Convenient ordering system

**Order Types:**
- Personal meal orders
- Staff meal benefit orders

**Permissions:**
- `place_order` - Order meals for personal use
- `use_employee_discount` - Apply staff discounts

---

### 6. **Delivery Person** (Staff + Customer)
**Status:** Delivery Personnel who can order
**Can Order:** ✅ YES (Personal Use)
**Can Order For:** Self

**Features:**
- Place personal meal orders
- Order meals for delivery breaks
- Access staff meal program
- Quick ordering during deliveries

**Order Types:**
- Personal meal orders
- Quick break-time meals
- Staff benefit orders

**Permissions:**
- `place_order` - Order meals for personal use
- `use_employee_discount` - Apply staff discounts

---

### 7. **Support Staff** (Staff + Customer)
**Status:** Support Team who can order
**Can Order:** ✅ YES (Personal Use)
**Can Order For:** Self

**Features:**
- Place personal meal orders
- Access employee meal program
- Order meals during shifts
- Team meal coordination

**Order Types:**
- Personal meal orders
- Support team meals
- Office meal orders

**Permissions:**
- `place_order` - Order meals for personal use
- `use_employee_discount` - Apply staff discounts

---

### 8. **Hospital Manager** (Manager + Customer)
**Status:** Hospital Administrator who can order
**Can Order:** ✅ YES
**Can Order For:** Personal + Team Events + Staff Meals

**Features:**
- Place personal orders
- Order meals for hospital events
- Bulk meal ordering for conferences
- Staff meal programs
- Catering coordination
- Order approval authority

**Order Types:**
- Personal meal orders
- Catering orders for hospital events
- Staff meal programs
- Bulk team orders
- Hospital-wide meal distributions

**Permissions:**
- `place_order` - Order meals for self
- `order_for_team` - Order for staff
- `bulk_ordering` - Create bulk orders
- `catering_management` - Manage catering orders
- `approve_orders` - Approve large orders

**Example Workflow:**
```
Manager places order:
1. Personal order - manager's lunch
2. Team order - staff meeting meals
3. Catering order - hospital event/conference
4. Program order - weekly staff meals
5. All orders tracked and paid through hospital account
```

---

### 9. **Admin** (System Administrator)
**Status:** System Control (Can Override)
**Can Order:** ✅ YES (Test Orders)
**Can Order For:** Testing/Demonstration

**Features:**
- Create test orders for system verification
- View all orders in system
- Modify/cancel orders if needed
- System-level order management
- Testing and quality assurance

**Order Types:**
- System test orders
- Demonstration orders

**Permissions:**
- `place_order` - Full ordering system access
- `manage_all_orders` - View/modify all orders
- `system_testing` - Test order creation

---

### 10. **Caregiver** (Visitor/Support + Customer)
**Status:** Patient Support who can order
**Can Order:** ✅ YES
**Can Order For:** Self + Assigned Patient

**Features:**
- Place personal meal orders
- Order meals for assigned patient
- Coordinate patient care meals
- Track patient nutrition

**Order Types:**
- Personal meal orders
- Patient care meal orders
- Coordinated meal deliveries

**Permissions:**
- `place_order` - Order meals for self
- `order_for_patient` - Order for patient care
- `view_patient_orders` - Track patient meals

---

## Cross-Role Order Scenarios

### Scenario 1: Doctor Orders for Patient
```
Doctor's Actions:
1. Logs into system
2. Patient admitted with dietary restrictions
3. Goes to "Patient Orders" tab
4. Prescribes specific meal plan: "Diabetic-Friendly Menu"
5. Sets delivery schedule: Breakfast, Lunch, Dinner
6. System automatically delivers according to plan
7. Doctor monitors compliance in patient health record

System:
- Prescriber: Dr. Smith (Medical Staff)
- Patient: John Doe (Patient)
- Order Type: Medical Prescription
- Status: Tracked with meal compliance
```

### Scenario 2: Hospital Manager Orders Team Meals
```
Manager's Actions:
1. Creates staff meeting on Friday
2. Goes to "Team Orders" tab
3. Orders 20 lunch boxes for staff
4. Selects: Sandwiches, Salads, Drinks
5. Delivery time: 12:00 PM Friday
6. Location: Conference Room
7. Charges to department budget

System:
- Orderer: Hospital Manager
- Order Type: Bulk/Team Order
- Recipient: Hospital Staff
- Status: Catering Order
```

### Scenario 3: Chef Orders Personal Meal
```
Chef's Actions:
1. On afternoon break
2. Quick app login
3. "My Orders" tab
4. Selects 2 items from menu
5. Uses 20% staff discount
6. Ready-to-eat in 15 minutes
7. Pickup from kitchen

System:
- Orderer: Chef
- Order Type: Personal/Employee
- Discount Applied: 20%
- Status: Quick Order
```

### Scenario 4: Nutritionist Designs & Orders Patient Meals
```
Nutritionist's Actions:
1. Patient consultation: Weight loss goal
2. Creates customized meal plan
3. Places order with specific nutritional targets
4. Macros: Protein 25%, Carbs 45%, Fat 30%
5. Daily meals for 30 days
6. Tracks patient nutrition compliance

System:
- Orderer: Nutritionist
- Patient: John Doe
- Order Type: Nutrition Program
- Status: Ongoing subscription with monitoring
```

### Scenario 5: Support Staff Coordinates Hospital Meals
```
Support Staff Actions:
1. New patient arrives with allergies
2. Takes order from patient
3. Places meal order in system
4. Special instructions: "No nuts, shellfish"
5. Coordinates delivery timing
6. Confirms patient received meal

System:
- Orderer: Support Staff
- Customer: Patient
- Order Type: Assisted Order (Patient + Support)
- Status: Special Requirements Flagged
```

---

## Order Processing by Role

### Customer Order Types

| Role | Type | Recipient | Approval | Billing |
|------|------|-----------|----------|---------|
| Patient | Personal | Self | Auto | Personal Account |
| Medical Staff | Personal | Self | Auto | Personal Account |
| Medical Staff | Patient | Patient | Medical | Hospital Account |
| Nutritionist | Client | Client | Auto | Client Account |
| Chef | Personal | Self | Auto | Employee Budget |
| Hospital Manager | Personal | Self | Auto | Personal Account |
| Hospital Manager | Team | Staff | Manager | Department Budget |
| Hospital Manager | Event | Multiple | Manager | Hospital Event Budget |

---

## Permissions Matrix

```
Role                  | Order For Self | Order For Others | View Orders | Approve | Bulk Orders
--                    | -- | -- | -- | -- | --
Patient              | YES | NO | YES (own) | NO | NO
Medical Staff        | YES | YES (patients) | YES (own + patients) | NO | NO
Nutritionist         | YES | YES (clients) | YES (own + clients) | NO | NO
Chef                 | YES | NO | YES (own) | NO | NO
Kitchen Staff        | YES | NO | YES (own) | NO | NO
Delivery Person      | YES | NO | YES (own) | NO | NO
Support Staff        | YES | YES (assisted) | YES (own + assisted) | NO | NO
Hospital Manager     | YES | YES (any) | YES (all) | YES | YES
Admin                | YES | YES (any) | YES (all) | YES | YES
Caregiver            | YES | YES (patient) | YES (own + patient) | NO | NO
```

---

## System Features for Multi-Role Orders

### 1. Order History
- Separate tabs for different order types
- Filter by role, date, status, recipient
- Search and export capabilities

### 2. Role-Based Dashboards
```
Patient Dashboard:
├── My Orders
├── My Subscriptions
├── Delivery Tracking
└── Rating History

Doctor Dashboard:
├── My Orders (Personal)
├── Patient Orders
├── Prescription Management
└── Compliance Tracking

Manager Dashboard:
├── My Orders (Personal)
├── Team Orders
├── Event Orders
└── Budget Tracking
```

### 3. Notifications
- Order confirmation emails
- Delivery updates
- Role-specific alerts (e.g., doctor notified when patient meal delivered)
- Budget notifications (for managers)

### 4. Billing Coordination
```
Patient Order → Patient Pays
Doctor Order for Patient → Hospital Pays
Manager Team Order → Department Budget
Chef Personal Order → Employee Benefits (Discounted)
```

---

## Implementation Guide

### In Templates
```django
<!-- Show role-based tabs -->
{% if user.profile.role == 'medical_staff' %}
<button class="tab-btn" data-tab="patient-orders">
    Patient Orders
</button>
{% endif %}

<!-- Show role-specific order forms -->
{% if user.profile.role == 'hospital_manager' %}
<form id="bulk-order-form">
    <!-- Bulk order specific fields -->
</form>
{% endif %}

<!-- Show role permissions -->
{% if 'order_for_patient' in user_permissions %}
<section>Order for Patient</section>
{% endif %}
```

### In Views
```python
from dsg.rbac import permission_required, role_required

@permission_required('place_order')
def place_order(request):
    # General order placement
    pass

@permission_required('order_for_patient')
def order_for_patient(request):
    # Patient-specific ordering
    pass

@permission_required('bulk_ordering')
def bulk_order(request):
    # Bulk order management
    pass
```

### In Models
```python
class Order(models.Model):
    ORDERER_TYPES = (
        ('patient', 'Patient'),
        ('medical_staff', 'Doctor'),
        ('nutritionist', 'Nutritionist'),
        ('manager', 'Manager'),
        ('staff', 'Staff'),
    )
    
    orderer = models.ForeignKey(User, on_delete=models.CASCADE)
    orderer_type = models.CharField(max_length=20, choices=ORDERER_TYPES)
    recipient = models.ForeignKey(User, null=True, blank=True)  # If different from orderer
    recipient_type = models.CharField(max_length=20, null=True)
```

---

## Benefits of Multi-Role Ordering

✅ **Convenience** - All users can order meals without switching accounts
✅ **Efficiency** - Doctors/managers can coordinate meals in single system
✅ **Accessibility** - Hospital visitors can order while caring for patients
✅ **Integration** - Medical orders integrated with health records
✅ **Compliance** - Track medical meal adherence and nutrition
✅ **Revenue** - Increases order volume across all user types
✅ **Engagement** - Staff benefits encourage system usage
✅ **Flexibility** - Role-based permissions ensure security

---

## Security Considerations

### Permissions
- Each role has specific permissions for ordering
- Cannot order for others without explicit permission
- Patient data protected when doctors place orders
- Budget limits enforced for team/bulk orders

### Data Privacy
- Patients can see their own orders only
- Doctors see only assigned patients
- Managers see team data only
- Admin has full visibility

### Audit Trail
- All orders logged with: who, when, what, for whom
- Changes tracked for compliance
- Billing reconciliation records

---

## Future Enhancements

🔄 **Recurring Orders** - Auto-place orders on schedule
📅 **Order Calendar** - Visual scheduling interface
🤖 **AI Recommendations** - Smart meal suggestions by role
📊 **Analytics** - Order patterns and trends
💳 **Payment Integration** - Multiple payment methods
🔔 **Smart Notifications** - Role-based alerts
📱 **Mobile App** - Quick ordering on-the-go

---

## Support

For questions about multi-role ordering:
- Contact: support@dusangire.com
- Documentation: See RBAC_SYSTEM_DOCUMENTATION.md
- FAQ: Visit help section in application

---

**Last Updated:** February 2026  
**Version:** 1.0  
**Status:** Production Ready
