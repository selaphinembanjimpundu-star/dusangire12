"""
Support Staff Dashboard Views
Handles customer support tickets and inquiries
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone

from accounts.models import UserRole
from support.models import SupportTicket


def require_support_staff(view_func):
    """Decorator to require support staff role"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        
        user_role = getattr(request.user.profile, 'role', None)
        if user_role not in [UserRole.SUPPORT_STAFF, UserRole.ADMIN]:
            messages.error(request, "You do not have permission to access this page.")
            return redirect('accounts:dashboard_home')
        
        return view_func(request, *args, **kwargs)
    
    wrapper.__name__ = view_func.__name__
    return wrapper


@login_required
@require_support_staff
def support_dashboard(request):
    """
    Support staff dashboard showing ticket management
    """
    # Get ticket statistics
    open_tickets = SupportTicket.objects.filter(status='open').count()
    in_progress_tickets = SupportTicket.objects.filter(status='in_progress').count()
    resolved_tickets = SupportTicket.objects.filter(status='resolved').count()
    closed_tickets = SupportTicket.objects.filter(status='closed').count()
    
    # Get recent tickets
    recent_tickets = SupportTicket.objects.all().order_by('-created_at')[:10]
    
    # Get urgent tickets
    urgent_tickets = SupportTicket.objects.filter(
        priority='high',
        status__in=['open', 'in_progress']
    ).order_by('-created_at')
    
    # Get unassigned tickets
    unassigned_tickets = SupportTicket.objects.filter(
        assigned_to__isnull=True
    ).order_by('created_at')
    
    context = {
        'title': 'Support Dashboard',
        'open_tickets': open_tickets,
        'in_progress_tickets': in_progress_tickets,
        'resolved_tickets': resolved_tickets,
        'closed_tickets': closed_tickets,
        'recent_tickets': recent_tickets,
        'urgent_tickets': urgent_tickets,
        'unassigned_tickets': unassigned_tickets,
        'total_tickets': open_tickets + in_progress_tickets,
    }
    
    return render(request, 'support/support_dashboard.html', context)
