# Hospital Ward System - Architecture & Visual Guide

## 🏗️ System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    DUSANGIRE HOSPITAL                       │
│                  MANAGEMENT SYSTEM                          │
└─────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
        ┌───────▼──────┐ ┌───▼────────┐ ┌──▼─────────┐
        │  WEB BROWSER │ │   MOBILE   │ │   ADMIN    │
        │   (Patient)  │ │    APP     │ │   PANEL    │
        └───────┬──────┘ └───┬────────┘ └──┬─────────┘
                │            │             │
                └────────────┼─────────────┘
                             │
                    ┌────────▼────────┐
                    │  DJANGO VIEWS   │
                    │  & ENDPOINTS    │
                    └────────┬────────┘
                             │
                ┌────────────┼────────────┐
                │            │            │
        ┌───────▼──────┐ ┌──▼────────┐ ┌─▼──────────┐
        │   FORMS &    │ │   MODELS  │ │  ADMIN     │
        │  TEMPLATES   │ │           │ │  CLASSES   │
        └───────┬──────┘ └──┬────────┘ └─┬──────────┘
                │            │            │
                └────────────┼────────────┘
                             │
                    ┌────────▼────────┐
                    │    DATABASE     │
                    │   (SQLite)      │
                    └─────────────────┘
```

---

## 🗄️ Database Schema Diagram

```
USER (Django Auth)
├── id (PK)
├── username
├── email
├── first_name
├── last_name
└── password

    │
    ├─────┬──────────────────────┐
    │     │                      │
    │     ▼                      ▼
    │  WARD                   PATIENT ADMISSION
    │  ├─ id (PK)            ├─ id (PK)
    │  ├─ name               ├─ patient_id (FK→User)
    │  ├─ location           ├─ bed_id (FK→WardBed)
    │  ├─ capacity           ├─ admission_date
    │  └─ is_active          ├─ reason
    │     │                  ├─ chief_complaint
    │     ▼                  ├─ medical_history
    │  WARD BED              ├─ allergies
    │  ├─ id (PK)            ├─ current_medications
    │  ├─ ward_id (FK)       └─ is_active
    │  ├─ bed_number              │
    │  ├─ status                  ▼
    │  ├─ patient_id (FK→User)  PATIENT DISCHARGE
    │  ├─ assigned_at            ├─ id (PK)
    │  └─ notes                  ├─ admission_id (1-to-1)
    │     │                      ├─ discharge_date
    │     ├─────┬────────────┐   ├─ discharge_status
    │     │     │            │   ├─ medications_prescribed
    │     ▼     ▼            ▼   ├─ follow_up_instructions
    │   PATIENT PATIENT   BED     ├─ restrictions
    │   TRANSFER EDUCATION MAINTENANCE
    │   ├─ id     ├─ id     ├─ id
    │   ├─ patient├─ category├─ bed_id
    │   ├─ from_bed└─ title ├─ type
    │   ├─ to_bed    └─ content└─ date
    │   └─ reason
    │
    └─────────► STAFF ROLES (via Groups/Permissions)
               ├─ Support Staff
               ├─ Hospital Manager
               ├─ Medical Staff
               └─ Admin

```

---

## 🔄 Patient Admission Workflow

```
START
  │
  ▼
[Patient arrives at hospital]
  │
  ▼
[Support Staff login]
  │
  ▼
[Open Support Staff Dashboard]
  │
  ▼
[Click "Admit New Patient"]
  │
  ▼
[admission_form.html]
  ├─ Select Patient from dropdown
  │  │
  │  └─► AJAX: Load patient details
  │
  ├─ Select Available Bed
  │  │
  │  └─► Show only available beds
  │
  ├─ Enter Medical Information
  │  ├─ Admission Reason
  │  ├─ Chief Complaint
  │  ├─ Medical History
  │  ├─ Allergies
  │  └─ Current Medications
  │
  ▼
[Submit Form via AJAX]
  │
  ▼
[patient_admission() view processes]
  │
  ├─ Validate: Patient exists
  ├─ Validate: Bed available
  ├─ Create: PatientAdmission record
  ├─ Update: WardBed status → "occupied"
  ├─ Update: WardBed.patient → Patient
  └─ Return: JSON response
  │
  ▼
[Database Updated]
  │
  ▼
[Dashboard refreshes]
  │
  ▼
[Patient visible in "Active Admissions"]
  │
  ▼
[Medical Staff can see patient]
  │
  ▼
[Bed marked as occupied]
  │
  ▼
END ✅

```

---

## 🔄 Patient Discharge Workflow

```
START
  │
  ▼
[Patient ready for discharge]
  │
  ▼
[Support Staff opens dashboard]
  │
  ▼
[Finds patient in "Pending Discharges"]
  │
  ▼
[Click "Discharge" button]
  │
  ▼
[discharge_form.html]
  │
  ├─ Shows Current Admission
  │  ├─ Patient Name
  │  ├─ Bed Number
  │  ├─ Admission Date
  │  └─ Reason
  │
  ├─ Select Discharge Status
  │  ├─ Discharged (normal)
  │  ├─ Referral (transferred)
  │  ├─ Absconded (left AMA)
  │  └─ Deceased
  │
  ├─ Enter Discharge Details
  │  ├─ Discharge Notes
  │  ├─ Medications Prescribed
  │  ├─ Follow-up Instructions
  │  ├─ Restrictions
  │  └─ Return Visit Date
  │
  ▼
[Submit Form via AJAX]
  │
  ▼
[patient_discharge() view processes]
  │
  ├─ Validate: Admission exists
  ├─ Validate: Not yet discharged
  ├─ Create: PatientDischarge record
  ├─ Update: PatientAdmission.is_active → False
  ├─ Update: WardBed.patient → NULL
  ├─ Update: WardBed.status → "available"
  └─ Return: JSON response
  │
  ▼
[Database Updated]
  │
  ▼
[Bed becomes available]
  │
  ▼
[Patient removed from active list]
  │
  ▼
[Discharge record created]
  │
  ▼
[Can be viewed in occupancy report]
  │
  ▼
END ✅

```

---

## 🔄 Patient Transfer Workflow

```
START
  │
  ▼
[Patient needs to move beds]
  │
  ▼
[Support Staff opens dashboard]
  │
  ▼
[Click "Transfer Patient"]
  │
  ▼
[transfer_form.html]
  │
  ├─ Select Patient
  │  │
  │  └─► AJAX to get_patient_current_bed()
  │
  ├─ Current Bed (Auto-populated)
  │  ├─ Bed Number
  │  └─ Ward Name
  │
  ├─ Select New Bed
  │  └─ Show only available beds in other wards
  │
  ├─ Enter Transfer Reason
  │
  ▼
[Submit Form via AJAX]
  │
  ▼
[transfer_patient_bed() view processes]
  │
  ├─ Validate: Patient exists
  ├─ Validate: From bed occupied by patient
  ├─ Validate: To bed available
  ├─ Get: Who transferred (staff member)
  │
  ├─ Create: PatientTransfer record
  │  ├─ From Bed: Original bed
  │  ├─ To Bed: New bed
  │  ├─ Transferred by: Staff member ID
  │  └─ Reason: Clinical reason
  │
  ├─ Update: Original bed
  │  ├─ patient → NULL
  │  └─ status → "available"
  │
  ├─ Update: New bed
  │  ├─ patient → Patient
  │  └─ status → "occupied"
  │
  └─ Return: JSON response
  │
  ▼
[Database Updated]
  │
  ▼
[Patient now in new bed]
  │
  ▼
[Original bed available]
  │
  ▼
[Transfer audit trail recorded]
  │
  ▼
END ✅

```

---

## 📊 Occupancy Report Workflow

```
START
  │
  ▼
[Hospital Manager/Admin login]
  │
  ▼
[Navigate to Occupancy Report]
  │
  ▼
[occupancy_report() view]
  │
  ├─ Calculate: Total beds (SUM all ward capacities)
  │
  ├─ Calculate: Occupied beds (COUNT where status='occupied')
  │
  ├─ Calculate: Available beds (Total - Occupied)
  │
  ├─ Calculate: Occupancy percentage
  │  └─ (Occupied / Total) * 100
  │
  ├─ For each Ward:
  │  ├─ Count: Total capacity
  │  ├─ Count: Occupied beds
  │  ├─ Count: Available beds
  │  ├─ Count: Maintenance beds
  │  └─ Calculate: Ward occupancy %
  │
  ├─ Get: Last 10 admissions
  │  └─ Patient, Bed, Reason, Date
  │
  ├─ Get: Last 10 discharges
  │  └─ Patient, Status, Date
  │
  ▼
[occupancy_report.html renders]
  │
  ├─ Statistics Cards (4)
  │  ├─ Total Beds
  │  ├─ Occupied Beds
  │  ├─ Available Beds
  │  └─ Occupancy % with progress bar
  │
  ├─ Ward Breakdown Table
  │  ├─ Ward Name
  │  ├─ Total | Occupied | Available | Maintenance
  │  └─ Occupancy % with color coding
  │
  ├─ Recent Admissions Table
  │  ├─ Patient Name
  │  ├─ Bed Number
  │  ├─ Reason
  │  └─ Date
  │
  ├─ Recent Discharges Table
  │  ├─ Patient Name
  │  ├─ Status
  │  └─ Date
  │
  ├─ Export Options
  │  ├─ Print (PDF)
  │  └─ CSV (Excel)
  │
  ▼
[User views report]
  │
  ▼
[Optional: Export to file]
  │
  ▼
END ✅

```

---

## 🔐 Authentication & Permission Flow

```
┌─ LOGIN ─────────────────────┐
│ Username & Password         │
└────────────┬────────────────┘
             │
             ▼
    ┌────────────────────┐
    │  Django Auth       │
    │  Verify User       │
    └────────┬───────────┘
             │
             ▼
    ┌────────────────────┐
    │  Check Groups      │
    │  & Permissions     │
    └────────┬───────────┘
             │
    ┌────────┴────────────────────────┐
    │                                 │
    ▼                                 ▼
┌─────────────┐              ┌──────────────────┐
│  SUPPORT    │              │  HOSPITAL        │
│  STAFF      │              │  MANAGER         │
└──────┬──────┘              └────────┬─────────┘
       │                              │
       ├─ Admit patients             ├─ All support staff access
       ├─ Discharge patients         ├─ View occupancy reports
       ├─ Transfer patients          ├─ Analytics dashboard
       └─ View dashboards            └─ Admin panel (read-only)
                                           │
                                           ▼
                                      ┌──────────────┐
                                      │  ADMIN       │
                                      │  SUPER USER  │
                                      └──────┬───────┘
                                             │
                                             ├─ Everything
                                             ├─ Manage users
                                             ├─ Manage roles
                                             ├─ View all data
                                             └─ System settings

```

---

## 📊 Data Models Relationship Diagram

```
User
 │
 ├─ Patient (is User)
 │  │
 │  └─ PatientAdmission (1-to-many)
 │     │
 │     ├─ WardBed (assigned bed)
 │     │
 │     └─ PatientDischarge (1-to-1)
 │
 ├─ Staff (is User)
 │  │
 │  ├─ Hospital Manager (role)
 │  ├─ Support Staff (role)
 │  ├─ Medical Staff (role)
 │  │
 │  └─ BedMaintenanceSchedule (assigned to)
 │     │
 │     └─ WardBed (bed to maintain)
 │
 └─ PatientTransfer (transferred_by)
    │
    ├─ Patient (patient being transferred)
    ├─ WardBed (from_bed)
    └─ WardBed (to_bed)

Ward
 │
 └─ WardBed (1-to-many)
    │
    ├─ Patient (current occupant)
    ├─ PatientAdmission (admission record)
    └─ BedMaintenanceSchedule (maintenance history)

```

---

## 🔗 URL Routing Map

```
/hospital/
├── /patients/
│   ├── /admit/                           [POST/GET]
│   │   └─ admission_form.html
│   │   └─ patient_admission() view
│   │
│   ├── /<id>/discharge/                  [POST/GET]
│   │   └─ discharge_form.html
│   │   └─ patient_discharge() view
│   │
│   └── /transfer-bed/                    [POST/GET]
│       └─ transfer_form.html
│       └─ transfer_patient_bed() view
│
├── /api/
│   └── /patient/<id>/current-bed/        [GET - AJAX]
│       └─ get_patient_current_bed() view
│       └─ Returns: JSON {bed_id, bed_number, ward}
│
├── /reports/
│   └── /occupancy/                       [GET]
│       └─ occupancy_report.html
│       └─ occupancy_report() view
│       └─ With statistics and export
│
└── /admin/                               [Django Admin]
    ├── /hospital_wards/patientadmission/
    ├── /hospital_wards/patientdischarge/
    ├── /hospital_wards/patienttransfer/
    └── /hospital_wards/bedmaintenanceschedule/

```

---

## 📱 User Interface Flow

```
┌─────────────────┐
│  Login Page     │
└────────┬────────┘
         │
    ┌────┴────┐
    │          │
    ▼          ▼
┌──────────┐ ┌──────────────────┐
│ SUPPORT  │ │  HOSPITAL        │
│ STAFF    │ │  MANAGER         │
└────┬─────┘ └────────┬─────────┘
     │                │
     ▼                ▼
┌─────────────┐   ┌──────────────┐
│ Dashboard   │   │ Dashboard    │
│ - Admissions│   │ - Analytics  │
│ - Transfers │   │ - Reports    │
│ - Discharges│   │ - Statistics │
└────┬────────┘   └──────┬───────┘
     │                   │
     ├─────┬─────┬───────┤
     │     │     │       │
     ▼     ▼     ▼       ▼
   ADMIT  DISCHARGE TRANSFER OCCUPANCY
   FORM   FORM      FORM      REPORT
     │     │         │         │
     └─────┴─────────┴─────────┘
             │
             ▼
       [AJAX Submit]
             │
             ▼
       [Update Data]
             │
             ▼
    [Refresh Dashboard]
             │
             ▼
         [Success!]

```

---

## ⚙️ System Configuration

### Required Settings (settings.py)
```python
INSTALLED_APPS = [
    'hospital_wards',
    # ... other apps
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        # ... other options
    },
]

# Permissions required
LOGIN_REQUIRED = True
AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend']
```

### Database Requirements
- SQLite (default) or PostgreSQL/MySQL
- Migration 0002_bedmaintenanceschedule_patientadmission_and_more applied
- Foreign key constraints enabled

### Static Files
```
/static/
├── /css/
│   └── hospital_ward.css
├── /js/
│   └── hospital_ward.js
└── /images/
```

---

## 🚀 Deployment Architecture

```
┌──────────────────────────────────────┐
│       PRODUCTION SERVER              │
│     (e.g., PythonAnywhere)          │
└──────────────────────────────────────┘
             │
    ┌────────┼────────┐
    │        │        │
    ▼        ▼        ▼
┌────┐  ┌─────┐  ┌───────┐
│APP │  │WSGI │  │STATIC │
│CODE│  │     │  │ FILES │
└──┬─┘  └──┬──┘  └───────┘
   │       │
   └───┬───┘
       │
       ▼
  ┌─────────┐
  │DATABASE │ (SQLite or PostgreSQL)
  └─────────┘
       │
       ├─ User accounts
       ├─ Wards
       ├─ Beds
       ├─ Admissions
       ├─ Discharges
       ├─ Transfers
       └─ Maintenance schedules

```

---

## 📈 Performance Optimization

### Database Query Optimization
```python
# GOOD: Optimized queries used in views
admission = (
    PatientAdmission.objects
    .select_related('patient', 'bed__ward')  # Reduce queries
    .prefetch_related('patient__groups')     # Related objects
    .filter(is_active=True)
    .order_by('-admission_date')
)

# Result: 1-2 queries instead of N+1
```

### Caching Strategy
```
- Ward occupancy: Cache for 5 minutes
- Available beds: Cache for 2 minutes
- Patient dashboard: No cache (real-time)
- Reports: Cache for 1 hour
```

### Index Strategy
```
CREATE INDEX idx_patientadmission_is_active 
ON hospital_wards_patientadmission(is_active);

CREATE INDEX idx_wardbed_status 
ON hospital_wards_wardbed(status);

CREATE INDEX idx_patienttransfer_date 
ON hospital_wards_patienttransfer(transfer_date);
```

---

**Last Updated**: February 2, 2026  
**Version**: 1.0  
**Status**: ✅ Production Ready

