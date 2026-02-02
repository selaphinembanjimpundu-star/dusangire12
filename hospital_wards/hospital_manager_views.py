"""
Hospital Manager Dashboard Views
Handles hospital operations, staff management, and strategic planning
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, Q, Avg, F
from django.utils import timezone
from datetime import timedelta

from accounts.models import UserRole, Profile
from hospital_wards.models import (
    Ward, WardBed, PatientAdmission, PatientDischarge,
    MealNutritionInfo, PatientEducationContent
)
from nutritionist_dashboard.models import MealPlan
from orders.models import Order
from payments.models import Payment


def require_hospital_manager(view_func):
    """Decorator to require hospital manager role"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        
        user_role = getattr(request.user.profile, 'role', None)
        if user_role not in [UserRole.HOSPITAL_MANAGER, UserRole.ADMIN]:
            messages.error(request, "You do not have permission to access this page.")
            return redirect('accounts:dashboard_home')
        
        return view_func(request, *args, **kwargs)
    
    wrapper.__name__ = view_func.__name__
    return wrapper


@login_required
@require_hospital_manager
def hospital_manager_dashboard(request):
    """
    Hospital Manager Dashboard with comprehensive hospital operations metrics
    """
    today = timezone.now()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Hospital Bed Statistics
    total_wards = Ward.objects.filter(is_active=True).count()
    total_beds = WardBed.objects.filter(ward__is_active=True).count()
    occupied_beds = WardBed.objects.filter(
        ward__is_active=True,
        status='occupied'
    ).count()
    available_beds = total_beds - occupied_beds
    occupancy_rate = (occupied_beds / total_beds * 100) if total_beds > 0 else 0
    
    # Patient Statistics
    current_patients = WardBed.objects.filter(
        patient__isnull=False,
        is_active=True
    ).count()
    
    total_admissions_month = PatientAdmission.objects.filter(
        admission_date__gte=month_ago
    ).count()
    
    total_discharges_month = PatientDischarge.objects.filter(
        discharge_date__gte=month_ago
    ).count()
    
    # Nutritional Programs
    active_meal_plans = MealPlan.objects.filter(is_active=True).count()
    nutrition_programs = MealNutritionInfo.objects.filter(is_active=True).count()
    education_materials = PatientEducationContent.objects.filter(is_active=True).count()
    
    # Order & Revenue Statistics
    total_orders_month = Order.objects.filter(
        created_at__gte=month_ago
    ).count()
    
    orders_this_week = Order.objects.filter(
        created_at__gte=week_ago
    ).count()
    
    total_revenue_month = Payment.objects.filter(
        paid_at__gte=month_ago,
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Staff Statistics
    medical_staff_count = Profile.objects.filter(
        role=UserRole.MEDICAL_STAFF,
        is_active=True
    ).count()
    
    nutritionist_count = Profile.objects.filter(
        role=UserRole.NUTRITIONIST,
        is_active=True
    ).count()
    
    kitchen_staff_count = Profile.objects.filter(
        role__in=[UserRole.CHEF, UserRole.KITCHEN_STAFF],
        is_active=True
    ).count()
    
    delivery_staff_count = Profile.objects.filter(
        role=UserRole.DELIVERY_PERSON,
        is_active=True
    ).count()
    
    # Ward Performance
    wards = Ward.objects.filter(is_active=True).annotate(
        available_beds=Count('beds', filter=Q(beds__status='available')),
        occupied_beds=Count('beds', filter=Q(beds__status='occupied')),
    )
    
    # Recent Activity
    recent_admissions = PatientAdmission.objects.select_related(
        'patient', 'ward'
    ).order_by('-admission_date')[:5]
    
    context = {
        'title': 'Hospital Manager Dashboard',
        # Bed Statistics
        'total_wards': total_wards,
        'total_beds': total_beds,
        'occupied_beds': occupied_beds,
        'available_beds': available_beds,
        'occupancy_rate': occupancy_rate,
        # Patient Statistics
        'current_patients': current_patients,
        'total_admissions_month': total_admissions_month,
        'total_discharges_month': total_discharges_month,
        # Nutrition & Education
        'active_meal_plans': active_meal_plans,
        'nutrition_programs': nutrition_programs,
        'education_materials': education_materials,
        # Orders & Revenue
        'total_orders_month': total_orders_month,
        'orders_this_week': orders_this_week,
        'total_revenue_month': total_revenue_month,
        # Staff
        'medical_staff_count': medical_staff_count,
        'nutritionist_count': nutritionist_count,
        'kitchen_staff_count': kitchen_staff_count,
        'delivery_staff_count': delivery_staff_count,
        # Wards
        'wards': wards,
        # Recent Activity
        'recent_admissions': recent_admissions,
    }
    
    return render(request, 'hospital_wards/hospital_manager_dashboard.html', context)


@login_required
@require_hospital_manager
def staff_management_dashboard(request):
    """
    Manage hospital staff and their assignments
    """
    # Get all staff members by role
    medical_staff = Profile.objects.filter(
        role=UserRole.MEDICAL_STAFF,
        is_active=True
    ).select_related('user')
    
    nutritionists = Profile.objects.filter(
        role=UserRole.NUTRITIONIST,
        is_active=True
    ).select_related('user')
    
    kitchen_staff = Profile.objects.filter(
        role__in=[UserRole.CHEF, UserRole.KITCHEN_STAFF],
        is_active=True
    ).select_related('user')
    
    delivery_staff = Profile.objects.filter(
        role=UserRole.DELIVERY_PERSON,
        is_active=True
    ).select_related('user')
    
    support_staff = Profile.objects.filter(
        role=UserRole.SUPPORT_STAFF,
        is_active=True
    ).select_related('user')
    
    context = {
        'title': 'Staff Management',
        'medical_staff': medical_staff,
        'nutritionists': nutritionists,
        'kitchen_staff': kitchen_staff,
        'delivery_staff': delivery_staff,
        'support_staff': support_staff,
        'total_staff': (
            medical_staff.count() + nutritionists.count() +
            kitchen_staff.count() + delivery_staff.count() + support_staff.count()
        ),
    }
    
    return render(request, 'hospital_wards/staff_management_dashboard.html', context)


@login_required
@require_hospital_manager
def nutrition_program_dashboard(request):
    """
    Manage nutrition programs and meal planning
    """
    # Get active meal plans
    meal_plans = MealPlan.objects.filter(is_active=True).select_related(
        'nutritionist', 'client'
    ).annotate(
        assigned_patients=Count('id')
    )
    
    # Get nutrition programs
    nutrition_programs = MealNutritionInfo.objects.filter(is_active=True)
    
    # Get education content
    education_content = PatientEducationContent.objects.filter(is_active=True)
    
    # Get nutrition statistics
    total_clients = MealPlan.objects.filter(is_active=True).values('client').distinct().count()
    
    context = {
        'title': 'Nutrition Program Management',
        'meal_plans': meal_plans,
        'nutrition_programs': nutrition_programs,
        'education_content': education_content,
        'total_clients': total_clients,
        'active_nutritionists': Profile.objects.filter(
            role=UserRole.NUTRITIONIST,
            is_active=True
        ).count(),
    }
    
    return render(request, 'hospital_wards/nutrition_program_dashboard.html', context)


@login_required
@require_hospital_manager
def hospital_analytics(request):
    """
    Comprehensive hospital analytics and reporting
    """
    today = timezone.now()
    month_ago = today - timedelta(days=30)
    quarter_ago = today - timedelta(days=90)
    
    # Time-based statistics
    admissions_by_day = PatientAdmission.objects.filter(
        admission_date__gte=month_ago
    ).values('admission_date__date').annotate(count=Count('id')).order_by('admission_date__date')
    
    orders_by_day = Order.objects.filter(
        created_at__gte=month_ago
    ).values('created_at__date').annotate(count=Count('id')).order_by('created_at__date')
    
    revenue_by_day = Payment.objects.filter(
        paid_at__gte=month_ago,
        status='completed'
    ).values('paid_at__date').annotate(total=Sum('amount')).order_by('paid_at__date')
    
    # Performance metrics
    avg_occupancy = WardBed.objects.filter(
        ward__is_active=True
    ).aggregate(
        occupancy=Count('id', filter=Q(status='occupied')) * 100.0 / Count('id')
    )['occupancy'] or 0
    
    # Ward-wise statistics
    ward_performance = Ward.objects.filter(is_active=True).annotate(
        occupancy_rate=(
            Count('beds', filter=Q(beds__status='occupied')) * 100.0 /
            Count('beds')
        ),
        total_patients=Count('beds', filter=Q(beds__patient__isnull=False))
    )
    
    context = {
        'title': 'Hospital Analytics',
        'admissions_by_day': list(admissions_by_day),
        'orders_by_day': list(orders_by_day),
        'revenue_by_day': list(revenue_by_day),
        'avg_occupancy': avg_occupancy,
        'ward_performance': ward_performance,
    }
    
    return render(request, 'hospital_wards/hospital_analytics.html', context)
