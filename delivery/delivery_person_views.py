"""
Delivery Person Dashboard Views
Handles real-time delivery tracking and route management
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone

from accounts.models import UserRole
from orders.models import Order, OrderStatus
from delivery.models import DeliveryAddress


def require_delivery_person(view_func):
    """Decorator to require delivery person role"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        
        user_role = getattr(request.user.profile, 'role', None)
        if user_role not in [UserRole.DELIVERY_PERSON, UserRole.ADMIN]:
            messages.error(request, "You do not have permission to access this page.")
            return redirect('accounts:dashboard_home')
        
        return view_func(request, *args, **kwargs)
    
    wrapper.__name__ = view_func.__name__
    return wrapper


@login_required
@require_delivery_person
def delivery_dashboard(request):
    """
    Delivery person dashboard showing assigned deliveries
    """
    today = timezone.now().date()
    
    # Get assigned deliveries for today
    assigned_deliveries = Order.objects.filter(
        status=OrderStatus.READY,
        created_at__date=today
    ).select_related('user', 'delivery_address').order_by('created_at')
    
    # Get in-transit deliveries
    in_transit = Order.objects.filter(
        status=OrderStatus.IN_TRANSIT,
        created_at__date=today
    ).select_related('user', 'delivery_address').order_by('created_at')
    
    # Get delivered orders
    delivered_today = Order.objects.filter(
        status=OrderStatus.DELIVERED,
        created_at__date=today
    ).select_related('user', 'delivery_address').order_by('-updated_at')
    
    # Get delivery statistics
    total_assigned = assigned_deliveries.count()
    total_in_transit = in_transit.count()
    total_delivered = delivered_today.count()
    
    context = {
        'title': 'Delivery Dashboard',
        'assigned_deliveries': assigned_deliveries,
        'in_transit': in_transit,
        'delivered_today': delivered_today,
        'total_assigned': total_assigned,
        'total_in_transit': total_in_transit,
        'total_delivered': total_delivered,
        'completion_rate': (total_delivered / (total_assigned + total_in_transit + total_delivered) * 100) if (total_assigned + total_in_transit + total_delivered) > 0 else 0,
    }
    
    return render(request, 'delivery/delivery_dashboard.html', context)


@login_required
@require_delivery_person
def active_deliveries(request):
    """
    Real-time view of active deliveries with route information
    """
    today = timezone.now().date()
    
    # Get all active deliveries (ready and in-transit)
    active_deliveries = Order.objects.filter(
        status__in=[OrderStatus.READY, OrderStatus.IN_TRANSIT],
        created_at__date=today
    ).select_related('user', 'delivery_address').order_by('status', 'created_at')
    
    context = {
        'title': 'Active Deliveries',
        'active_deliveries': active_deliveries,
    }
    
    return render(request, 'delivery/active_deliveries.html', context)


@login_required
@require_delivery_person
def delivery_addresses(request):
    """
    View all unique delivery addresses and coverage zones
    """
    # Get unique delivery addresses with order counts
    addresses = DeliveryAddress.objects.filter(
        user__orders__isnull=False
    ).annotate(
        order_count=Count('orders')
    ).order_by('-order_count')
    
    context = {
        'title': 'Delivery Addresses',
        'addresses': addresses,
    }
    
    return render(request, 'delivery/delivery_addresses.html', context)
