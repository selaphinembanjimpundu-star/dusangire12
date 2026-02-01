# Quick Reference - Patient Admission & Discharge System

## 🚀 Quick Start (5 Minutes)

### 1. Initialize Test Data
```bash
cd "path/to/Dusangire"
python manage.py populate_hospital_data --patients 20 --wards 4
```

### 2. Login with Test Account
- **URL**: http://localhost:8000/accounts/login/
- **Username**: `manager1` (for full access)
- **Password**: `testpass123`

### 3. Access Features
| Feature | URL | Role |
|---------|-----|------|
| Admit Patient | /hospital/patients/admit/ | Support Staff+ |
| Discharge Patient | /hospital/patients/<id>/discharge/ | Support Staff+ |
| Transfer Patient | /hospital/patients/transfer-bed/ | Support Staff+ |
| Occupancy Report | /hospital/reports/occupancy/ | Manager+ |
| Admin Panel | /admin/ | Admin |

---

## 🎯 Common Tasks

### Admit a Patient
1. Go to: **Support Staff Dashboard**
2. Click: **"Admit New Patient"** button
3. Select: Patient from dropdown
4. Select: Available bed
5. Fill: Medical information
6. Click: **Submit**
✅ Patient assigned to bed

### Discharge a Patient
1. Go to: **Support Staff Dashboard**
2. Find: Patient in "Pending Discharges"
3. Click: **"Discharge"** button
4. Fill: Discharge details
5. Click: **Submit**
✅ Bed becomes available

### Transfer Patient
1. Go to: **Support Staff Dashboard**
2. Click: **"Transfer Patient"** button
3. Select: Patient
4. Select: New bed
5. Click: **Submit**
✅ Patient moved to new bed

### View Occupancy
1. Go to: **Hospital Manager Dashboard**
2. Click: **"View Occupancy Report"**
3. View:
   - Total occupancy %
   - Ward breakdown
   - Recent admissions/discharges
4. Export: CSV or Print

---

## 📱 User Interfaces

### 1. Admission Form
```
Patient Selection ▼
Bed Selection ▼
Admission Reason ▼
Chief Complaint [_______]
Allergies [________]
Current Medications [________]
```

### 2. Discharge Form
```
Discharge Status ▼
Discharge Notes [_______]
Medications [_______]
Follow-up Instructions [_______]
Activity Restrictions [_______]
Return Visit Date [_______]
```

### 3. Transfer Form
```
Patient Selection ▼
Current Bed [Auto-filled]
New Bed Selection ▼
Transfer Reason [_______]
```

### 4. Occupancy Report
```
[Total Beds: 65] [Occupied: 34] [Available: 31] [Occupancy: 52%]

WARD BREAKDOWN
Ward | Total | Occupied | Available | %
-----|-------|----------|-----------|---
General A | 20 | 10 | 10 | 50%
General B | 20 | 8 | 12 | 40%
ICU | 10 | 8 | 2 | 80%
Pediatric | 15 | 8 | 7 | 53%

RECENT ADMISSIONS
Patient | Bed | Reason | Date
--------|-----|--------|------

RECENT DISCHARGES
Patient | Status | Date
--------|--------|------
```

---

## 🔑 Key URLs

```
# Admission/Discharge/Transfer
POST /hospital/patients/admit/
GET  /hospital/patients/admit/
POST /hospital/patients/<admission_id>/discharge/
GET  /hospital/patients/<admission_id>/discharge/
POST /hospital/patients/transfer-bed/
GET  /hospital/patients/transfer-bed/

# Reports
GET /hospital/reports/occupancy/

# AJAX
GET /hospital/api/patient/<patient_id>/current-bed/

# Admin
GET /admin/hospital_wards/patientadmission/
GET /admin/hospital_wards/patientdischarge/
GET /admin/hospital_wards/patienttransfer/
GET /admin/hospital_wards/bedmaintenanceschedule/
```

---

## 📊 Database Models

### PatientAdmission
```
id (PK)
patient_id (FK) → User
bed_id (FK) → WardBed
admission_date
admitted_by_id (FK) → User
reason
chief_complaint
medical_history
allergies
current_medications
is_active
created_at
updated_at
```

### PatientDischarge
```
id (PK)
admission_id (OneToOne) → PatientAdmission
discharge_date
discharge_status
discharged_by_id (FK) → User
discharge_notes
follow_up_instructions
medications_prescribed
restrictions
return_visit_date
created_at
updated_at
```

### PatientTransfer
```
id (PK)
patient_id (FK) → User
from_bed_id (FK) → WardBed
to_bed_id (FK) → WardBed
transfer_date
transferred_by_id (FK) → User
reason
is_completed
created_at
updated_at
```

### BedMaintenanceSchedule
```
id (PK)
bed_id (FK) → WardBed
maintenance_type
scheduled_date
completed_date
assigned_to_id (FK) → User
description
notes
is_completed
created_at
updated_at
```

---

## 🔐 Permissions Matrix

| Action | Support Staff | Manager | Admin |
|--------|:----------:|:-------:|:-----:|
| Admit | ✅ | ✅ | ✅ |
| Discharge | ✅ | ✅ | ✅ |
| Transfer | ✅ | ✅ | ✅ |
| View Report | ❌ | ✅ | ✅ |
| Admin Panel | ❌ | ❌ | ✅ |

---

## 🧪 Test Data

```
Wards: 4
├─ General Ward A (20 beds)
├─ General Ward B (20 beds)
├─ ICU Ward (10 beds)
└─ Pediatric Ward (15 beds)

Beds: 65 total
├─ Occupied: ~34
└─ Available: ~31

Patients: 20
Staff: 12
```

---

## 🐛 Troubleshooting

### "Bed not available"
- Patient already in bed? Check "Active Admissions"
- Bed in maintenance? Select different bed
- **Solution:** Try another available bed

### "Patient not found"
- Patient must exist in system
- **Solution:** Create patient first or use existing one

### "Permission denied"
- Not logged in? Login first
- Wrong role? Request access from admin
- **Solution:** Use appropriate user account

### "Transfer failed"
- New bed not available? Select another
- Patient not currently admitted? Admit first
- **Solution:** Check patient's current status

---

## 📝 Common Workflows

### New Patient Admission
```
1. Support Staff Dashboard
   ↓
2. Click "Admit New Patient"
   ↓
3. Select patient & bed
   ↓
4. Enter medical info
   ↓
5. Submit form
   ↓
6. System assigns bed
   ↓
7. Patient appears in "Active Admissions"
```

### Patient Discharge
```
1. Support Staff Dashboard
   ↓
2. Find in "Pending Discharges"
   ↓
3. Click "Discharge"
   ↓
4. Enter discharge details
   ↓
5. Submit form
   ↓
6. System releases bed
   ↓
7. Bed becomes available
```

### Occupancy Check
```
1. Manager/Admin Dashboard
   ↓
2. Click "View Occupancy Report"
   ↓
3. Review statistics
   ↓
4. Check ward breakdown
   ↓
5. Export if needed
```

---

## 🔧 Admin Operations

### Manage Admissions
1. Go to: `/admin/hospital_wards/patientadmission/`
2. Actions:
   - ✓ View all admissions
   - ✓ Filter by reason/date
   - ✓ Search patients
   - ✓ Edit admission details
   - ✓ Mark active/inactive

### Manage Discharges
1. Go to: `/admin/hospital_wards/patientdischarge/`
2. Actions:
   - ✓ View discharge history
   - ✓ Filter by status
   - ✓ Search patients
   - ✓ View follow-up instructions

### Manage Transfers
1. Go to: `/admin/hospital_wards/patienttransfer/`
2. Actions:
   - ✓ View transfer history
   - ✓ Filter by date
   - ✓ Search patients
   - ✓ Mark completed

### Manage Maintenance
1. Go to: `/admin/hospital_wards/bedmaintenanceschedule/`
2. Actions:
   - ✓ Schedule maintenance
   - ✓ Track completion
   - ✓ Assign staff
   - ✓ Record notes

---

## 📞 Support

### Documentation
- Main Guide: `PATIENT_ADMISSION_DISCHARGE_WORKFLOW.md`
- Implementation: `PHASE_3_COMPLETION_REPORT.md`
- Summary: `IMPLEMENTATION_SUMMARY.md`

### Code Reference
- Models: `hospital_wards/models.py`
- Views: `hospital_wards/views.py`
- URLs: `hospital_wards/urls.py`
- Admin: `hospital_wards/admin.py`

### Templates
- `templates/hospital_wards/admission_form.html`
- `templates/hospital_wards/discharge_form.html`
- `templates/hospital_wards/transfer_form.html`
- `templates/hospital_wards/occupancy_report.html`

---

## ⚡ Performance Tips

- Use occupancy report for quick statistics
- Filter admissions by date for faster loading
- Use search for specific patients
- Export data in CSV for analysis
- Check bed availability before transfer

---

**Version:** 1.0  
**Last Updated:** 2026-02-01  
**Status:** ✅ Production Ready

