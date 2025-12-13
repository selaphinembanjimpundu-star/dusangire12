from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction, models
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal

from .models import SubscriptionPlan, UserSubscription, SubscriptionStatus, PlanType, SubscriptionOrder
from .forms import SubscriptionForm, SubscriptionUpdateForm
from orders.models import Order, OrderItem, OrderStatus
from payments.models import Payment, PaymentMethod, PaymentStatus
from delivery.models import DeliveryAddress


@login_required
def subscription_plans(request):
    """Display all available subscription plans"""
    plans = SubscriptionPlan.objects.filter(is_active=True).prefetch_related('menu_items')
    
    # Group by plan type
    daily_plans = plans.filter(plan_type=PlanType.DAILY)
    weekly_plans = plans.filter(plan_type=PlanType.WEEKLY)
    monthly_plans = plans.filter(plan_type=PlanType.MONTHLY)
    
    # Check if user has active subscription
    active_subscription = None
    if request.user.is_authenticated:
        active_subscription = UserSubscription.objects.filter(
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
    }
    return render(request, 'subscriptions/plans.html', context)


@login_required
def subscribe(request, plan_id):
    """Subscribe to a subscription plan"""
    plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)
    
    # Check if user already has active subscription
    active_subscription = UserSubscription.objects.filter(
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
        form = SubscriptionForm(request.POST, user=request.user)
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
                    subscription = UserSubscription.objects.create(
                        user=request.user,
                        plan=plan,
                        status=SubscriptionStatus.ACTIVE,
                        start_date=start_date,
                        end_date=end_date,
                        next_billing_date=next_billing_date,
                        preferred_delivery_time=form.cleaned_data.get('preferred_delivery_time'),
                        dietary_preferences=form.cleaned_data.get('dietary_preferences', ''),
                        auto_order_enabled=form.cleaned_data.get('auto_order_enabled', True)
                    )
                    
                    messages.success(request, f'Successfully subscribed to {plan.name}!')
                    return redirect('subscriptions:my_subscriptions')
                    
            except Exception as e:
                messages.error(request, f'Error creating subscription: {str(e)}')
    else:
        form = SubscriptionForm(user=request.user)
        # Set default delivery address
        default_address = delivery_addresses.filter(is_default=True).first()
        if default_address:
            form.fields['delivery_address'].initial = default_address
    
    context = {
        'plan': plan,
        'form': form,
        'delivery_addresses': delivery_addresses,
    }
    return render(request, 'subscriptions/subscribe.html', context)


@login_required
def my_subscriptions(request):
    """User's subscription management page"""
    subscriptions = UserSubscription.objects.filter(user=request.user).select_related('plan').order_by('-created_at')
    active_subscription = subscriptions.filter(status=SubscriptionStatus.ACTIVE).first()
    
    context = {
        'subscriptions': subscriptions,
        'active_subscription': active_subscription,
    }
    return render(request, 'subscriptions/my_subscriptions.html', context)


@login_required
def subscription_detail(request, subscription_id):
    """Subscription detail page"""
    subscription = get_object_or_404(
        UserSubscription.objects.select_related('plan', 'user'),
        id=subscription_id,
        user=request.user
    )
    
    # Get subscription orders
    subscription_orders = SubscriptionOrder.objects.filter(
        subscription=subscription
    ).select_related('order').order_by('-scheduled_date')[:10]
    
    context = {
        'subscription': subscription,
        'subscription_orders': subscription_orders,
    }
    return render(request, 'subscriptions/subscription_detail.html', context)


@login_required
def pause_subscription(request, subscription_id):
    """Pause a subscription"""
    subscription = get_object_or_404(
        UserSubscription,
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
        UserSubscription,
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
        UserSubscription,
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
    """Update subscription preferences"""
    subscription = get_object_or_404(
        UserSubscription,
        id=subscription_id,
        user=request.user
    )
    
    if request.method == 'POST':
        form = SubscriptionUpdateForm(request.POST, instance=subscription)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subscription updated successfully.')
            return redirect('subscriptions:subscription_detail', subscription_id=subscription.id)
    else:
        form = SubscriptionUpdateForm(instance=subscription)
    
    context = {
        'subscription': subscription,
        'form': form,
    }
    return render(request, 'subscriptions/update_subscription.html', context)
