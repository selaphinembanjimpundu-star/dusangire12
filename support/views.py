from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import SupportTicket, SupportMessage
from .forms import SupportTicketForm, SupportMessageForm


@login_required
def create_ticket(request):
    """Create a new support ticket"""
    if request.method == 'POST':
        form = SupportTicketForm(request.POST, user=request.user)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            
            # Create initial message
            if form.cleaned_data.get('message'):
                SupportMessage.objects.create(
                    ticket=ticket,
                    user=request.user,
                    message=form.cleaned_data['message']
                )
            
            messages.success(request, "Your support ticket has been created. We'll get back to you soon!")
            return redirect('support:ticket_detail', ticket_id=ticket.id)
    else:
        form = SupportTicketForm(user=request.user)
    
    context = {
        'form': form,
    }
    return render(request, 'support/create_ticket.html', context)


@login_required
def ticket_list(request):
    """List user's support tickets"""
    tickets = SupportTicket.objects.filter(user=request.user).order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(tickets, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'current_status': status_filter,
    }
    return render(request, 'support/ticket_list.html', context)


@login_required
def ticket_detail(request, ticket_id):
    """View and respond to a support ticket"""
    ticket = get_object_or_404(SupportTicket, id=ticket_id, user=request.user)
    
    if request.method == 'POST':
        form = SupportMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.ticket = ticket
            message.user = request.user
            message.save()
            
            # Update ticket status if needed
            if ticket.status == 'resolved':
                ticket.status = 'open'
                ticket.save()
            
            messages.success(request, "Your message has been sent.")
            return redirect('support:ticket_detail', ticket_id=ticket.id)
    else:
        form = SupportMessageForm()
    
    messages_list = ticket.messages.all().select_related('user')
    
    context = {
        'ticket': ticket,
        'messages_list': messages_list,
        'form': form,
    }
    return render(request, 'support/ticket_detail.html', context)


@login_required
def staff_ticket_list(request):
    """List all tickets for staff"""
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('support:ticket_list')
    
    tickets = SupportTicket.objects.all().select_related('user', 'assigned_to').order_by('-created_at')
    
    # Filters
    status_filter = request.GET.get('status', '')
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    
    assigned_filter = request.GET.get('assigned', '')
    if assigned_filter == 'me':
        tickets = tickets.filter(assigned_to=request.user)
    elif assigned_filter == 'unassigned':
        tickets = tickets.filter(assigned_to__isnull=True)
    
    # Pagination
    paginator = Paginator(tickets, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'current_status': status_filter,
        'current_assigned': assigned_filter,
    }
    return render(request, 'support/staff_ticket_list.html', context)


@login_required
def staff_ticket_detail(request, ticket_id):
    """Staff view of ticket detail"""
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('support:ticket_list')
    
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'reply':
            form = SupportMessageForm(request.POST)
            if form.is_valid():
                message = form.save(commit=False)
                message.ticket = ticket
                message.user = request.user
                message.save()
                messages.success(request, "Message sent.")
        elif action == 'update_status':
            ticket.status = request.POST.get('status', ticket.status)
            ticket.priority = request.POST.get('priority', ticket.priority)
            assigned_id = request.POST.get('assigned_to')
            if assigned_id:
                from django.contrib.auth.models import User
                try:
                    ticket.assigned_to = User.objects.get(id=assigned_id, is_staff=True)
                except User.DoesNotExist:
                    pass
            ticket.save()
            messages.success(request, "Ticket updated.")
        elif action == 'resolve':
            ticket.mark_resolved()
            messages.success(request, "Ticket marked as resolved.")
        
        return redirect('support:staff_ticket_detail', ticket_id=ticket.id)
    
    form = SupportMessageForm()
    messages_list = ticket.messages.all().select_related('user')
    
    # Get staff users for assignment
    from django.contrib.auth.models import User
    staff_users = User.objects.filter(is_staff=True)
    
    context = {
        'ticket': ticket,
        'messages_list': messages_list,
        'form': form,
        'staff_users': staff_users,
    }
    return render(request, 'support/staff_ticket_detail.html', context)
