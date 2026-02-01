# Patient Admission & Discharge Workflow Implementation

## Overview

This document describes the comprehensive patient admission, discharge, and transfer workflow system implemented for the Dusangire Hospital Management System. The system allows support staff and hospital managers to efficiently manage patient bed assignments, admissions, discharges, and transfers between beds.

## Features Implemented

### 1. Patient Admission System

**Models:**
- `PatientAdmission` - Tracks patient admissions with complete medical history

**Fields:**
- `patient` - ForeignKey to User
- `bed` - ForeignKey to WardBed
- `admission_date` - Auto-set to current date/time
- `admitted_by` - User who performed admission
- `reason` - Choice field (routine, emergency, referral, transfer, planned_surgery)
- `chief_complaint` - Primary health concern
- `medical_history` - Past medical conditions
- `allergies` - Known allergies
- `current_medications` - Current medication list
- `is_active` - Whether admission is still active

**View: `patient_admission()`**
```
URL: /hospital/patients/admit/
Methods: GET (show form), POST (process admission)
Permissions: support_staff, hospital_manager, admin
```

**Features:**
- Patient selection dropdown with phone numbers
- Available bed selection with ward information
- Admission reason selection
- Medical information capture (allergies, medications, chief complaint)
- Automatic bed assignment upon admission
- Caregiver notification creation
- JSON response for AJAX integration

### 2. Patient Discharge System

**Models:**
- `PatientDischarge` - Tracks patient discharge with follow-up instructions

**Fields:**
- `admission` - OneToOneField to PatientAdmission
- `discharge_date` - Auto-set to current date/time
- `discharge_status` - Choice field (discharged, referral, absconded, deceased)
- `discharged_by` - User who performed discharge
- `discharge_notes` - Summary of hospital stay
- `follow_up_instructions` - Post-discharge care instructions
- `medications_prescribed` - Medications to take home
- `restrictions` - Physical activity restrictions
- `return_visit_date` - Scheduled follow-up appointment

**View: `patient_discharge()`**
```
URL: /hospital/patients/<admission_id>/discharge/
Methods: GET (show form), POST (process discharge)
Permissions: support_staff, hospital_manager, admin
```

**Features:**
- Admission information display (patient name, bed, admission date)
- Discharge status selection
- Comprehensive discharge note form
- Follow-up instructions and medication recording
- Activity restrictions documentation
- Return visit date scheduling
- Automatic bed release upon discharge
- Caregiver notification

### 3. Patient Transfer System

**Models:**
- `PatientTransfer` - Tracks patient bed/ward transfers

**Fields:**
- `patient` - ForeignKey to User
- `from_bed` - Source bed
- `to_bed` - Destination bed
- `transfer_date` - Auto-set to current date/time
- `transferred_by` - User who performed transfer
- `reason` - Transfer reason (clinical, isolation, isolation_removal, family_request, bed_maintenance)
- `is_completed` - Transfer completion status

**View: `transfer_patient_bed()`**
```
URL: /hospital/patients/transfer-bed/
Methods: GET (show form), POST (process transfer)
Permissions: support_staff, hospital_manager
```

**Features:**
- Currently hospitalized patient list
- Current bed display with AJAX lookup
- Available bed selection from other wards
- Transfer reason documentation
- Automatic bed assignment/release
- Caregiver notification
- Complete transfer audit trail

### 4. Bed Maintenance Scheduling

**Models:**
- `BedMaintenanceSchedule` - Track preventive bed maintenance

**Fields:**
- `bed` - ForeignKey to WardBed
- `maintenance_type` - Choice field (cleaning, repair, replacement, inspection)
- `scheduled_date` - Planned maintenance date
- `completed_date` - Actual completion date
- `assigned_to` - User assigned to maintenance
- `description` - Maintenance details
- `notes` - Additional notes
- `is_completed` - Completion status

**Admin Interface:**
- List display: bed_number, maintenance_type, scheduled_date, is_completed
- Filters by type, date, and completion status
- Search by bed number

### 5. Occupancy Report System

**View: `occupancy_report()`**
```
URL: /hospital/reports/occupancy/
Methods: GET (display report)
Permissions: hospital_manager, admin
```

**Features:**
- Overall hospital occupancy statistics
  - Total beds
  - Occupied beds
  - Available beds
  - Occupancy percentage
- Ward-by-ward breakdown with:
  - Total beds per ward
  - Occupied/available/maintenance bed counts
  - Occupancy rate per ward
  - Status indicators (High/Moderate/Low)
- Recent admissions list (last 10)
  - Patient name, bed number, admission date, reason
- Recent discharges list (last 10)
  - Patient name, discharge status, discharge date
- Export functionality:
  - Print report
  - CSV download

### 6. Support Staff Dashboard Enhancement

**View: `support_staff_dashboard()`**

**New Sections:**
- Quick Actions toolbar with:
  - Admit New Patient button
  - Transfer Patient button
  - View Occupancy Report button
- Bed Status table showing:
  - Ward, bed number, status, patient assignment
  - Quick action buttons (View, Transfer)
- Active Admissions list:
  - Patient names, bed assignments, admission dates, reasons
  - Recent patient activities
- Pending Discharges table:
  - Patients ready for discharge
  - Length of stay calculation
  - Discharge button for quick processing

**Context Data:**
```python
{
    'active_beds': count of occupied beds,
    'available_beds': count of available beds,
    'maintenance_beds': count of maintenance beds,
    'support_requests': count of pending discharges,
    'active_admissions': list of active admission records,
    'pending_discharges': list of admissions ready for discharge,
    'bed_status_summary': dict with status counts,
    'ward_beds': sample of bed records,
    'bed_assignments': assigned beds with patient info,
    'ward_summary': list of wards,
}
```

### 7. Hospital Manager Dashboard Enhancement

**Quick Actions Section:**
- View Occupancy Report button
- Admit Patient button  
- Transfer Patient button
- Admin Panel button

**Available for:**
- Comprehensive hospital analytics
- Occupancy monitoring
- Patient flow oversight
- Staff management

## API Endpoints

### AJAX Endpoints

**Get Patient's Current Bed**
```
URL: /hospital/api/patient/<patient_id>/current-bed/
Method: GET
Response: {
    "bed_id": int,
    "bed_number": str,
    "ward": str
}
Error Response: {"error": "Patient not currently in hospital"}
```

## URL Configuration

```python
# Patient Admission & Discharge Workflow
path('patients/admit/', views.patient_admission, name='patient_admission'),
path('patients/<int:admission_id>/discharge/', views.patient_discharge, name='patient_discharge'),
path('patients/transfer-bed/', views.transfer_patient_bed, name='transfer_patient_bed'),
path('api/patient/<int:patient_id>/current-bed/', views.get_patient_current_bed, name='get_patient_current_bed'),
path('reports/occupancy/', views.occupancy_report, name='occupancy_report'),
```

## Templates Created

### 1. `admission_form.html`
- Patient and bed selection dropdowns
- Admission reason field
- Chief complaint input
- Allergies text area
- Current medications text area
- Form submission with AJAX
- Automatic redirect after successful admission

### 2. `discharge_form.html`
- Current admission information display
- Discharge status selection
- Discharge notes field
- Medications prescribed field
- Follow-up instructions field
- Activity restrictions field
- Return visit date picker
- Form submission with AJAX

### 3. `transfer_form.html`
- Patient selection dropdown
- Current bed auto-lookup via AJAX
- Available bed selection (across all wards)
- Transfer reason field
- Form submission with AJAX
- Automatic redirect after transfer

### 4. `occupancy_report.html`
- Overall statistics cards
- Ward-by-ward occupancy table with:
  - Bed counts and status distribution
  - Occupancy rate progress bars
  - Status indicators
- Recent admissions table
- Recent discharges table
- Print and CSV export buttons

## Database Migrations

**Migration: `0002_bedmaintenanceschedule_patientadmission_and_more.py`**

Creates four new tables:
- `hospital_wards_patientadmission`
- `hospital_wards_patientdischarge`
- `hospital_wards_patienttransfer`
- `hospital_wards_bedmaintenanceschedule`

All tables include:
- Primary key (`id`)
- Foreign key relationships
- Timestamp fields (created_at/updated_at where applicable)
- Choice field columns for status types
- Text fields for notes/descriptions

## Admin Interface Extensions

**Four New Admin Classes:**

1. **PatientAdmissionAdmin**
   - Fieldsets: Patient Info, Admission Details, Medical History, Status
   - List display: patient_name, admission_date, reason, bed_number, admitted_by
   - Filters: reason, admission_date, is_active
   - Search: patient first/last name

2. **PatientDischargeAdmin**
   - Fieldsets: Discharge Info, Instructions & Medications, Follow Up
   - List display: patient_name, discharge_date, discharge_status, discharged_by
   - Filters: discharge_status, discharge_date
   - Search: patient name

3. **PatientTransferAdmin**
   - List display: patient_name, from_bed_number, to_bed_number, transfer_date, is_completed
   - Filters: transfer_date, is_completed
   - Search: patient name

4. **BedMaintenanceScheduleAdmin**
   - List display: bed_number, maintenance_type, scheduled_date, is_completed
   - Filters: maintenance_type, scheduled_date, is_completed
   - Search: bed number

## Sample Data Generation

**Management Command: `populate_hospital_data`**

Creates realistic test data:
```bash
python manage.py populate_hospital_data --patients 20 --wards 4 --clear
```

**Generates:**
- 4-5 wards with realistic capacities
- 65+ beds across wards with status distribution
- 12 staff members with various roles
- 20 patient users
- Patient-to-bed assignments
- Education categories and materials

**Test Credentials (password: testpass123):**
- doctor1
- chef1
- manager1
- patient1
- admin1

## Permissions & Access Control

**Views Protected By Role:**

| Feature | support_staff | manager | admin |
|---------|:----------:|:-------:|:-----:|
| Admit Patient | ✅ | ✅ | ✅ |
| Discharge Patient | ✅ | ✅ | ✅ |
| Transfer Patient | ✅ | ✅ | ✅ |
| View Occupancy | ✅ | ✅ | ✅ |
| Occupancy Report | ❌ | ✅ | ✅ |

## Integration Points

### Models Integration
- **PatientAdmission** ↔ **User** (patient)
- **PatientAdmission** ↔ **WardBed** (bed assignment)
- **PatientAdmission** ↔ **User** (admitted_by staff)
- **PatientDischarge** ↔ **PatientAdmission** (one-to-one)
- **PatientTransfer** ↔ **WardBed** (from/to beds)

### View Integration
- Support Staff Dashboard displays active admissions & pending discharges
- Hospital Manager Dashboard includes occupancy metrics & reports
- Medical Staff Dashboard shows real patient-bed occupancy data

### Admin Integration
- New admin classes registered with Django admin
- Full CRUD operations available for clinical staff
- Custom fieldsets for organized data entry
- Search and filter capabilities for quick access

## Workflow Diagrams

### Admission Workflow
```
1. Support Staff → Click "Admit Patient"
2. Select Patient → Select Bed → Enter Medical Info
3. System → Validates bed availability
4. System → Creates PatientAdmission record
5. System → Updates WardBed.patient & status to 'occupied'
6. System → Creates notification
7. Dashboard → Displays in "Active Admissions"
```

### Discharge Workflow
```
1. Support Staff → Patient ready for discharge
2. System → Identifies admission from "Pending Discharges"
3. Staff → Click "Discharge" button
4. Form → Enter discharge details & follow-up info
5. System → Creates PatientDischarge record
6. System → Updates PatientAdmission.is_active = False
7. System → Releases WardBed (status = 'available')
8. System → Creates notification
```

### Transfer Workflow
```
1. Support Staff → Select patient in "Transfer Patient"
2. System → AJAX lookup current bed
3. Staff → Select new destination bed
4. System → Validates bed availability
5. System → Creates PatientTransfer record
6. System → Releases old bed
7. System → Assigns to new bed
8. System → Creates notification
```

## Error Handling

All views include try-catch blocks returning:
- `JsonResponse({'success': True, 'message': '...'})` on success
- `JsonResponse({'error': '...', 'success': False}, status=400)` on error
- Appropriate HTTP status codes (403, 404, 400)

## Future Enhancements

1. **Bulk Operations:**
   - CSV import for patient admissions
   - Batch discharge processing
   - Transfer multiple patients

2. **Notifications:**
   - SMS/Email alerts for patient admissions
   - Discharge reminders
   - Bed maintenance scheduling notifications

3. **Analytics:**
   - Average length of stay calculations
   - Ward capacity utilization trends
   - Admission/discharge statistics over time

4. **Clinical Features:**
   - Patient medical history timeline
   - Medication tracking
   - Vital signs monitoring

5. **Integration:**
   - Billing system integration
   - Lab results linking
   - Radiology report attachment

## Testing

**Test Data Available:**
- 20 patients already assigned to beds
- 65 beds across 4 wards
- Multiple staff roles for testing permissions
- Ready-to-use test credentials

**Manual Testing Steps:**
1. Login as support staff with `support1` account
2. Navigate to Support Staff Dashboard
3. Test "Admit New Patient" feature
4. Test "Transfer Patient" feature
5. Test "View Occupancy Report"
6. Verify patients appear in appropriate lists
7. Test discharge functionality
8. Monitor bed status updates in real-time

## Performance Considerations

- Views use `select_related()` and `prefetch_related()` for query optimization
- Occupancy report uses aggregation for statistics
- AJAX endpoints return JSON for lightweight responses
- Admin queries optimized with proper indexing hints

## Security

- All views protected with `@login_required` decorator
- Role-based access control with `@_require_role()` decorator
- CSRF protection on all POST requests
- Input validation on all forms
- SQL injection prevention via ORM

---

**Last Updated:** 2026-02-01  
**Status:** ✅ Complete & Tested  
**Version:** 1.0
