"""
Signals for subscription notifications and tracking
"""

import uuid
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta

from .models import (
    Subscription, SubscriptionStatus, SubscriptionPlan, 
    SubscriptionAutoRenewal, ReferralProgram
)
from payments.models import Payment
from notifications.models import Notification
from .services import LoyaltyService


@receiver(post_save, sender=Subscription)
def handle_subscription_save(sender, instance, created, **kwargs):
    """Handle subscription creation and updates"""
    if created:
        # Create auto-renewal configuration
        SubscriptionAutoRenewal.objects.create(
            subscription=instance,
            auto_renew_enabled=instance.auto_renewal_enabled,
            renewal_date=instance.end_date,
            renewal_interval_days=instance.plan.duration_days
        )
        
        # Create notification
        Notification.objects.create(
            user=instance.user,
            notification_type='subscription',
            title='Subscription Activated',
            message=f'Your subscription to {instance.plan.name} has been activated. Your first order will be created automatically.'
        )
    else:
        # Status change notifications
        if instance.status == SubscriptionStatus.PAUSED:
            Notification.objects.create(
                user=instance.user,
                notification_type='subscription',
                title='Subscription Paused',
                message=f'Your subscription to {instance.plan.name} has been paused. No new orders will be created until you resume.'
            )
        elif instance.status == SubscriptionStatus.CANCELLED:
            Notification.objects.create(
                user=instance.user,
                notification_type='subscription',
                title='Subscription Cancelled',
                message=f'Your subscription to {instance.plan.name} has been cancelled. You can subscribe again anytime.'
            )
        elif instance.status == SubscriptionStatus.EXPIRED:
            Notification.objects.create(
                user=instance.user,
                notification_type='subscription',
                title='Subscription Expired',
                message=f'Your subscription to {instance.plan.name} has expired. Renew now to continue receiving meals.'
            )


@receiver(post_save, sender=Payment)
def handle_payment_completion(sender, instance, created, **kwargs):
    """
    Handle actions when a payment is completed:
    1. Award loyalty points
    2. Update VIP tier
    3. Check for referral completion
    """
    if instance.status == 'completed':
        user = instance.user
        if not user:
            return

        # 1. Award loyalty points
        LoyaltyService.award_loyalty_points(
            user=user,
            amount=instance.amount,
            reason=f"Payment for {instance.invoice_number or 'Order'}",
            related_object=instance
        )
        
        # 2. Update VIP Tier
        LoyaltyService.calculate_vip_tier(user)
        
        # 3. Check referral completion (if this is the first payment)
        # We check if this is the user's first completed payment
        # Note: We filter by order__user or subscription__user since Payment doesn't have direct user field
        completed_payments_count = Payment.objects.filter(
            models.Q(order__user=user) | models.Q(subscription__user=user),
            status='completed'
        ).count()
        
        if completed_payments_count == 1:
            LoyaltyService.process_referral_completion(user)


@receiver(post_save, sender=ReferralProgram)
def ensure_referral_code(sender, instance, created, **kwargs):
    """Ensure referral code and link exist"""
    if created and not instance.referral_code:
        # Generate unique code
        while True:
            code = str(uuid.uuid4())[:8].upper()
            if not ReferralProgram.objects.filter(referral_code=code).exists():
                instance.referral_code = code
                break
        
        instance.generate_referral_link()
        instance.save()
    elif created and not instance.referral_link:
        instance.generate_referral_link()
        instance.save()














