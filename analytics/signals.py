from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from decimal import Decimal
from orders.models import Order
from payments.models import Payment
from .models import ConversionEvent, RevenueStream
from .services import AnalyticsService


@receiver(post_save, sender=Order)
def track_order_completion(sender, instance, created, **kwargs):
    """Track order completion and update analytics"""
    
    # Only track completed orders
    if instance.status not in ['completed', 'delivered']:
        return
    
    # Record conversion event
    ConversionEvent.objects.create(
        user=instance.user,
        event_type='complete_order',
        session_id=getattr(instance, 'session_id', ''),
        metadata={
            'order_id': instance.id,
            'amount': float(instance.total_price),
            'payment_method': instance.payment_method,
        }
    )
    
    # Track revenue stream
    today = timezone.now().date()
    
    # Determine revenue channel
    channel = 'direct_order'
    if instance.subscription_order:
        channel = 'subscription'
    elif instance.is_corporate:
        channel = 'corporate'
    elif instance.is_catering:
        channel = 'catering'
    
    # Update revenue stream
    AnalyticsService.track_revenue_stream(
        date=today,
        channel=channel,
        amount=instance.total_price,
        transaction_count=1
    )
    
    # Update customer metrics
    AnalyticsService.update_customer_metrics(instance.user)


@receiver(post_save, sender=Payment)
def track_payment_completion(sender, instance, created, **kwargs):
    """Track payment completion"""
    
    if not created or instance.status != 'completed':
        return
    
    # Record conversion event for successful payment
    ConversionEvent.objects.create(
        user=instance.order.user if hasattr(instance, 'order') else None,
        event_type='complete_order',
        session_id='',
        metadata={
            'payment_id': instance.id,
            'amount': float(instance.amount),
            'payment_method': instance.payment_method,
        }
    )
