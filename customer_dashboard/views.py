# customer_dashboard/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db import models
from orders.models import Order
from subscriptions.models import Subscription
import logging

logger = logging.getLogger(__name__)


@login_required
def dashboard(request):
    """Customer dashboard main view"""
    try:
        # Get recent orders
        recent_orders = Order.objects.filter(
            user=request.user
        ).order_by('-created_at')[:5]
        
        # Get active subscription
        active_subscription = None
        try:
            active_subscription = Subscription.objects.filter(
                user=request.user,
                status='active'
            ).first()
        except Exception as e:
            logger.error(f"Error getting subscription: {e}")
            pass
        
        # Get statistics for dashboard
        try:
            total_orders = Order.objects.filter(user=request.user).count()
        except:
            total_orders = 0
        
        try:
            active_subscriptions_count = Subscription.objects.filter(
                user=request.user,
                status='active'
            ).count()
        except:
            active_subscriptions_count = 0
        
        # Get meal plans count
        meal_plans_count = 0
        try:
            from nutritionist_dashboard.models import MealPlan
            meal_plans_count = MealPlan.objects.filter(client=request.user).count()
        except ImportError:
            pass
        except Exception as e:
            logger.error(f"Error getting meal plans: {e}")
        
        # Get health profile
        health_profile = None
        try:
            from health_profiles.models import HealthProfile
            health_profile = HealthProfile.objects.filter(user=request.user).first()
        except:
            pass
            
        context = {
            'title': _('Customer Dashboard'),
            'recent_orders': recent_orders,
            'active_subscription': active_subscription,
            'user': request.user,
            'total_orders': total_orders,
            'active_subscriptions': active_subscriptions_count,
            'meal_plans_count': meal_plans_count,
            'health_profile': health_profile,
        }
        return render(request, 'customer_dashboard/dashboard.html', context)
    except Exception as e:
        logger.error(f"Error loading customer dashboard for user {request.user.id}: {e}")
        messages.error(request, _('Error loading dashboard. Please try again.'))
        return redirect('home')


@login_required
def my_orders(request):
    """View customer orders"""
    try:
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        total_spent = sum(order.total_amount for order in orders if order.total_amount)
    except Exception as e:
        logger.error(f"Error loading orders: {e}")
        orders = []
        total_spent = 0
    
    return render(request, 'customer_dashboard/my_orders.html', {
        'orders': orders,
        'total_spent': total_spent,
        'title': _('My Orders'),
        'user': request.user,
    })


@login_required
def order_detail(request, order_id):
    """View customer order details"""
    try:
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        # Get order items
        try:
            order_items = order.items.all()
        except:
            order_items = []
        
        context = {
            'order': order,
            'order_items': order_items,
            'title': _('Order Details'),
            'user': request.user,
        }
        return render(request, 'customer_dashboard/order_detail.html', context)
    except Exception as e:
        logger.error(f"Error loading order detail {order_id} for user {request.user.id}: {e}")
        messages.error(request, _('Order not found or access denied.'))
        return redirect('customer_dashboard:my_orders')


@login_required
def my_subscriptions(request):
    """View customer subscriptions"""
    try:
        subscriptions = Subscription.objects.filter(user=request.user).order_by('-created_at')
        
        # Get active subscription
        active_subscription = Subscription.objects.filter(
            user=request.user,
            status='active'
        ).first()
        
    except Exception as e:
        logger.error(f"Error loading subscriptions: {e}")
        subscriptions = []
        active_subscription = None
    
    return render(request, 'customer_dashboard/my_subscriptions.html', {
        'subscriptions': subscriptions,
        'active_subscription': active_subscription,
        'title': _('My Subscriptions'),
        'user': request.user,
    })


@login_required
def my_profile(request):
    """Customer profile view with statistics"""
    try:
        # Get statistics for the template
        from nutritionist_dashboard.models import MealPlan, Consultation
        
        # Orders count
        orders_count = Order.objects.filter(user=request.user).count()
        
        # Active subscriptions count
        active_subscriptions_count = Subscription.objects.filter(
            user=request.user,
            status='active'
        ).count()
        
        # Meal plans count
        meal_plans_count = MealPlan.objects.filter(client=request.user).count()
        
        # Consultation count
        consultation_count = Consultation.objects.filter(client=request.user).count()
        
        context = {
            'title': _('My Profile'),
            'user': request.user,
            'orders': {'count': orders_count},
            'active_subscriptions': active_subscriptions_count,
            'meal_plans': {'count': meal_plans_count},
            'consultations': {'count': consultation_count},
        }
        return render(request, 'customer_dashboard/my_profile.html', context)
    except Exception as e:
        logger.error(f"Error loading profile for user {request.user.id}: {e}")
        messages.error(request, _('Error loading profile. Please try again.'))
        return redirect('customer_dashboard:dashboard')


@login_required
def my_meal_plans(request):
    """View customer meal plans"""
    try:
        from nutritionist_dashboard.models import MealPlan
        meal_plans = MealPlan.objects.filter(client=request.user).order_by('-created_at')
        active_meal_plan = meal_plans.filter(status='active').first()
    except Exception as e:
        logger.error(f"Error loading meal plans: {e}")
        meal_plans = []
        active_meal_plan = None
    
    return render(request, 'customer_dashboard/my_meal_plans.html', {
        'meal_plans': meal_plans,
        'active_meal_plan': active_meal_plan,
        'title': _('My Meal Plans'),
        'user': request.user,
    })


@login_required
def view_meal_plan(request, plan_id):
    """View specific meal plan details"""
    from nutritionist_dashboard.models import MealPlan
    plan = get_object_or_404(MealPlan, id=plan_id, client=request.user)
    
    return render(request, 'customer_dashboard/view_meal_plan.html', {
        'plan': plan,
        'title': plan.title,
        'user': request.user,
    })


@login_required
def my_consultations(request):
    """View customer consultations"""
    try:
        from nutritionist_dashboard.models import Consultation
        consultations = Consultation.objects.filter(client=request.user).order_by('-scheduled_at')
        upcoming_consultations = consultations.filter(scheduled_at__gte=timezone.now()).order_by('scheduled_at')
        past_consultations = consultations.filter(scheduled_at__lt=timezone.now()).order_by('-scheduled_at')
    except Exception as e:
        logger.error(f"Error loading consultations: {e}")
        consultations = []
        upcoming_consultations = []
        past_consultations = []
    
    return render(request, 'customer_dashboard/my_consultations.html', {
        'consultations': consultations,
        'upcoming_consultations': upcoming_consultations,
        'past_consultations': past_consultations,
        'title': _('My Consultations'),
        'user': request.user,
    })


@login_required
def reschedule_consultation(request, consultation_id):
    """Placeholder for rescheduling a consultation"""
    messages.info(request, _('Please contact support or your nutritionist to reschedule.'))
    return redirect('customer_dashboard:my_consultations')


@login_required
def cancel_consultation(request, consultation_id):
    """Cancel a scheduled consultation"""
    from nutritionist_dashboard.models import Consultation
    consultation = get_object_or_404(Consultation, id=consultation_id, client=request.user, status='scheduled')
    consultation.status = 'cancelled'
    consultation.save()
    messages.success(request, _('Consultation cancelled successfully.'))
    return redirect('customer_dashboard:my_consultations')


@login_required
def book_consultation(request):
    """Book a new consultation"""
    return redirect('nutritionist_dashboard:book_consultation_list')


@login_required
def no_access(request):
    """Display no access page"""
    return render(request, 'customer_dashboard/no_access.html', {
        'title': _('Access Denied'),
        'user': request.user,
    })


@login_required
def activity_log(request):
    """View user activity log"""
    return render(request, 'customer_dashboard/activity_log.html', {
        'activities': [],
        'title': _('Activity Log'),
        'user': request.user,
    })


@login_required
def preferences(request):
    """User preferences and settings"""
    return render(request, 'customer_dashboard/preferences.html', {
        'title': _('Preferences & Settings'),
        'user': request.user,
    })


@login_required
def help_center(request):
    """Help center and FAQ"""
    return render(request, 'customer_dashboard/help_center.html', {
        'title': _('Help Center'),
        'user': request.user,
    })


@login_required
def notifications_view(request):
    """User notifications"""
    from notifications.models import Notification
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:20]
    
    if request.method == 'POST' and 'mark_all_read' in request.POST:
        notifications.update(is_read=True)
        messages.success(request, _('All notifications marked as read.'))
        return redirect('customer_dashboard:notifications')
    
    return render(request, 'customer_dashboard/notifications.html', {
        'notifications': notifications,
        'title': _('Notifications'),
        'user': request.user,
    })


# Subscription & Loyalty Actions
@login_required
def loyalty_dashboard(request):
    """View customer loyalty points, VIP tier, and referrals"""
    from subscriptions.models import LoyaltyPoints, VIPTier, ReferralProgram, LoyaltyTransaction
    
    loyalty_points, created = LoyaltyPoints.objects.get_or_create(user=request.user)
    vip_tier, created = VIPTier.objects.get_or_create(
        user=request.user,
        defaults={'achieved_at': timezone.now().date()}
    )
    referrals = ReferralProgram.objects.filter(referrer=request.user).order_by('-created_at')
    transactions = LoyaltyTransaction.objects.filter(user=request.user).order_by('-created_at')[:20]
    
    # Calculate points value in RWF (1 point = 100 RWF)
    points_value_rwf = loyalty_points.balance * 100 if loyalty_points.balance else 0
    
    context = {
        'loyalty_points': loyalty_points,
        'points_value_rwf': points_value_rwf,
        'vip_tier': vip_tier,
        'referrals': referrals,
        'transactions': transactions,
        'title': _('Loyalty & Rewards'),
        'user': request.user,
    }
    return render(request, 'customer_dashboard/loyalty.html', context)


@login_required
def payment_history(request):
    """View customer payment history"""
    from payments.models import Payment
    payments = Payment.objects.filter(
        models.Q(order__user=request.user) | models.Q(subscription__user=request.user)
    ).order_by('-created_at')
    
    context = {
        'payments': payments,
        'title': _('Payment History'),
        'user': request.user,
    }
    return render(request, 'customer_dashboard/payment_history.html', context)


@login_required
def payment_receipt(request, payment_id):
    """View/Download payment receipt (Invoice)"""
    from payments.models import Payment
    payment = get_object_or_404(Payment, id=payment_id)
    
    # Security check
    if payment.order and payment.order.user != request.user:
        return redirect('customer_dashboard:no_access')
    if payment.subscription and payment.subscription.user != request.user:
        return redirect('customer_dashboard:no_access')
        
    context = {
        'payment': payment,
        'title': _('Payment Receipt'),
        'user': request.user,
    }
    return render(request, 'customer_dashboard/payment_receipt.html', context)


@login_required
def billing_info(request):
    """View billing information"""
    from payments.models import PaymentMethod as PM_Choices
    
    context = {
        'title': _('Billing Information'),
        'user': request.user,
        'payment_methods': PM_Choices.choices,
    }
    return render(request, 'customer_dashboard/billing_info.html', context)


@login_required
def pause_subscription(request, subscription_id):
    """Redirect to subscriptions app pause view"""
    return redirect('subscriptions:pause_subscription', subscription_id=subscription_id)


@login_required
def resume_subscription(request, subscription_id):
    """Redirect to subscriptions app resume view"""
    return redirect('subscriptions:resume_subscription', subscription_id=subscription_id)


@login_required
def cancel_subscription(request, subscription_id):
    """Redirect to subscriptions app cancel view"""
    return redirect('subscriptions:cancel_subscription', subscription_id=subscription_id)


@login_required
def cancel_order(request, order_id):
    """Cancel a pending order"""
    order = get_object_or_404(Order, id=order_id, user=request.user, status='pending')
    order.status = 'cancelled'
    order.save()
    messages.success(request, _('Order cancelled successfully.'))
    return redirect('customer_dashboard:my_orders')


@login_required
def repeat_order(request, order_id):
    """Repeat a previous order"""
    messages.info(request, _('Order repeat functionality coming soon.'))
    return redirect('customer_dashboard:my_orders')


@login_required
def update_dietary_preferences(request):
    """Update user dietary preferences"""
    if request.method == 'POST':
        dietary = request.POST.get('dietary_preferences')
        medical = request.POST.get('medical_alerts')
        
        profile = request.user.profile
        profile.dietary_preferences = dietary
        profile.medical_alerts = medical
        profile.save()
        
        messages.success(request, _('Preferences updated successfully.'))
    return redirect('customer_dashboard:my_profile')


@login_required
def health_reports(request):
    """View customer health impact reports and metrics"""
    from health_profiles.models import HealthProfile, PatientNutritionStatus, RecoveryMetrics, MedicalPrescription
    
    health_profile = HealthProfile.objects.filter(user=request.user).first()
    nutrition_history = []
    recovery_metrics = []
    prescriptions = []
    
    if health_profile:
        nutrition_history = PatientNutritionStatus.objects.filter(health_profile=health_profile).order_by('-assessment_date')
        recovery_metrics = RecoveryMetrics.objects.filter(health_profile=health_profile).order_by('-hospital_admission_date')
        prescriptions = MedicalPrescription.objects.filter(health_profile=health_profile).order_by('-prescription_date')
    
    context = {
        'health_profile': health_profile,
        'nutrition_history': nutrition_history,
        'recovery_metrics': recovery_metrics,
        'prescriptions': prescriptions,
        'title': _('Health Impact Reports'),
        'user': request.user,
    }
    return render(request, 'customer_dashboard/health_reports.html', context)


@login_required
def update_health_profile(request):
    """Update user health profile metrics"""
    from health_profiles.models import HealthProfile
    health_profile, created = HealthProfile.objects.get_or_create(
        user=request.user,
        defaults={'date_of_birth': timezone.now().date(), 'weight_kg': 0, 'height_cm': 0}
    )
    
    if request.method == 'POST':
        health_profile.date_of_birth = request.POST.get('date_of_birth')
        health_profile.blood_type = request.POST.get('blood_type')
        health_profile.weight_kg = request.POST.get('weight_kg')
        health_profile.height_cm = request.POST.get('height_cm')
        health_profile.medical_history = request.POST.get('medical_history')
        health_profile.current_conditions = request.POST.get('current_conditions')
        health_profile.medications = request.POST.get('medications')
        health_profile.allergies = request.POST.get('allergies')
        health_profile.dietary_restrictions = request.POST.get('dietary_restrictions')
        health_profile.save()
        
        messages.success(request, _('Health profile updated successfully.'))
        return redirect('customer_dashboard:health_reports')
        
    return render(request, 'customer_dashboard/update_health_profile.html', {
        'health_profile': health_profile,
        'title': _('Update Health Profile'),
        'user': request.user,
    })


@login_required
def emergency_contact(request):
    """View/Update emergency contact information"""
    from health_profiles.models import HealthProfile
    health_profile, created = HealthProfile.objects.get_or_create(
        user=request.user,
        defaults={'date_of_birth': timezone.now().date(), 'weight_kg': 0, 'height_cm': 0}
    )
    
    if request.method == 'POST':
        health_profile.emergency_contact_name = request.POST.get('name')
        health_profile.emergency_contact_phone = request.POST.get('phone')
        health_profile.save()
        messages.success(request, _('Emergency contact updated successfully.'))
        return redirect('customer_dashboard:emergency_contact')
        
    return render(request, 'customer_dashboard/emergency_contact.html', {
        'health_profile': health_profile,
        'title': _('Emergency Contact'),
        'user': request.user,
    })


@login_required
def dietary_emergency(request):
    """View dietary emergency information (allergies, etc.)"""
    from health_profiles.models import HealthProfile
    health_profile = HealthProfile.objects.filter(user=request.user).first()
    
    return render(request, 'customer_dashboard/dietary_emergency.html', {
        'health_profile': health_profile,
        'title': _('Dietary Emergency Info'),
        'user': request.user,
    })


@login_required
def medical_alerts(request):
    """View medical alerts and conditions"""
    from health_profiles.models import HealthProfile
    health_profile = HealthProfile.objects.filter(user=request.user).first()
    
    return render(request, 'customer_dashboard/medical_alerts.html', {
        'health_profile': health_profile,
        'title': _('Medical Alerts'),
        'user': request.user,
    })


# Other placeholders
@login_required
def update_address(request): pass
@login_required
def update_password(request): pass
@login_required
def submit_meal_feedback(request, plan_id): pass
@login_required
def update_billing_info(request): pass
@login_required
def support_tickets(request): pass
@login_required
def new_support_ticket(request): pass
@login_required
def view_support_ticket(request, ticket_id): pass
@login_required
def analytics_dashboard(request): pass
@login_required
def order_reports(request): pass
@login_required
def quick_order(request): pass
@login_required
def favorites_list(request): pass
@login_required
def add_to_favorites(request, item_id): pass
@login_required
def remove_from_favorites(request, item_id): pass
@login_required
def account_settings(request): pass
@login_required
def notification_settings(request): pass
@login_required
def privacy_settings(request): pass
@login_required
def update_profile_picture(request): pass
@login_required
def mark_notification_read(request, notification_id): pass
@login_required
def get_recent_activity(request): pass
@login_required
def check_order_status(request, order_id): pass