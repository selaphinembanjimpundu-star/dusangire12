from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction, models
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal

from .models import SubscriptionPlan, Subscription, SubscriptionStatus, PlanType, SubscriptionOrder
from .forms import SubscriptionForm, SubscriptionUpdateForm
from orders.models import Order, OrderItem, OrderStatus
from payments.models import Payment, PaymentMethod, PaymentStatus
from delivery.models import DeliveryAddress


@login_required
def subscription_plans(request):
    """Display all available subscription plans with category filtering"""
    from .models import PlanCategory
    
    category = request.GET.get('category')
    plans = SubscriptionPlan.objects.filter(is_active=True).prefetch_related('menu_items')
    
    if category and category in PlanCategory.values:
        plans = plans.filter(category=category)
    
    # Group by plan type
    daily_plans = plans.filter(plan_type=PlanType.DAILY)
    weekly_plans = plans.filter(plan_type=PlanType.WEEKLY)
    monthly_plans = plans.filter(plan_type=PlanType.MONTHLY)
    
    # Check if user has active subscription
    active_subscription = None
    if request.user.is_authenticated:
        active_subscription = Subscription.objects.filter(
            user=request.user,
            status=SubscriptionStatus.ACTIVE
        ).first()
    
    # Calculate average menu price for savings comparison
    from menu.models import MenuItem
    avg_menu_price = MenuItem.objects.filter(is_available=True).aggregate(
        avg_price=models.Avg('price')
    )['avg_price'] or Decimal('5000.00')
    
    context = {
        'daily_plans': daily_plans,
        'weekly_plans': weekly_plans,
        'monthly_plans': monthly_plans,
        'active_subscription': active_subscription,
        'avg_menu_price': avg_menu_price,
        'categories': PlanCategory.choices,
        'selected_category': category,
    }
    return render(request, 'subscriptions/plans.html', context)


@login_required
def subscribe(request, plan_id):
    """Subscribe to a subscription plan with professional validation"""
    from accounts.validators import validate_account_for_payment
    
    plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)
    
    # Validate user account before subscription
    account_validation = validate_account_for_payment(request.user)
    if not account_validation['valid']:
        for error in account_validation['errors']:
            messages.error(request, error)
        # Show warnings but don't block
        for warning in account_validation.get('warnings', []):
            messages.warning(request, warning)
        # Redirect to profile if critical errors
        if account_validation['errors']:
            return redirect('accounts:profile')
    
    # Check if user already has active subscription
    active_subscription = Subscription.objects.filter(
        user=request.user,
        status=SubscriptionStatus.ACTIVE
    ).first()
    
    if active_subscription:
        messages.warning(request, 'You already have an active subscription. Please cancel it first to subscribe to a new plan.')
        return redirect('subscriptions:my_subscriptions')
    
    # Get user delivery addresses
    delivery_addresses = DeliveryAddress.objects.filter(user=request.user)
    
    if not delivery_addresses.exists():
        messages.warning(request, 'Please add a delivery address before subscribing.')
        return redirect('delivery:address_create')
    
    if request.method == 'POST':
        form = SubscriptionForm(request.POST, user=request.user, plan=plan)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Get selected delivery address
                    delivery_address = form.cleaned_data['delivery_address']
                    
                    # Calculate dates
                    start_date = timezone.now().date()
                    end_date = start_date + timedelta(days=plan.duration_days)
                    next_billing_date = end_date
                    
                    # Create subscription
                    subscription = Subscription.objects.create(
                        user=request.user,
                        plan=plan,
                        status=SubscriptionStatus.ACTIVE,
                        start_date=start_date,
                        end_date=end_date,
                        next_billing_date=next_billing_date,
                        preferred_delivery_time=form.cleaned_data.get('preferred_delivery_time'),
                        dietary_preferences=form.cleaned_data.get('dietary_preferences', ''),
                        auto_order_enabled=form.cleaned_data.get('auto_order_enabled', True),
                        auto_renewal_enabled=form.cleaned_data.get('auto_renewal_enabled', False),
                        delivery_address_id=delivery_address.id
                    )
                    
                    # Add preferred meals if selected
                    preferred_meals = form.cleaned_data.get('preferred_meals', [])
                    if preferred_meals:
                        subscription.preferred_meals.set(preferred_meals)
                    
                    # Update plan subscriber count
                    plan.subscribers_count = (plan.subscribers_count or 0) + 1
                    plan.save(update_fields=['subscribers_count'])
                    
                    # Create notification
                    from notifications.models import Notification
                    Notification.objects.create(
                        user=request.user,
                        notification_type='subscription',
                        title='Subscription Activated',
                        message=f'Your subscription to {plan.name} has been activated successfully! Your first order will be created automatically.'
                    )
                    
                    messages.success(request, f'Successfully subscribed to {plan.name}!')
                    return redirect('subscriptions:subscription_detail', subscription_id=subscription.id)
                    
            except Exception as e:
                messages.error(request, f'Error creating subscription: {str(e)}')
    else:
        form = SubscriptionForm(user=request.user, plan=plan)
        # Set default delivery address
        default_address = delivery_addresses.filter(is_default=True).first()
        if default_address:
            form.fields['delivery_address'].initial = default_address
    
    # Get recommended meals for display
    from .services import MealSelectionService
    recommended_meals = MealSelectionService.get_recommended_meals(request.user, count=10)
    
    context = {
        'plan': plan,
        'form': form,
        'delivery_addresses': delivery_addresses,
        'recommended_meals': recommended_meals,
    }
    return render(request, 'subscriptions/subscribe.html', context)


@login_required
def my_subscriptions(request):
    """User's subscription management page"""
    subscriptions = Subscription.objects.filter(user=request.user).select_related('plan').order_by('-created_at')
    active_subscription = subscriptions.filter(status=SubscriptionStatus.ACTIVE).first()
    
    context = {
        'subscriptions': subscriptions,
        'active_subscription': active_subscription,
    }
    return render(request, 'subscriptions/my_subscriptions.html', context)


@login_required
def subscription_detail(request, subscription_id):
    """Subscription detail page with analytics"""
    subscription = get_object_or_404(
        Subscription.objects.select_related('plan', 'user').prefetch_related('preferred_meals'),
        id=subscription_id,
        user=request.user
    )
    
    # Get subscription orders
    subscription_orders = SubscriptionOrder.objects.filter(
        subscription=subscription
    ).select_related('order').order_by('-scheduled_date')[:10]
    
    # Get analytics
    analytics = subscription.get_analytics()
    
    context = {
        'subscription': subscription,
        'subscription_orders': subscription_orders,
        'analytics': analytics,
    }
    return render(request, 'subscriptions/subscription_detail.html', context)


@login_required
def pause_subscription(request, subscription_id):
    """Pause a subscription"""
    subscription = get_object_or_404(
        Subscription,
        id=subscription_id,
        user=request.user,
        status=SubscriptionStatus.ACTIVE
    )
    
    if request.method == 'POST':
        subscription.pause()
        messages.success(request, 'Subscription paused successfully.')
        return redirect('subscriptions:my_subscriptions')
    
    context = {
        'subscription': subscription,
    }
    return render(request, 'subscriptions/pause_subscription.html', context)


@login_required
def resume_subscription(request, subscription_id):
    """Resume a paused subscription"""
    subscription = get_object_or_404(
        Subscription,
        id=subscription_id,
        user=request.user,
        status=SubscriptionStatus.PAUSED
    )
    
    if request.method == 'POST':
        subscription.resume()
        messages.success(request, 'Subscription resumed successfully.')
        return redirect('subscriptions:my_subscriptions')
    
    context = {
        'subscription': subscription,
    }
    return render(request, 'subscriptions/resume_subscription.html', context)


@login_required
def cancel_subscription(request, subscription_id):
    """Cancel a subscription"""
    subscription = get_object_or_404(
        Subscription,
        id=subscription_id,
        user=request.user
    )
    
    if request.method == 'POST':
        subscription.cancel()
        messages.success(request, 'Subscription cancelled successfully.')
        return redirect('subscriptions:my_subscriptions')
    
    context = {
        'subscription': subscription,
    }
    return render(request, 'subscriptions/cancel_subscription.html', context)


@login_required
def update_subscription(request, subscription_id):
    """Update subscription preferences with validation"""
    subscription = get_object_or_404(
        Subscription.objects.prefetch_related('preferred_meals'),
        id=subscription_id,
        user=request.user
    )
    
    if request.method == 'POST':
        form = SubscriptionUpdateForm(request.POST, instance=subscription)
        if form.is_valid():
            subscription = form.save()
            # Update preferred meals
            preferred_meals = form.cleaned_data.get('preferred_meals', [])
            subscription.preferred_meals.set(preferred_meals)
            
            # Create notification
            from notifications.models import Notification
            Notification.objects.create(
                user=request.user,
                notification_type='subscription',
                title='Subscription Updated',
                message=f'Your subscription preferences have been updated successfully.'
            )
            
            messages.success(request, 'Subscription updated successfully.')
            return redirect('subscriptions:subscription_detail', subscription_id=subscription.id)
    else:
        form = SubscriptionUpdateForm(instance=subscription)
    
    context = {
        'subscription': subscription,
        'form': form,
    }
    return render(request, 'subscriptions/update_subscription.html', context)
