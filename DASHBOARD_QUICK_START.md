# Hospital Dashboard System - Quick Reference Guide

## 🎯 Quick Links

### Documentation
- [Full Integration Guide](DASHBOARD_INTEGRATION_COMPLETE.md)
- [Change Log](DASHBOARD_INTEGRATION_CHANGELOG.md)
- [Implementation Plan](COMPREHENSIVE_IMPLEMENTATION_PLAN.md)

### Key Files
- Views: `hospital_wards/views.py` (25 functions)
- URLs: `hospital_wards/urls.py` (38 routes)
- Models: `hospital_wards/models.py` (10 models)
- Templates: `templates/hospital_wards/` (22 files)

---

## 🚀 Getting Started

### 1. Access Dashboard
```
URL: /hospital_wards/
Route: hospital_wards:dashboard
```

### 2. Dashboard URLs by Role

| Role | URL |
|------|-----|
| Patient | `/hospital_wards/dashboards/patient/` |
| Caregiver | `/hospital_wards/dashboards/caregiver/` |
| Nutritionist | `/hospital_wards/dashboards/nutritionist/` |
| Medical Staff | `/hospital_wards/dashboards/medical-staff/` |
| Chef | `/hospital_wards/dashboards/chef/` |
| Kitchen Staff | `/hospital_wards/dashboards/kitchen-staff/` |
| Delivery Person | `/hospital_wards/dashboards/delivery-person/` |
| Support Staff | `/hospital_wards/dashboards/support-staff/` |
| Hospital Manager | `/hospital_wards/dashboards/hospital-manager/` |
| Admin | `/hospital_wards/dashboards/admin/` |

---

## 🔗 AJAX Endpoint Reference

### Mark Meal Complete (Chef)
```
Endpoint: {% url 'hospital_wards:mark_meal_complete' meal_id %}
Method: POST
Role: chef
Response: {success: bool, message: str}
```

### Update Order Status (Kitchen Staff)
```
Endpoint: {% url 'hospital_wards:update_order_status' order_id %}
Method: POST
Body: {status: 'value'}
Role: kitchen_staff
Response: {success: bool, message: str}
```

### Start Delivery Route (Delivery Person)
```
Endpoint: {% url 'hospital_wards:start_delivery_route' route_id %}
Method: POST
Role: delivery_person
Response: {success: bool, message: str}
```

### Mark Order Delivered (Delivery Person)
```
Endpoint: {% url 'hospital_wards:mark_order_delivered' order_id %}
Method: POST
Role: delivery_person
Response: {success: bool, message: str}
```

### Discharge Bed (Support Staff)
```
Endpoint: {% url 'hospital_wards:discharge_bed' bed_id %}
Method: POST
Role: support_staff
Response: {success: bool, message: str}
```

### Deactivate User (Admin)
```
Endpoint: {% url 'hospital_wards:deactivate_user' user_id %}
Method: POST
Role: admin
Response: {success: bool, message: str}
```

---

## 📝 Common AJAX Pattern

Use this pattern in all dashboard templates:

```javascript
function actionName(itemId) {
    fetch(`{% url 'hospital_wards:endpoint_name' 0 %}`.replace('0', itemId), {
        method: 'POST',
        headers: {
            'X-CSRFToken': '{{ csrf_token }}',
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Error: ' + data.error);
        }
    })
    .catch(error => alert('Error: ' + error));
}
```

---

## 🔐 Role-Based Access

All dashboards are protected by role-based decorator:

```python
@_require_role('role_name')
def dashboard_view(request):
    # Only users with matching role can access
    return render(request, 'template.html', context)
```

### Available Roles
- `patient`
- `caregiver`
- `nutritionist`
- `medical_staff`
- `chef`
- `kitchen_staff`
- `delivery_person`
- `support_staff`
- `hospital_manager`
- `admin`

---

## 📊 Core Routes

### Ward Management
```
/hospital_wards/wards/                    # List all wards
/hospital_wards/wards/<id>/               # Ward details
/hospital_wards/beds/<id>/                # Bed details
```

### Delivery Scheduling
```
/hospital_wards/delivery-schedule/        # View schedule
/hospital_wards/delivery-slots/<id>/book/ # Book delivery
```

### Patient Education
```
/hospital_wards/education/                # Browse education
/hospital_wards/education/<id>/           # Read content
/hospital_wards/education/<id>/complete/  # Mark complete
```

### Nutrition
```
/hospital_wards/nutrition/                # Browse nutrition
/hospital_wards/nutrition/<id>/           # Meal details
```

### Notifications
```
/hospital_wards/notifications/            # View all
/hospital_wards/notifications/<id>/       # View one
/hospital_wards/notifications/<id>/mark-read/  # Mark read
/hospital_wards/notifications/<id>/delete/     # Delete
```

---

## 🛠️ Development Workflow

### Adding New Dashboard Action

1. **Create View Function in `hospital_wards/views.py`**
```python
@require_http_methods(["POST"])
@_require_role('role_name')
def new_action(request, item_id):
    try:
        item = Model.objects.get(id=item_id)
        # Do something
        return JsonResponse({'success': True, 'message': 'Done'})
    except Model.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Not found'}, status=404)
```

2. **Add URL Route in `hospital_wards/urls.py`**
```python
path('api/item/<int:item_id>/action/', views.new_action, name='new_action'),
```

3. **Add AJAX Function in Dashboard Template**
```javascript
function newAction(itemId) {
    fetch(`{% url 'hospital_wards:new_action' 0 %}`.replace('0', itemId), {
        method: 'POST',
        headers: {
            'X-CSRFToken': '{{ csrf_token }}',
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Error: ' + data.error);
        }
    })
    .catch(error => alert('Error: ' + error));
}
```

---

## 🧪 Testing Checklist

- [ ] Can access dashboard for my role
- [ ] Cannot access other roles' dashboards (403 error)
- [ ] All navigation links work
- [ ] AJAX actions return success/error properly
- [ ] Page reloads after successful AJAX call
- [ ] Error messages display correctly
- [ ] CSRF token validated on POST requests

---

## ❌ Troubleshooting

### "Access Denied" Error
**Check**: User's profile.role matches decorator requirement

### AJAX Returns 404
**Check**: URL name in template matches `urls.py` exactly

### CSRF Error on AJAX
**Check**: Include `'X-CSRFToken': '{{ csrf_token }}'` in headers

### Data Not Showing
**Check**: Dashboard view provides context variables

---

## 📞 Support

For issues:
1. Check error message in browser console
2. Review Django debug toolbar (if enabled)
3. Check server logs: `tail -f logs/django.log`
4. Review documentation files

---

**Last Updated**: Current Session
**Version**: 1.0
**Status**: ✅ Ready for Production
