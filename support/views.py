from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from .models import SupportTicket, SupportMessage
from .forms import SupportTicketForm, SupportMessageForm, FeedbackForm
from django.db.models import Q

def is_staff_or_admin(user):
    """Check if user is staff or admin"""
    return user.is_authenticated and (user.is_staff or (hasattr(user, 'profile') and user.profile.role in ['admin', 'staff']))


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


def feedback(request):
    """Public feedback form (doesn't require login)"""
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            # Send email to admin
            subject = f"[Feedback] {form.cleaned_data['feedback_type'].title()}: {form.cleaned_data['subject']}"
            message = f"""
From: {form.cleaned_data['name']} ({form.cleaned_data['email']})
Type: {form.cleaned_data['feedback_type']}
Subject: {form.cleaned_data['subject']}

Message:
{form.cleaned_data['message']}
"""
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.ADMINS[0][1] if settings.ADMINS else settings.DEFAULT_FROM_EMAIL],
                    fail_silently=False,
                )
                messages.success(request, "Thank you for your feedback! We'll review it and get back to you if needed.")
                return redirect('support:feedback')
            except Exception as e:
                messages.error(request, "Sorry, there was an error sending your feedback. Please try again later.")
    else:
        form = FeedbackForm()
    
    context = {
        'form': form,
    }
    return render(request, 'support/feedback.html', context)


def faq(request):
    """FAQ page"""
    faqs = [
        {
            'question': 'How do I place an order?',
            'answer': 'Browse our menu, add items to your cart, and proceed to checkout. You can choose your delivery address and payment method during checkout.'
        },
        {
            'question': 'What payment methods do you accept?',
            'answer': 'We accept mobile money (MTN, Airtel), bank transfers, and cash on delivery.'
        },
        {
            'question': 'How long does delivery take?',
            'answer': 'Delivery times vary by location. For hospital deliveries, we typically deliver within 30-60 minutes. Outside hospital deliveries may take longer.'
        },
        {
            'question': 'Can I subscribe to regular meals?',
            'answer': 'Yes! We offer daily, weekly, and monthly subscription plans. You can customize your meal preferences and delivery schedule.'
        },
        {
            'question': 'Do you offer meals for special dietary needs?',
            'answer': 'Absolutely! We have meals for diabetic, low-sodium, high-protein, post-surgery, vegetarian, and other dietary requirements. Use the filters on our menu page to find suitable meals.'
        },
        {
            'question': 'How do I track my order?',
            'answer': 'After placing an order, you can track its status in your Order History. You\'ll also receive notifications when your order status changes.'
        },
        {
            'question': 'Can I cancel or modify my order?',
            'answer': 'You can cancel orders that are still pending. Once an order is confirmed and being prepared, please contact support for assistance.'
        },
        {
            'question': 'How do loyalty points work?',
            'answer': 'You earn points with every order. Points can be redeemed for discounts on future orders. Check your loyalty dashboard to see your points balance and redemption options.'
        },
    ]
    
    context = {
        'faqs': faqs,
    }
    return render(request, 'support/faq.html', context)
@login_required
@user_passes_test(is_staff_or_admin)
def staff_dashboard(request):
    """Dashboard for support staff with metrics"""
    from django.db.models import Count, Avg, F
    from django.utils import timezone
    from datetime import timedelta
    
    # Basic counts
    total_tickets = SupportTicket.objects.count()
    open_tickets = SupportTicket.objects.filter(status='open').count()
    in_progress_tickets = SupportTicket.objects.filter(status='in_progress').count()
    resolved_tickets = SupportTicket.objects.filter(status='resolved').count()
    
    # Average resolution time
    resolved_with_time = SupportTicket.objects.filter(
        status='resolved', 
        resolved_at__isnull=False
    ).annotate(
        resolution_time=F('resolved_at') - F('created_at')
    ).aggregate(avg_time=Avg('resolution_time'))
    
    avg_resolution_time = resolved_with_time['avg_time']
    
    # Tickets by priority
    priority_stats = SupportTicket.objects.values('priority').annotate(count=Count('id'))
    
    # Recent tickets
    recent_tickets = SupportTicket.objects.select_related('user', 'assigned_to').order_by('-created_at')[:10]
    
    # Staff performance
    staff_stats = SupportTicket.objects.filter(assigned_to__isnull=False).values(
        'assigned_to__username'
    ).annotate(
        total=Count('id'),
        resolved=Count('id', filter=Q(status='resolved'))
    ).order_by('-total')

    context = {
        'total_tickets': total_tickets,
        'open_tickets': open_tickets,
        'in_progress_tickets': in_progress_tickets,
        'resolved_tickets': resolved_tickets,
        'avg_resolution_time': avg_resolution_time,
        'priority_stats': priority_stats,
        'recent_tickets': recent_tickets,
        'staff_stats': staff_stats,
        'title': _('Support Dashboard'),
    }
    return render(request, 'support/staff_dashboard.html', context)


def about_us(request):
    """About Us page"""
    from .models import AboutUsPage
    try:
        about = AboutUsPage.objects.first()
    except:
        about = None
    
    context = {
        'about': about,
        'page_title': 'About Dusangire',
    }
    return render(request, 'support/about_us.html', context)


def faq_list(request):
    """FAQ list view with auto-reply suggestion"""
    from .models import FAQ
    
    category = request.GET.get('category')
    search = request.GET.get('search', '')
    
    faqs = FAQ.objects.filter(is_active=True).order_by('category', 'order')
    
    if category:
        faqs = faqs.filter(category=category)
    
    if search:
        faqs = faqs.filter(
            Q(question__icontains=search) | 
            Q(answer__icontains=search)
        )
    
    # Group by category
    categories = FAQ.CATEGORY_CHOICES
    
    # Check if user found answer
    found_answer = request.GET.get('found', False)
    
    context = {
        'faqs': faqs,
        'categories': categories,
        'selected_category': category,
        'search_query': search,
        'found_answer': found_answer,
        'support_email': settings.CONTACT_EMAIL,
        'support_phone': settings.CONTACT_PHONE,
        'page_title': 'Frequently Asked Questions',
    }
    return render(request, 'support/faq_list.html', context)


def contact_form(request):
    """Contact form view with auto-reply and HTML emails"""
    from .models import ContactMessage
    from django.template.loader import render_to_string
    from django.core.mail import EmailMultiAlternatives
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Save contact message
        contact = ContactMessage.objects.create(
            name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message
        )
        
        # Send HTML email to admin with fallback plain text
        try:
            admin_context = {
                'name': name,
                'email': email,
                'phone': phone,
                'subject': subject,
                'message': message,
                'contact_id': contact.id,
                'created_at': contact.created_at,
            }
            
            admin_html = render_to_string('emails/contact_admin_notification.html', admin_context)
            admin_text = f"""New Contact Form Submission

Name: {name}
Email: {email}
Phone: {phone}
Subject: {subject}

Message:
{message}

---
Contact ID: {contact.id}
Submitted: {contact.created_at}
"""
            
            email_msg = EmailMultiAlternatives(
                f'New Contact Form Submission: {subject}',
                admin_text,
                settings.DEFAULT_FROM_EMAIL,
                [settings.CONTACT_EMAIL]
            )
            email_msg.attach_alternative(admin_html, "text/html")
            email_msg.send(fail_silently=True)
        except Exception as e:
            print(f"Error sending admin email: {e}")
        
        # Send HTML auto-reply to user with fallback plain text
        try:
            user_context = {
                'name': name,
                'email': email,
                'subject': subject,
                'contact_id': contact.id,
                'created_at': contact.created_at,
            }
            
            user_html = render_to_string('emails/contact_auto_reply.html', user_context)
            user_text = f"""Hi {name},

Thank you for contacting Dusangire Health Platform!

We have received your message regarding: {subject}

Our support team will review your inquiry and get back to you as soon as possible. We typically respond within 24-48 hours.

In the meantime, if you have any urgent concerns, please reach out to us directly:

Contact Details:
Email: {settings.CONTACT_EMAIL}
Phone: {settings.CONTACT_PHONE}

Your contact ID for reference: #{contact.id}

Best regards,
Dusangire Health Platform Support Team
Rwanda
"""
            
            email_msg = EmailMultiAlternatives(
                'We received your message - Dusangire Support',
                user_text,
                settings.DEFAULT_FROM_EMAIL,
                [email]
            )
            email_msg.attach_alternative(user_html, "text/html")
            email_msg.send(fail_silently=True)
        except Exception as e:
            print(f"Error sending user confirmation: {e}")
        
        messages.success(request, 'Your message has been sent successfully. We will get back to you soon.')
        return redirect('support:contact_form')
    
    context = {
        'page_title': 'Contact Us',
        'support_email': settings.CONTACT_EMAIL,
        'support_phone': settings.CONTACT_PHONE,
    }
    return render(request, 'support/contact_form.html', context)

