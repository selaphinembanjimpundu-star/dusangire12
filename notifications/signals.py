from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.models import Order, OrderStatus
from payments.models import Payment, PaymentStatus
from .models import Notification


@receiver(post_save, sender=Order)
def create_order_notifications(sender, instance, created, **kwargs):
    """Create notifications when order status changes"""
    if created:
        # Order created
        Notification.create_order_notification(
            user=instance.user,
            order=instance,
            title="Order Placed",
            message=f"Your order {instance.order_number} has been placed successfully. We'll notify you when it's confirmed."
        )
    else:
        # Order status changed
        status_messages = {
            OrderStatus.CONFIRMED: f"Your order {instance.order_number} has been confirmed and is being prepared.",
            OrderStatus.PREPARING: f"Your order {instance.order_number} is now being prepared.",
            OrderStatus.READY: f"Your order {instance.order_number} is ready for pickup/delivery.",
            OrderStatus.DELIVERED: f"Your order {instance.order_number} has been delivered. Thank you for your order!",
            OrderStatus.CANCELLED: f"Your order {instance.order_number} has been cancelled. If you have any questions, please contact us."
        }
        
        if instance.status in status_messages:
            Notification.create_order_notification(
                user=instance.user,
                order=instance,
                title=f"Order {instance.get_status_display()}",
                message=status_messages[instance.status]
            )


@receiver(post_save, sender=Payment)
def create_payment_notifications(sender, instance, created, **kwargs):
    """Create notifications when payment status changes"""
    if created:
        # Payment created
        Notification.create_payment_notification(
            user=instance.order.user,
            payment=instance,
            title="Payment Initiated",
            message=f"Payment of RWF {instance.amount} for order {instance.order.order_number} has been initiated."
        )
    else:
        # Payment status changed
        if instance.status == PaymentStatus.COMPLETED:
            Notification.create_payment_notification(
                user=instance.order.user,
                payment=instance,
                title="Payment Confirmed",
                message=f"Your payment of RWF {instance.amount} for order {instance.order.order_number} has been confirmed."
            )
        elif instance.status == PaymentStatus.FAILED:
            Notification.create_payment_notification(
                user=instance.order.user,
                payment=instance,
                title="Payment Failed",
                message=f"Your payment for order {instance.order.order_number} has failed. Please try again or contact support."
            )

















