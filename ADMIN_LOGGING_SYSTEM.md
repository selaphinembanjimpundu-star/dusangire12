# Admin Panel Logging System Documentation

## Overview

The Admin Logging System is a comprehensive audit trail solution for tracking all administrative activities in the Dusangire platform. It provides detailed logs of who did what, when, and the results of their actions.

## Features

### 1. **Automatic Activity Tracking**
- Tracks all admin actions (CREATE, UPDATE, DELETE, etc.)
- Records user information, timestamp, and IP address
- Captures request duration and performance metrics
- Logs changes with before/after values

### 2. **Flexible Action Types**
The system supports the following action types:
- **CREATE** - Creating new objects
- **UPDATE** - Modifying existing objects
- **DELETE** - Removing objects
- **VIEW** - Accessing data
- **EXPORT** - Exporting data
- **IMPORT** - Importing data
- **APPROVE** - Approving requests
- **REJECT** - Rejecting requests
- **ASSIGN** - Assigning tasks/items
- **UNASSIGN** - Unassigning tasks/items
- **PAYMENT_PROCESS** - Processing payments
- **ORDER_UPDATE** - Updating orders
- **USER_ACTION** - User-related actions
- **SYSTEM_ACTION** - System operations
- **REPORT_GENERATE** - Generating reports
- **CONFIG_CHANGE** - Configuration changes
- **LOGIN** - Admin login
- **LOGOUT** - Admin logout

### 3. **Status Tracking**
Each log entry records:
- **SUCCESS** - Action completed successfully
- **FAILED** - Action failed with error details
- **PENDING** - Action is pending
- **WARNING** - Action completed with warnings

## Model: AdminLog

### Fields

```python
AdminLog
├── admin_user (ForeignKey) - User who performed the action
├── action (CharField) - Type of action performed
├── model_name (CharField) - Name of affected model
├── object_id (IntegerField) - ID of affected object
├── description (TextField) - Detailed description
├── old_values (JSONField) - Previous field values
├── new_values (JSONField) - New field values
├── ip_address (IPAddressField) - Client IP
├── user_agent (TextField) - Browser information
├── status (CharField) - Action status
├── error_message (TextField) - Error details if failed
├── timestamp (DateTimeField) - When action occurred
└── duration_ms (IntegerField) - Time taken (milliseconds)
```

## Usage Guide

### 1. Manual Logging

```python
from admin_dashboard.logger import log_admin_action

# Log an action
log_admin_action(
    user=request.user,
    action='UPDATE',
    model_name='Order',
    object_id=order.id,
    description=f'Updated order status to confirmed',
    status='SUCCESS',
    request=request
)
```

### 2. Using the Decorator

```python
from admin_dashboard.logger import admin_action_logger

@admin_action_logger('UPDATE', 'Order')
def update_order(request, order_id):
    # Your code here
    order = Order.objects.get(id=order_id)
    order.status = 'confirmed'
    order.save()
    return redirect('admin_dashboard:order_detail', order_id=order_id)
```

### 3. Logging Model Changes

```python
from admin_dashboard.logger import log_model_change

# When creating an object
user = User.objects.create(username='john', email='john@example.com')
log_model_change(request.user, user, 'CREATE', request=request)

# When updating an object
old_user = User.objects.get(id=user_id)
user = User.objects.get(id=user_id)
user.email = 'newemail@example.com'
user.save()
log_model_change(request.user, user, 'UPDATE', old_user, request=request)
```

## Views

### 1. **View All Logs**
- **URL**: `/admin/logs/`
- **Template**: `admin_dashboard/logs.html`
- **Features**:
  - Paginated list of all admin logs
  - Filter by action, user, status, model
  - Search functionality
  - Export options (CSV, JSON)
  - Direct links to log details

### 2. **Log Detail View**
- **URL**: `/admin/logs/<log_id>/`
- **Template**: `admin_dashboard/log_detail.html`
- **Shows**:
  - Complete log information
  - Before/after values for updates
  - Request details (IP, user agent)
  - Error messages if failed
  - Execution duration

### 3. **Activity Summary**
- **URL**: `/admin/activity-summary/`
- **Template**: `admin_dashboard/activity_summary.html`
- **Displays**:
  - Activity statistics (today, week, month)
  - Top actions chart
  - Most modified models
  - Most active admins
  - Recent activities list

### 4. **Export Logs**
- **URL**: `/admin/logs/export/`
- **Formats**: CSV or JSON
- **Features**: Download with filters applied

## Helper Functions

### Getting Logs

```python
from admin_dashboard.logger import get_recent_logs, get_logs_by_date_range

# Get recent logs
logs = get_recent_logs(limit=50, action='UPDATE', user=user)

# Get logs by date range
from datetime import date
logs = get_logs_by_date_range(
    date(2024, 1, 1),
    date(2024, 1, 31),
    action='CREATE'
)
```

### Exporting Logs

```python
from admin_dashboard.logger import export_logs_to_json

logs = AdminLog.objects.filter(action='UPDATE')
json_data = export_logs_to_json(logs)
# Returns JSON string ready for download
```

## Integration Examples

### Example 1: Logging Order Updates

```python
from admin_dashboard.logger import log_admin_action
from orders.models import Order

@login_required
def update_order_status(request, order_id):
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
        description=f'Status changed from {old_status} to confirmed',
        old_values={'status': old_status},
        new_values={'status': 'confirmed'},
        status='SUCCESS',
        request=request
    )
    
    return redirect('admin_dashboard:order_detail', order_id=order_id)
```

### Example 2: Logging Payment Processing

```python
from admin_dashboard.logger import log_admin_action

def process_payment(request, payment_id):
    payment = Payment.objects.get(id=payment_id)
    
    try:
        # Process payment
        payment.process()
        payment.save()
        
        log_admin_action(
            user=request.user,
            action='PAYMENT_PROCESS',
            model_name='Payment',
            object_id=payment_id,
            description=f'Processed payment of {payment.amount}',
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
            description=f'Failed to process payment',
            status='FAILED',
            error_message=str(e),
            request=request
        )
        messages.error(request, f'Payment processing failed: {str(e)}')
    
    return redirect('admin_dashboard:payments')
```

### Example 3: Using Signal Handlers

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.models import Order
from admin_dashboard.logger import log_admin_action

@receiver(post_save, sender=Order)
def log_order_changes(sender, instance, created, **kwargs):
    if created:
        log_admin_action(
            user=instance.created_by,  # If applicable
            action='CREATE',
            model_name='Order',
            object_id=instance.id,
            description=f'New order created: {instance.id}',
            status='SUCCESS'
        )
```

## Django Admin Integration

The AdminLog model is fully integrated with Django Admin:

1. **Access**: Navigate to Django Admin → Admin Logs
2. **View**: See all log entries in a searchable, filterable table
3. **Details**: Click any entry to see full details
4. **Filters**: Filter by action, status, user, timestamp, model
5. **Search**: Search by description, model name, or error message

### Permissions

- **View**: All staff users can view logs
- **Add**: Logs are created automatically (manual creation disabled)
- **Delete**: Only superusers can delete logs
- **Change**: Logs are read-only (immutable audit trail)

## Database Indexes

The AdminLog model includes optimized indexes for common queries:

```python
# Timestamp index
models.Index(fields=['-timestamp'])

# User activity timeline
models.Index(fields=['admin_user', '-timestamp'])

# Action type tracking
models.Index(fields=['action', '-timestamp'])

# Model change tracking
models.Index(fields=['model_name', '-timestamp'])
```

## Best Practices

### 1. **Always Include Request Context**
```python
log_admin_action(
    user=request.user,
    action='UPDATE',
    model_name='Order',
    object_id=order.id,
    description='Updated order status',
    request=request  # Include this for IP and user agent
)
```

### 2. **Log Before and After Values**
```python
log_admin_action(
    user=request.user,
    action='UPDATE',
    model_name='Order',
    object_id=order.id,
    old_values={'status': old_status},
    new_values={'status': new_status},
    description=f'Status: {old_status} → {new_status}'
)
```

### 3. **Handle Errors Properly**
```python
try:
    # Your code
    pass
except Exception as e:
    log_admin_action(
        user=request.user,
        action='UPDATE',
        model_name='Order',
        object_id=order_id,
        status='FAILED',
        error_message=str(e),
        request=request
    )
    raise
```

### 4. **Use Appropriate Action Types**
Choose the correct action type for better filtering and analysis:
- Use 'PAYMENT_PROCESS' for payments
- Use 'ORDER_UPDATE' for order changes
- Use 'USER_ACTION' for user management

### 5. **Regular Log Review**
- Monitor the Activity Summary dashboard regularly
- Review failed actions for potential issues
- Check for suspicious IP addresses

## Performance Considerations

1. **Automatic Cleanup**: Consider archiving old logs periodically
   ```python
   from datetime import timedelta
   from django.utils import timezone
   from admin_dashboard.models import AdminLog
   
   # Delete logs older than 90 days
   ninety_days_ago = timezone.now() - timedelta(days=90)
   AdminLog.objects.filter(timestamp__lt=ninety_days_ago).delete()
   ```

2. **Query Optimization**: The model includes database indexes for optimal performance

3. **Storage**: Monitor database growth; consider log archival strategy

## Troubleshooting

### Logs Not Appearing
- Ensure the migration has been run: `python manage.py migrate admin_dashboard`
- Check that `log_admin_action()` is being called
- Verify the admin user is authenticated

### Missing IP Address
- IP address requires a request object: `request=request`
- Check if proxy settings are affecting IP detection

### Performance Issues
- Use the provided indexes
- Archive old logs regularly
- Consider pagination when querying large log sets

## Configuration

### Django Settings

Add logging configuration to `settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'admin_panel.log',
        },
    },
    'loggers': {
        'admin_panel': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## Support

For issues or questions about the logging system, refer to:
- AdminLog model documentation
- Logger utility functions
- View implementations in `views.py`

---

**Last Updated**: February 2024
**Version**: 1.0
**Status**: Production Ready
