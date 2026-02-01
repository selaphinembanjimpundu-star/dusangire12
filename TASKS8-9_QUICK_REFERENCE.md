# Phase 3 Tasks 8-9 Quick Reference Guide

## 🚀 Quick Start

### URLs to Access Features

#### Bulk Operations
```
http://localhost:8000/hospital/bulk/operations/          # View operations history
http://localhost:8000/hospital/bulk/discharge/           # Bulk discharge form
http://localhost:8000/hospital/bulk/export/patients/     # Export patients CSV
http://localhost:8000/hospital/bulk/export/occupancy/    # Export occupancy CSV
```

#### Notifications
```
http://localhost:8000/hospital/patient-notifications/    # View all notifications
http://localhost:8000/hospital/api/notifications/unread-count/  # Get unread count (JSON)
```

---

## 📋 Testing Quick Commands

### Check System
```bash
python manage.py check
```

### Run Migrations
```bash
python manage.py makemigrations hospital_wards
python manage.py migrate hospital_wards
```

### Send Notifications
```bash
python manage.py send_notifications --send-emails --send-sms
python manage.py send_notifications --send-emails  # Email only
python manage.py send_notifications --send-sms     # SMS only
```

---

## 🗄️ Database Quick Reference

### New Tables
- `BulkOperation` - Tracks bulk operations with metrics
- `PatientNotification` - Multi-channel notifications
- `NotificationTemplate` - Email/SMS templates

### Key Models

#### BulkOperation Fields
```python
operation_type      # 'export_patients', 'export_occupancy', 'bulk_discharge'
status             # 'pending', 'processing', 'completed', 'failed'
initiated_by       # User who started operation
total_records      # Total items processed
successful_records # Items that succeeded
failed_records     # Items that failed
started_at         # Operation start time
completed_at       # Operation completion time
success_rate()     # Method to get percentage
duration()         # Method to get duration in seconds
```

#### PatientNotification Fields
```python
notification_type  # 'admission', 'discharge', 'transfer', 'appointment', etc.
recipient          # User receiving notification
patient            # Related patient (optional)
admission          # Related admission (optional)
title              # Notification title
message            # Notification content
send_email         # Send via email flag
send_sms           # Send via SMS flag
send_in_app        # Show in-app flag
scheduled_for      # Scheduled delivery time (optional)
is_read            # Read status
read_at            # When marked as read
```

#### NotificationTemplate Fields
```python
name               # Template name
notification_type  # Type of notification
email_subject      # Email subject line
email_body         # Email HTML body
sms_body           # SMS text (160 chars max)
is_active          # Whether template is active
```

---

## 👥 Admin Interface Quick Access

### Bulk Operations Admin
```
http://localhost:8000/admin/hospital_wards/bulkoperation/
```

**Features**:
- View all operations with status badges
- Filter by type and status
- See success rates and metrics
- Download export files

### Patient Notifications Admin
```
http://localhost:8000/admin/hospital_wards/patientnotification/
```

**Features**:
- View all notifications
- Filter by type and read status
- Search by title or recipient
- Bulk actions for marking read

### Notification Templates Admin
```
http://localhost:8000/admin/hospital_wards/notificationtemplate/
```

**Features**:
- Create/edit templates
- Set email subject and body
- Configure SMS template
- Toggle active status
- View variable substitution guide

---

## 🔐 Permissions

### Bulk Operations
- **Required Role**: hospital_manager or admin
- **Check**: `user.profile.role in ['hospital_manager', 'admin']`

### Notifications
- **View Own**: Any logged-in user
- **Create**: System automatic on events
- **Edit**: Admin only
- **Send**: Management command (background)

---

## 💾 CSV Export Formats

### Patients Export
```
First Name,Last Name,Email,Bed Number,Ward,Admission Date,Reason,Chief Complaint
John,Doe,john@example.com,101,Cardiology,2024-01-15 10:30,Chest Pain,Severe
```

### Occupancy Export
```
Ward Name,Total Beds,Occupied,Available,Maintenance,Occupancy %
Cardiology,20,15,5,0,75.0
Orthopedics,15,12,3,0,80.0
```

---

## 📧 Email Template Variables

Available variables for template substitution:

```
{patient_name}      - Patient's full name
{bed_number}        - Bed number
{ward_name}         - Ward name
{admission_date}    - Admission date/time
{discharge_date}    - Discharge date/time
{hospital_name}     - Hospital name
{hospital_phone}    - Hospital phone
```

---

## 🛠️ Common Operations

### Create a Notification
```python
from hospital_wards.models import PatientNotification

notification = PatientNotification.objects.create(
    notification_type='admission',
    recipient=patient_user,
    patient=patient_user,
    admission=admission_obj,
    title='Welcome to Hospital',
    message='You have been admitted.',
    send_email=True,
    send_sms=False,
    send_in_app=True
)
```

### Mark Notification as Read
```python
notification = PatientNotification.objects.get(id=123)
notification.mark_as_read()
```

### Create Notification Template
```python
from hospital_wards.models import NotificationTemplate

template = NotificationTemplate.objects.create(
    name='Admission Welcome',
    notification_type='admission',
    email_subject='Welcome to {hospital_name}',
    email_body='Dear {patient_name}, you have been admitted...',
    sms_body='Welcome to {hospital_name}. Your bed is {bed_number}',
    is_active=True
)
```

### Bulk Discharge Manually
```python
from hospital_wards.models import PatientAdmission, PatientDischarge, BulkOperation
from django.utils import timezone

# Get admissions
admissions = PatientAdmission.objects.filter(id__in=[1, 2, 3])

# Create bulk operation
bulk_op = BulkOperation.objects.create(
    operation_type='bulk_discharge',
    status='processing',
    initiated_by=request.user,
    total_records=len(admissions)
)

for admission in admissions:
    # Create discharge
    PatientDischarge.objects.create(admission=admission)
    
    # Release bed
    admission.bed.patient = None
    admission.bed.status = 'available'
    admission.bed.save()
    
    admission.is_active = False
    admission.save()

# Update operation
bulk_op.status = 'completed'
bulk_op.successful_records = len(admissions)
bulk_op.completed_at = timezone.now()
bulk_op.save()
```

---

## 🐛 Troubleshooting Quick Fixes

### Permissions Denied
```
Error: "You do not have permission to perform bulk operations"
Fix: Ensure user has hospital_manager or admin role
```

### No Notifications Showing
```
Error: Notifications created but not visible
Fix: Verify user is logged in and is recipient
```

### CSV Export Fails
```
Error: Export button returns error
Fix: Check hospital_manager+ permission and disk space
```

### Emails Not Sending
```
Error: Notification command runs but emails don't arrive
Fix: Check EMAIL settings in settings.py and SMTP credentials
```

---

## 📊 Key Metrics

### Operation Tracking
- **Operation Type**: What kind of operation (export, discharge, etc.)
- **Status**: Current state (pending, processing, completed, failed)
- **Total Records**: Items to process
- **Success Rate**: (successful / total) * 100
- **Duration**: (completed_at - started_at) in seconds

### Notification Metrics
- **Unread Count**: Number of unread notifications per user
- **By Type**: Count notifications by type (admission, discharge, etc.)
- **Delivery Method**: Track email, SMS, in-app delivery

---

## 📝 Important Files

### Implementation Files
- `hospital_wards/models.py` - BulkOperation, PatientNotification, NotificationTemplate
- `hospital_wards/views.py` - All view functions for bulk ops and notifications
- `hospital_wards/admin.py` - Admin interface configurations
- `hospital_wards/urls.py` - URL routing for new endpoints
- `hospital_wards/management/commands/send_notifications.py` - Background notification sender

### Template Files
- `bulk_operations_list.html` - Operations dashboard
- `bulk_discharge_form.html` - Discharge selection form
- `patient_notifications.html` - Notifications dashboard

### Documentation Files
- `PHASE3_TASKS8-9_IMPLEMENTATION.md` - Complete implementation guide
- `TASKS8-9_SESSION_COMPLETION_SUMMARY.md` - Session summary
- This file - Quick reference

---

## ✅ Verification Checklist

### After Deployment, Verify:
- [ ] Django check passes: `python manage.py check`
- [ ] Migrations applied: `python manage.py migrate`
- [ ] Admin interface accessible: `/admin/`
- [ ] Bulk operations link works
- [ ] Notifications page loads
- [ ] CSV exports generate files
- [ ] Email service configured (for production)
- [ ] Static files collected: `python manage.py collectstatic`

---

## 🚀 Deployment Command

```bash
# Complete deployment steps
cd /path/to/project
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py check --deploy
# Fix any issues, then restart server
```

---

**Quick Reference Version**: 1.0  
**Last Updated**: 2024-01-15  
**Status**: Production Ready
