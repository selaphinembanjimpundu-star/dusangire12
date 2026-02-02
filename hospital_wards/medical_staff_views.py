"""
Medical Staff Dashboard Views
Handles medical staff interactions with hospital wards, patients, and health data
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q, F
from django.utils import timezone
from datetime import timedelta

from accounts.models import UserRole
from hospital_wards.models import (
    Ward, WardBed, PatientAdmission, PatientDischarge,
    MealNutritionInfo, PatientEducationProgress
)
from orders.models import Order


def require_medical_staff(view_func):
    """Decorator to require medical staff role"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        
        user_role = getattr(request.user.profile, 'role', None)
        if user_role not in [UserRole.MEDICAL_STAFF, UserRole.HOSPITAL_MANAGER, UserRole.ADMIN]:
            messages.error(request, "You do not have permission to access this page.")
            return redirect('accounts:dashboard_home')
        
        return view_func(request, *args, **kwargs)
    
    wrapper.__name__ = view_func.__name__
    return wrapper


@login_required
@require_medical_staff
def medical_staff_dashboard(request):
    """
    Medical staff dashboard showing ward management and patient care
    """
    today = timezone.now()
    week_ago = today - timedelta(days=7)
    
    # Get wards assigned to this medical staff member
    wards = Ward.objects.filter(is_active=True)
    
    # Get bed statistics
    total_beds = WardBed.objects.filter(ward__is_active=True).count()
    occupied_beds = WardBed.objects.filter(
        ward__is_active=True,
        status='occupied'
    ).count()
    available_beds = total_beds - occupied_beds
    
    # Get recent admissions
    recent_admissions = PatientAdmission.objects.select_related(
        'patient', 'ward'
    ).filter(
        admission_date__date__gte=week_ago.date()
    ).order_by('-admission_date')[:10]
    
    # Get pending discharges (patients due to be discharged)
    pending_discharges = PatientDischarge.objects.filter(
        discharge_date__isnull=True
    ).select_related('patient').order_by('created_at')[:5]
    
    # Get patient education progress
    education_progress = PatientEducationProgress.objects.filter(
        completed_at__isnull=False,
        completed_at__gte=week_ago
    ).select_related('content', 'patient').count()
    
    # Get meal nutrition info
    nutrition_programs = MealNutritionInfo.objects.filter(
        is_active=True
    ).count()
    
    # Get orders for ward patients
    ward_patient_orders = Order.objects.filter(
        user__in=[bed.patient for bed in WardBed.objects.filter(patient__isnull=False)]
    ).count()
    
    context = {
        'title': 'Medical Staff Dashboard',
        'wards': wards,
        'total_beds': total_beds,
        'occupied_beds': occupied_beds,
        'available_beds': available_beds,
        'recent_admissions': recent_admissions,
        'pending_discharges': pending_discharges,
        'education_progress': education_progress,
        'nutrition_programs': nutrition_programs,
        'ward_patient_orders': ward_patient_orders,
    }
    
    return render(request, 'hospital_wards/medical_staff_dashboard.html', context)


@login_required
@require_medical_staff
def ward_management_dashboard(request):
    """
    Detailed ward management with real-time bed status and patient info
    """
    wards = Ward.objects.filter(is_active=True).prefetch_related(
        'beds__patient'
    ).annotate(
        available_beds=Count('beds', filter=Q(beds__status='available')),
        occupied_beds=Count('beds', filter=Q(beds__status='occupied')),
    )
    
    # Get ward statistics
    ward_stats = []
    for ward in wards:
        stats = {
            'ward': ward,
            'beds': ward.beds.filter(is_active=True),
            'available_count': ward.available_beds,
            'occupied_count': ward.occupied_beds,
            'occupancy_rate': (ward.occupied_beds / ward.capacity * 100) if ward.capacity > 0 else 0,
        }
        ward_stats.append(stats)
    
    context = {
        'title': 'Ward Management',
        'ward_stats': ward_stats,
        'total_wards': wards.count(),
    }
    
    return render(request, 'hospital_wards/ward_management_dashboard.html', context)


@login_required
@require_medical_staff
def patient_admission_dashboard(request):
    """
    Patient admission and discharge management
    """
    # Recent admissions
    recent_admissions = PatientAdmission.objects.select_related(
        'patient', 'ward'
    ).order_by('-admission_date')[:20]
    
    # Pending discharges
    pending_discharges = PatientDischarge.objects.filter(
        discharge_date__isnull=True
    ).select_related('patient').order_by('created_at')
    
    # Readmission risk (patients with frequent admissions)
    readmission_risk = PatientAdmission.objects.values('patient').annotate(
        admission_count=Count('id')
    ).filter(
        admission_count__gt=2
    ).order_by('-admission_count')
    
    context = {
        'title': 'Patient Admission & Discharge',
        'recent_admissions': recent_admissions,
        'pending_discharges': pending_discharges,
        'readmission_risk': readmission_risk,
    }
    
    return render(request, 'hospital_wards/patient_admission_dashboard.html', context)
