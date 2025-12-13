from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from orders.models import Order, OrderStatus
from .models import LoyaltyPoints


# Store the old status before save
_old_order_status = {}


@receiver(pre_save, sender=Order)
def store_old_order_status(sender, instance, **kwargs):
    """Store the old status before saving"""
    if instance.pk:
        try:
            old_instance = Order.objects.get(pk=instance.pk)
            _old_order_status[instance.pk] = old_instance.status
        except Order.DoesNotExist:
            _old_order_status[instance.pk] = None
    else:
        _old_order_status[instance.pk] = None


@receiver(post_save, sender=Order)
def award_loyalty_points(sender, instance, created, **kwargs):
    """Award loyalty points when order status changes to DELIVERED"""
    # Only award points when order status changes to DELIVERED (not on creation)
    if not created and instance.status == OrderStatus.DELIVERED:
        old_status = _old_order_status.get(instance.pk)
        
        # Only award if status actually changed to DELIVERED
        if old_status != OrderStatus.DELIVERED:
            # Check if points were already awarded for this order
            if instance.points_transactions.exists():
                return
            
            # Get or create loyalty points for user
            loyalty_points, _ = LoyaltyPoints.objects.get_or_create(user=instance.user)
            
            # Calculate points from order total
            points = loyalty_points.calculate_points_from_order(instance.total)
            
            if points > 0:
                # Award points
                loyalty_points.add_points(
                    points=points,
                    reason=f"Order {instance.order_number} delivered",
                    order=instance
                )
                
                # Create notification
                from notifications.models import Notification
                Notification.create_loyalty_notification(
                    user=instance.user,
                    title="Points Earned!",
                    message=f"You've earned {points} loyalty points for your order {instance.order_number}. Your new balance is {loyalty_points.total_points} points."
                )
        
        # Clean up
        if instance.pk in _old_order_status:
            del _old_order_status[instance.pk]

