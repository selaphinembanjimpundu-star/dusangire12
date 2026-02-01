# Health Check Auto-Assignment - Technical Reference

## Quick Reference Guide

### Model Fields

#### HealthCheck
```python
id                          # Auto-incremented primary key
patient                     # ForeignKey(User) - Patient requesting check
check_type                  # CharField choices: initial, follow_up, nutrition, medical, wellness
status                      # CharField choices: pending, assigned, in_progress, completed, cancelled
priority                    # CharField choices: urgent, high, normal, low
assigned_consultant         # ForeignKey(User, null=True) - Assigned consultant
auto_assigned              # BooleanField - True if system assigned
description                # TextField - Patient's concern description
requested_date             # DateField, null=True - Preferred date
scheduled_datetime         # DateTimeField, null=True - Scheduled time
completed_datetime         # DateTimeField, null=True - When completed
consultant_notes           # TextField - Clinical notes
recommendations            # TextField - Recommendations
created_at                 # DateTimeField auto_now_add=True
assigned_at               # DateTimeField, null=True
```

#### ConsultantAvailability
```python
id                          # Auto-incremented primary key
user                        # OneToOneField(User) - Link to consultant
status                      # CharField choices: available, busy, break, offline
current_assignments         # IntegerField - Active check count
max_concurrent_checks       # IntegerField default=3 - Capacity limit
specialization             # CharField - e.g., "Medical", "Nutrition"
preferred_check_types      # CharField - Comma-separated list
preferred_priority         # CharField - Preferred priority level
average_rating            # DecimalField 0-5 - Performance rating
total_completed_checks    # IntegerField - Career total
```

#### AutoAssignmentLog
```python
id                          # Auto-incremented primary key
health_check               # ForeignKey(HealthCheck)
assigned_consultant        # ForeignKey(User, null=True)
result                     # CharField choices: success, no_available, error
message                    # TextField - Detailed message
timestamp                  # DateTimeField auto_now_add=True
```

### Choices/Constants

```python
# Check Types
CHECK_TYPES = [
    ('initial', 'Initial Health Check'),
    ('follow_up', 'Follow-up Consultation'),
    ('nutrition', 'Nutrition Consultation'),
    ('medical', 'Medical Consultation'),
    ('wellness', 'Wellness Check'),
]

# Status
STATUS_CHOICES = [
    ('pending', 'Pending Assignment'),
    ('assigned', 'Assigned'),
    ('in_progress', 'In Progress'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
]

# Priority
PRIORITY_CHOICES = [
    ('urgent', 'Urgent'),
    ('high', 'High'),
    ('normal', 'Normal'),
    ('low', 'Low'),
]

# Consultant Status
CONSULTANT_STATUS_CHOICES = [
    ('available', 'Available'),
    ('busy', 'Busy'),
    ('break', 'On Break'),
    ('offline', 'Offline'),
]

# Assignment Result
RESULT_CHOICES = [
    ('success', 'Successfully Assigned'),
    ('no_available', 'No Available Consultants'),
    ('error', 'Assignment Error'),
]
```

### API/View Parameters

#### Create Health Check
```
POST /health-checks/request/
{
    'check_type': 'initial',
    'priority': 'high',
    'description': 'Text description',
    'requested_date': '2026-02-15',
    'medical_history': 'Optional text',
    'current_medications': 'Optional text',
    'notify_email': True,
    'notify_sms': False,
}
```

#### Update Availability
```
POST /health-checks/availability/update/
{
    'status': 'available',
    'max_concurrent': 3,
}
```

#### Complete Consultation
```
POST /health-checks/<id>/complete/
{
    'consultant_notes': 'Findings and observations',
    'recommendations': 'Patient recommendations',
}
```

### Signals Reference

#### Signal 1: ConsultantAvailability.post_save
```python
# Triggered when consultant availability changes
# Automatically assigns pending checks if status='available'

Signal Flow:
  1. Consultant status changes → signal fires
  2. Check if status is 'available' and has capacity
  3. Find pending checks matching specialization
  4. Sort by priority (urgent first)
  5. Assign up to available slots
  6. Update workload
  7. Create audit log
  8. Send notifications
```

#### Signal 2: HealthCheck.pre_save
```python
# Triggered before health check saves
# Tracks status changes and workload

Monitors:
  - Status change from assigned → completed
  - Reduces consultant current_assignments
  - Increases total_completed_checks
  - Sends notification on status change
```

#### Signal 3: HealthCheck.post_save
```python
# Triggered after health check saves
# Sends notifications for completed checks

Monitors:
  - When status is completed
  - Sends email to patient with recommendations
  - Sends confirmation to consultant
```

### Management Command

#### Usage
```bash
# Run assignment with details
python manage.py auto_assign_health_checks --verbose

# Test without making changes
python manage.py auto_assign_health_checks --dry-run

# Both verbose and dry-run
python manage.py auto_assign_health_checks --verbose --dry-run
```

#### Output
```
Found 5 pending health checks
Processing by priority: urgent → high → normal → low

[URGENT] (1 checks)
  ✓ Check #1 → Dr. Smith (Rating: 4.8, Workload: 1/3)

[HIGH] (2 checks)
  ✓ Check #2 → Dr. Johnson (Rating: 4.7, Workload: 2/3)
  ✓ Check #3 → Dr. Williams (Rating: 4.5, Workload: 1/3)

[NORMAL] (1 checks)
  ✗ Check #4 → No available consultants (all at capacity)

[LOW] (1 checks)
  ✗ Check #5 → No matching specialization

=== ASSIGNMENT REPORT ===
Total processed: 5
Successfully assigned: 3
Failed/Pending: 2
Average assignment time: 0.12s
Processing time: 0.45s
```

### Database Queries

#### Find Pending Checks
```python
from health_profiles.models import HealthCheck

pending = HealthCheck.objects.filter(
    status=HealthCheck.StatusChoices.PENDING,
    assigned_consultant__isnull=True
).order_by('-priority', 'created_at')
```

#### Find Available Consultants
```python
from health_profiles.models import ConsultantAvailability
from django.db.models import F

available = ConsultantAvailability.objects.filter(
    status='available',
    current_assignments__lt=F('max_concurrent_checks')
).order_by('-average_rating')
```

#### Count by Status
```python
from django.db.models import Count

summary = HealthCheck.objects.values('status').annotate(
    count=Count('id')
)
# Output: [
#   {'status': 'pending', 'count': 5},
#   {'status': 'assigned', 'count': 3},
#   {'status': 'completed', 'count': 12},
# ]
```

#### Consultant Workload
```python
consultant_availability = ConsultantAvailability.objects.get(user_id=1)
workload_percent = (consultant_availability.current_assignments / 
                   consultant_availability.max_concurrent_checks * 100)
# Output: 66.67 (for 2/3 assignments)
```

### Email Templates

#### health_check_assigned.html
```html
<!-- Shows when check is assigned -->
Subject: Health Check Assigned - Check #{check_id}
Content:
  - Consultant name
  - Specialization
  - Rating
  - Next steps (consultant will reach out)
```

#### consultation_started.html
```html
<!-- Shows when consultation begins -->
Subject: Consultation Started - Check #{check_id}
Content:
  - Consultant name
  - Reminder to have medical info ready
  - Confirmation message
```

#### consultation_completed.html
```html
<!-- Shows when consultation completes -->
Subject: Consultation Complete - Check #{check_id}
Content:
  - Clinical findings
  - Recommendations
  - Next steps
  - Option to view full details
```

### Permission Decorators

```python
@role_required(['patient', 'medical_staff'])
def view_health_check(request, pk):
    # Only allows these roles
    pass

# Equivalent to:
if request.user.profile.role not in ['patient', 'medical_staff']:
    raise PermissionDenied
```

### Status Transitions

```
Valid Transitions:
  pending → assigned (auto)
  assigned → in_progress (consultant starts)
  in_progress → completed (consultant finishes)
  pending → cancelled (patient cancels)
  assigned → cancelled (rare - consultant unable)
```

### URL Patterns

```
GET  /health-checks/                              # List all checks
GET  /health-checks/<id>/                         # View check details
POST /health-checks/request/                      # Create new check
POST /health-checks/<id>/cancel/                  # Cancel pending check
POST /health-checks/<id>/start/                   # Start consultation
POST /health-checks/<id>/complete/                # Complete consultation
POST /health-checks/availability/update/          # Update availability
GET  /health-checks/assigned/                     # View assigned to me
GET  /health-checks/analytics/                    # View analytics (admin)
GET  /health-checks/assignment-logs/              # View assignment logs (admin)
```

### Role-Based Access

```
Patient:
  - Request check
  - View own checks
  - Cancel pending checks
  - View recommendations

Consultant (Medical Staff/Nutritionist):
  - View assigned checks
  - Update availability
  - Start consultation
  - Complete consultation
  - Record findings

Hospital Manager/Admin:
  - View all checks system-wide
  - Manually override assignments
  - View analytics
  - View assignment logs
  - Manage consultants
```

### Performance Considerations

#### Database Indexes
```python
class Meta:
    indexes = [
        Index(fields=['patient', 'status']),
        Index(fields=['status', 'assigned_consultant']),
        Index(fields=['priority', 'status']),
        Index(fields=['created_at']),
    ]
```

#### Query Optimization
```python
# Bad - N+1 problem
checks = HealthCheck.objects.all()
for check in checks:
    print(check.patient.email)  # Query per check!

# Good - use select_related
checks = HealthCheck.objects.select_related('patient', 'assigned_consultant')
for check in checks:
    print(check.patient.email)  # No additional query
```

#### Caching Strategy
```python
from django.core.cache import cache

# Cache available consultants for 1 minute
key = f'available_consultants_{priority}'
available = cache.get(key)
if not available:
    available = find_available_consultants(priority)
    cache.set(key, available, 60)
```

### Logging

#### Enable Debug Logging
```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'health_checks.log',
        },
    },
    'loggers': {
        'health_profiles': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

#### Log Events
```
HEALTH_CHECK EVENTS:
  [INFO] Auto-assignment triggered for check #{id}
  [INFO] Consultant {name} assigned to check #{id}
  [WARNING] No available consultants for check #{id}
  [ERROR] Assignment failed: {reason}

SIGNAL EVENTS:
  [INFO] Consultant {name} status changed to available
  [INFO] Auto-assign: {count} checks assigned in {time}s
  [INFO] Workload updated: {current}/{max} assignments
```

### Common Queries

#### Get my assigned checks
```python
assigned = HealthCheck.objects.filter(
    assigned_consultant=request.user,
    status__in=['assigned', 'in_progress']
)
```

#### Get my pending checks (as patient)
```python
pending = HealthCheck.objects.filter(
    patient=request.user,
    status='pending'
)
```

#### Get assignment statistics
```python
from django.db.models import Count, Q

stats = {
    'total': HealthCheck.objects.count(),
    'auto_assigned': HealthCheck.objects.filter(auto_assigned=True).count(),
    'average_time': calculate_avg_assignment_time(),
}
```

#### Check consultant availability
```python
availability = ConsultantAvailability.objects.get(user_id=consultant_id)
if availability.is_available:
    # Can assign more checks
    slots = availability.available_slots
```

---

**Last Updated**: February 1, 2026  
**Version**: 1.0  
**Status**: Complete & Ready for Integration
