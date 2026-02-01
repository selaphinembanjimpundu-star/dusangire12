from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, F
from django.utils import timezone
from .models import HealthCheck, ConsultantAvailability, AutoAssignmentLog


def role_required(roles):
    """Decorator to check user role"""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not hasattr(request.user, 'profile') or request.user.profile.role not in roles:
                return redirect('accounts:login')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


@login_required
@role_required(['patient', 'medical_staff', 'nutritionist', 'hospital_manager', 'admin'])
def health_checks_list(request):
    """Display health checks dashboard"""
    user_role = request.user.profile.role if hasattr(request.user, 'profile') else None
    
    context = {
        'user_role': user_role,
    }
    
    # Patient view - their own checks
    if user_role == 'patient':
        checks = HealthCheck.objects.filter(patient=request.user).select_related('assigned_consultant')
        paginator = Paginator(checks, 20)
        page_obj = paginator.get_page(request.GET.get('page'))
        
        context.update({
            'page_obj': page_obj,
            'patient_checks': page_obj.object_list,
            'pending_count': checks.filter(status='pending').count(),
        })
    
    # Consultant view - assigned checks
    elif user_role in ['medical_staff', 'nutritionist']:
        checks = HealthCheck.objects.filter(assigned_consultant=request.user).select_related('patient')
        paginator = Paginator(checks, 20)
        page_obj = paginator.get_page(request.GET.get('page'))
        
        try:
            availability = ConsultantAvailability.objects.get(user=request.user)
            context['consultant_availability'] = availability
        except ConsultantAvailability.DoesNotExist:
            pass
        
        context.update({
            'page_obj': page_obj,
            'assigned_checks': page_obj.object_list,
            'assigned_count': checks.filter(status__in=['assigned', 'in_progress']).count(),
        })
    
    # Manager/Admin view - all checks
    else:
        checks = HealthCheck.objects.all().select_related('patient', 'assigned_consultant')
        paginator = Paginator(checks, 50)
        page_obj = paginator.get_page(request.GET.get('page'))
        context['page_obj'] = page_obj
    
    return render(request, 'health_checks/list.html', context)


@login_required
@role_required(['patient', 'medical_staff', 'hospital_manager', 'admin'])
def request_health_check(request):
    """Create new health check request"""
    if request.method == 'POST':
        check = HealthCheck(patient=request.user)
        check.check_type = request.POST.get('check_type', 'initial')
        check.priority = request.POST.get('priority', 'normal')
        check.description = request.POST.get('description', '')
        check.requested_date = request.POST.get('requested_date') or None
        check.status = 'pending'
        check.save()
        
        # Signal will auto-assign if consultant available
        return redirect('health_checks:health_check_detail', pk=check.pk)
    
    return render(request, 'health_checks/request_form.html')


@login_required
def health_check_detail(request, pk):
    """View health check details"""
    check = get_object_or_404(HealthCheck, pk=pk)
    
    # Permission check
    if not (request.user == check.patient or 
            request.user == check.assigned_consultant or
            (hasattr(request.user, 'profile') and request.user.profile.role in ['hospital_manager', 'admin'])):
        return redirect('accounts:login')
    
    logs = AutoAssignmentLog.objects.filter(health_check=check).order_by('-timestamp')
    
    context = {
        'check': check,
        'assignment_logs': logs,
    }
    return render(request, 'health_checks/detail.html', context)


@login_required
@role_required(['patient'])
def cancel_health_check(request, pk):
    """Cancel pending health check"""
    check = get_object_or_404(HealthCheck, pk=pk, patient=request.user)
    
    if check.status == 'pending':
        check.status = 'cancelled'
        check.save()
    
    return redirect('health_checks:health_checks_list')


@login_required
@role_required(['medical_staff', 'nutritionist', 'admin'])
def start_consultation(request, pk):
    """Start consultation on assigned health check"""
    check = get_object_or_404(HealthCheck, pk=pk)
    
    if check.assigned_consultant != request.user and request.user.profile.role != 'admin':
        return redirect('accounts:login')
    
    if check.status == 'assigned':
        check.status = 'in_progress'
        check.save()
    
    return redirect('health_checks:health_check_detail', pk=check.pk)


@login_required
@role_required(['medical_staff', 'nutritionist', 'admin'])
def complete_consultation(request, pk):
    """Complete consultation and add recommendations"""
    check = get_object_or_404(HealthCheck, pk=pk)
    
    if check.assigned_consultant != request.user and request.user.profile.role != 'admin':
        return redirect('accounts:login')
    
    if request.method == 'POST':
        check.consultant_notes = request.POST.get('consultant_notes', '')
        check.recommendations = request.POST.get('recommendations', '')
        check.status = 'completed'
        check.completed_datetime = timezone.now()
        check.save()
        
        # Update availability workload
        if check.assigned_consultant:
            try:
                availability = ConsultantAvailability.objects.get(user=check.assigned_consultant)
                availability.total_completed_checks += 1
                availability.save()
            except ConsultantAvailability.DoesNotExist:
                pass
        
        return redirect('health_checks:health_check_detail', pk=check.pk)
    
    return render(request, 'health_checks/complete_form.html', {'check': check})


@login_required
@require_http_methods(["POST"])
@role_required(['medical_staff', 'nutritionist', 'admin'])
def update_availability(request):
    """Update consultant availability status"""
    try:
        availability = ConsultantAvailability.objects.get(user=request.user)
    except ConsultantAvailability.DoesNotExist:
        return JsonResponse({'error': 'No availability record found'}, status=404)
    
    availability.status = request.POST.get('status', availability.status)
    max_concurrent = request.POST.get('max_concurrent')
    if max_concurrent:
        availability.max_concurrent_checks = int(max_concurrent)
    
    availability.save()
    
    return JsonResponse({
        'success': True,
        'message': 'Availability updated',
        'status': availability.status,
        'workload': f"{availability.current_assignments}/{availability.max_concurrent_checks}"
    })


@login_required
@role_required(['hospital_manager', 'admin'])
def health_check_analytics(request):
    """View health check analytics"""
    stats = {
        'total_checks': HealthCheck.objects.count(),
        'pending': HealthCheck.objects.filter(status='pending').count(),
        'assigned': HealthCheck.objects.filter(status='assigned').count(),
        'in_progress': HealthCheck.objects.filter(status='in_progress').count(),
        'completed': HealthCheck.objects.filter(status='completed').count(),
        'auto_assigned': HealthCheck.objects.filter(auto_assigned=True).count(),
    }
    
    # Consultant utilization
    consultants = ConsultantAvailability.objects.all().select_related('user').order_by('-average_rating')
    
    context = {
        'stats': stats,
        'consultants': consultants,
    }
    return render(request, 'health_checks/analytics.html', context)


@login_required
@role_required(['hospital_manager', 'admin'])
def assignment_logs(request):
    """View assignment logs"""
    logs = AutoAssignmentLog.objects.all().select_related(
        'health_check', 'assigned_consultant'
    ).order_by('-timestamp')
    
    # Filter by result
    result_filter = request.GET.get('result')
    if result_filter:
        logs = logs.filter(result=result_filter)
    
    paginator = Paginator(logs, 50)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    context = {
        'page_obj': page_obj,
        'result_filter': result_filter,
    }
    return render(request, 'health_checks/assignment_logs.html', context)
