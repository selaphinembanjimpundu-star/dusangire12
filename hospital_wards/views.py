"""
Hospital Ward Management Views
Handles ward/bed management, delivery scheduling, patient education, and caregiver notifications
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.db.models import Q, Count
from django.utils import timezone
from django.contrib import messages
from datetime import datetime, timedelta

from .models import (
    Ward, WardBed, WardDeliveryRoute, WardAvailability,
    MealNutritionInfo, DeliveryScheduleSlot,
    PatientEducationCategory, PatientEducationContent, PatientEducationProgress,
    CaregiverNotification
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
def notification_detail(request, notification_id):
    """Display full notification detail"""
    notification = get_object_or_404(CaregiverNotification, id=notification_id, caregiver=request.user)
    
    # Mark as read
    if not notification.is_read:
        notification.mark_as_read()
    
    context = {
        'notification': notification,
    }
    return render(request, 'hospital_wards/notification_detail.html', context)


# ==================== DASHBOARD VIEWS ====================

@login_required
def hospital_dashboard(request):
    """Hospital dashboard with overview statistics"""
    # Ward statistics
    wards = Ward.objects.filter(is_active=True)
    total_beds = sum(w.capacity for w in wards)
    occupied_beds = sum(w.beds.filter(status='occupied').count() for w in wards)
    available_beds = total_beds - occupied_beds
    
    # Education statistics
    total_education_items = PatientEducationContent.objects.filter(is_published=True).count()
    user_education_progress = PatientEducationProgress.objects.filter(patient=request.user).count()
    
    # Recent orders
    recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    # Unread notifications
    unread_notifications = CaregiverNotification.objects.filter(
        caregiver=request.user,
        is_read=False
    ).count()
    
    context = {
        'wards': wards,
        'total_beds': total_beds,
        'occupied_beds': occupied_beds,
        'available_beds': available_beds,
        'occupancy_percentage': (occupied_beds / total_beds * 100) if total_beds > 0 else 0,
        'total_education_items': total_education_items,
        'user_education_progress': user_education_progress,
        'recent_orders': recent_orders,
        'unread_notifications': unread_notifications,
    }
    return render(request, 'hospital_wards/dashboard.html', context)
