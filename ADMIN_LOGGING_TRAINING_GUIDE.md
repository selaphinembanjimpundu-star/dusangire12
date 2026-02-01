# Admin Logging System - Training Guide

## 👥 Training Materials for Different Roles

---

## 👨‍💼 For Administrators (15 minutes)

### What is the Admin Logging System?
The Admin Logging System is a tool that automatically records all admin activities - who did what, when, and with what results.

### Why Should I Care?
- **Security**: See who accessed what and when
- **Compliance**: Have an audit trail for business requirements
- **Debugging**: Find out what changed when something broke
- **Accountability**: Track who made what changes

### How to Access Logs

#### Method 1: Web Interface (Easiest)
1. Log in to the admin panel
2. Visit: `http://yoursite.com/admin/logs/`
3. You'll see a table of all activities
4. Use the filters to find specific actions
5. Click "View" to see details

#### Method 2: Dashboard
1. Visit: `http://yoursite.com/admin/activity-summary/`
2. See statistics and charts
3. View top actions and active admins
4. Recent activities list at bottom

#### Method 3: Django Admin
1. Go to: `http://yoursite.com/admin/`
2. Look for "Admin Dashboard" section
3. Click "Admin Logs"
4. Browse, filter, and search logs

### Filtering Logs

**By Action Type**
- Look for specific operations: UPDATE, CREATE, DELETE, etc.

**By User**
- See which admin did what

**By Status**
- SUCCESS = it worked ✅
- FAILED = there was an error ❌
- PENDING = still processing ⏳
- WARNING = worked but with issues ⚠️

**By Model**
- See changes to Orders, Users, Payments, etc.

### Searching Logs
- Search by description
- Search by error message
- Search by model name

### Exporting Data
```
Click "Export CSV" or "Export JSON" buttons
Use for reports, backup, or further analysis
```

### What Information is Logged

| Item | Example |
|------|---------|
| Who | Admin username |
| What | Update order status |
| When | 2024-02-01 14:30:00 |
| Where | IP address: 192.168.1.1 |
| Which | Order #42 |
| Status | Success/Failed |
| Time taken | 245 milliseconds |
| Changes | Old value → New value |

### Key Metrics to Monitor

**Daily**
- Check for failed actions
- Look for unusual IP addresses

**Weekly**
- Review most modified objects
- Check who's making most changes

**Monthly**
- Analyze activity trends
- Identify peak activity times

### Common Questions

**Q: How long are logs kept?**
A: Indefinitely by default. Your admin can set up archival.

**Q: Can I modify logs?**
A: No, logs are read-only (for security).

**Q: Can I delete logs?**
A: Only superadmins can delete logs.

**Q: What if I need a report?**
A: Export as CSV or JSON and use Excel/tools to analyze.

---

## 👨‍💻 For Developers (30 minutes)

### Architecture Overview

```
Admin Action Happens
        ↓
log_admin_action() is called
        ↓
AdminLog database entry created
        ↓
Viewable via:
  - Web UI (/admin/logs/)
  - Django Admin (/admin/)
  - API functions
  - Export (CSV/JSON)
```

### Basic Integration (Easiest)

**Using the Decorator:**
```python
from admin_dashboard.logger import admin_action_logger

@admin_action_logger('UPDATE', 'Order')
def update_order(request, order_id):
    order = Order.objects.get(id=order_id)
    order.status = 'confirmed'
    order.save()
    return redirect('order_detail', id=order_id)
```

**What the decorator does:**
- Captures the action automatically
- Measures execution time
- Logs success or failure
- Includes all context (user, IP, etc.)

### Intermediate Integration (More Control)

**Using the Function:**
```python
from admin_dashboard.logger import log_admin_action

def update_order(request, order_id):
    order = Order.objects.get(id=order_id)
    old_status = order.status
    
    order.status = 'confirmed'
    order.save()
    
    # Log the specific change
    log_admin_action(
        user=request.user,
        action='ORDER_UPDATE',
        model_name='Order',
        object_id=order_id,
        old_values={'status': old_status},
        new_values={'status': order.status},
        description=f'Changed status from {old_status} to confirmed',
        request=request
    )
    
    return redirect('order_detail', id=order_id)
```

### Advanced Integration (Model Changes)

**Tracking Model Changes Automatically:**
```python
from admin_dashboard.logger import log_model_change

def update_order(request, order_id):
    old_order = Order.objects.get(id=order_id)
    order = Order.objects.get(id=order_id)
    
    # Make changes
    order.status = 'confirmed'
    order.save()
    
    # Log the changes
    log_model_change(
        user=request.user,
        instance=order,
        action='UPDATE',
        old_instance=old_order,
        request=request
    )
```

### The Three Approaches Compared

| Approach | Effort | Control | When to Use |
|----------|--------|---------|------------|
| **Decorator** | Minimal | Medium | Simple actions |
| **Function** | Medium | High | Complex changes |
| **Model Logger** | Low | High | All model changes |

### Helper Functions

**Get Recent Logs**
```python
from admin_dashboard.logger import get_recent_logs

# Get last 50 UPDATE actions
logs = get_recent_logs(
    limit=50,
    action='UPDATE',
    user=request.user
)
```

**Get Logs by Date**
```python
from admin_dashboard.logger import get_logs_by_date_range
from datetime import date

# Get logs from this month
logs = get_logs_by_date_range(
    date(2024, 2, 1),
    date(2024, 2, 29),
    action='CREATE'
)
```

**Export to JSON**
```python
from admin_dashboard.logger import export_logs_to_json

logs = AdminLog.objects.all()
json_data = export_logs_to_json(logs)
# Returns ready-to-use JSON string
```

### Database Model

```python
AdminLog
├── admin_user      → Who did it
├── action          → What type (UPDATE, CREATE, etc.)
├── model_name      → Which model (Order, User, etc.)
├── object_id       → Which specific object
├── description     → Human-readable description
├── old_values      → Before state (JSON)
├── new_values      → After state (JSON)
├── ip_address      → Where from
├── user_agent      → Browser info
├── status          → Success/Failed/Pending
├── error_message   → Error details if failed
├── timestamp       → When it happened
└── duration_ms     → How long it took
```

### Querying Logs Programmatically

**Basic Queries:**
```python
from admin_dashboard.models import AdminLog

# All logs
AdminLog.objects.all()

# Logs for specific user
AdminLog.objects.filter(admin_user=request.user)

# Failed actions
AdminLog.objects.filter(status='FAILED')

# Specific model
AdminLog.objects.filter(model_name='Order')

# Today's logs
from django.utils import timezone
today = timezone.now().date()
AdminLog.objects.filter(timestamp__date=today)
```

**Aggregate Queries:**
```python
from django.db.models import Count

# Count actions by type
AdminLog.objects.values('action').annotate(
    count=Count('id')
).order_by('-count')

# Count by user
AdminLog.objects.values('admin_user__username').annotate(
    count=Count('id')
)

# Count failed actions
AdminLog.objects.filter(status='FAILED').count()
```

### Error Handling with Logging

**Pattern: Log Both Success and Failure**
```python
def process_payment(request, payment_id):
    payment = Payment.objects.get(id=payment_id)
    
    try:
        payment.process()
        payment.save()
        
        log_admin_action(
            user=request.user,
            action='PAYMENT_PROCESS',
            model_name='Payment',
            object_id=payment_id,
            status='SUCCESS',
            description=f'Processed payment {payment_id}',
            request=request
        )
        messages.success(request, 'Payment processed')
    
    except Exception as e:
        log_admin_action(
            user=request.user,
            action='PAYMENT_PROCESS',
            model_name='Payment',
            object_id=payment_id,
            status='FAILED',
            error_message=str(e),
            description='Failed to process payment',
            request=request
        )
        messages.error(request, f'Payment failed: {e}')
        
        raise
```

### Testing Your Logging

**In Django Shell:**
```bash
python manage.py shell

# Import
from admin_dashboard.logger import log_admin_action
from django.contrib.auth import get_user_model

# Get a user
User = get_user_model()
user = User.objects.filter(is_staff=True).first()

# Create test log
log_admin_action(
    user=user,
    action='TEST',
    model_name='TestModel',
    object_id=1,
    description='This is a test log entry',
    status='SUCCESS'
)

# Verify
from admin_dashboard.models import AdminLog
logs = AdminLog.objects.filter(action='TEST')
print(logs.count())  # Should be 1
print(logs[0])
```

### Best Practices

1. **Always pass request** for IP tracking
2. **Log before and after values** for audit trails
3. **Use specific action types** for better filtering
4. **Handle errors** with FAILED status
5. **Include meaningful descriptions** explaining changes
6. **Use decorator for simple actions** (less code)
7. **Use function for complex changes** (more control)

### Common Integration Points

**Orders**
```python
@admin_action_logger('ORDER_UPDATE', 'Order')
def confirm_order(request, order_id):
    pass
```

**Payments**
```python
@admin_action_logger('PAYMENT_PROCESS', 'Payment')
def process_payment(request, payment_id):
    pass
```

**Users**
```python
@admin_action_logger('CREATE', 'User')
def create_admin_user(request):
    pass
```

**Reports**
```python
@admin_action_logger('REPORT_GENERATE', 'Report')
def generate_report(request):
    pass
```

---

## 🎓 Training Exercises

### Exercise 1: View Logs (5 minutes)
1. Log in as admin
2. Visit `/admin/logs/`
3. Filter by action "CREATE"
4. Search for "order"
5. Click on a log to see details

### Exercise 2: Manual Logging (10 minutes)
1. Open a Django shell: `python manage.py shell`
2. Import the logger function
3. Create a test log entry
4. Visit `/admin/logs/` to see it

### Exercise 3: Add Logging to View (15 minutes)
1. Pick a simple admin view
2. Add the decorator: `@admin_action_logger('UPDATE', 'Model')`
3. Test the view
4. Check `/admin/logs/` to see the entry

### Exercise 4: Export Data (10 minutes)
1. Visit `/admin/logs/`
2. Click "Export CSV"
3. Open in Excel or text editor
4. Notice the columns and data format

---

## 📊 Monitoring Dashboard

The Activity Summary shows:

**Today's Activities**: How many actions this session  
**This Week**: Weekly trend  
**This Month**: Monthly trend  
**Failed Actions**: Errors to investigate  

**Top Actions Chart**: Most used features  
**Most Active Admins**: Who's using the system  
**Most Modified Models**: Most changed objects  
**Recent Activities**: Last 20 actions  

---

## 🔒 Security Training

**What Gets Logged**
- User who performed action ✅
- Action type ✅
- Object changed ✅
- When it happened ✅
- Where from (IP) ✅
- Status and errors ✅

**What Doesn't Get Logged**
- Passwords ❌
- Tokens ❌
- Sensitive secrets ❌

**Access Control**
- Only staff/admin can view logs
- Only superusers can delete logs
- Logs cannot be modified
- Immutable audit trail

---

## 🐛 Troubleshooting for Developers

**Logs not appearing?**
- Run migration first
- Check log_admin_action() is being called
- Verify user is authenticated

**Missing IP address?**
- Pass request parameter: `request=request`
- IP is optional but recommended

**Import errors?**
- Check file paths
- Verify models.py exists
- Run migration

**Permission denied?**
- User must be staff: `is_staff=True`
- Check user roles

---

## 📚 Learning Resources

| Resource | Time | Level |
|----------|------|-------|
| This guide | 30m | All |
| Quick reference card | 5m | Dev |
| Full docs | 60m | Dev |
| Code examples | 20m | Dev |

---

## 🎯 After Training

### Administrators
- Review logs daily
- Watch for failed actions
- Export for reports as needed

### Developers
- Add logging to new views
- Use decorator for simple cases
- Use function for complex changes
- Test your logging

### Managers
- Monitor activity summary
- Track team activity
- Review failed actions
- Analyze trends

---

**Training Complete!** You now know how to use the Admin Logging System. 🎉
