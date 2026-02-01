from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum, Q, Avg
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from orders.models import Order, OrderItem, OrderStatus
from menu.models import MenuItem, Category
from payments.models import Payment, PaymentStatus
from accounts.models import User
from delivery.models import DeliveryAddress


def is_staff_or_admin(user):
    """Check if user is staff or admin"""
    return user.is_authenticated and (user.is_staff or user.profile.role in ['admin', 'staff'])


@login_required
@user_passes_test(is_staff_or_admin)
def dashboard(request):
    """Admin dashboard with statistics"""
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Order Statistics
    total_orders = Order.objects.count()
    today_orders = Order.objects.filter(created_at__date=today).count()
    week_orders = Order.objects.filter(created_at__date__gte=week_ago).count()
    month_orders = Order.objects.filter(created_at__date__gte=month_ago).count()
    
    # Revenue Statistics
    total_revenue = Payment.objects.filter(status=PaymentStatus.COMPLETED).aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')
    
    today_revenue = Payment.objects.filter(
        status=PaymentStatus.COMPLETED,
        paid_at__date=today
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    week_revenue = Payment.objects.filter(
        status=PaymentStatus.COMPLETED,
        paid_at__date__gte=week_ago
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    month_revenue = Payment.objects.filter(
        status=PaymentStatus.COMPLETED,
        paid_at__date__gte=month_ago
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    # Order Status Breakdown
    pending_orders = Order.objects.filter(status=OrderStatus.PENDING).count()
    confirmed_orders = Order.objects.filter(status=OrderStatus.CONFIRMED).count()
    preparing_orders = Order.objects.filter(status=OrderStatus.PREPARING).count()
    ready_orders = Order.objects.filter(status=OrderStatus.READY).count()
    delivered_orders = Order.objects.filter(status=OrderStatus.DELIVERED).count()
    
    # Recent Orders
    recent_orders = Order.objects.select_related('user', 'payment').order_by('-created_at')[:10]
    
    # Popular Items (top 10)
    popular_items = OrderItem.objects.values(
        'menu_item__name', 'menu_item__id'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_orders=Count('order', distinct=True)
    ).order_by('-total_quantity')[:10]
    
    # Payment Status Breakdown
    pending_payments = Payment.objects.filter(status=PaymentStatus.PENDING).count()
    completed_payments = Payment.objects.filter(status=PaymentStatus.COMPLETED).count()
    failed_payments = Payment.objects.filter(status=PaymentStatus.FAILED).count()
    
    # Average Order Value
    avg_order_value = Order.objects.aggregate(avg=Avg('total'))['avg'] or Decimal('0.00')
    
    # Corporate Statistics
    from corporate.models import CorporateContract, CorporatePartner
    total_partners = CorporatePartner.objects.count()
    #active_contracts = CorporateContract.objects.filter(status='active').count()
    active_contracts = CorporateContract.objects.filter(is_active=True).count()
    
    
    # Catering Statistics
    from catering.models import CateringBooking
    pending_catering = CateringBooking.objects.filter(status='pending').count()
    total_catering_revenue = CateringBooking.objects.filter(status='completed').aggregate(
        total=Sum('total_price')
    )['total'] or Decimal('0.00')

    context = {
        # Order Stats
        'total_orders': total_orders,
        'today_orders': today_orders,
        'week_orders': week_orders,
        'month_orders': month_orders,
        
        # Revenue Stats
        'total_revenue': total_revenue,
        'today_revenue': today_revenue,
        'week_revenue': week_revenue,
        'month_revenue': month_revenue,
        
        # Order Status
        'pending_orders': pending_orders,
        'confirmed_orders': confirmed_orders,
        'preparing_orders': preparing_orders,
        'ready_orders': ready_orders,
        'delivered_orders': delivered_orders,
        
        # Payment Status
        'pending_payments': pending_payments,
        'completed_payments': completed_payments,
        'failed_payments': failed_payments,
        
        # Corporate & Catering
        'total_partners': total_partners,
        'active_contracts': active_contracts,
        'pending_catering': pending_catering,
        'total_catering_revenue': total_catering_revenue,

        # Other Stats
        'recent_orders': recent_orders,
        'popular_items': popular_items,
        'avg_order_value': avg_order_value,
    }
    
    return render(request, 'admin_dashboard/dashboard.html', context)


@login_required
@user_passes_test(is_staff_or_admin)
def order_management(request):
    """Order management interface with filters"""
    orders = Order.objects.select_related('user', 'payment').prefetch_related('items').order_by('-created_at')
    
    # Filters
    status_filter = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    search_query = request.GET.get('search', '')
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    if date_from:
        orders = orders.filter(created_at__date__gte=date_from)
    
    if date_to:
        orders = orders.filter(created_at__date__lte=date_to)
    
    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(customer_name__icontains=search_query) |
            Q(customer_phone__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(orders, 25)  # 25 orders per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'orders': page_obj,  # For backward compatibility
        'status_choices': OrderStatus.choices,
        'current_status': status_filter,
        'date_from': date_from,
        'date_to': date_to,
        'search_query': search_query,
    }
    return render(request, 'admin_dashboard/order_management.html', context)


@login_required
@user_passes_test(is_staff_or_admin)
def order_detail_admin(request, order_id):
    """Admin view of order details"""
    order = get_object_or_404(Order.objects.select_related('user', 'payment').prefetch_related('items__menu_item'), id=order_id)
    order_items = order.items.select_related('menu_item').all()
    
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'admin_dashboard/order_detail.html', context)


@login_required
@user_passes_test(is_staff_or_admin)
def update_order_status(request, order_id):
    """Update order status"""
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        
        if new_status in dict(OrderStatus.choices):
            old_status = order.status
            order.status = new_status
            
            # Update delivered_at if status is delivered
            if new_status == OrderStatus.DELIVERED and not order.delivered_at:
                from django.utils import timezone
                order.delivered_at = timezone.now()
            
            order.save()
            messages.success(request, f'Order {order.order_number} status updated from {old_status} to {new_status}')
        else:
            messages.error(request, 'Invalid status')
    
    return redirect('admin_dashboard:order_detail', order_id=order_id)


@login_required
@user_passes_test(is_staff_or_admin)
def kitchen_dashboard(request):
    """Kitchen dashboard showing orders by status"""
    # Get orders that need kitchen attention
    pending_orders = Order.objects.filter(status=OrderStatus.PENDING).select_related('user', 'payment').prefetch_related('items__menu_item').order_by('created_at')
    confirmed_orders = Order.objects.filter(status=OrderStatus.CONFIRMED).select_related('user', 'payment').prefetch_related('items__menu_item').order_by('created_at')
    preparing_orders = Order.objects.filter(status=OrderStatus.PREPARING).select_related('user', 'payment').prefetch_related('items__menu_item').order_by('created_at')
    ready_orders = Order.objects.filter(status=OrderStatus.READY).select_related('user', 'payment').prefetch_related('items__menu_item').order_by('created_at')
    
    context = {
        'pending_orders': pending_orders,
        'confirmed_orders': confirmed_orders,
        'preparing_orders': preparing_orders,
        'ready_orders': ready_orders,
    }
    return render(request, 'admin_dashboard/kitchen_dashboard.html', context)


@login_required
@user_passes_test(is_staff_or_admin)
def reports(request):
    """Reports and analytics"""
    # Date range
    date_from = request.GET.get('date_from', (timezone.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    date_to = request.GET.get('date_to', timezone.now().strftime('%Y-%m-%d'))
    
    try:
        date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
        date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
    except:
        date_from_obj = timezone.now().date() - timedelta(days=30)
        date_to_obj = timezone.now().date()
    
    # Sales Report
    orders_in_range = Order.objects.filter(created_at__date__range=[date_from_obj, date_to_obj])
    total_sales = orders_in_range.aggregate(total=Sum('total'))['total'] or Decimal('0.00')
    total_orders = orders_in_range.count()
    avg_order_value = orders_in_range.aggregate(avg=Avg('total'))['avg'] or Decimal('0.00')
    
    # Sales by day
    daily_sales = orders_in_range.extra(
        select={'day': 'date(created_at)'}
    ).values('day').annotate(
        total=Sum('total'),
        count=Count('id')
    ).order_by('day')
    
    # Popular Items
    popular_items = OrderItem.objects.filter(
        order__created_at__date__range=[date_from_obj, date_to_obj]
    ).values(
        'menu_item__name', 'menu_item__category__name'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum('subtotal'),
        order_count=Count('order', distinct=True)
    ).order_by('-total_quantity')[:20]
    
    # Sales by Category
    category_sales = OrderItem.objects.filter(
        order__created_at__date__range=[date_from_obj, date_to_obj]
    ).values('menu_item__category__name').annotate(
        total_revenue=Sum('subtotal'),
        total_quantity=Sum('quantity')
    ).order_by('-total_revenue')
    
    # Payment Methods Breakdown
    payment_methods = Payment.objects.filter(
        order__created_at__date__range=[date_from_obj, date_to_obj]
    ).values('payment_method').annotate(
        count=Count('id'),
        total=Sum('amount')
    ).order_by('-total')
    
    context = {
        'date_from': date_from,
        'date_to': date_to,
        'total_sales': total_sales,
        'total_orders': total_orders,
        'avg_order_value': avg_order_value,
        'daily_sales': daily_sales,
        'popular_items': popular_items,
        'category_sales': category_sales,
        'payment_methods': payment_methods,
    }
    
    return render(request, 'admin_dashboard/reports.html', context)
@login_required
@user_passes_test(is_staff_or_admin)
def bi_dashboard(request):
    """Business Intelligence Dashboard with advanced analytics"""
    from django.db.models import Count, Sum, Avg, Q
    from django.utils import timezone
    from datetime import timedelta
    
    # Time periods
    now = timezone.now()
    month_ago = now - timedelta(days=30)
    two_months_ago = now - timedelta(days=60)
    
    # 1. Average Order Value (AOV)
    aov = Order.objects.filter(status=OrderStatus.DELIVERED).aggregate(avg=Avg('total'))['avg'] or Decimal('0.00')
    
    # 2. Customer Retention Rate
    # Customers who ordered in the previous month
    prev_month_customers = Order.objects.filter(
        created_at__range=[two_months_ago, month_ago]
    ).values('user').distinct().count()
    
    # Customers from prev month who also ordered this month
    retained_customers = Order.objects.filter(
        created_at__range=[month_ago, now],
        user__in=Order.objects.filter(created_at__range=[two_months_ago, month_ago]).values('user')
    ).values('user').distinct().count()
    
    retention_rate = (retained_customers / prev_month_customers * 100) if prev_month_customers > 0 else 0
    
    # 3. Customer Lifetime Value (CLV)
    # CLV = AOV * Purchase Frequency
    total_orders = Order.objects.filter(status=OrderStatus.DELIVERED).count()
    total_customers = Order.objects.values('user').distinct().count()
    purchase_frequency = (total_orders / total_customers) if total_customers > 0 else 0
    clv = aov * Decimal(str(purchase_frequency))
    
    # 4. Revenue vs Target (Placeholder target)
    monthly_revenue = Payment.objects.filter(
        status=PaymentStatus.COMPLETED,
        paid_at__gte=month_ago
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    revenue_target = Decimal('5000000.00') # Example target: 5M RWF
    target_achievement = (monthly_revenue / revenue_target * 100) if revenue_target > 0 else 0
    
    # 5. Churn Rate
    churn_rate = 100 - retention_rate if prev_month_customers > 0 else 0

    # 6. Revenue by Category
    category_revenue = OrderItem.objects.values(
        'menu_item__category__name'
    ).annotate(
        revenue=Sum('subtotal')
    ).order_by('-revenue')

    context = {
        'aov': aov,
        'retention_rate': retention_rate,
        'clv': clv,
        'monthly_revenue': monthly_revenue,
        'revenue_target': revenue_target,
        'target_achievement': target_achievement,
        'churn_rate': churn_rate,
        'category_revenue': category_revenue,
        'title': ('Business Intelligence Dashboard'),
    }
    return render(request, 'admin_dashboard/bi_dashboard.html', context)


# ============================================================================
# ADMIN LOGGING VIEWS
# ============================================================================

@login_required
@user_passes_test(is_staff_or_admin)
def view_admin_logs(request):
    """Display admin activity logs with filtering and pagination"""
    from .models import AdminLog
    from .logger import get_recent_logs
    
    # Get all logs
    logs = AdminLog.objects.all()
    
    # Apply filters
    action_filter = request.GET.get('action')
    user_filter = request.GET.get('user')
    model_filter = request.GET.get('model_name')
    status_filter = request.GET.get('status')
    search_query = request.GET.get('search')
    
    if action_filter:
        logs = logs.filter(action=action_filter)
    
    if user_filter:
        logs = logs.filter(admin_user_id=user_filter)
    
    if model_filter:
        logs = logs.filter(model_name__icontains=model_filter)
    
    if status_filter:
        logs = logs.filter(status=status_filter)
    
    if search_query:
        logs = logs.filter(
            Q(description__icontains=search_query) |
            Q(model_name__icontains=search_query) |
            Q(error_message__icontains=search_query)
        )
    
    # Get unique values for filter dropdowns
    action_choices = AdminLog.ACTION_CHOICES
    admin_users = User.objects.filter(is_staff=True).order_by('username')
    
    # Pagination
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'action_choices': action_choices,
        'admin_users': admin_users,
        'current_action': action_filter,
        'current_user': user_filter,
        'current_model': model_filter,
        'current_status': status_filter,
        'search_query': search_query,
        'total_logs': logs.count(),
        'title': 'Admin Activity Logs',
    }
    
    return render(request, 'admin_dashboard/logs.html', context)


@login_required
@user_passes_test(is_staff_or_admin)
def log_detail(request, log_id):
    """Display detailed view of a specific log entry"""
    from .models import AdminLog
    
    log = get_object_or_404(AdminLog, id=log_id)
    
    context = {
        'log': log,
        'title': f'Log Detail - {log.get_action_display()}',
    }
    
    return render(request, 'admin_dashboard/log_detail.html', context)


@login_required
@user_passes_test(is_staff_or_admin)
def admin_activity_summary(request):
    """Display summary statistics of admin activities"""
    from .models import AdminLog
    from django.db.models import Count
    
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Activity statistics
    today_logs = AdminLog.objects.filter(timestamp__date=today).count()
    week_logs = AdminLog.objects.filter(timestamp__date__gte=week_ago).count()
    month_logs = AdminLog.objects.filter(timestamp__date__gte=month_ago).count()
    
    # Failed actions
    failed_actions = AdminLog.objects.filter(status='FAILED').count()
    
    # Top actions
    top_actions = AdminLog.objects.values('action').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Top admins
    top_admins = AdminLog.objects.values(
        'admin_user__username',
        'admin_user__id'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Most modified models
    most_modified = AdminLog.objects.values('model_name').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Recent logs
    recent_logs = AdminLog.objects.select_related('admin_user').order_by('-timestamp')[:20]
    
    context = {
        'today_logs': today_logs,
        'week_logs': week_logs,
        'month_logs': month_logs,
        'failed_actions': failed_actions,
        'top_actions': top_actions,
        'top_admins': top_admins,
        'most_modified': most_modified,
        'recent_logs': recent_logs,
        'title': 'Admin Activity Summary',
    }
    
    return render(request, 'admin_dashboard/activity_summary.html', context)


@login_required
@user_passes_test(is_staff_or_admin)
def export_logs(request):
    """Export admin logs to CSV or JSON"""
    from .models import AdminLog
    from .logger import export_logs_to_json
    import csv
    from django.http import HttpResponse
    
    # Get filtered logs
    logs = AdminLog.objects.all()
    
    action_filter = request.GET.get('action')
    if action_filter:
        logs = logs.filter(action=action_filter)
    
    format_type = request.GET.get('format', 'csv')
    
    if format_type == 'json':
        json_data = export_logs_to_json(logs)
        response = HttpResponse(json_data, content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="admin_logs.json"'
        return response
    
    else:  # CSV format (default)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="admin_logs.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID',
            'Admin User',
            'Action',
            'Model',
            'Object ID',
            'Description',
            'Status',
            'Timestamp',
            'IP Address',
            'Duration (ms)',
            'Error Message'
        ])
        
        for log in logs:
            writer.writerow([
                log.id,
                str(log.admin_user),
                log.get_action_display(),
                log.model_name,
                log.object_id,
                log.description,
                log.status,
                log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                log.ip_address or '',
                log.duration_ms or '',
                log.error_message or '',
            ])
        
        return response
