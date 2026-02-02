"""
Hospital Ward Management Views
Handles ward/bed management, delivery scheduling, patient education, and caregiver notifications
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.decorators.http import require_http_methods, require_POST
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count
from django.utils import timezone
from django.contrib import messages
from django.db import transaction
from datetime import datetime, timedelta
import csv
import io

from .models import (
    Ward, WardBed, WardDeliveryRoute, WardAvailability,
    MealNutritionInfo, DeliveryScheduleSlot,
    PatientEducationCategory, PatientEducationContent, PatientEducationProgress,
    CaregiverNotification, PatientAdmission, PatientDischarge, PatientTransfer,
    BulkOperation, PatientNotification, NotificationTemplate
)
from .forms import (
    BulkPatientImportForm, BulkPatientAssignmentForm, BulkDischargeForm,
    ExportReportForm, FilterBulkOperationForm
)
from .notification_views import (
    send_admission_notification, send_discharge_notification,
    send_transfer_notification, send_bed_status_notification,
    get_or_create_templates, setup_notification_signals
)
from orders.models import Order


# ==================== WARD MANAGEMENT VIEWS ====================

@login_required
def ward_list(request):
    """Display list of all wards"""
    wards = Ward.objects.filter(is_active=True).annotate(
        available_beds=Count('beds', filter=Q(beds__status='available')),
        occupied_beds=Count('beds', filter=Q(beds__status='occupied'))
    )
    
    context = {
        'wards': wards,
        'total_wards': wards.count(),
        'total_capacity': sum(w.capacity for w in wards),
    }
    return render(request, 'hospital_wards/ward_list.html', context)


@login_required
def ward_detail(request, ward_id):
    """Display ward details including beds and delivery routes"""
    ward = get_object_or_404(Ward, id=ward_id, is_active=True)
    beds = ward.beds.filter(is_active=True).select_related('patient')
    delivery_routes = ward.delivery_routes.filter(is_active=True)
    
    context = {
        'ward': ward,
        'beds': beds,
        'available_beds': beds.filter(status='available'),
        'occupied_beds': beds.filter(status='occupied'),
        'delivery_routes': delivery_routes,
        'availability': ward.availability,
    }
    return render(request, 'hospital_wards/ward_detail.html', context)


@login_required
def ward_bed_detail(request, bed_id):
    """Display individual bed details"""
    bed = get_object_or_404(WardBed, id=bed_id, is_active=True)
    
    # Get related orders if patient is assigned
    orders = None
    if bed.patient:
        orders = Order.objects.filter(user=bed.patient).order_by('-created_at')[:10]
    
    context = {
        'bed': bed,
        'orders': orders,
    }
    return render(request, 'hospital_wards/bed_detail.html', context)


# ==================== DELIVERY SCHEDULING VIEWS ====================

@login_required
def delivery_schedule(request, ward_id=None):
    """Display and manage delivery schedules"""
    ward = None
    slots = DeliveryScheduleSlot.objects.select_related('ward').order_by('date', 'start_time')
    
    if ward_id:
        ward = get_object_or_404(Ward, id=ward_id, is_active=True)
        slots = slots.filter(ward=ward)
    
    # Filter by date range if provided
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if date_from:
        slots = slots.filter(date__gte=date_from)
    if date_to:
        slots = slots.filter(date__lte=date_to)
    
    context = {
        'ward': ward,
        'slots': slots,
        'wards': Ward.objects.filter(is_active=True),
        'today': timezone.now().date(),
    }
    return render(request, 'hospital_wards/delivery_schedule.html', context)


@login_required
@require_http_methods(["POST"])
def book_delivery_slot(request, slot_id):
    """Book a delivery slot"""
    slot = get_object_or_404(DeliveryScheduleSlot, id=slot_id)
    
    try:
        if not slot.has_availability():
            return JsonResponse({'error': 'Slot is fully booked'}, status=400)
        
        slot.book_slot()
        return JsonResponse({
            'success': True,
            'message': 'Slot booked successfully',
            'current_bookings': slot.current_bookings
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# ==================== PATIENT EDUCATION VIEWS ====================

@login_required
def education_hub(request):
    """Patient education hub"""
    categories = PatientEducationCategory.objects.filter(is_active=True).prefetch_related('contents')
    contents = PatientEducationContent.objects.filter(is_published=True).select_related('category', 'author')
    
    # Filter by category if provided
    category_id = request.GET.get('category')
    if category_id:
        contents = contents.filter(category_id=category_id)
    
    # Filter by diet type if provided
    diet_type = request.GET.get('diet_type')
    if diet_type:
        contents = contents.filter(applicable_diet_types__icontains=diet_type)
    
    # Get user's progress
    user_progress = {}
    if request.user.is_authenticated:
        progress_objs = PatientEducationProgress.objects.filter(patient=request.user)
        user_progress = {p.content_id: p for p in progress_objs}
    
    context = {
        'categories': categories,
        'contents': contents,
        'selected_category': category_id,
        'selected_diet': diet_type,
        'user_progress': user_progress,
    }
    return render(request, 'hospital_wards/education_hub.html', context)


@login_required
def education_content_detail(request, content_id):
    """Display education content detail"""
    content = get_object_or_404(PatientEducationContent, id=content_id, is_published=True)
    
    # Track progress
    progress, created = PatientEducationProgress.objects.get_or_create(
        patient=request.user,
        content=content
    )
    
    if not created:
        progress.last_accessed = timezone.now()
        progress.view_count += 1
    
    progress.save()
    
    # Get related contents in same category
    related_contents = PatientEducationContent.objects.filter(
        category=content.category,
        is_published=True
    ).exclude(id=content_id)[:5]
    
    context = {
        'content': content,
        'progress': progress,
        'related_contents': related_contents,
    }
    return render(request, 'hospital_wards/education_detail.html', context)


@login_required
@require_http_methods(["POST"])
def mark_education_complete(request, content_id):
    """Mark education content as completed"""
    content = get_object_or_404(PatientEducationContent, id=content_id)
    
    try:
        progress, _ = PatientEducationProgress.objects.get_or_create(
            patient=request.user,
            content=content
        )
        progress.completed = True
        progress.completion_date = timezone.now()
        progress.save()
        
        return JsonResponse({'success': True, 'message': 'Content marked as complete'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# ==================== NUTRITION INFORMATION VIEWS ====================

@login_required
def nutrition_info(request):
    """Display nutrition information for meals"""
    nutrition_items = MealNutritionInfo.objects.select_related('menu_item').order_by('menu_item__name')
    
    # Filter by allergen if provided
    allergen = request.GET.get('allergen')
    if allergen:
        # Map allergen to field
        allergen_field_map = {
            'gluten': 'contains_gluten',
            'dairy': 'contains_dairy',
            'nuts': 'contains_nuts',
            'shellfish': 'contains_shellfish',
            'eggs': 'contains_eggs',
            'soy': 'contains_soy',
        }
        field = allergen_field_map.get(allergen.lower())
        if field:
            nutrition_items = nutrition_items.filter(**{field: True})
    
    # Filter by diet type if provided
    diet_type = request.GET.get('diet_type')
    if diet_type:
        nutrition_items = nutrition_items.filter(suitable_for_diets__icontains=diet_type)
    
    context = {
        'nutrition_items': nutrition_items,
        'selected_allergen': allergen,
        'selected_diet': diet_type,
    }
    return render(request, 'hospital_wards/nutrition_info.html', context)


@login_required
def meal_detail(request, nutrition_id):
    """Display detailed nutrition information for a meal"""
    nutrition = get_object_or_404(MealNutritionInfo, id=nutrition_id)
    
    context = {
        'nutrition': nutrition,
        'menu_item': nutrition.menu_item,
        'allergens': nutrition.get_allergen_list(),
    }
    return render(request, 'hospital_wards/meal_detail.html', context)


# ==================== CAREGIVER NOTIFICATION VIEWS ====================

@login_required
def caregiver_notifications(request):
    """Display caregiver notifications"""
    notifications = CaregiverNotification.objects.filter(
        caregiver=request.user
    ).select_related('patient', 'related_order', 'related_education').order_by('-created_at')
    
    # Filter by read status if provided
    read_status = request.GET.get('read')
    if read_status == 'unread':
        notifications = notifications.filter(is_read=False)
    elif read_status == 'read':
        notifications = notifications.filter(is_read=True)
    
    # Count unread
    unread_count = notifications.filter(is_read=False).count()
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count,
        'read_status': read_status,
    }
    return render(request, 'hospital_wards/caregiver_notifications.html', context)


@login_required
@require_http_methods(["POST"])
def mark_notification_read(request, notification_id):
    """Mark notification as read"""
    notification = get_object_or_404(CaregiverNotification, id=notification_id, caregiver=request.user)
    
    try:
        notification.mark_as_read()
        return JsonResponse({'success': True, 'message': 'Notification marked as read'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def delete_notification(request, notification_id):
    """Delete a notification"""
    notification = get_object_or_404(CaregiverNotification, id=notification_id, caregiver=request.user)
    
    try:
        notification.delete()
        return JsonResponse({'success': True, 'message': 'Notification deleted'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def notification_detail(request, notification_id):
    """Display full notification detail"""
    notification = get_object_or_404(CaregiverNotification, id=notification_id, caregiver=request.user)
    
    # Mark as read
    if not notification.is_read:
        notification.mark_as_read()
    
    # Get stats for sidebar
    unread_count = CaregiverNotification.objects.filter(caregiver=request.user, is_read=False).count()
    today_count = CaregiverNotification.objects.filter(
        caregiver=request.user,
        created_at__date=timezone.now().date()
    ).count()
    week_count = CaregiverNotification.objects.filter(
        caregiver=request.user,
        created_at__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    context = {
        'notification': notification,
        'unread_count': unread_count,
        'today_count': today_count,
        'week_count': week_count,
    }
    return render(request, 'hospital_wards/notification_detail.html', context)


# ==================== DASHBOARD VIEWS ====================

def _require_role(*allowed_roles):
    """Decorator to check user role"""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.profile.role not in allowed_roles:
                messages.error(request, 'You do not have access to this dashboard.')
                return redirect('hospital_wards:dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


@login_required
def hospital_dashboard(request):
    """Main hospital dashboard - redirects based on user role"""
    user_role = request.user.profile.role
    
    # Route to appropriate dashboard
    dashboard_routes = {
        'patient': 'hospital_wards:patient_dashboard',
        'caregiver': 'hospital_wards:caregiver_dashboard',
        'nutritionist': 'hospital_wards:nutritionist_dashboard',
        'medical_staff': 'hospital_wards:medical_staff_dashboard',
        'chef': 'hospital_wards:chef_dashboard',
        'kitchen_staff': 'hospital_wards:kitchen_staff_dashboard',
        'delivery_person': 'hospital_wards:delivery_person_dashboard',
        'support_staff': 'hospital_wards:support_staff_dashboard',
        'hospital_manager': 'hospital_wards:hospital_manager_dashboard',
        'admin': 'hospital_wards:admin_dashboard',
    }
    
    target_dashboard = dashboard_routes.get(user_role, 'hospital_wards:patient_dashboard')
    return redirect(target_dashboard)


# ==================== PATIENT DASHBOARD ====================
@login_required
@_require_role('patient')
def patient_dashboard(request):
    """Patient personal dashboard"""
    user_patient = getattr(request.user, 'patient_profile', None)
    
    context = {
        'current_bed': user_patient.bed if user_patient else None,
        'current_ward': user_patient.bed.ward if user_patient and user_patient.bed else None,
        'pending_orders': Order.objects.filter(user=request.user, status='pending').order_by('-created_at') if user_patient else [],
        'unread_notifications': CaregiverNotification.objects.filter(patient=user_patient, is_read=False).count() if user_patient else 0,
        'education_progress': 0,
        'education_by_category': {},
    }
    return render(request, 'hospital_wards/dashboards/patient_dashboard.html', context)


# ==================== CAREGIVER DASHBOARD ====================
@login_required
@_require_role('caregiver')
def caregiver_dashboard(request):
    """Caregiver monitoring dashboard"""
    user_caregiver = getattr(request.user, 'caregiver_profile', None)
    assigned_patients = []
    
    if user_caregiver:
        assigned_patients = getattr(user_caregiver, 'assigned_patients', [])
    
    context = {
        'assigned_patients': assigned_patients,
        'recent_notifications': CaregiverNotification.objects.filter(caregiver=request.user).order_by('-created_at')[:5],
        'total_pending_orders': Order.objects.filter(status='pending').count(),
        'total_unread': CaregiverNotification.objects.filter(caregiver=request.user, is_read=False).count(),
        'care_duration': 0,
    }
    return render(request, 'hospital_wards/dashboards/caregiver_dashboard.html', context)


# ==================== NUTRITIONIST DASHBOARD ====================
@login_required
@_require_role('nutritionist')
def nutritionist_dashboard(request):
    """Nutritionist meal planning dashboard"""
    context = {
        'active_patients': Order.objects.filter(status='pending').values('user').distinct().count(),
        'special_diet_count': MealNutritionInfo.objects.filter(suitable_for_diets__isnull=False).count(),
        'allergen_alerts': 0,
        'todays_orders': Order.objects.filter(created_at__date=timezone.now().date()).count(),
        'nutrition_meals': MealNutritionInfo.objects.all()[:5],
        'dietary_requirements': [],
        'patient_nutrition': [],
    }
    return render(request, 'hospital_wards/dashboards/nutritionist_dashboard.html', context)


# ==================== MEDICAL STAFF DASHBOARD ====================
@login_required
@_require_role('medical_staff')
def medical_staff_dashboard(request):
    """Medical staff patient health tracking dashboard with real patient-bed data"""
    from django.db.models import Count, Q
    
    # Get all active wards with related beds and patients
    wards = Ward.objects.filter(is_active=True).prefetch_related(
        'beds__patient__profile'
    ).annotate(
        occupied_count=Count('beds', filter=Q(beds__status='occupied')),
        available_count=Count('beds', filter=Q(beds__status='available')),
    )
    
    # Get all occupied beds with patient details
    occupied_beds = WardBed.objects.filter(
        status='occupied',
        is_active=True
    ).select_related('patient__profile', 'ward').order_by('ward__name', 'bed_number')
    
    # Calculate statistics
    total_beds = WardBed.objects.filter(is_active=True).count()
    total_occupied = occupied_beds.count()
    total_available = WardBed.objects.filter(status='available', is_active=True).count()
    occupancy_rate = (total_occupied / total_beds * 100) if total_beds > 0 else 0
    
    # Get patients with recent admissions
    recent_admissions = occupied_beds.order_by('-assigned_at')[:5]
    
    # Get education statistics
    education_contents = PatientEducationContent.objects.filter(is_active=True)[:8]
    education_count = education_contents.count()
    
    # Get notifications for patients
    notifications = CaregiverNotification.objects.filter(
        is_read=False,
        notification_type__in=['alert', 'reminder']
    ).select_related('patient').order_by('-sent_at')[:5]
    
    # Prepare patient-bed assignment details
    patient_assignments = []
    for bed in occupied_beds[:20]:  # Show first 20 assignments
        duration = timezone.now() - bed.assigned_at if bed.assigned_at else None
        patient_assignments.append({
            'patient_id': bed.patient.id,
            'patient_name': bed.patient.get_full_name(),
            'bed_id': bed.id,
            'bed_number': bed.bed_number,
            'ward': bed.ward.name,
            'assigned_at': bed.assigned_at,
            'duration': duration,
            'phone': bed.patient.profile.phone if hasattr(bed.patient, 'profile') else '',
            'notes': bed.notes,
        })
    
    context = {
        # Statistics
        'occupied_beds': total_occupied,
        'total_beds': total_beds,
        'available_beds': total_available,
        'occupancy_rate': round(occupancy_rate, 1),
        'patient_alerts': notifications.count(),
        
        # Ward data
        'wards': wards,
        'ward_capacity': 65,
        
        # Patient assignments
        'patient_assignments': patient_assignments,
        'recent_admissions': recent_admissions,
        'total_patients_in_care': total_occupied,
        
        # Notifications and alerts
        'health_alerts': notifications,
        'unread_alerts_count': notifications.count(),
        
        # Education tracking
        'education_contents': education_contents,
        'education_count': education_count,
        'avg_learning_progress': 65,  # Placeholder
        'content_completion_rate': 72,  # Placeholder
        'patient_engagement_rate': 78,  # Placeholder
    }
    return render(request, 'hospital_wards/dashboards/medical_staff_dashboard.html', context)


# ==================== CHEF DASHBOARD ====================
@login_required
@_require_role('chef')
def chef_dashboard(request):
    """Chef meal preparation dashboard"""
    todays_orders = Order.objects.filter(created_at__date=timezone.now().date()).count()
    
    context = {
        'todays_orders': todays_orders,
        'pending_items': Order.objects.filter(status='pending').count(),
        'special_requests': 0,
        'completed_today': Order.objects.filter(updated_at__date=timezone.now().date(), status='completed').count(),
        'meal_queue': Order.objects.filter(status='pending').order_by('created_at')[:8],
        'dietary_restrictions': [],
        'nutrition_details': MealNutritionInfo.objects.all()[:6],
        'weekly_schedule': [],
    }
    return render(request, 'hospital_wards/dashboards/chef_dashboard.html', context)


# ==================== KITCHEN STAFF DASHBOARD ====================
@login_required
@_require_role('kitchen_staff')
def kitchen_staff_dashboard(request):
    """Kitchen staff order processing dashboard"""
    context = {
        'current_orders': Order.objects.filter(status='in_progress').count(),
        'queue_items': Order.objects.filter(status='pending').count(),
        'ready_count': Order.objects.filter(status='ready').count(),
        'avg_wait_time': 15,
        'active_orders': Order.objects.filter(status='in_progress').order_by('created_at')[:5],
        'pending_queue': Order.objects.filter(status='pending').order_by('created_at')[:5],
        'prep_tasks': [],
        'delivery_routes': WardDeliveryRoute.objects.all()[:5],
    }
    return render(request, 'hospital_wards/dashboards/kitchen_staff_dashboard.html', context)


# ==================== DELIVERY PERSON DASHBOARD ====================
@login_required
@_require_role('delivery_person')
def delivery_person_dashboard(request):
    """Delivery person route management dashboard"""
    context = {
        'total_routes': WardDeliveryRoute.objects.filter(is_active=True).count(),
        'completed_deliveries': Order.objects.filter(status='delivered').count(),
        'pending_deliveries': Order.objects.filter(status='in_transit').count(),
        'total_distance': 25,
        'delivery_routes': WardDeliveryRoute.objects.filter(is_active=True)[:3],
        'current_route_orders': Order.objects.filter(status='in_transit')[:5],
        'on_time_percent': 95,
        'avg_delivery_time': 20,
        'customer_rating': 4.8,
        'efficiency_score': 92,
        'delivery_time': '4h 30m',
        'shift_start_time': timezone.now().time(),
        'delivery_issues': [],
    }
    return render(request, 'hospital_wards/dashboards/delivery_person_dashboard.html', context)


# ==================== SUPPORT STAFF DASHBOARD ====================
@login_required
@_require_role('support_staff')
def support_staff_dashboard(request):
    """Support staff ward management dashboard"""
    wards = Ward.objects.filter(is_active=True)
    beds = WardBed.objects.filter(is_active=True).select_related('ward', 'patient')
    
    # Get active admissions (patients currently in hospital)
    active_admissions = PatientAdmission.objects.filter(
        is_active=True
    ).select_related('patient', 'bed', 'admitted_by').order_by('-admission_date')[:10]
    
    # Get pending discharges (patients ready to leave)
    pending_discharges = PatientAdmission.objects.filter(
        is_active=True,
        bed__status='occupied'
    ).select_related('patient', 'bed').order_by('admission_date')[:5]
    
    # Get bed status summary
    bed_status_summary = {
        'occupied': beds.filter(status='occupied').count(),
        'available': beds.filter(status='available').count(),
        'maintenance': beds.filter(status='maintenance').count(),
        'reserved': beds.filter(status='reserved').count(),
    }
    
    context = {
        'active_beds': bed_status_summary['occupied'],
        'available_beds': bed_status_summary['available'],
        'maintenance_beds': bed_status_summary['maintenance'],
        'support_requests': pending_discharges.count(),
        'ward_beds': beds[:8],
        'active_admissions': active_admissions,
        'pending_discharges': pending_discharges,
        'bed_assignments': beds.filter(patient__isnull=False)[:8],
        'ward_summary': wards,
        'bed_status_summary': bed_status_summary,
    }
    return render(request, 'hospital_wards/dashboards/support_staff_dashboard.html', context)


# ==================== HOSPITAL MANAGER DASHBOARD ====================
@login_required
@_require_role('hospital_manager')
def hospital_manager_dashboard(request):
    """Hospital manager analytics and oversight dashboard"""
    wards = Ward.objects.filter(is_active=True)
    total_beds = sum(w.capacity for w in wards)
    occupied_beds = sum(w.beds.filter(status='occupied').count() for w in wards)
    
    context = {
        'total_patients': Order.objects.values('user').distinct().count(),
        'bed_occupancy': int((occupied_beds / total_beds * 100) if total_beds > 0 else 0),
        'todays_revenue': 150000,
        'total_staff': User.objects.filter(profile__is_active=True).count(),
        'wards': wards,
        'staff_distribution': [],
        'service_efficiency': 88,
        'patient_satisfaction': 92,
        'orders_today': Order.objects.filter(created_at__date=timezone.now().date()).count(),
        'orders_weekly_avg': 120,
        'orders_monthly_avg': 500,
        'ontime_today': 94,
        'ontime_weekly': 91,
        'ontime_monthly': 89,
        'checkins_today': 45,
        'checkins_weekly_avg': 40,
        'checkins_monthly_avg': 35,
        'monthly_revenue': 3500000,
        'avg_order_value': 25000,
        'api_response_time': 145,
        'active_users': User.objects.filter(profile__is_active=True, last_login__gte=timezone.now() - timedelta(hours=1)).count(),
        'recent_activities': [],
    }
    return render(request, 'hospital_wards/dashboards/hospital_manager_dashboard.html', context)


# ==================== ADMIN DASHBOARD ====================
@login_required
@_require_role('admin')
def admin_dashboard(request):
    """System administrator dashboard"""
    from accounts.models import Profile
    
    all_users = User.objects.select_related('profile')
    all_profiles = Profile.objects.all()
    
    context = {
        'total_users': all_users.count(),
        'active_sessions': User.objects.filter(profile__is_active=True).count(),
        'api_calls_24h': 5420,
        'system_uptime': '99.9%',
        'users': all_users[:8],
        'role_distribution': [],
        'total_orders': Order.objects.count(),
        'total_patients': all_profiles.filter(role='patient').count(),
        'total_logs': 1250,
        'users_size': '15MB',
        'orders_size': '8MB',
        'patients_size': '5MB',
        'logs_size': '22MB',
        'recent_logs': [],
    }
    return render(request, 'hospital_wards/dashboards/admin_dashboard.html', context)


# ==================== AJAX ENDPOINTS ====================

@login_required
@require_http_methods(["POST"])
def mark_meal_complete(request, meal_id):
    """Mark meal as complete (Chef)"""
    try:
        order = get_object_or_404(Order, id=meal_id)
        order.status = 'completed'
        order.updated_at = timezone.now()
        order.save()
        return JsonResponse({'success': True, 'message': 'Meal marked complete'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def update_order_status(request, order_id):
    """Update order status (Kitchen Staff)"""
    try:
        order = get_object_or_404(Order, id=order_id)
        status = request.POST.get('status', 'pending')
        order.status = status
        order.updated_at = timezone.now()
        order.save()
        return JsonResponse({'success': True, 'message': f'Order updated to {status}'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def start_delivery_route(request, route_id):
    """Start a delivery route (Delivery Person)"""
    try:
        route = get_object_or_404(WardDeliveryRoute, id=route_id)
        # Update route status
        return JsonResponse({'success': True, 'message': 'Route started'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def mark_order_delivered(request, order_id):
    """Mark order as delivered (Delivery Person)"""
    try:
        order = get_object_or_404(Order, id=order_id)
        order.status = 'delivered'
        order.updated_at = timezone.now()
        order.save()
        return JsonResponse({'success': True, 'message': 'Order marked as delivered'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def discharge_bed(request, bed_id):
    """Discharge patient from bed (Support Staff)"""
    try:
        bed = get_object_or_404(WardBed, id=bed_id)
        bed.patient = None
        bed.status = 'available'
        bed.save()
        return JsonResponse({'success': True, 'message': 'Patient discharged'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def deactivate_user(request, user_id):
    """Deactivate a user (Admin only)"""
    if request.user.profile.role != 'admin':
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        user = get_object_or_404(User, id=user_id)
        user.profile.is_active = False
        user.profile.save()
        user.is_active = False
        user.save()
        return JsonResponse({'success': True, 'message': 'User deactivated'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# ============================================================================
# PATIENT ADMISSION & DISCHARGE WORKFLOW VIEWS
# ============================================================================

@login_required
@_require_role('support_staff', 'hospital_manager', 'admin')
def patient_admission(request):
    """Admit a patient and assign to a bed"""
    from .models import PatientAdmission
    
    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        bed_id = request.POST.get('bed_id')
        reason = request.POST.get('reason', 'routine')
        chief_complaint = request.POST.get('chief_complaint', '')
        allergies = request.POST.get('allergies', '')
        current_medications = request.POST.get('current_medications', '')
        
        try:
            patient = get_object_or_404(User, id=patient_id)
            bed = get_object_or_404(WardBed, id=bed_id, status='available')
            
            # Assign patient to bed
            bed.assign_patient(patient)
            
            # Create admission record
            admission = PatientAdmission.objects.create(
                patient=patient,
                bed=bed,
                admitted_by=request.user,
                reason=reason,
                chief_complaint=chief_complaint,
                allergies=allergies,
                current_medications=current_medications,
            )
            
            # Send admission notifications
            send_admission_notification(admission)
            
            # Create notification for medical staff
            CaregiverNotification.objects.create(
                patient=patient,
                title=f'New Patient Admitted',
                message=f'{patient.get_full_name()} admitted to {bed.bed_number}',
                notification_type='alert',
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Patient {patient.get_full_name()} admitted to bed {bed.bed_number}',
                'admission_id': admission.id
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    # GET: Show admission form
    patients = User.objects.filter(profile__role='patient', is_active=True)
    beds = WardBed.objects.filter(status='available', is_active=True).select_related('ward')
    
    context = {
        'patients': patients,
        'beds': beds,
        'admission_reasons': PatientAdmission._meta.get_field('reason').choices,
    }
    return render(request, 'hospital_wards/admission_form.html', context)


@login_required
@_require_role('support_staff', 'hospital_manager', 'admin')
def patient_discharge(request, admission_id):
    """Discharge a patient from hospital"""
    from .models import PatientAdmission, PatientDischarge
    
    admission = get_object_or_404(PatientAdmission, id=admission_id, is_active=True)
    
    if request.method == 'POST':
        discharge_status = request.POST.get('discharge_status', 'discharged')
        discharge_notes = request.POST.get('discharge_notes', '')
        follow_up_instructions = request.POST.get('follow_up_instructions', '')
        medications_prescribed = request.POST.get('medications_prescribed', '')
        restrictions = request.POST.get('restrictions', '')
        return_visit_date = request.POST.get('return_visit_date', None)
        
        try:
            # Release bed
            bed = admission.bed
            if bed:
                bed.release_patient()
            
            # Create discharge record
            discharge = PatientDischarge.objects.create(
                admission=admission,
                discharge_status=discharge_status,
                discharged_by=request.user,
                discharge_notes=discharge_notes,
                follow_up_instructions=follow_up_instructions,
                medications_prescribed=medications_prescribed,
                restrictions=restrictions,
                return_visit_date=return_visit_date if return_visit_date else None,
            )
            
            admission.is_active = False
            admission.save()
            
            # Send discharge notifications
            send_discharge_notification(discharge)
            
            # Create notification
            CaregiverNotification.objects.create(
                patient=admission.patient,
                title='Patient Discharge',
                message=f'Patient discharged: {discharge_status}',
                notification_type='info',
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Patient {admission.patient.get_full_name()} discharged',
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    # GET: Show discharge form
    context = {
        'admission': admission,
        'discharge_statuses': PatientDischarge._meta.get_field('discharge_status').choices,
    }
    return render(request, 'hospital_wards/discharge_form.html', context)


@login_required
@_require_role('support_staff', 'hospital_manager')
def transfer_patient_bed(request):
    """Transfer patient between beds"""
    from .models import PatientTransfer
    
    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        from_bed_id = request.POST.get('from_bed_id')
        to_bed_id = request.POST.get('to_bed_id')
        reason = request.POST.get('reason', '')
        
        try:
            patient = get_object_or_404(User, id=patient_id)
            from_bed = get_object_or_404(WardBed, id=from_bed_id, patient=patient)
            to_bed = get_object_or_404(WardBed, id=to_bed_id, status='available')
            
            # Release from old bed
            from_bed.release_patient()
            
            # Assign to new bed
            to_bed.assign_patient(patient)
            
            # Create transfer record
            transfer = PatientTransfer.objects.create(
                patient=patient,
                from_bed=from_bed,
                to_bed=to_bed,
                transferred_by=request.user,
                reason=reason,
            )
            
            # Send transfer notifications
            send_transfer_notification(transfer)
            
            # Create notification
            CaregiverNotification.objects.create(
                patient=patient,
                title='Bed Transfer',
                message=f'Transferred from {from_bed.bed_number} to {to_bed.bed_number}',
                notification_type='info',
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Patient transferred to {to_bed.bed_number}',
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    # GET: Show transfer form
    patients = User.objects.filter(
        hospital_bed__status='occupied',
        profile__role='patient',
        is_active=True
    ).distinct()
    available_beds = WardBed.objects.filter(status='available', is_active=True).select_related('ward')
    
    context = {
        'patients': patients,
        'available_beds': available_beds,
    }
    return render(request, 'hospital_wards/transfer_form.html', context)


@login_required
@_require_role('hospital_manager', 'admin')
def occupancy_report(request):
    """View bed occupancy statistics and reports"""
    from django.db.models import Count, Q
    
    wards = Ward.objects.filter(is_active=True).prefetch_related('beds').annotate(
        total_beds=Count('beds'),
        occupied_beds=Count('beds', filter=Q(beds__status='occupied')),
        available_beds=Count('beds', filter=Q(beds__status='available')),
        maintenance_beds=Count('beds', filter=Q(beds__status='maintenance')),
    )
    
    # Calculate overall statistics
    total_beds = WardBed.objects.filter(is_active=True).count()
    occupied_beds = WardBed.objects.filter(status='occupied', is_active=True).count()
    occupancy_rate = (occupied_beds / total_beds * 100) if total_beds > 0 else 0
    
    # Get recent admissions
    recent_admissions = PatientAdmission.objects.filter(
        is_active=True
    ).select_related('patient', 'bed', 'admitted_by').order_by('-admission_date')[:10]
    
    # Get recent discharges
    recent_discharges = PatientDischarge.objects.select_related(
        'admission__patient'
    ).order_by('-discharge_date')[:10]
    
    context = {
        'wards': wards,
        'total_beds': total_beds,
        'occupied_beds': occupied_beds,
        'occupancy_rate': round(occupancy_rate, 1),
        'recent_admissions': recent_admissions,
        'recent_discharges': recent_discharges,
    }
    return render(request, 'hospital_wards/occupancy_report.html', context)


@login_required
def get_patient_current_bed(request, patient_id):
    """AJAX endpoint to get patient's current bed"""
    try:
        patient = get_object_or_404(User, id=patient_id, profile__role='patient')
        bed = WardBed.objects.filter(patient=patient, status='occupied').first()
        
        if bed:
            return JsonResponse({
                'bed_id': bed.id,
                'bed_number': bed.bed_number,
                'ward': bed.ward.name,
            })
        else:
            return JsonResponse({'error': 'Patient not currently in hospital'}, status=404)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Patient not found'}, status=404)


# ==================== BULK OPERATIONS VIEWS ====================

@login_required
def bulk_operations_list(request):
    """Display list of bulk operations"""
    if not (hasattr(request.user, 'profile') and request.user.profile.role in ['hospital_manager', 'admin']):
        messages.error(request, 'You do not have permission to access bulk operations')
        return redirect('home')
    
    operations = BulkOperation.objects.all().order_by('-created_at')
    context = {
        'operations': operations,
    }
    return render(request, 'hospital_wards/bulk_operations_list.html', context)


@login_required
def bulk_discharge_patients(request):
    """Bulk discharge multiple patients"""
    if not (hasattr(request.user, 'profile') and request.user.profile.role in ['hospital_manager', 'admin']):
        messages.error(request, 'You do not have permission to perform bulk operations')
        return redirect('home')
    
    if request.method == 'POST':
        import json
        
        # Handle both JSON and form data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            admission_ids = data.get('admission_ids', [])
        else:
            admission_ids = request.POST.getlist('admission_ids[]')
        
        if not admission_ids:
            return JsonResponse({'success': False, 'error': 'No admissions selected'})
        
        try:
            # Create bulk operation record
            bulk_op = BulkOperation.objects.create(
                operation_type='bulk_discharge',
                status='processing',
                initiated_by=request.user,
                total_records=len(admission_ids),
                started_at=timezone.now()
            )
            
            successful = 0
            failed = 0
            
            # Process each admission
            for admission_id in admission_ids:
                try:
                    admission = PatientAdmission.objects.get(id=admission_id)
                    if admission.is_active:
                        # Create discharge record
                        PatientDischarge.objects.create(
                            admission=admission,
                            discharge_status='discharged'
                        )
                        
                        # Release bed
                        admission.bed.patient = None
                        admission.bed.status = 'available'
                        admission.bed.save()
                        
                        admission.is_active = False
                        admission.save()
                        
                        # Send notification
                        PatientNotification.objects.create(
                            notification_type='discharge',
                            recipient=admission.patient,
                            patient=admission.patient,
                            admission=admission,
                            title='Hospital Discharge',
                            message=f'You have been discharged from {admission.bed.ward.name}',
                            send_email=True,
                            send_in_app=True
                        )
                        
                        successful += 1
                except Exception as e:
                    failed += 1
            
            # Update bulk operation
            bulk_op.status = 'completed'
            bulk_op.successful_records = successful
            bulk_op.failed_records = failed
            bulk_op.completed_at = timezone.now()
            bulk_op.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Successfully discharged {successful} patients',
                'operation_id': bulk_op.id
            })
        
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    # GET request - show form with active admissions
    admissions = PatientAdmission.objects.filter(is_active=True).select_related('patient', 'bed__ward')
    context = {
        'admissions': admissions,
    }
    return render(request, 'hospital_wards/bulk_discharge_form.html', context)


@login_required
def export_patients_csv(request):
    """Export patient data to CSV"""
    if not (hasattr(request.user, 'profile') and request.user.profile.role in ['hospital_manager', 'admin']):
        messages.error(request, 'You do not have permission to export data')
        return redirect('home')
    
    # Get all active admissions
    admissions = PatientAdmission.objects.filter(
        is_active=True
    ).select_related('patient', 'bed__ward').values_list(
        'patient__first_name',
        'patient__last_name',
        'patient__email',
        'bed__bed_number',
        'bed__ward__name',
        'admission_date',
        'reason',
        'chief_complaint'
    )
    
    # Create CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="patients_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'First Name', 'Last Name', 'Email', 'Bed Number', 'Ward',
        'Admission Date', 'Reason', 'Chief Complaint'
    ])
    
    for row in admissions:
        writer.writerow(row)
    
    # Log operation
    BulkOperation.objects.create(
        operation_type='export_patients',
        status='completed',
        initiated_by=request.user,
        total_records=admissions.count(),
        successful_records=admissions.count()
    )
    
    return response


@login_required
def export_occupancy_report_csv(request):
    """Export occupancy report to CSV"""
    if not (hasattr(request.user, 'profile') and request.user.profile.role in ['hospital_manager', 'admin']):
        messages.error(request, 'You do not have permission to export reports')
        return redirect('home')
    
    # Get ward occupancy data
    wards = Ward.objects.annotate(
        total_beds=Count('beds'),
        occupied_beds=Count('beds', filter=Q(beds__status='occupied')),
        available_beds=Count('beds', filter=Q(beds__status='available')),
        maintenance_beds=Count('beds', filter=Q(beds__status='maintenance'))
    )
    
    # Create CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="occupancy_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Ward Name', 'Total Beds', 'Occupied', 'Available', 'Maintenance',
        'Occupancy %'
    ])
    
    for ward in wards:
        occupancy = (ward.occupied_beds / ward.total_beds * 100) if ward.total_beds > 0 else 0
        writer.writerow([
            ward.name,
            ward.total_beds,
            ward.occupied_beds,
            ward.available_beds,
            ward.maintenance_beds,
            f'{occupancy:.1f}%'
        ])
    
    # Log operation
    BulkOperation.objects.create(
        operation_type='export_report',
        status='completed',
        initiated_by=request.user,
        total_records=wards.count(),
        successful_records=wards.count()
    )
    
    return response


# ==================== NOTIFICATION VIEWS ====================

@login_required
def patient_notifications(request):
    """Display patient's notifications with filtering and pagination"""
    from django.core.paginator import Paginator
    
    notifications = PatientNotification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')
    
    # Filter by type
    notification_type = request.GET.get('type', 'all')
    if notification_type != 'all':
        notifications = notifications.filter(notification_type=notification_type)
    
    # Count by type for sidebar
    all_notifications = PatientNotification.objects.filter(recipient=request.user)
    total_count = all_notifications.count()
    unread_count = all_notifications.filter(is_read=False).count()
    admission_count = all_notifications.filter(notification_type='admission').count()
    discharge_count = all_notifications.filter(notification_type='discharge').count()
    transfer_count = all_notifications.filter(notification_type='transfer').count()
    appointment_count = all_notifications.filter(notification_type='appointment').count()
    
    # Pagination
    paginator = Paginator(notifications, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'notifications': page_obj.object_list,
        'unread_count': unread_count,
        'total_count': total_count,
        'admission_count': admission_count,
        'discharge_count': discharge_count,
        'transfer_count': transfer_count,
        'appointment_count': appointment_count,
    }
    return render(request, 'hospital_wards/patient_notifications.html', context)


@login_required
def mark_notification_read(request, notification_id):
    """Mark notification as read"""
    notification = get_object_or_404(PatientNotification, id=notification_id, recipient=request.user)
    notification.mark_as_read()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('patient_notifications')


@login_required
def notification_count(request):
    """Get unread notification count (AJAX)"""
    count = PatientNotification.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()
    
    return JsonResponse({'unread_count': count})


# ==================== BULK OPERATIONS VIEWS ====================

@login_required
@require_http_methods(["GET", "POST"])
def bulk_import_patients(request):
    """Import patients from CSV file"""
    if request.method == 'POST':
        form = BulkPatientImportForm(request.POST, request.FILES)
        if form.is_valid():
            return handle_patient_import(request, form.cleaned_data['csv_file'])
    else:
        form = BulkPatientImportForm()
    
    context = {'form': form}
    return render(request, 'hospital_wards/bulk_import_patients.html', context)


def handle_patient_import(request, csv_file):
    """Process patient import CSV"""
    bulk_op = BulkOperation.objects.create(
        operation_type='import_patients',
        status='processing',
        initiated_by=request.user,
        total_records=0
    )
    
    try:
        decoded = csv_file.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(decoded))
        
        successful = 0
        failed = 0
        errors = []
        
        with transaction.atomic():
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (skip header)
                try:
                    # Validate and create patient
                    patient_id = row.get('patient_id', '').strip()
                    first_name = row.get('first_name', '').strip()
                    last_name = row.get('last_name', '').strip()
                    email = row.get('email', '').strip()
                    phone = row.get('phone', '').strip()
                    date_of_birth = row.get('date_of_birth', '').strip()
                    gender = row.get('gender', '').strip()
                    
                    if not all([first_name, last_name, email]):
                        errors.append(f"Row {row_num}: Missing required fields")
                        failed += 1
                        continue
                    
                    # Check if patient already exists
                    if User.objects.filter(email=email).exists():
                        errors.append(f"Row {row_num}: Patient with email {email} already exists")
                        failed += 1
                        continue
                    
                    # Create patient user account
                    user = User.objects.create_user(
                        username=email.split('@')[0] + str(datetime.now().timestamp()),
                        email=email,
                        first_name=first_name,
                        last_name=last_name
                    )
                    
                    # Create patient record
                    patient = Patient.objects.create(
                        user=user,
                        phone=phone,
                        date_of_birth=date_of_birth if date_of_birth else None,
                        gender=gender if gender in ['M', 'F', 'O'] else 'O'
                    )
                    
                    successful += 1
                
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
                    failed += 1
        
        # Update bulk operation record
        bulk_op.total_records = successful + failed
        bulk_op.successful_records = successful
        bulk_op.failed_records = failed
        bulk_op.status = 'completed' if failed == 0 else 'completed'
        bulk_op.completed_at = timezone.now()
        
        if errors:
            bulk_op.error_message = '\n'.join(errors[:20])  # Store first 20 errors
        
        bulk_op.save()
        
        messages.success(
            request,
            f'Import completed: {successful} patients created, {failed} failed'
        )
    
    except Exception as e:
        bulk_op.status = 'failed'
        bulk_op.error_message = str(e)
        bulk_op.completed_at = timezone.now()
        bulk_op.save()
        messages.error(request, f'Import failed: {str(e)}')
    
    return redirect('hospital_wards:bulk_operations_list')


@login_required
@require_http_methods(["GET", "POST"])
def bulk_assign_patients(request):
    """Bulk assign patients to beds"""
    if request.method == 'POST':
        form = BulkPatientAssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            return handle_bulk_assignment(
                request,
                form.cleaned_data['csv_file'],
                form.cleaned_data.get('send_notifications', False)
            )
    else:
        form = BulkPatientAssignmentForm()
    
    context = {'form': form}
    return render(request, 'hospital_wards/bulk_assign_patients.html', context)


def handle_bulk_assignment(request, csv_file, send_notifications):
    """Process bulk patient assignment CSV"""
    bulk_op = BulkOperation.objects.create(
        operation_type='bulk_assignment',
        status='processing',
        initiated_by=request.user,
        total_records=0
    )
    
    try:
        decoded = csv_file.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(decoded))
        
        successful = 0
        failed = 0
        errors = []
        
        with transaction.atomic():
            for row_num, row in enumerate(reader, start=2):
                try:
                    patient_id = int(row.get('patient_id', 0))
                    bed_id = int(row.get('bed_id', 0))
                    reason = row.get('reason', '').strip()
                    chief_complaint = row.get('chief_complaint', '').strip()
                    
                    if not all([patient_id, bed_id, reason]):
                        errors.append(f"Row {row_num}: Missing required fields")
                        failed += 1
                        continue
                    
                    # Get patient and bed
                    patient = Patient.objects.get(id=patient_id)
                    bed = WardBed.objects.get(id=bed_id, status='available')
                    
                    # Create admission
                    admission = PatientAdmission.objects.create(
                        patient=patient,
                        bed=bed,
                        reason=reason,
                        chief_complaint=chief_complaint
                    )
                    
                    # Update bed status
                    bed.status = 'occupied'
                    bed.current_patient = patient
                    bed.save()
                    
                    successful += 1
                
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
                    failed += 1
        
        bulk_op.total_records = successful + failed
        bulk_op.successful_records = successful
        bulk_op.failed_records = failed
        bulk_op.status = 'completed'
        bulk_op.completed_at = timezone.now()
        
        if errors:
            bulk_op.error_message = '\n'.join(errors[:20])
        
        bulk_op.save()
        
        messages.success(
            request,
            f'Bulk assignment completed: {successful} patients assigned, {failed} failed'
        )
    
    except Exception as e:
        bulk_op.status = 'failed'
        bulk_op.error_message = str(e)
        bulk_op.completed_at = timezone.now()
        bulk_op.save()
        messages.error(request, f'Bulk assignment failed: {str(e)}')
    
    return redirect('hospital_wards:bulk_operations_list')


@login_required
@require_http_methods(["GET", "POST"])
def bulk_discharge(request):
    """Bulk discharge multiple patients"""
    if request.method == 'POST':
        form = BulkDischargeForm(request.POST)
        if form.is_valid():
            return handle_bulk_discharge(
                request,
                form.cleaned_data['admissions'],
                form.cleaned_data.get('discharge_notes', ''),
                form.cleaned_data.get('send_notifications', False)
            )
    else:
        form = BulkDischargeForm()
    
    context = {'form': form}
    return render(request, 'hospital_wards/bulk_discharge.html', context)


def handle_bulk_discharge(request, admissions, discharge_notes, send_notifications):
    """Process bulk discharge"""
    bulk_op = BulkOperation.objects.create(
        operation_type='bulk_discharge',
        status='processing',
        initiated_by=request.user,
        total_records=len(admissions)
    )
    
    try:
        successful = 0
        failed = 0
        
        with transaction.atomic():
            for admission in admissions:
                try:
                    # Create discharge record
                    discharge = PatientDischarge.objects.create(
                        admission=admission,
                        discharge_notes=discharge_notes
                    )
                    
                    # Release bed
                    bed = admission.bed
                    bed.status = 'available'
                    bed.current_patient = None
                    bed.save()
                    
                    # Mark admission as inactive
                    admission.is_active = False
                    admission.save()
                    
                    successful += 1
                
                except Exception as e:
                    failed += 1
        
        bulk_op.successful_records = successful
        bulk_op.failed_records = failed
        bulk_op.status = 'completed'
        bulk_op.completed_at = timezone.now()
        bulk_op.save()
        
        messages.success(
            request,
            f'Bulk discharge completed: {successful} patients discharged, {failed} failed'
        )
    
    except Exception as e:
        bulk_op.status = 'failed'
        bulk_op.error_message = str(e)
        bulk_op.completed_at = timezone.now()
        bulk_op.save()
        messages.error(request, f'Bulk discharge failed: {str(e)}')
    
    return redirect('hospital_wards:bulk_operations_list')


@login_required
@require_http_methods(["GET"])
def export_patients_csv(request):
    """Export patient list to CSV"""
    bulk_op = BulkOperation.objects.create(
        operation_type='export_patients',
        status='processing',
        initiated_by=request.user
    )
    
    try:
        # Get all patients with current admissions
        admissions = PatientAdmission.objects.filter(is_active=True).select_related(
            'patient__user', 'bed__ward'
        )
        
        # Create CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="patients_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Patient ID', 'Name', 'Email', 'Phone', 'Bed', 'Ward', 'Admission Date', 'Reason'])
        
        for admission in admissions:
            writer.writerow([
                admission.patient.id,
                admission.patient.user.get_full_name(),
                admission.patient.user.email,
                admission.patient.phone,
                admission.bed.bed_number,
                admission.bed.ward.name,
                admission.admission_date.strftime('%Y-%m-%d %H:%M'),
                admission.reason,
            ])
        
        bulk_op.total_records = admissions.count()
        bulk_op.successful_records = admissions.count()
        bulk_op.status = 'completed'
        bulk_op.completed_at = timezone.now()
        bulk_op.save()
        
        return response
    
    except Exception as e:
        bulk_op.status = 'failed'
        bulk_op.error_message = str(e)
        bulk_op.completed_at = timezone.now()
        bulk_op.save()
        messages.error(request, f'Export failed: {str(e)}')
        return redirect('hospital_wards:bulk_operations_list')


@login_required
@require_http_methods(["GET", "POST"])
def export_report(request):
    """Generate and export hospital reports"""
    if request.method == 'POST':
        form = ExportReportForm(request.POST)
        if form.is_valid():
            return handle_report_export(request, form.cleaned_data)
    else:
        form = ExportReportForm()
    
    context = {'form': form}
    return render(request, 'hospital_wards/export_report.html', context)


def handle_report_export(request, data):
    """Process report export"""
    report_type = data.get('report_type')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    ward = data.get('ward')
    
    bulk_op = BulkOperation.objects.create(
        operation_type='export_report',
        status='processing',
        initiated_by=request.user
    )
    
    try:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{report_type}_report.csv"'
        writer = csv.writer(response)
        
        if report_type == 'occupancy':
            return export_occupancy_report(writer, ward, bulk_op, response)
        elif report_type == 'patient_list':
            return export_patient_list_report(writer, start_date, end_date, ward, bulk_op, response)
        elif report_type == 'admission_discharge':
            return export_admission_discharge_report(writer, start_date, end_date, ward, bulk_op, response)
        elif report_type == 'bed_utilization':
            return export_bed_utilization_report(writer, start_date, end_date, ward, bulk_op, response)
    
    except Exception as e:
        bulk_op.status = 'failed'
        bulk_op.error_message = str(e)
        bulk_op.completed_at = timezone.now()
        bulk_op.save()
        messages.error(request, f'Report export failed: {str(e)}')
        return redirect('hospital_wards:bulk_operations_list')


def export_occupancy_report(writer, ward_filter, bulk_op, response):
    """Export occupancy report"""
    wards = Ward.objects.filter(is_active=True)
    if ward_filter:
        wards = wards.filter(id=ward_filter.id)
    
    writer.writerow(['Ward', 'Total Beds', 'Occupied', 'Available', 'Maintenance', 'Occupancy %'])
    
    total_occupied = 0
    total_beds = 0
    
    for ward in wards:
        total = ward.beds.count()
        occupied = ward.beds.filter(status='occupied').count()
        available = ward.beds.filter(status='available').count()
        maintenance = ward.beds.filter(status='maintenance').count()
        occupancy_pct = (occupied / total * 100) if total > 0 else 0
        
        writer.writerow([
            ward.name,
            total,
            occupied,
            available,
            maintenance,
            f'{occupancy_pct:.1f}%'
        ])
        
        total_occupied += occupied
        total_beds += total
    
    writer.writerow([])
    writer.writerow(['TOTAL', total_beds, total_occupied, '', '', f'{(total_occupied/total_beds*100):.1f}%' if total_beds > 0 else '0%'])
    
    bulk_op.total_records = wards.count()
    bulk_op.successful_records = wards.count()
    bulk_op.status = 'completed'
    bulk_op.completed_at = timezone.now()
    bulk_op.save()
    
    return response


def export_patient_list_report(writer, start_date, end_date, ward_filter, bulk_op, response):
    """Export patient list report"""
    admissions = PatientAdmission.objects.filter(is_active=True).select_related(
        'patient__user', 'bed__ward'
    )
    
    if ward_filter:
        admissions = admissions.filter(bed__ward=ward_filter)
    
    if start_date:
        admissions = admissions.filter(admission_date__gte=start_date)
    if end_date:
        admissions = admissions.filter(admission_date__lte=end_date)
    
    writer.writerow(['Patient ID', 'Name', 'Email', 'Phone', 'Bed', 'Ward', 'Admission Date', 'Days Admitted', 'Reason'])
    
    for admission in admissions:
        days = (timezone.now().date() - admission.admission_date.date()).days
        writer.writerow([
            admission.patient.id,
            admission.patient.user.get_full_name(),
            admission.patient.user.email,
            admission.patient.phone,
            admission.bed.bed_number,
            admission.bed.ward.name,
            admission.admission_date.strftime('%Y-%m-%d'),
            days,
            admission.reason,
        ])
    
    bulk_op.total_records = admissions.count()
    bulk_op.successful_records = admissions.count()
    bulk_op.status = 'completed'
    bulk_op.completed_at = timezone.now()
    bulk_op.save()
    
    return response


def export_admission_discharge_report(writer, start_date, end_date, ward_filter, bulk_op, response):
    """Export admission/discharge summary"""
    discharges = PatientDischarge.objects.select_related(
        'admission__patient__user', 'admission__bed__ward'
    )
    
    if ward_filter:
        discharges = discharges.filter(admission__bed__ward=ward_filter)
    
    if start_date:
        discharges = discharges.filter(created_at__gte=start_date)
    if end_date:
        discharges = discharges.filter(created_at__lte=end_date)
    
    writer.writerow(['Date', 'Patient', 'Ward', 'Admission Date', 'Discharge Date', 'Days Admitted', 'Status'])
    
    for discharge in discharges:
        days = (discharge.created_at.date() - discharge.admission.admission_date.date()).days
        writer.writerow([
            discharge.created_at.strftime('%Y-%m-%d'),
            discharge.admission.patient.user.get_full_name(),
            discharge.admission.bed.ward.name,
            discharge.admission.admission_date.strftime('%Y-%m-%d'),
            discharge.created_at.strftime('%Y-%m-%d'),
            days,
            discharge.discharge_status,
        ])
    
    bulk_op.total_records = discharges.count()
    bulk_op.successful_records = discharges.count()
    bulk_op.status = 'completed'
    bulk_op.completed_at = timezone.now()
    bulk_op.save()
    
    return response


def export_bed_utilization_report(writer, start_date, end_date, ward_filter, bulk_op, response):
    """Export bed utilization report"""
    beds = WardBed.objects.filter(is_active=True).select_related('ward')
    
    if ward_filter:
        beds = beds.filter(ward=ward_filter)
    
    writer.writerow(['Ward', 'Bed Number', 'Status', 'Current Patient', 'Assigned Since', 'Days Occupied'])
    
    for bed in beds:
        days = ''
        if bed.current_patient and bed.status == 'occupied':
            admission = PatientAdmission.objects.filter(
                bed=bed, is_active=True
            ).first()
            if admission:
                days = (timezone.now().date() - admission.admission_date.date()).days
        
        writer.writerow([
            bed.ward.name,
            bed.bed_number,
            bed.get_status_display(),
            bed.current_patient.user.get_full_name() if bed.current_patient else 'N/A',
            '',
            days if days != '' else '0',
        ])
    
    bulk_op.total_records = beds.count()
    bulk_op.successful_records = beds.count()
    bulk_op.status = 'completed'
    bulk_op.completed_at = timezone.now()
    bulk_op.save()
    
    return response


@login_required
def bulk_operations_list(request):
    """List all bulk operations"""
    operations = BulkOperation.objects.all().select_related('initiated_by')
    
    # Filter form
    form = FilterBulkOperationForm(request.GET)
    if form.is_valid():
        if form.cleaned_data.get('operation_type'):
            operations = operations.filter(operation_type=form.cleaned_data['operation_type'])
        if form.cleaned_data.get('status'):
            operations = operations.filter(status=form.cleaned_data['status'])
        if form.cleaned_data.get('date_from'):
            operations = operations.filter(created_at__gte=form.cleaned_data['date_from'])
        if form.cleaned_data.get('date_to'):
            operations = operations.filter(created_at__lte=form.cleaned_data['date_to'])
    
    context = {
        'operations': operations,
        'form': form,
    }
    return render(request, 'hospital_wards/bulk_operations_list.html', context)


# ==================== NOTIFICATION VIEWS ====================

@login_required
def notifications_dashboard(request):
    """Dashboard showing all notifications for current user"""
    from .notification_views import notifications_dashboard as notif_dashboard
    return notif_dashboard(request)


@login_required
@require_http_methods(["GET", "POST"])
def notification_preferences(request):
    """User notification preferences"""
    from .notification_views import notification_preferences as notif_prefs
    return notif_prefs(request)


@login_required
@require_http_methods(["POST"])
def mark_notification_read(request, notification_id):
    """Mark notification as read"""
    from .notification_views import mark_notification_read as mark_read
    return mark_read(request, notification_id)


@login_required
@require_http_methods(["POST"])
def delete_notification(request, notification_id):
    """Delete notification"""
    from .notification_views import delete_notification as delete_notif
    return delete_notif(request, notification_id)


@login_required
@require_POST
def mark_all_read(request):
    """Mark all notifications as read"""
    from .notification_views import mark_all_read as mark_all
    return mark_all(request)


@login_required
@require_POST
def clear_notifications(request):
    """Clear all notifications"""
    from .notification_views import clear_notifications as clear_notifs
    return clear_notifs(request)


@login_required
def notification_count(request):
    """Get unread notification count (AJAX)"""
    from .notification_views import notification_count as notif_count
    return notif_count(request)


@login_required
def notification_stats(request):
    """Get notification statistics (AJAX)"""
    from .notification_views import notification_stats as notif_stats
    return notif_stats(request)


