# 🏥 Hospital Dashboard Redirects - Quick Reference

## Login Flow Summary

**User logs in** → System checks role → Redirects to role-specific dashboard

---

## 10 Hospital Roles & Their Dashboards

### 1. 🩺 **Medical Staff**
- **Role**: `medical_staff`
- **Dashboard**: `/hospital/dashboards/medical-staff/`
- **Template**: `medical_staff_dashboard.html`
- **Access**: Admit/discharge/transfer patients, view medical records

### 2. 🏥 **Patient**
- **Role**: `patient`
- **Dashboard**: `/hospital/dashboards/patient/`
- **Template**: `patient_dashboard.html`
- **Access**: Personal dashboard, education, meal info, notifications

### 3. 👨‍👩‍👧 **Caregiver**
- **Role**: `caregiver`
- **Dashboard**: `/hospital/dashboards/caregiver/`
- **Template**: `caregiver_dashboard.html`
- **Access**: Monitor assigned patients, view notifications

### 4. 🥗 **Nutritionist**
- **Role**: `nutritionist`
- **Dashboard**: `/hospital/dashboards/nutritionist/`
- **Template**: `nutritionist_dashboard.html`
- **Access**: Nutrition info, meal plans, patient nutrition tracking

### 5. 👨‍🍳 **Chef**
- **Role**: `chef`
- **Dashboard**: `/hospital/dashboards/chef/`
- **Template**: `chef_dashboard.html`
- **Access**: Kitchen dashboard, meal orders, preparation tracking

### 6. 🔪 **Kitchen Staff**
- **Role**: `kitchen_staff`
- **Dashboard**: `/hospital/dashboards/kitchen-staff/`
- **Template**: `kitchen_staff_dashboard.html`
- **Access**: Meal orders, kitchen operations, inventory

### 7. 🚚 **Delivery Person**
- **Role**: `delivery_person`
- **Dashboard**: `/hospital/dashboards/delivery-person/`
- **Template**: `delivery_person_dashboard.html`
- **Access**: Delivery schedule, meal delivery tracking

### 8. 🔧 **Support Staff**
- **Role**: `support_staff`
- **Dashboard**: `/hospital/dashboards/support-staff/`
- **Template**: `support_staff_dashboard.html`
- **Access**: Bed management, maintenance scheduling

### 9. 📊 **Hospital Manager**
- **Role**: `hospital_manager`
- **Dashboard**: `/hospital/dashboards/hospital-manager/`
- **Template**: `hospital_manager_dashboard.html`
- **Access**: Analytics, reporting, hospital operations monitoring

### 10. ⚙️ **Admin**
- **Role**: `admin`
- **Dashboard**: `/hospital/dashboards/admin/`
- **Template**: `admin_dashboard.html`
- **Access**: Full system control, user management, configuration

---

## Configuration Points

| File | Purpose |
|------|---------|
| `accounts/views.py` | Contains `dashboard_redirect()` & `hospital_ward_login_redirect()` functions |
| `accounts/urls.py` | Defines `/accounts/dashboard-redirect/` & `/accounts/hospital-dashboard/` routes |
| `hospital_wards/views.py` | Contains role decorator `@_require_role()` |
| `hospital_wards/urls.py` | Defines all 10 dashboard URL routes |
| `templates/hospital_wards/dashboards/` | Contains 10 dashboard HTML templates |

---

## Testing URLs

```
Login:           http://localhost:8000/accounts/login/
Logout:          http://localhost:8000/accounts/logout/

Hospital Entry:  http://localhost:8000/accounts/hospital-dashboard/
Main Dashboard:  http://localhost:8000/hospital/

Patient:         http://localhost:8000/hospital/dashboards/patient/
Medical Staff:   http://localhost:8000/hospital/dashboards/medical-staff/
Nutritionist:    http://localhost:8000/hospital/dashboards/nutritionist/
Chef:            http://localhost:8000/hospital/dashboards/chef/
Kitchen Staff:   http://localhost:8000/hospital/dashboards/kitchen-staff/
Delivery:        http://localhost:8000/hospital/dashboards/delivery-person/
Support Staff:   http://localhost:8000/hospital/dashboards/support-staff/
Manager:         http://localhost:8000/hospital/dashboards/hospital-manager/
Admin:           http://localhost:8000/hospital/dashboards/admin/
```

---

## Implementation Details

### Redirect Logic (accounts/views.py)

```python
def dashboard_redirect(request):
    hospital_ward_roles = {
        'patient': 'hospital_wards:patient_dashboard',
        'caregiver': 'hospital_wards:caregiver_dashboard',
        'nutritionist': 'hospital_wards:nutritionist_dashboard',
        'medical_staff': 'hospital_wards:medical_staff_dashboard',
        'chef': 'hospital_wards:chef_dashboard',
        'kitchen_staff': 'hospital_wards:kitchen_staff_dashboard',
        'delivery_person': 'hospital_wards:delivery_person_dashboard',
        'support_staff': 'hospital_wards:support_staff_dashboard',
        'hospital_manager': 'hospital_wards:hospital_manager_dashboard',
        'admin': 'hospital_wards:admin_dashboard',
    }
    
    if profile.role in hospital_ward_roles:
        return redirect(hospital_ward_roles[profile.role])
```

### Access Control (hospital_wards/views.py)

```python
@login_required
@_require_role('medical_staff')  # Only medical staff can access
def medical_staff_dashboard(request):
    return render(request, 'hospital_wards/dashboards/medical_staff_dashboard.html', context)
```

---

## Common Tasks

### Verify User Can Access Dashboard
```python
# In view or template:
if request.user.profile.role in ['medical_staff', 'hospital_manager']:
    # Show advanced analytics
```

### Check User Role
```python
user_role = request.user.profile.role
print(f"User role: {user_role}")
```

### Restrict to Multiple Roles
```python
@_require_role('medical_staff', 'hospital_manager')  # Either role
def restricted_view(request):
    pass
```

---

## Status

✅ All 10 roles configured  
✅ Dashboard templates created  
✅ Redirect logic implemented  
✅ Access control in place  
✅ Documentation complete  

**System is ready for production!** 🚀
