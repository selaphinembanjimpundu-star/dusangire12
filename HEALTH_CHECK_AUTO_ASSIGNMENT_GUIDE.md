# Health Check Auto-Assignment System - Complete Guide

## Overview

The Health Check Auto-Assignment System automatically matches patient health check requests with available consultants based on:
- **Priority levels** (Urgent > High > Normal > Low)
- **Consultant specialization** and availability
- **Workload** and capacity limits
- **Performance ratings** for quality-based matching

## System Architecture

### 1. Database Models

#### HealthCheck Model
Tracks patient health check requests:

```python
class HealthCheck(models.Model):
    patient = ForeignKey(User)  # Patient requesting check
    check_type = CharField()  # initial, follow_up, nutrition, medical, wellness
    status = CharField()  # pending, assigned, in_progress, completed, cancelled
    priority = CharField()  # urgent, high, normal, low
    
    assigned_consultant = ForeignKey(User, null=True)  # Auto-assigned consultant
    auto_assigned = BooleanField()  # Track if system assigned
    
    requested_date = DateField(null=True)  # Preferred date
    scheduled_datetime = DateTimeField(null=True)  # Scheduled time
    completed_datetime = DateTimeField(null=True)  # When completed
    
    description = TextField()  # Patient's description
    consultant_notes = TextField()  # Consultant's clinical notes
    recommendations = TextField()  # Post-consultation recommendations
```

#### ConsultantAvailability Model
Tracks consultant status and capacity:

```python
class ConsultantAvailability(models.Model):
    user = OneToOneField(User)  # Link to consultant user
    status = CharField()  # available, busy, break, offline
    
    # Capacity management
    current_assignments = IntegerField()  # Active health checks
    max_concurrent_checks = IntegerField()  # Capacity limit (default 3)
    
    # Specialization
    specialization = CharField()  # Nutrition, Medical Staff, etc.
    preferred_check_types = CharField()  # Comma-separated list
    preferred_priority = CharField()  # Preferred priority level
    
    # Performance tracking
    average_rating = DecimalField()  # 0-5 rating
    total_completed_checks = IntegerField()  # Career total
```

#### AutoAssignmentLog Model
Audit trail for all assignment attempts:

```python
class AutoAssignmentLog(models.Model):
    health_check = ForeignKey(HealthCheck)
    assigned_consultant = ForeignKey(User, null=True)
    result = CharField()  # success, no_available, error
    message = TextField()  # Description of attempt
    timestamp = DateTimeField(auto_now_add=True)
```

### 2. Assignment Logic

#### Priority Order
Assignments are processed by priority:
1. **Urgent** - Immediate assignment
2. **High** - Next 2-4 hours
3. **Normal** - Same day/next day
4. **Low** - Within 3-5 days

#### Matching Algorithm
For each pending check:

```
1. Group pending checks by priority (urgent first)
2. For each priority level:
   a. Filter consultants by specialization match
   b. Filter available consultants (status='available')
   c. Filter by capacity (current < max_concurrent)
   d. Sort by average_rating (highest first)
   e. Assign to top-rated available consultant
   f. Update consultant workload
   g. Create audit log entry
   h. Send notifications
```

#### Capacity Management
- Each consultant has `max_concurrent_checks` limit
- When check completes: `current_assignments` decreases
- System respects workload limits - never over-assigns

### 3. Triggering Auto-Assignment

#### Method 1: Real-Time Signals
When consultant status changes to 'available':

```python
# Automatically triggered by Django signals
@receiver(post_save, sender=ConsultantAvailability)
def auto_assign_on_availability_change(sender, instance, **kwargs):
    # Finds pending checks matching consultant's specialization
    # Assigns up to available slots
    # Creates audit logs
    # Sends notifications
```

**Advantages:**
- Immediate assignment when consultant becomes available
- No waiting for manual command execution
- Real-time user experience

#### Method 2: Management Command
Scheduled batch assignment:

```bash
# Run periodically (every 5-15 minutes via cron/Celery)
python manage.py auto_assign_health_checks --verbose

# Dry-run to test without making changes
python manage.py auto_assign_health_checks --dry-run --verbose
```

**Advantages:**
- Catches checks that didn't get auto-assigned
- Provides detailed logging
- Can be scheduled for specific times

### 4. Notification System

#### Automatic Notifications Sent

**When Check is Assigned:**
- ✉️ Email to patient with consultant details
- Includes: Check ID, consultant name, specialization, rating

**When Consultation Starts:**
- ✉️ Email to patient that consultant is ready
- Reminder to have medical info ready

**When Consultation Completes:**
- ✉️ Email to patient with recommendations
- Includes: Clinical notes, next steps, follow-up info
- ✉️ Email to consultant confirming recording

### 5. Permission & RBAC Integration

Health check operations respect existing RBAC:

| Role | Can Request | Can Assign To | Can View |
|------|------------|---------------|----------|
| Patient | Own requests | N/A | Own checks |
| Medical Staff | Patient checks | To themselves | Assigned checks |
| Nutritionist | Patient checks | To themselves | Assigned checks |
| Hospital Manager | Any request | Any consultant | All checks |
| Admin | Any request | Any consultant | All checks |

## Usage Guide

### For Patients

#### Requesting a Health Check

1. Go to **Health Checks** → **Request New Check**
2. Select check type:
   - Initial Health Check
   - Follow-up Consultation
   - Nutrition Consultation
   - Medical Consultation
   - Wellness Check

3. Select priority:
   - Low (can wait 3-5 days)
   - Normal (next available)
   - High (urgent, 2-4 hours)
   - Urgent (immediate)

4. Describe your concern (optional but recommended)
5. Add medical history if relevant
6. Confirm notification preferences
7. Submit request

**What happens next:**
- Check added to pending queue
- Auto-assignment triggers immediately if consultant available
- You receive email notification when consultant assigned
- Consultant reaches out to schedule appointment

#### Tracking Your Checks

1. Go to **Health Checks** → **My Health Checks**
2. View all your requests in one place
3. Click check to see:
   - Current status
   - Assigned consultant details
   - Consultant's specialization and rating
   - Recommendations and notes
   - Timeline of all events

### For Consultants (Medical Staff/Nutritionist)

#### Managing Availability

1. Go to **Health Checks** → **My Availability**
2. Update your status:
   - **Available** - Ready for new assignments
   - **Busy** - Currently in consultation
   - **Break** - On break, not taking new checks
   - **Offline** - Not working today

3. Set max concurrent checks:
   - Default: 3 (can handle up to 3 checks simultaneously)
   - Adjust based on your workload capacity

4. Update specialization and preferred check types

**Real-Time Assignment:**
When you set status to "Available":
- System automatically finds matching pending checks
- Assigns up to available slots based on priority
- You receive notification of new assignments
- Your workload updates instantly

#### Managing Assigned Checks

1. Go to **Health Checks** → **Assigned Checks**
2. Filter by status (Assigned, In Progress, Completed)
3. For each check:
   - View patient details and medical history
   - See check type and priority
   - Schedule appointment time
   - Start consultation
   - Record recommendations

**Check Lifecycle:**
- **Assigned** → Start consultation
- **In Progress** → Record notes and findings
- **Mark Complete** → Add recommendations
- **Completed** → Patient gets email with recommendations

### For Hospital Manager/Admin

#### Dashboard Overview

1. Go to **Health Checks** → **All Health Checks**
2. View system-wide metrics:
   - Total pending checks
   - Pending by priority
   - Average assignment time
   - Consultant utilization

#### Consultant Management

1. Go to **Consultants** (Admin)
2. View all consultant availability records
3. Manually adjust if needed:
   - Update max concurrent checks
   - Modify specialization
   - Reset workload (emergency only)

#### Monitoring Auto-Assignments

1. View **Assignment Logs**
2. See all assignment attempts (success/failed)
3. Identify bottlenecks:
   - Insufficient consultants for urgent checks
   - Capacity issues
   - Specialization gaps

## Configuration

### Settings (settings.py)

```python
# Email settings for notifications
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'your-email-provider'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email'
EMAIL_HOST_PASSWORD = 'your-password'
DEFAULT_FROM_EMAIL = 'noreply@dusangire.com'

# Site configuration
SITE_NAME = 'Dusangire'
CONTACT_EMAIL = 'support@dusangire.com'

# Auto-assignment settings
HEALTH_CHECK_AUTO_ASSIGN_ON_STATUS_CHANGE = True
HEALTH_CHECK_ASSIGNMENT_PRIORITY_ORDER = ['urgent', 'high', 'normal', 'low']
```

### Scheduled Auto-Assignment (using Celery)

```python
# celery.py
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'auto-assign-health-checks': {
        'task': 'health_profiles.tasks.run_auto_assignment',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
}
```

## API Endpoints (if REST API enabled)

### Patient Endpoints
- `POST /api/health-checks/` - Create new check request
- `GET /api/health-checks/` - List my checks
- `GET /api/health-checks/{id}/` - View check details

### Consultant Endpoints
- `GET /api/health-checks/assigned/` - Get assigned checks
- `PATCH /api/availability/` - Update availability status
- `POST /api/health-checks/{id}/complete/` - Complete consultation

### Admin Endpoints
- `GET /api/health-checks/all/` - View all checks
- `GET /api/assignment-logs/` - View assignment history
- `GET /api/analytics/` - System analytics

## Monitoring & Analytics

### Key Metrics

1. **Assignment Success Rate**
   - Percentage of checks auto-assigned vs manual
   - Goal: >90% auto-assigned

2. **Average Assignment Time**
   - Time from request to assignment
   - Goal: <5 minutes for urgent, <1 hour for normal

3. **Consultant Utilization**
   - Percentage of max capacity being used
   - Identifies under/over capacity situations

4. **Patient Satisfaction**
   - Rating of assigned consultants
   - Quality of recommendations

### Viewing Analytics

1. Go to **Admin** → **Health Check Analytics**
2. View charts:
   - Assignment trend over time
   - Consultant utilization by role
   - Check completion time
   - Priority distribution

## Troubleshooting

### Issue: Checks not auto-assigning

**Check 1: Signals enabled?**
```bash
# In Django shell
from health_profiles import signals
# Should see: "Health check auto-assignment signals initialized"
```

**Check 2: Consultants available?**
```bash
from health_profiles.models import ConsultantAvailability
ConsultantAvailability.objects.filter(
    status='available',
    current_assignments__lt=F('max_concurrent_checks')
)
# Should return available consultants
```

**Check 3: Specialization match?**
```bash
# Check if pending check type matches consultant's preferred types
pending_check.check_type in consultant_availability.preferred_check_types
```

**Check 4: Run assignment manually**
```bash
python manage.py auto_assign_health_checks --verbose --dry-run
# See what would be assigned without actually assigning
```

### Issue: Consultant overloaded

**Symptoms:** Consultants receiving too many checks

**Solution:**
1. Reduce `max_concurrent_checks` for that consultant
2. Add more consultants with that specialization
3. Adjust priority thresholds temporarily

### Issue: Notifications not sending

**Check email configuration:**
```bash
python manage.py shell
from django.core.mail import send_mail
send_mail('Test', 'Message', 'from@example.com', ['to@example.com'])
# Should complete without error
```

**Check email templates exist:**
```bash
ls templates/emails/
# Should have: health_check_assigned.html, consultation_completed.html, etc.
```

## Performance Optimization

### Database Indexes
Automatic indexes on high-query fields:
```python
# health_profiles/models.py
class HealthCheck:
    class Meta:
        indexes = [
            Index(fields=['patient', 'status']),
            Index(fields=['status', 'assigned_consultant']),
            Index(fields=['priority', 'status']),
        ]
```

### Bulk Assignment (Celery Task)
For high volume:
```python
# health_profiles/tasks.py
@shared_task
def bulk_auto_assign():
    """Run assignment in background without blocking UI"""
    pending = HealthCheck.objects.filter(status='pending')
    for check in pending[:50]:  # Process 50 at a time
        # Run assignment logic
```

### Caching Consultant Availability
```python
from django.core.cache import cache

# Cache available consultants for 1 minute
key = 'available_consultants_urgent'
available = cache.get(key)
if not available:
    available = ConsultantAvailability.objects.filter(...)
    cache.set(key, available, 60)
```

## Security Considerations

1. **Permission Checks:** All views verify user role/permissions
2. **Audit Logging:** All assignments logged to `AutoAssignmentLog`
3. **Data Privacy:** Patient details only visible to assigned consultant
4. **HIPAA Compliance:** Email notifications can be disabled if needed

## Future Enhancements

1. **Machine Learning Matching**
   - Learn optimal assignments based on outcomes
   - Predict consultant availability patterns

2. **Multi-Language Support**
   - Localized email notifications
   - Consultant language preferences

3. **Video Consultation Integration**
   - Direct video link in notifications
   - Real-time in-app consultations

4. **Appointment Reminder**
   - Automated reminders before scheduled time
   - Integration with calendar systems

5. **Follow-up Automation**
   - Automatic follow-up check scheduling
   - Treatment outcome tracking

## Support & Maintenance

### Regular Maintenance Tasks

```bash
# Weekly: Check assignment logs for errors
python manage.py health_check_report --since-days=7

# Monthly: Review consultant utilization
python manage.py report_utilization --month

# Quarterly: Audit email notification delivery
python manage.py check_email_logs --quarter
```

### Getting Help

- **Documentation**: See HEALTH_CHECKS_README.md
- **Code Examples**: Check health_profiles/examples/
- **Support Email**: support@dusangire.com
- **Admin Console**: Go to /admin/ for Django admin

---

**System Version:** 1.0  
**Last Updated:** February 1, 2026  
**Author:** AI Development Team  
**Status:** Production Ready ✅
