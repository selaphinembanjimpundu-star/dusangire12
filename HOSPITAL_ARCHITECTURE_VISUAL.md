# 🏥 Hospital Dashboard Redirects - Visual Architecture

## System Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                      USER LOGIN FLOW                              │
└──────────────────────────────────────────────────────────────────┘

                        ┌─────────────┐
                        │   Login     │
                        │   Form      │
                        │ /login/     │
                        └──────┬──────┘
                               │
                               ↓
                    ┌──────────────────────┐
                    │ Validate Credentials │
                    │  (Django Auth)       │
                    └──────────┬───────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
                    ↓                     ↓
              ✅ VALID               ❌ INVALID
                    │                     │
                    ↓                     ↓
            ┌──────────────┐      ┌───────────────┐
            │  Create       │      │ Show Error    │
            │  Session      │      │ Redirect to   │
            │               │      │ login again   │
            └───────┬───────┘      └───────────────┘
                    │
                    ↓
    ┌────────────────────────────────────┐
    │  Redirect to Dashboard             │
    │  (accounts/dashboard-redirect/)    │
    └────────┬─────────────────────────┘
             │
             ↓
    ┌────────────────────────────────┐
    │ Check: user.profile.role       │
    │ (Hospital or Main System?)     │
    └────────┬───────────────────────┘
             │
    ┌────────┴──────────┐
    │                   │
    ↓                   ↓
    
 HOSPITAL            MAIN SYSTEM
 ROLES               ROLES
    │                   │
    │                   ├── ADMIN → /dashboard/
    │                   │
    ├─ patient ─→ /hospital/dashboards/patient/
    │                   ├── NUTRITIONIST → /nutritionist/
    ├─ caregiver → /hospital/dashboards/caregiver/
    │                   │
    ├─ nutritionist → /hospital/dashboards/nutritionist/
    │                   ├── KITCHEN_STAFF → /dashboard/kitchen/
    ├─ medical_staff → /hospital/dashboards/medical-staff/
    │                   │
    ├─ chef ─→ /hospital/dashboards/chef/
    │                   ├── DELIVERY_PERSON → /dashboard/orders/
    ├─ kitchen_staff → /hospital/dashboards/kitchen-staff/
    │                   │
    ├─ delivery_person → /hospital/dashboards/delivery-person/
    │                   ├── CUSTOMER → /customer_dashboard/
    ├─ support_staff → /hospital/dashboards/support-staff/
    │                   
    ├─ hospital_manager → /hospital/dashboards/hospital-manager/
    │
    └─ admin ─→ /hospital/dashboards/admin/


    ↓                   ↓
    
┌─────────────────────────────────────┐
│  Role-Specific View Function        │
│  (with @_require_role() decorator)  │
│                                     │
│  Checks:                            │
│  1. @login_required ✓              │
│  2. @_require_role('role') ✓       │
│  3. Prepare context                │
└────────┬────────────────────────────┘
         │
         ↓
┌──────────────────────────────────────┐
│  Render Role-Specific Template       │
│  (with role-specific context data)   │
│                                      │
│  Example for medical_staff:          │
│  - occupied_beds                     │
│  - patient_assignments               │
│  - health_alerts                     │
│  - education_contents                │
│  - ward_statistics                   │
└──────────────────────────────────────┘
         │
         ↓
┌──────────────────────────────────────┐
│  Display Dashboard to User           │
│                                      │
│  ✅ Personalized to their role      │
│  ✅ Shows relevant data              │
│  ✅ Accessible features only         │
│  ✅ Secure access control            │
└──────────────────────────────────────┘
```

---

## Database & Configuration Flow

```
┌─────────────────────────────────────────────────────────────┐
│                  DATABASE                                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  auth_user (Django Built-in)                              │
│  ├── id                                                    │
│  ├── username                                              │
│  ├── password (hashed)                                     │
│  └── ...                                                   │
│                                                             │
│  accounts_userprofile (Custom)                             │
│  ├── user_id → FK(auth_user)                               │
│  ├── role ← THIS IS USED FOR ROUTING!                      │
│  │        ('patient', 'medical_staff', 'admin', etc.)     │
│  └── ...                                                   │
│                                                             │
│  hospital_wards_* (Domain Models)                          │
│  ├── Ward, WardBed, PatientAdmission, ...                 │
│  └── All data accessed by dashboard views                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
         ↑
         │
         │ Uses
         │
┌─────────────────────────────────────────────────────────────┐
│                  REDIRECT LOGIC                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  accounts/views.py::dashboard_redirect()                   │
│  ┌──────────────────────────────────────────────────┐     │
│  │ hospital_ward_roles = {                          │     │
│  │   'patient': 'hospital_wards:patient_dashboard',│     │
│  │   'medical_staff': ...,                          │     │
│  │   'admin': ...,                                  │     │
│  │   ...10 total...                                │     │
│  │ }                                                │     │
│  │                                                  │     │
│  │ if profile.role in hospital_ward_roles:        │     │
│  │   return redirect(hospital_ward_roles[...])    │     │
│  └──────────────────────────────────────────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
         ↓
         │ Routes to
         │
┌─────────────────────────────────────────────────────────────┐
│              VIEW FUNCTIONS & DECORATORS                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  hospital_wards/views.py                                   │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ @login_required                                      │ │
│  │ @_require_role('medical_staff')                      │ │
│  │ def medical_staff_dashboard(request):                │ │
│  │     # Prepare context with medical data            │ │
│  │     context = {...}                                │ │
│  │     return render(request, 'template.html', ctx)   │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                             │
│  [Decorator Chain]:                                        │
│  1. @login_required - Check if user authenticated         │
│  2. @_require_role() - Check if user has required role   │
│  3. View function - Execute and prepare context           │
│  4. Render template - Display to user                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
         ↓
         │ Renders
         │
┌─────────────────────────────────────────────────────────────┐
│            TEMPLATES (10 Role-Specific)                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  templates/hospital_wards/dashboards/                      │
│  ├── patient_dashboard.html                               │
│  ├── caregiver_dashboard.html                             │
│  ├── nutritionist_dashboard.html                          │
│  ├── medical_staff_dashboard.html                         │
│  ├── chef_dashboard.html                                 │
│  ├── kitchen_staff_dashboard.html                         │
│  ├── delivery_person_dashboard.html                       │
│  ├── support_staff_dashboard.html                         │
│  ├── hospital_manager_dashboard.html                      │
│  └── admin_dashboard.html                                │
│                                                             │
│  Each template receives role-specific context data        │
│  and displays personalized interface                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## URL Routing Map

```
LOGIN ENDPOINTS
│
├─ /accounts/login/
│  └─ POST credentials → validate → session created
│     └─ Redirect → dashboard-redirect/
│
├─ /accounts/dashboard-redirect/
│  └─ Check role → Route to appropriate dashboard
│
└─ /accounts/hospital-dashboard/
   └─ Hospital-specific redirect (for hospital users only)


HOSPITAL DASHBOARDS
│
└─ /hospital/
   └─ Main entry point (routes by role)
      │
      ├─ /hospital/dashboards/patient/
      ├─ /hospital/dashboards/caregiver/
      ├─ /hospital/dashboards/nutritionist/
      ├─ /hospital/dashboards/medical-staff/
      ├─ /hospital/dashboards/chef/
      ├─ /hospital/dashboards/kitchen-staff/
      ├─ /hospital/dashboards/delivery-person/
      ├─ /hospital/dashboards/support-staff/
      ├─ /hospital/dashboards/hospital-manager/
      └─ /hospital/dashboards/admin/


OTHER HOSPITAL ROUTES
│
└─ /hospital/
   ├─ /wards/
   ├─ /delivery-schedule/
   ├─ /education/
   ├─ /nutrition/
   ├─ /notifications/
   └─ /bulk-operations/
```

---

## Security Layers

```
┌─────────────────────────────────────────────────────────────┐
│              SECURITY ARCHITECTURE                          │
└─────────────────────────────────────────────────────────────┘

LAYER 1: AUTHENTICATION
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Validate User Credentials                                │
│  ├─ Username check                                        │
│  ├─ Password hash verification                            │
│  └─ Session creation (Django SessionMiddleware)           │
│                                                             │
│  Gate: @login_required decorator                          │
│  └─ Only authenticated users proceed                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
              ↓
LAYER 2: AUTHORIZATION
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Check User Role & Permissions                            │
│  ├─ user.profile.role read from database                  │
│  ├─ Compare with required role(s)                         │
│  └─ Grant or deny access                                  │
│                                                             │
│  Gate: @_require_role() decorator                         │
│  └─ Only users with correct role proceed                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
              ↓
LAYER 3: DATA ACCESS CONTROL
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Role-Specific Data Access                                │
│  ├─ Views filter data by role                            │
│  ├─ Templates only show relevant widgets                  │
│  └─ API endpoints respect role permissions               │
│                                                             │
│  Example: Medical staff dashboard only shows              │
│  └─ Beds (not kitchen info)                               │
│     Patients (not delivery data)                          │
│     Medical alerts (not nutrition info)                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
              ↓
LAYER 4: AUDIT & LOGGING
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Track Access                                             │
│  ├─ All redirects logged                                  │
│  ├─ Failed access attempts recorded                       │
│  └─ User actions in dashboard logged                      │
│                                                             │
│  Example Log Entry:                                       │
│  "Dashboard redirect for user: doctor1"                   │
│  "Redirecting medical_staff to medical_staff_dashboard"   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Role Hierarchy

```
┌───────────────────────────────────────────────────────────┐
│           HOSPITAL WARD SYSTEM HIERARCHY                 │
└───────────────────────────────────────────────────────────┘

                          ADMIN
                            │
             ┌──────────────┼──────────────┐
             │              │              │
        HOSPITAL_MANAGER    │          Unrestricted
             │              │           Full Access
             │              │
    ┌────────┴───────────┐  │
    │                    │  │
MEDICAL_STAFF      NUTRITIONIST
    │                    │
    ├─ Admit patients    └─ Nutrition plans
    ├─ Discharge         └─ Meal planning
    ├─ Transfer
    └─ Medical records


        KITCHEN OPERATIONS
             │
    ┌────────┼────────┐
    │        │        │
  CHEF   KITCHEN_STAFF │
    │        │        │
    └────────┼────────┘
             │
        Meal Delivery


        SUPPORT STAFF
             │
        ├─ Bed Management
        ├─ Maintenance
        └─ General Operations


PATIENT-FACING ROLES
        │
    ┌───┴──────┐
    │          │
 PATIENT   CAREGIVER
    │          │
    └──────────┤
       Personal Dashboard


LOGISTICS
             │
     DELIVERY_PERSON
             │
        Delivery Tracking
```

---

## Error Handling Flow

```
┌──────────────────────────────────────────────────────────┐
│         ERROR HANDLING IN REDIRECTS                      │
└──────────────────────────────────────────────────────────┘

NO PROFILE
│
├─ User authenticated but no profile
├─ Message: "Please complete your profile setup first."
├─ Action: Redirect to /accounts/profile/
└─ User completes profile and returns


INVALID ROLE
│
├─ User has unrecognized role value
├─ Message: "Your account role is not configured properly."
├─ Action: Redirect to home page
└─ Administrator corrects role in database


UNAUTHORIZED ACCESS
│
├─ User tries to access dashboard they don't have access to
├─ Message: "You do not have access to this dashboard."
├─ Action: Redirect to main hospital dashboard
└─ User is routed to their correct dashboard instead


NOT AUTHENTICATED
│
├─ User not logged in tries to access dashboard
├─ Action: Django's @login_required redirects to login
├─ User logs in and is then routed to dashboard
└─ Normal flow resumes


EXCEPTION IN VIEW
│
├─ Unexpected error in dashboard view
├─ Error logged for debugging
├─ Message: "An error occurred while redirecting to your dashboard."
├─ Action: Redirect to home page
└─ Administrator checks error logs
```

---

## File Organization

```
dusangire/
│
├── accounts/
│   ├── views.py                    ← Redirect logic
│   │   ├── dashboard_redirect()
│   │   └── hospital_ward_login_redirect()
│   │
│   ├── urls.py                     ← Redirect URLs
│   │   ├── /dashboard-redirect/
│   │   └── /hospital-dashboard/
│   │
│   ├── models.py
│   │   └── UserProfile (contains role field)
│   │
│   └── forms.py
│
├── hospital_wards/
│   ├── views.py                    ← Dashboard views
│   │   ├── @_require_role decorator
│   │   ├── patient_dashboard()
│   │   ├── medical_staff_dashboard()
│   │   ├── ...8 more dashboards...
│   │   └── admin_dashboard()
│   │
│   ├── urls.py                     ← Dashboard routes
│   │   ├── /dashboards/patient/
│   │   ├── /dashboards/medical-staff/
│   │   ├── ...8 more routes...
│   │   └── /dashboards/admin/
│   │
│   ├── models.py
│   │   ├── Ward
│   │   ├── WardBed
│   │   ├── PatientAdmission
│   │   └── ...14 more models...
│   │
│   └── admin.py
│
├── templates/
│   └── hospital_wards/
│       └── dashboards/
│           ├── patient_dashboard.html
│           ├── caregiver_dashboard.html
│           ├── nutritionist_dashboard.html
│           ├── medical_staff_dashboard.html
│           ├── chef_dashboard.html
│           ├── kitchen_staff_dashboard.html
│           ├── delivery_person_dashboard.html
│           ├── support_staff_dashboard.html
│           ├── hospital_manager_dashboard.html
│           └── admin_dashboard.html
│
└── Documentation/
    ├── HOSPITAL_ROLE_BASED_REDIRECTS.md
    │   └── Comprehensive 443-line guide
    │
    ├── HOSPITAL_DASHBOARD_QUICK_REFERENCE.md
    │   └── Quick lookup table
    │
    └── ROLE_BASED_REDIRECTS_SUMMARY.md
        └── Implementation summary
```

---

## Summary

This architecture provides:

✅ **Clean Separation** - Auth, routing, and views are separate
✅ **Scalability** - Easy to add new roles
✅ **Security** - Multiple authentication/authorization layers
✅ **Maintainability** - Clear mapping of role → view → template
✅ **User Experience** - Automatic routing to correct dashboard
✅ **Error Handling** - Graceful fallbacks and clear messages
✅ **Logging** - Audit trail of all redirects

**Result**: Users automatically see their role-appropriate dashboard! 🎉
