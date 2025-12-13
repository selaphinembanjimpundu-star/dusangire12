from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Notification


@login_required
def notification_list(request):
    """Display user's notifications"""
    notifications = Notification.objects.filter(
        user=request.user
    ).select_related('order', 'payment').order_by('-created_at')
    
    # Filter by type if provided
    notification_type = request.GET.get('type', '')
    if notification_type:
        notifications = notifications.filter(notification_type=notification_type)
    
    # Filter by read status
    read_filter = request.GET.get('read', '')
    if read_filter == 'unread':
        notifications = notifications.filter(is_read=False)
    elif read_filter == 'read':
        notifications = notifications.filter(is_read=True)
    
    # Pagination
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get unread count
    unread_count = Notification.get_unread_count(request.user)
    
    context = {
        'page_obj': page_obj,
        'unread_count': unread_count,
        'current_type': notification_type,
        'current_read_filter': read_filter,
    }
    return render(request, 'notifications/list.html', context)


@login_required
def notification_detail(request, notification_id):
    """View notification details"""
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        user=request.user
    )
    
    # Mark as read
    notification.mark_as_read()
    
    context = {
        'notification': notification,
    }
    return render(request, 'notifications/detail.html', context)


@login_required
def mark_notification_read(request, notification_id):
    """Mark a notification as read (AJAX)"""
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        user=request.user
    )
    
    notification.mark_as_read()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'is_read': notification.is_read})
    
    messages.success(request, "Notification marked as read.")
    return redirect('notifications:list')


@login_required
def mark_all_read(request):
    """Mark all notifications as read"""
    Notification.mark_all_as_read(request.user)
    messages.success(request, "All notifications marked as read.")
    return redirect('notifications:list')


@login_required
def notification_count(request):
    """Get unread notification count (AJAX)"""
    count = Notification.get_unread_count(request.user)
    return JsonResponse({'count': count})
