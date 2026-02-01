# Nutritionist Dashboard Module

A comprehensive Django application for managing nutritionist profiles and client assignments in the Dusangire restaurant platform.

## Features

✅ **Nutritionist Profile Management**
- Professional profile creation and updates
- License number tracking
- Specialization management
- Availability and capacity tracking
- Status management (active, inactive, on leave)

✅ **Client Assignment System**
- Assign clients to nutritionists
- Track assignment lifecycle
- Status management (active, paused, completed, terminated)
- Assignment notes and history
- Unique constraint to prevent duplicate assignments

✅ **Dashboard & Views**
- Nutritionist dashboard with statistics
- Client management interface
- Client detail pages with order history
- Advanced filtering and search

✅ **Admin Interface**
- Bulk actions for nutritionists
- Bulk actions for client assignments
- Advanced filtering and search
- Read-only audit timestamps

✅ **Testing & Quality**
- Comprehensive unit tests (20+ test cases)
- Model validation tests
- Form validation tests
- View permission tests
- Integration tests

✅ **Production Ready**
- Proper logging and audit trail
- Database indexes for performance
- Signal handlers for automation
- Environment-based configuration
- Security best practices

## Quick Start

### 1. Installation

```bash
# Already included in project
# Verify it's in INSTALLED_APPS in settings.py:
INSTALLED_APPS = [
    ...
    'nutritionist_dashboard',
    ...
]
```

### 2. Run Migrations

```bash
python manage.py migrate nutritionist_dashboard
```

### 3. Create Initial Data

```bash
# Seed demo nutritionists
python manage.py seed_nutritionists

# Or clear and reseed
python manage.py seed_nutritionists --clear
```

### 4. Access Admin Panel

```
http://localhost:8000/admin/nutritionist_dashboard/
```

### 5. Access Dashboard

```
http://localhost:8000/nutritionist/
```

## Project Structure

```
nutritionist_dashboard/
├── models.py                          # Database models
├── views.py                          # View logic
├── forms.py                          # Form definitions
├── serializers.py                    # DRF serializers
├── signals.py                        # Signal handlers
├── urls.py                           # URL routing
├── admin.py                          # Admin interface
├── tests.py                          # Test suite
├── apps.py                           # App configuration
├── management/
│   └── commands/
│       └── seed_nutritionists.py     # Data seeding command
├── DEPLOYMENT.md                     # Deployment guide
└── README.md                         # This file
```

## Models

### NutritionistProfile

Represents a nutritionist's professional profile.

**Fields:**
- `user` (OneToOneField) - Link to User model
- `bio` (TextField) - Professional biography
- `specialization` (CharField) - Area of specialization
- `license_number` (CharField, unique) - Professional license
- `phone_number` (CharField) - Contact number
- `status` (CharField) - active/inactive/on_leave
- `max_clients` (IntegerField) - Maximum client capacity
- `created_at` (DateTimeField) - Audit timestamp
- `updated_at` (DateTimeField) - Audit timestamp

**Methods:**
- `current_client_count` - Get active assigned clients
- `is_available` - Check if can take more clients
- `clean()` - Validation logic
- `__str__()` - String representation

### ClientAssignment

Represents assignment of a client to a nutritionist.

**Fields:**
- `nutritionist` (ForeignKey) - Assigned nutritionist
- `client` (ForeignKey) - Assigned client
- `start_date` (DateField) - Assignment start
- `end_date` (DateField) - Assignment end (null if active)
- `status` (CharField) - active/paused/completed/terminated
- `notes` (TextField) - Additional notes
- `created_at` (DateTimeField) - Audit timestamp
- `updated_at` (DateTimeField) - Audit timestamp

**Methods:**
- `is_active` - Check if currently active
- `terminate()` - End the assignment
- `clean()` - Validation logic
- `__str__()` - String representation

## Views

### Public Views (Authentication Required)

#### `dashboard_router()` 
Redirects users to appropriate dashboard based on role.

#### `dashboard(request)` 
Nutritionist dashboard showing profile and statistics.
- **URL**: `/nutritionist/`
- **Permission**: Must have NutritionistProfile
- **Methods**: GET

#### `manage_clients(request)`
List and manage all assigned clients.
- **URL**: `/nutritionist/clients/`
- **Permission**: Must be nutritionist
- **Methods**: GET
- **Filters**: status, search by name/email
- **Pagination**: 20 per page

#### `client_detail(request, assignment_id)`
View details of specific client assignment.
- **URL**: `/nutritionist/clients/<id>/`
- **Permission**: Must be assigned nutritionist
- **Methods**: GET

#### `create_profile(request)`
Create initial nutritionist profile.
- **URL**: `/nutritionist/create-profile/`
- **Permission**: Authenticated user
- **Methods**: GET, POST

#### `update_profile(request)`
Update existing nutritionist profile.
- **URL**: `/nutritionist/update-profile/`
- **Permission**: Must have profile
- **Methods**: GET, POST

#### `terminate_assignment(request, assignment_id)`
Terminate a client assignment.
- **URL**: `/nutritionist/clients/<id>/terminate/`
- **Permission**: Must be assigned nutritionist
- **Methods**: POST

## Forms

### NutritionistProfileForm

Validates and creates/updates nutritionist profiles.

**Fields:**
- `bio` (CharField) - Max 1000 characters
- `specialization` (CharField)
- `license_number` (CharField) - Must be unique
- `phone_number` (CharField)
- `max_clients` (IntegerField) - Min 1, Max 500

**Validations:**
- Bio length validation
- License number uniqueness
- Phone number format
- Max clients range

## Admin Interface

### Nutritionist Profile Admin

**List Display:**
- Name, Email, Specialization, Status
- Client count vs max capacity
- Created timestamp

**Filters:**
- Status
- Created date
- Updated date

**Search:**
- By name, email, license, specialization

**Actions:**
- Activate nutritionists
- Deactivate nutritionists
- Mark as on leave

### Client Assignment Admin

**List Display:**
- Client name, Nutritionist name
- Status, Start/End dates
- Active status indicator

**Filters:**
- Status
- Start date
- End date

**Search:**
- By client name/email
- By nutritionist name/email

**Actions:**
- Mark as active
- Mark as paused
- Mark as completed
- Terminate assignments

## Testing

### Run All Tests

```bash
python manage.py test nutritionist_dashboard
```

### Run Specific Test Class

```bash
python manage.py test nutritionist_dashboard.tests.NutritionistProfileModelTests
```

### Run with Verbose Output

```bash
python manage.py test nutritionist_dashboard --verbosity=2
```

### Test Coverage

- **Model Tests**: 12 tests
- **Form Tests**: 5 tests
- **View Tests**: 8 tests
- **Integration Tests**: 3 tests

**Total: 28 comprehensive tests**

## API Serializers

### NutritionistProfileSerializer
- Used for API endpoints
- Includes nested user details
- Computed fields for stats

### ClientAssignmentListSerializer
- List view serializer
- Optimized for performance

### ClientAssignmentDetailSerializer
- Detailed view serializer
- Includes all assignment data

## Logging

The module logs important events:
- Profile creation/updates
- Assignment changes
- Terminations
- Errors

**Log Location**: `logs/nutritionist_dashboard.log`

**Log Levels:**
- INFO: Normal operations
- WARNING: Profile/assignment deletions
- ERROR: Exceptions and failures

## Permissions & Security

- ✓ Login required for all views
- ✓ Nutritionist-only dashboard
- ✓ Client data access control
- ✓ Assignment ownership validation
- ✓ Admin bulk actions
- ✓ CSRF protection
- ✓ SQL injection prevention
- ✓ XSS protection

## Performance Features

- Database indexes on frequently filtered fields
- Pagination on list views
- `select_related()` for FK optimization
- `prefetch_related()` for reverse FK optimization
- Bulk action support in admin
- Query optimization in views

## Database Optimization

**Indexes:**
```python
class Meta:
    indexes = [
        models.Index(fields=['user']),
        models.Index(fields=['status']),
        models.Index(fields=['-created_at']),
    ]
```

**Unique Constraints:**
```python
unique_together = ('nutritionist', 'client')
```

## Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for comprehensive deployment instructions.

### Quick Deploy

```bash
# 1. Run migrations
python manage.py migrate nutritionist_dashboard

# 2. Create superuser (if needed)
python manage.py createsuperuser

# 3. Seed initial data
python manage.py seed_nutritionists

# 4. Collect static files
python manage.py collectstatic --noinput

# 5. Run security checks
python manage.py check --deploy

# 6. Run tests
python manage.py test nutritionist_dashboard
```

## Troubleshooting

### Profile Not Found

```bash
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> from nutritionist_dashboard.models import NutritionistProfile
>>> User = get_user_model()
>>> user = User.objects.get(username='username')
>>> NutritionistProfile.objects.create(user=user)
```

### Duplicate Assignment Error

Cannot assign the same client twice to the same nutritionist. This is by design.

### Status Not Updating

Ensure the status value is one of: `active`, `inactive`, `on_leave`, `paused`, `completed`, `terminated`

## Contributing

When modifying this module:

1. ✓ Write tests for new features
2. ✓ Update models documentation
3. ✓ Run all tests before committing
4. ✓ Follow Django best practices
5. ✓ Add logging for important events
6. ✓ Update this README

## Future Enhancements

- [ ] REST API endpoints
- [ ] Mobile app support
- [ ] Nutritionist ratings
- [ ] Client feedback system
- [ ] Meal plan tracking
- [ ] Appointment scheduling
- [ ] Video consultation integration
- [ ] Progress tracking metrics

## Support

For issues or questions:
1. Check the logs: `logs/nutritionist_dashboard.log`
2. Review the admin interface
3. Run tests: `python manage.py test nutritionist_dashboard`
4. Check [DEPLOYMENT.md](./DEPLOYMENT.md)

## License

Part of the Dusangire Restaurant Platform.

---

**Version**: 1.0 (Production Ready)
**Last Updated**: January 2025
**Status**: ✅ Ready for Deployment
