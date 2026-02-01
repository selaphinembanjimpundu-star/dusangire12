# Health Check URLs Configuration

## Usage

Add these URLs to your main `urls.py`:

```python
# dusangire/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # ... other paths ...
    path('health-checks/', include('health_profiles.urls')),
]
```

## URL Patterns

```python
# health_profiles/urls.py

from django.urls import path
from . import views

app_name = 'health_checks'

urlpatterns = [
    # Health Check List & Management
    path('', views.health_checks_list, name='health_checks_list'),
    path('request/', views.request_health_check, name='request_health_check'),
    path('<int:pk>/', views.health_check_detail, name='health_check_detail'),
    path('<int:pk>/cancel/', views.cancel_health_check, name='cancel_health_check'),
    
    # Consultant Operations
    path('assigned/', views.consultant_assigned_checks, name='consultant_assigned_checks'),
    path('<int:pk>/start/', views.start_consultation, name='start_consultation'),
    path('<int:pk>/complete/', views.complete_consultation, name='complete_consultation'),
    
    # Availability Management
    path('availability/update/', views.update_availability, name='update_availability'),
    
    # Admin/Analytics
    path('analytics/', views.health_check_analytics, name='health_check_analytics'),
    path('assignment-logs/', views.assignment_logs, name='assignment_logs'),
]
```

## Views to Create

Each URL pattern above needs a corresponding view. Here's the template structure:

### 1. health_checks_list
```python
@login_required
@role_required(['patient', 'medical_staff', 'nutritionist', 'hospital_manager', 'admin'])
def health_checks_list(request):
    """Display health checks dashboard based on user role"""
    if request.user.profile.role == 'patient':
        checks = HealthCheck.objects.filter(patient=request.user)
        template = 'health_checks/list.html'
    else:
        checks = HealthCheck.objects.filter(assigned_consultant=request.user)
        template = 'health_checks/list.html'
    
    return render(request, template, {
        'patient_checks': checks,
        'pending_count': checks.filter(status='pending').count(),
        # ... more context
    })
```

### 2. request_health_check
```python
@login_required
@role_required(['patient', 'medical_staff', 'hospital_manager', 'admin'])
def request_health_check(request):
    """Create new health check request"""
    if request.method == 'POST':
        check = HealthCheck(patient=request.user)
        check.check_type = request.POST['check_type']
        check.priority = request.POST['priority']
        check.description = request.POST.get('description', '')
        check.requested_date = request.POST.get('requested_date')
        check.save()
        # Signal automatically triggers assignment
        return redirect('health_checks:health_check_detail', pk=check.pk)
    
    return render(request, 'health_checks/request_form.html')
```

### 3. health_check_detail
```python
@login_required
def health_check_detail(request, pk):
    """View health check details"""
    check = get_object_or_404(HealthCheck, pk=pk)
    
    # Permission check
    if not (request.user == check.patient or 
            request.user == check.assigned_consultant or
            request.user.profile.role in ['hospital_manager', 'admin']):
        raise PermissionDenied
    
    logs = AutoAssignmentLog.objects.filter(health_check=check)
    
    return render(request, 'health_checks/detail.html', {
        'check': check,
        'assignment_logs': logs,
    })
```

### 4. start_consultation
```python
@login_required
@role_required(['medical_staff', 'nutritionist', 'admin'])
def start_consultation(request, pk):
    """Start a consultation on an assigned health check"""
    check = get_object_or_404(HealthCheck, pk=pk)
    
    # Permission check
    if check.assigned_consultant != request.user:
        raise PermissionDenied
    
    if request.method == 'POST':
        check.status = HealthCheck.StatusChoices.IN_PROGRESS
        check.save()  # Signal sends notification
        return redirect('health_checks:health_check_detail', pk=check.pk)
    
    return redirect('health_checks:health_check_detail', pk=check.pk)
```

### 5. complete_consultation
```python
@login_required
@role_required(['medical_staff', 'nutritionist', 'admin'])
def complete_consultation(request, pk):
    """Complete a consultation and add recommendations"""
    check = get_object_or_404(HealthCheck, pk=pk)
    
    if check.assigned_consultant != request.user:
        raise PermissionDenied
    
    if request.method == 'POST':
        check.consultant_notes = request.POST.get('consultant_notes', '')
        check.recommendations = request.POST.get('recommendations', '')
        check.status = HealthCheck.StatusChoices.COMPLETED
        check.completed_datetime = timezone.now()
        check.save()  # Signal sends completion notification
        return redirect('health_checks:health_check_detail', pk=check.pk)
    
    return render(request, 'health_checks/complete_form.html', {'check': check})
```

### 6. update_availability
```python
@login_required
@role_required(['medical_staff', 'nutritionist', 'admin'])
def update_availability(request):
    """Update consultant availability status"""
    if request.method == 'POST':
        availability = request.user.consultant_availability
        availability.status = request.POST.get('status')
        availability.max_concurrent_checks = request.POST.get('max_concurrent', 3)
        availability.save()  # Signal triggers auto-assignment
        
        return JsonResponse({'success': True, 'message': 'Availability updated'})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
```

## Middleware & Decorators

### RBAC Decorator
```python
# health_profiles/decorators.py

from functools import wraps
from django.core.exceptions import PermissionDenied

def role_required(roles):
    """Check if user has required role"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.profile.role not in roles:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
```

## Template Rendering

### Base health_check context processor

```python
# health_profiles/context_processors.py

def health_checks_context(request):
    """Add health check data to all templates"""
    if not request.user.is_authenticated:
        return {}
    
    context = {
        'pending_health_checks': 0,
        'assigned_health_checks': 0,
    }
    
    if hasattr(request.user, 'profile'):
        if request.user.profile.role == 'patient':
            context['pending_health_checks'] = HealthCheck.objects.filter(
                patient=request.user,
                status='pending'
            ).count()
        else:
            context['assigned_health_checks'] = HealthCheck.objects.filter(
                assigned_consultant=request.user,
                status__in=['assigned', 'in_progress']
            ).count()
    
    return context
```

Register in settings.py:
```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # ... existing processors ...
                'health_profiles.context_processors.health_checks_context',
            ],
        },
    },
]
```

## API Endpoints (Optional)

If implementing REST API with Django REST Framework:

```python
# health_profiles/api_urls.py

from rest_framework.routers import DefaultRouter
from .api_views import HealthCheckViewSet, ConsultantAvailabilityViewSet

router = DefaultRouter()
router.register('health-checks', HealthCheckViewSet)
router.register('availability', ConsultantAvailabilityViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
```

## Static Files

Add to base template header:
```html
{% load static %}
<link rel="stylesheet" href="{% static 'health_checks/css/style.css' %}">
<script src="{% static 'health_checks/js/health-checks.js' %}"></script>
```

## Form Handling

```python
# health_profiles/forms.py

from django import forms
from .models import HealthCheck

class HealthCheckRequestForm(forms.ModelForm):
    class Meta:
        model = HealthCheck
        fields = ['check_type', 'priority', 'description', 'requested_date']
        widgets = {
            'check_type': forms.RadioSelect(),
            'priority': forms.RadioSelect(),
            'description': forms.Textarea(attrs={'rows': 6}),
            'requested_date': forms.DateInput(attrs={'type': 'date'}),
        }
```

## Pagination

```python
from django.core.paginator import Paginator

def health_checks_list(request):
    checks = HealthCheck.objects.all()
    paginator = Paginator(checks, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    return render(request, 'health_checks/list.html', {'page_obj': page_obj})
```

## Testing URLs

```bash
# Test URL patterns
python manage.py check
python manage.py urls

# View URL config
python manage.py show_urls
```

---

**Note:** Implement these views with proper permission checks and error handling. Use the RBAC system created in Phase 1 for role-based access control.
