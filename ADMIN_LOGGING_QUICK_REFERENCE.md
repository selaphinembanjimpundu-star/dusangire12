# Admin Logging System - Quick Reference Card

## 🚀 Quick Start (30 seconds)

```python
# Add this to any admin view
from admin_dashboard.logger import log_admin_action

# Log an action
log_admin_action(
    user=request.user,
    action='UPDATE',
    model_name='Order',
    object_id=order.id,
    description='Updated order status',
    request=request
)
```

Or use the decorator:

```python
from admin_dashboard.logger import admin_action_logger

@admin_action_logger('UPDATE', 'Order')
def update_order(request, order_id):
    # Your code here
    pass
```

## 📍 URL Endpoints

| Endpoint | Purpose |
|----------|---------|
| `/admin/logs/` | View logs (paginated, filtered, searchable) |
| `/admin/logs/<id>/` | View single log detail |
| `/admin/activity-summary/` | Dashboard with stats & charts |
| `/admin/logs/export/?format=csv` | Export as CSV |
| `/admin/logs/export/?format=json` | Export as JSON |
| `/admin/` | Django Admin (see Admin Logs) |

## 🔧 Logging Functions

### Main: log_admin_action()

```python
log_admin_action(
    user,                      # Request user (required)
    action,                    # Action type string (required)
    model_name,                # Model name (required)
    description,               # What happened (required)
    object_id=None,            # Affected object ID
    old_values=None,           # Dict: old field values
    new_values=None,           # Dict: new field values
    status='SUCCESS',          # SUCCESS|FAILED|PENDING|WARNING
    error_message='',          # Error details if failed
    request=None,              # HTTP request (for IP, user agent)
    duration_ms=None           # Execution time
)
```

### Decorator: @admin_action_logger()

```python
@admin_action_logger('ACTION_TYPE', 'ModelName')
def your_view(request, ...):
    # Automatically logs action with timing
    pass
```

### Model Changes: log_model_change()

```python
log_model_change(
    user,           # User making change
    instance,       # Current model instance
    action,         # 'CREATE', 'UPDATE', or 'DELETE'
    old_instance,   # Previous state (for UPDATE)
    request=None    # HTTP request (optional)
)
```

### Query Functions

```python
from admin_dashboard.logger import (
    get_recent_logs,
    get_logs_by_date_range,
    export_logs_to_json
)

# Recent logs
logs = get_recent_logs(limit=50, action='UPDATE', user=user)

# By date range
from datetime import date
logs = get_logs_by_date_range(
    date(2024, 1, 1),
    date(2024, 1, 31),
    action='CREATE'
)

# Export to JSON
json_data = export_logs_to_json(logs)
```

## 🎯 Action Types

```python
# Data Operations
CREATE, UPDATE, DELETE, VIEW

# Business Operations
APPROVE, REJECT, ASSIGN, UNASSIGN
PAYMENT_PROCESS, ORDER_UPDATE
REPORT_GENERATE

# System Operations
IMPORT, EXPORT, USER_ACTION, SYSTEM_ACTION, CONFIG_CHANGE
LOGIN, LOGOUT, OTHER
```

## 📊 Status Types

```python
SUCCESS   # Action succeeded
FAILED    # Action failed (must include error_message)
PENDING   # Action is pending completion
WARNING   # Action succeeded with warnings
```

## 💡 Common Patterns

### Pattern 1: Simple Update Logging

```python
def update_order(request, order_id):
    order = Order.objects.get(id=order_id)
    old_status = order.status
    
    order.status = 'confirmed'
    order.save()
    
    log_admin_action(
        user=request.user,
        action='ORDER_UPDATE',
        model_name='Order',
        object_id=order_id,
        old_values={'status': old_status},
        new_values={'status': order.status},
        description=f'Order {order_id} confirmed',
        request=request
    )
```

### Pattern 2: Error Handling with Logging

```python
def process_payment(request, payment_id):
    try:
        payment = Payment.objects.get(id=payment_id)
        payment.process()
        
        log_admin_action(
            user=request.user,
            action='PAYMENT_PROCESS',
            model_name='Payment',
            object_id=payment_id,
            status='SUCCESS',
            description=f'Payment processed: {payment.amount}',
            request=request
        )
    except Exception as e:
        log_admin_action(
            user=request.user,
            action='PAYMENT_PROCESS',
            model_name='Payment',
            object_id=payment_id,
            status='FAILED',
            error_message=str(e),
            request=request
        )
        raise
```

### Pattern 3: Using Decorator (Simplest)

```python
from admin_dashboard.logger import admin_action_logger

@admin_action_logger('APPROVE', 'CateringBooking')
@login_required
@user_passes_test(is_staff)
def approve_booking(request, booking_id):
    booking = CateringBooking.objects.get(id=booking_id)
    booking.status = 'approved'
    booking.save()
    return redirect('catering:detail', booking_id=booking_id)
```

## 🔍 Filtering Logs (In Template)

```html
<!-- From logs.html -->
<a href="{% url 'admin_dashboard:view_logs' %}?action=UPDATE">
    View updates
</a>

<a href="{% url 'admin_dashboard:view_logs' %}?status=FAILED">
    View failed actions
</a>

<a href="{% url 'admin_dashboard:view_logs' %}?model_name=Order">
    View order logs
</a>
```

## 📈 Accessing Log Data

```python
from admin_dashboard.models import AdminLog
from django.db.models import Count

# Get all logs
logs = AdminLog.objects.all()

# Filter by user
user_logs = AdminLog.objects.filter(admin_user=request.user)

# Filter by model
order_logs = AdminLog.objects.filter(model_name='Order')

# Failed actions
failed = AdminLog.objects.filter(status='FAILED')

# Today's activities
from django.utils import timezone
today = timezone.now().date()
today_logs = AdminLog.objects.filter(timestamp__date=today)

# Count by action type
stats = AdminLog.objects.values('action').annotate(
    count=Count('id')
).order_by('-count')
```

## 🛡️ Security Notes

✅ Always pass `request=request` for IP tracking  
✅ Log errors but don't expose sensitive details  
✅ Use appropriate action types for classification  
✅ Log before/after values for audit trail  
✅ Logs are immutable (read-only)  
⚠️ Don't log passwords, tokens, or secrets  

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| No logs appear | Run `python manage.py migrate admin_dashboard` |
| Can't access `/admin/logs/` | User must be staff/admin (is_staff=True) |
| Missing IP address | Add `request=request` parameter |
| Logs not in Django Admin | Check migration ran, restart server |
| Import errors | Verify file path is correct |

## 📝 Django Admin Access

1. Go to `/admin/`
2. Login with admin account
3. Find "Admin Dashboard" section
4. Click "Admin Logs"
5. Use filters, search, and pagination
6. Click any log to see full details

## 📊 Model Fields Reference

| Field | Type | Example |
|-------|------|---------|
| admin_user | User FK | John Smith |
| action | String | UPDATE |
| model_name | String | Order |
| object_id | Integer | 42 |
| description | Text | Order status changed |
| old_values | JSON | {"status": "pending"} |
| new_values | JSON | {"status": "confirmed"} |
| ip_address | IP | 192.168.1.1 |
| user_agent | String | Mozilla/5.0... |
| status | String | SUCCESS |
| error_message | Text | Division by zero |
| timestamp | DateTime | 2024-02-01 14:30:00 |
| duration_ms | Integer | 245 |

## 🚀 Performance Tips

1. **Use pagination** - Default 50 logs per page
2. **Use indexes** - Timestamp, user, action, model indexes included
3. **Archive old logs** - Delete/archive >90 days monthly
4. **Use filters** - Don't load all logs at once
5. **Paginate results** - Don't query thousands at once

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| ADMIN_LOGGING_SYSTEM.md | Complete API documentation |
| ADMIN_LOGGING_QUICK_START.md | Step-by-step setup guide |
| ADMIN_LOGGING_IMPLEMENTATION_SUMMARY.md | What was built |
| ADMIN_LOGGING_INTEGRATION_CHECKLIST.md | Deployment checklist |

## 💾 Database Migration

```bash
# Run this once to create the AdminLog table
python manage.py migrate admin_dashboard

# Check migration status
python manage.py showmigrations admin_dashboard

# Rollback if needed
python manage.py migrate admin_dashboard zero
```

## 🔐 Permissions

| Action | Who |
|--------|-----|
| View logs | Staff/Admin |
| View detail | Staff/Admin |
| Create logs | Automatic only |
| Delete logs | Superuser only |
| Export logs | Staff/Admin |

## 📞 Quick Reference Links

- View Logs: `/admin/logs/`
- Activity Summary: `/admin/activity-summary/`
- Django Admin: `/admin/`
- Export CSV: `/admin/logs/export/?format=csv`
- Export JSON: `/admin/logs/export/?format=json`

---

**Print this card and keep it handy!**  
**Last Updated**: February 1, 2026  
**Version**: 1.0
