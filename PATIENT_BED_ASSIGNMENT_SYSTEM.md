# Hospital Patient-Bed Assignment System

**System**: Dusangire Hospital Ward Management (CHUB - Rwanda)
**Current Date**: February 2, 2026
**Status**: ✅ Documented

---

## 🏥 Patient-Bed Assignment Architecture

### Overview

Your hospital system uses a **Django ORM-based relational model** for patient-bed assignments with professional identifiers and hospital-standard tracking:

```
User (Django Auth)
    ↓
User.id (System ID)
    ↓
Profile (Extended User Info)
    ├─ role: Patient/Caregiver/etc
    ├─ phone: Professional Contact
    ├─ status: Active/Inactive
    └─ is_active: Boolean Flag
    ↓
WardBed (Hospital Bed Model)
    ├─ patient: ForeignKey to User (OneToOne)
    ├─ bed_number: Professional Identifier (e.g., "A-101")
    ├─ status: occupied/available/maintenance/reserved
    ├─ assigned_at: Timestamp
    ├─ notes: Clinical Notes
    └─ is_active: Active Flag
```

---

## 📋 Database Schema

### User Model (Django Built-in)
```python
User
├── id (Primary Key - System ID)
├── username (Unique)
├── email (Contact)
├── first_name (Patient Name)
├── last_name (Family Name)
├── is_active (Account Status)
└── password (Encrypted)
```

### Profile Model (Extended)
```python
Profile (One-to-One with User)
├── id (Primary Key)
├── user_id (FK to User)
├── phone (Professional Contact Number)
├── role (Patient/Caregiver/Chef/etc) ← Hospital Role
├── status (active/inactive/suspended/pending_verification) ← Account Status
└── is_active (Boolean) ← Quick Status Check
```

### WardBed Model (Hospital Assignment)
```python
WardBed
├── id (Primary Key - Bed ID)
├── ward_id (FK to Ward - Which Ward)
├── bed_number (CharField, max 50) ← Professional Identifier "A-101"
├── patient_id (OneToOne FK to User) ← Assigned Patient
├── status (Choice: available/occupied/maintenance/reserved)
├── assigned_at (DateTime) ← Assignment Timestamp
├── notes (TextField) ← Clinical/Administrative Notes
├── is_active (Boolean) ← Bed Status
├── created_at (Auto)
└── updated_at (Auto)
```

---

## 🎯 Patient-Bed Assignment Flow

### Assignment Process

```
1. PATIENT ADMISSION
   └─ New User Created (or existing patient)
       └─ Profile Created with role='patient'
           └─ User ID = Professional Patient ID
   
2. BED SELECTION
   └─ Available WardBed Selected
       └─ Check: status = 'available'
           └─ Bed Number = Professional Identifier (e.g., "Ward A, Bed 101")
   
3. ASSIGNMENT
   └─ WardBed.assign_patient(user)
       ├─ Set WardBed.patient = User
       ├─ Set WardBed.status = 'occupied'
       ├─ Set WardBed.assigned_at = NOW()
       └─ Save to Database
   
4. OCCUPANCY TRACKING
   └─ Hospital Dashboard Shows
       ├─ Patient Name & ID
       ├─ Bed Location & Number
       ├─ Assignment Time
       ├─ Clinical Notes
       └─ Status (Active/Inactive)
```

---

## 🔍 Professional IDs Used in System

### 1. System User ID
```python
user.id  # Django Auto-generated Integer ID
Example: 42, 153, 1024
Purpose: System-level unique identifier
Database: User.id (Primary Key)
Used In: WardBed.patient_id (Foreign Key)
```

### 2. Patient Name (Professional Identifier)
```python
user.first_name + user.last_name
Example: "John Musyoka"
Purpose: Human-readable patient identification
Database: User.first_name, User.last_name
Used In: Hospital Staff Reference
```

### 3. Bed Number (Professional Identifier)
```python
wardbed.bed_number  # CharField, max 50
Examples: 
  - "A-101" (Ward A, Bed 101)
  - "Ward_3_Bed_5"
  - "ICU-Bed-12"
Purpose: Hospital-standard bed identification
Database: WardBed.bed_number
Used In: Clinical Records, Staff Communication
```

### 4. Email (Professional Contact)
```python
user.email
Example: "patient@chub.rw" or "john.musyoka@chub.rw"
Purpose: Contact & professional communication
Database: User.email
Used In: Notifications, Communication
```

### 5. Phone (Professional Contact)
```python
user.profile.phone
Example: "+250788123456"
Purpose: Emergency contact, Staff coordination
Database: Profile.phone
Used In: SMS Alerts, Staff Communication
```

### 6. Role (Professional Function)
```python
user.profile.role
Examples: 'patient', 'caregiver', 'chef', 'medical_staff'
Purpose: Determine dashboard & permissions
Database: Profile.role
Used In: Access Control, Dashboard Routing
```

---

## 💾 How Assignment Data is Stored

### Example: Patient John Assigned to Bed A-101

```
User Table:
┌────┬──────────┬──────────┬──────────────┬────────────┬──────────┐
│ id │ username │ email    │ first_name   │ last_name  │ is_active│
├────┼──────────┼──────────┼──────────────┼────────────┼──────────┤
│ 42 │ jmusyoka │ john@... │ John         │ Musyoka    │ True     │
└────┴──────────┴──────────┴──────────────┴────────────┴──────────┘

Profile Table:
┌────┬─────────┬──────────────────┬─────────┬─────────┬──────────────┐
│ id │ user_id │ phone            │ role    │ status  │ is_active    │
├────┼─────────┼──────────────────┼─────────┼─────────┼──────────────┤
│ 15 │ 42      │ +250788123456    │ patient │ active  │ True         │
└────┴─────────┴──────────────────┴─────────┴─────────┴──────────────┘

WardBed Table:
┌────┬─────────┬────────────┬────────────┬──────────┬──────────────────────────────┐
│ id │ ward_id │ bed_number │ patient_id │ status   │ assigned_at                  │
├────┼─────────┼────────────┼────────────┼──────────┼──────────────────────────────┤
│ 87 │ 3       │ A-101      │ 42         │ occupied │ 2026-02-02 09:30:00          │
└────┴─────────┴────────────┴────────────┴──────────┴──────────────────────────────┘

Ward Table:
┌────┬──────────────┬──────────────┐
│ id │ name         │ location     │
├────┼──────────────┼──────────────┤
│ 3  │ General Ward │ Building 2, 3F│
└────┴──────────────┴──────────────┘
```

**Professional Identifier Chain**:
- User ID: 42
- Patient Name: John Musyoka
- Bed Location: General Ward, Building 2, 3F
- Bed Number: A-101
- Phone: +250788123456
- Assignment Time: 2026-02-02 09:30:00

---

## 🔗 Dashboard Access with Patient-Bed Assignment

### How Dashboards Use This Information

```python
# In views.py - Patient Dashboard
def patient_dashboard(request):
    user = request.user
    
    # Get patient's assigned bed using OneToOne relationship
    bed = WardBed.objects.get(patient=user)  # or user.hospital_bed
    
    # Retrieve full information
    context = {
        'patient_name': f"{user.first_name} {user.last_name}",
        'patient_id': user.id,
        'bed_number': bed.bed_number,
        'ward_name': bed.ward.name,
        'assigned_at': bed.assigned_at,
        'status': bed.status,
        'notes': bed.notes,
        'phone': user.profile.phone,
    }
    
    return render(request, 'patient_dashboard.html', context)
```

### What Medical Staff Sees

```python
# In Medical Staff Dashboard
def medical_staff_dashboard(request):
    # Get all occupied beds in their assigned wards
    occupied_beds = WardBed.objects.filter(
        status='occupied',
        is_active=True
    ).select_related('patient', 'ward')
    
    # Display patient-bed assignments with professional IDs
    context = {
        'patient_assignments': [
            {
                'patient_name': bed.patient.get_full_name(),
                'patient_id': bed.patient.id,
                'bed_id': bed.id,
                'bed_number': bed.bed_number,
                'ward': bed.ward.name,
                'assigned_duration': timezone.now() - bed.assigned_at,
                'notes': bed.notes,
                'status': bed.status,
            }
            for bed in occupied_beds
        ]
    }
```

---

## 🛏️ Support Staff Dashboard Features

### Bed Management with Professional IDs

```python
# In Support Staff Dashboard - views.py
def support_staff_dashboard(request):
    # View all bed occupancy with professional identifiers
    all_beds = WardBed.objects.filter(is_active=True)
    
    context = {
        'bed_assignments': {
            'occupied': all_beds.filter(status='occupied').values_list(
                'id', 'bed_number', 'patient__first_name', 
                'patient__last_name', 'patient__id', 'assigned_at'
            ),
            'available': all_beds.filter(status='available').values_list(
                'id', 'bed_number', 'ward__name'
            ),
            'under_maintenance': all_beds.filter(status='maintenance'),
        }
    }
```

---

## 📊 Template Display Examples

### Patient Can See Own Bed Assignment

```html
<!-- templates/hospital_wards/dashboards/patient_dashboard.html -->
<div class="alert alert-info">
    <h5>Your Current Ward Assignment</h5>
    <p>
        <strong>Patient ID:</strong> {{ patient_id }}<br>
        <strong>Name:</strong> {{ patient_name }}<br>
        <strong>Ward:</strong> {{ ward_name }}<br>
        <strong>Bed Number:</strong> {{ bed_number }}<br>
        <strong>Assigned Since:</strong> {{ assigned_at|date:"M d, Y H:i" }}<br>
        <strong>Status:</strong> <span class="badge bg-success">{{ status }}</span>
    </p>
</div>

{% if notes %}
<div class="card">
    <div class="card-header">
        <h6>Clinical/Administrative Notes</h6>
    </div>
    <div class="card-body">
        {{ notes }}
    </div>
</div>
{% endif %}
```

### Medical Staff Can See All Assignments

```html
<!-- templates/hospital_wards/dashboards/medical_staff_dashboard.html -->
<table class="table table-striped">
    <thead>
        <tr>
            <th>Patient ID</th>
            <th>Patient Name</th>
            <th>Ward</th>
            <th>Bed Number</th>
            <th>Assigned</th>
            <th>Status</th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody>
        {% for assignment in patient_assignments %}
        <tr>
            <td>#{{ assignment.patient_id }}</td>
            <td>{{ assignment.patient_name }}</td>
            <td>{{ assignment.ward }}</td>
            <td><strong>{{ assignment.bed_number }}</strong></td>
            <td>{{ assignment.assigned_at|date:"M d" }}</td>
            <td>
                <span class="badge bg-success">{{ assignment.status }}</span>
            </td>
            <td>
                <a href="{% url 'hospital_wards:bed_detail' assignment.bed_id %}" 
                   class="btn btn-sm btn-primary">
                    View Details
                </a>
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>
```

---

## 🔄 Patient Assignment Lifecycle

### 1. Admission
```python
# Admin creates patient user
user = User.objects.create_user(
    username='jmusyoka',
    email='john.musyoka@chub.rw',
    first_name='John',
    last_name='Musyoka',
    password='secure_password'
)

# Create profile with role
profile = Profile.objects.create(
    user=user,
    phone='+250788123456',
    role='patient',
    status='active',
    is_active=True
)
```

### 2. Bed Assignment
```python
# Assign to bed
bed = WardBed.objects.get(bed_number='A-101')
bed.assign_patient(user)  # Calls the assign_patient() method

# Result:
# bed.patient = user (Patient ID 42)
# bed.status = 'occupied'
# bed.assigned_at = Now()
```

### 3. Active Occupancy
```python
# Patient dashboard shows assignment
patient_bed = user.hospital_bed  # OneToOne relationship
print(f"Patient {user.get_full_name()} is in Bed {patient_bed.bed_number}")
# Output: Patient John Musyoka is in Bed A-101
```

### 4. Discharge
```python
# Support staff releases patient
bed = WardBed.objects.get(patient=user)
bed.release_patient()  # Calls release_patient() method

# Result:
# bed.patient = None
# bed.status = 'available'
# bed.assigned_at = None
```

---

## 📈 Data Relationships

### Query Examples

#### Get a Patient's Bed
```python
# Method 1: From patient
patient = User.objects.get(id=42)
bed = patient.hospital_bed  # OneToOne relationship

# Method 2: From bed
bed = WardBed.objects.get(patient_id=42)

# Method 3: With full details
bed = WardBed.objects.select_related(
    'patient__profile', 'ward'
).get(patient_id=42)

print(f"{bed.patient.get_full_name()} in {bed.bed_number}")
# John Musyoka in A-101
```

#### Get All Occupied Beds
```python
occupied_beds = WardBed.objects.filter(
    status='occupied',
    is_active=True
).select_related('patient__profile', 'ward')

for bed in occupied_beds:
    print(f"Bed {bed.bed_number}: {bed.patient.get_full_name()} "
          f"(ID: {bed.patient.id})")
# Bed A-101: John Musyoka (ID: 42)
# Bed A-102: Jane Doe (ID: 43)
```

#### Get Patients in Specific Ward
```python
ward = Ward.objects.get(name='General Ward')
patients_in_ward = WardBed.objects.filter(
    ward=ward,
    status='occupied'
).values_list('patient__first_name', 'patient__last_name', 'bed_number')

for first, last, bed_num in patients_in_ward:
    print(f"{first} {last} - Bed {bed_num}")
```

---

## 🔒 Professional ID Security

### IDs Are Secure Because:

1. **Django ORM Protection**
   - Automatic SQL injection prevention
   - Parameterized queries

2. **OneToOne Relationship**
   - Enforces one patient per bed
   - Prevents duplicate assignments

3. **Database Constraints**
   - Unique: ward + bed_number
   - Foreign Key: patient_id → User.id
   - NOT NULL checking

4. **Status Validation**
   - Can only assign to 'available' beds
   - Cannot double-assign

5. **Audit Trail**
   - assigned_at timestamp
   - updated_at tracking
   - Admin logging available

---

## 📋 Professional Standards Met

✅ **Patient Identification**
- System ID (User.id)
- Full Name (first_name + last_name)
- Email (professional contact)
- Phone (emergency contact)

✅ **Bed Identification**
- Bed Number (professional identifier)
- Ward Location
- Status tracking
- Assignment time

✅ **Hospital Standards**
- OneToOne relationship (prevents double assignment)
- Status management (available/occupied/maintenance/reserved)
- Clinical notes support
- Audit trail (timestamps)

✅ **Data Integrity**
- Django ORM protection
- Database constraints
- Unique combinations
- Referential integrity

---

## 🎯 Summary

**Your system properly tracks patient-bed assignments using:**

1. **System IDs**: User.id (database primary key)
2. **Patient Names**: First & Last names (professional identification)
3. **Bed Numbers**: Professional hospital identifiers (e.g., "A-101")
4. **Professional Contacts**: Phone & Email
5. **Timestamps**: Assignment tracking
6. **Status Management**: Occupation status
7. **Clinical Notes**: Additional patient information

**All implemented with:**
- ✅ Database relational integrity
- ✅ Django ORM security
- ✅ Professional hospital standards
- ✅ Audit trail capability

---

**Status**: ✅ Hospital-grade patient-bed assignment system implemented
**Ready for**: Patient admission, bed management, clinical operations
