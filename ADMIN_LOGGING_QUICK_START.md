# Admin Logging System - Quick Implementation Guide

## Step-by-Step Setup

### 1. Run Database Migration

```bash
python manage.py migrate admin_dashboard
```

This creates the `AdminLog` table with all necessary fields and indexes.

### 2. Access the Logging Features

#### View Admin Logs Dashboard
- Navigate to: `/admin/logs/`
- Filter logs by action, user, status, or model
- Search for specific activities
- View detailed information for each log entry

#### View Activity Summary
- Navigate to: `/admin/activity-summary/`
- See statistics: today, this week, this month
- View top actions, most active admins, most modified models
- Track failed actions

#### Export Logs
- From logs page, click "Export CSV" or "Export JSON"
- Or navigate to: `/admin/logs/export/?format=csv` or `?format=json`

### 3. Integrate into Your Views

#### Option A: Using the Decorator (Easiest)

```python
from admin_dashboard.logger import admin_action_logger

@admin_action_logger('UPDATE', 'Order')
def update_order(request, order_id):
    order = Order.objects.get(id=order_id)
    order.status = 'confirmed'
    order.save()
    return redirect('admin_dashboard:order_detail', order_id=order_id)
```

#### Option B: Manual Logging

```python
from admin_dashboard.logger import log_admin_action

def update_order(request, order_id):
    order = Order.objects.get(id=order_id)
    old_status = order.status
    
    order.status = 'confirmed'
    order.save()
    
    # Log the action
    log_admin_action(
        user=request.user,
        action='UPDATE',
        model_name='Order',
        object_id=order_id,
        description=f'Updated order status to confirmed',
        old_values={'status': old_status},
        new_values={'status': order.status},
        request=request
    )
    
    return redirect('admin_dashboard:order_detail', order_id=order_id)
```

#### Option C: Logging Model Changes

```python
from admin_dashboard.logger import log_model_change

# In your model save method or view
order = Order.objects.get(id=order_id)
old_order = Order.objects.get(id=order_id)  # Get before update

order.status = 'confirmed'
order.save()

log_model_change(request.user, order, 'UPDATE', old_order, request=request)
```

### 4. Django Admin Integration

1. Log in to Django Admin (`/admin/`)
2. Navigate to "Admin Dashboard" → "Admin Logs"
3. View all logs in a searchable, filterable interface
4. Click any log entry to see complete details

## Files Created/Modified

### New Files
- `admin_dashboard/models.py` - AdminLog model
- `admin_dashboard/logger.py` - Logging utilities
- `admin_dashboard/migrations/0002_adminlog.py` - Database migration
- `admin_dashboard/templates/admin_dashboard/logs.html` - Logs list page
- `admin_dashboard/templates/admin_dashboard/log_detail.html` - Log detail page
- `admin_dashboard/templates/admin_dashboard/activity_summary.html` - Summary dashboard
- `ADMIN_LOGGING_SYSTEM.md` - Full documentation

### Modified Files
- `admin_dashboard/views.py` - Added log viewing views
- `admin_dashboard/urls.py` - Added log routes
- `admin_dashboard/admin.py` - Registered AdminLog in Django Admin

## Available Logging Functions

### Main Function: `log_admin_action()`

```python
log_admin_action(
    user,                  # Request user
    action,               # Action type (string)
    model_name,           # Model name (string)
    description,          # What happened (string)
    object_id=None,       # ID of affected object (optional)
    old_values=None,      # Previous values dict (optional)
    new_values=None,      # New values dict (optional)
    status='SUCCESS',     # Status (SUCCESS, FAILED, PENDING, WARNING)
    error_message='',     # Error details if failed (optional)
    request=None,         # HTTP request for IP/user agent (optional)
    duration_ms=None      # Time taken in milliseconds (optional)
)
```

### Decorator: `@admin_action_logger(action, model_name)`

Automatically logs the action with timing information.

### Model Change Logger: `log_model_change()`

```python
log_model_change(
    user,               # User making change
    instance,           # Current/new model instance
    action,             # CREATE, UPDATE, or DELETE
    old_instance=None,  # Previous state (for UPDATE)
    request=None        # HTTP request (optional)
)
```

### Utility Functions

```python
# Get recent logs
from admin_dashboard.logger import get_recent_logs
logs = get_recent_logs(limit=50, action='UPDATE', user=request.user)

# Get logs by date range
from admin_dashboard.logger import get_logs_by_date_range
from datetime import date
logs = get_logs_by_date_range(date(2024, 1, 1), date(2024, 1, 31))

# Export to JSON
from admin_dashboard.logger import export_logs_to_json
json_data = export_logs_to_json(logs)
```

## Common Use Cases

### 1. Log Order Status Changes

```python
from admin_dashboard.logger import log_admin_action

def confirm_order(request, order_id):
    order = Order.objects.get(id=order_id)
    old_status = order.status
    
    order.status = OrderStatus.CONFIRMED
    order.save()
    
    log_admin_action(
        user=request.user,
        action='ORDER_UPDATE',
        model_name='Order',
        object_id=order_id,
        description=f'Order {order_id} status changed: {old_status} → {order.status}',
        old_values={'status': old_status},
        new_values={'status': order.status},
        status='SUCCESS',
        request=request
    )
    
    messages.success(request, 'Order confirmed')
    return redirect('admin_dashboard:order_detail', order_id=order_id)
```

### 2. Log Payment Processing

```python
from admin_dashboard.logger import log_admin_action

def process_payment(request, payment_id):
    payment = Payment.objects.get(id=payment_id)
    
    try:
        # Your payment processing logic
        payment.process()
        payment.save()
        
        log_admin_action(
            user=request.user,
            action='PAYMENT_PROCESS',
            model_name='Payment',
            object_id=payment_id,
            description=f'Payment {payment_id} processed: {payment.amount}',
            new_values={'status': 'completed', 'amount': str(payment.amount)},
            status='SUCCESS',
            request=request
        )
        
        messages.success(request, 'Payment processed successfully')
    
    except Exception as e:
        log_admin_action(
            user=request.user,
            action='PAYMENT_PROCESS',
            model_name='Payment',
            object_id=payment_id,
            description=f'Payment processing failed',
            status='FAILED',
            error_message=str(e),
            request=request
        )
        messages.error(request, f'Payment processing failed: {str(e)}')
    
    return redirect('admin_dashboard:payments')
```

### 3. Log User Creation/Modification

```python
from admin_dashboard.logger import log_admin_action

def create_admin_user(request):
    if request.method == 'POST':
        form = AdminUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            log_admin_action(
                user=request.user,
                action='CREATE',
                model_name='User',
                object_id=user.id,
                description=f'Created admin user: {user.username}',
                new_values={
                    'username': user.username,
                    'email': user.email,
                    'is_staff': str(user.is_staff)
                },
                status='SUCCESS',
                request=request
            )
            
            messages.success(request, f'Admin user {user.username} created')
            return redirect('admin_dashboard:users')
    
    form = AdminUserForm()
    return render(request, 'admin_dashboard/create_user.html', {'form': form})
```

### 4. Log with Decorator

```python
from admin_dashboard.logger import admin_action_logger

@admin_action_logger('APPROVE', 'CateringBooking')
@login_required
@user_passes_test(is_staff_or_admin)
def approve_catering_booking(request, booking_id):
    booking = CateringBooking.objects.get(id=booking_id)
    booking.status = 'approved'
    booking.save()
    
    messages.success(request, 'Catering booking approved')
    return redirect('admin_dashboard:catering_bookings')
```

## URL Routes

```
/admin/logs/                    - View all logs
/admin/logs/<id>/               - View log detail
/admin/activity-summary/        - Activity summary dashboard
/admin/logs/export/             - Export logs (add ?format=csv or ?format=json)
```

## Django Admin

Access logs in Django Admin:
- Navigate to: `/admin/`
- Menu: Admin Dashboard → Admin Logs
- Full CRUD interface with filters and search

## Tips & Best Practices

1. **Always use request parameter** for IP address tracking
2. **Log both old and new values** for audit trail completeness
3. **Use appropriate action types** for better filtering
4. **Include meaningful descriptions** that explain what changed
5. **Handle errors properly** by logging with FAILED status
6. **Review logs regularly** for security and debugging

## Troubleshooting

**Logs not showing?**
- Run migration: `python manage.py migrate admin_dashboard`
- Check that log_admin_action() calls have correct parameters

**Can't access log views?**
- User must be staff or admin
- Check user role in User profile

**Missing IP address?**
- Pass request object: `log_admin_action(..., request=request)`

**Database error?**
- Check if migration was run successfully
- Verify models.py has been updated

---

**Ready to use!** Start logging admin activities in your views.
