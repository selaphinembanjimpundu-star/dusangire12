"""
Kitchen Staff Dashboard Views
Handles meal preparation and kitchen operations
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone

from accounts.models import UserRole
from orders.models import Order, OrderStatus, OrderItem
from hospital_wards.models import DeliveryScheduleSlot


def require_kitchen_staff(view_func):
    """Decorator to require kitchen staff role"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        
        user_role = getattr(request.user.profile, 'role', None)
        if user_role not in [UserRole.CHEF, UserRole.KITCHEN_STAFF, UserRole.ADMIN]:
            messages.error(request, "You do not have permission to access this page.")
            return redirect('accounts:dashboard_home')
        
        return view_func(request, *args, **kwargs)
    
    wrapper.__name__ = view_func.__name__
    return wrapper


@login_required
@require_kitchen_staff
def kitchen_dashboard(request):
    """
    Kitchen staff dashboard showing meal preparation status
    """
    today = timezone.now().date()
    
    # Get pending meals (not yet prepared)
    pending_meals = Order.objects.filter(
        status__in=[OrderStatus.PENDING, OrderStatus.CONFIRMED],
        created_at__date=today
    ).select_related('user').prefetch_related('items__menu_item').order_by('created_at')
    
    # Get preparing meals
    preparing_meals = Order.objects.filter(
        status=OrderStatus.PREPARING,
        created_at__date=today
    ).select_related('user').prefetch_related('items__menu_item').order_by('created_at')
    
    # Get ready meals (waiting for delivery)
    ready_meals = Order.objects.filter(
        status=OrderStatus.READY,
        created_at__date=today
    ).select_related('user').prefetch_related('items__menu_item').order_by('created_at')
    
    # Get meal items to prepare
    meal_items_to_prepare = OrderItem.objects.filter(
        order__status__in=[OrderStatus.PENDING, OrderStatus.CONFIRMED],
        order__created_at__date=today
    ).select_related('menu_item', 'order__user').order_by('order__created_at')
    
    # Get kitchen statistics
    total_orders_today = Order.objects.filter(created_at__date=today).count()
    completed_today = Order.objects.filter(
        created_at__date=today,
        status=OrderStatus.READY
    ).count()
    
    context = {
        'title': 'Kitchen Dashboard',
        'pending_meals': pending_meals,
        'preparing_meals': preparing_meals,
        'ready_meals': ready_meals,
        'meal_items_to_prepare': meal_items_to_prepare,
        'total_orders_today': total_orders_today,
        'completed_today': completed_today,
        'orders_pending': pending_meals.count(),
        'orders_preparing': preparing_meals.count(),
        'orders_ready': ready_meals.count(),
    }
    
    return render(request, 'catering/kitchen_dashboard.html', context)


@login_required
@require_kitchen_staff
def meal_preparation_list(request):
    """
    Detailed list of meals to prepare with filtering
    """
    today = timezone.now().date()
    
    # Get all meals for today
    meals = Order.objects.filter(
        created_at__date=today
    ).select_related('user').prefetch_related(
        'items__menu_item'
    ).order_by('status', 'created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status', '')
    if status_filter:
        meals = meals.filter(status=status_filter)
    
    context = {
        'title': 'Meal Preparation List',
        'meals': meals,
        'status_choices': OrderStatus.choices,
        'selected_status': status_filter,
    }
    
    return render(request, 'catering/meal_preparation_list.html', context)
