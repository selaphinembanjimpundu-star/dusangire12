from django.db import models
from django.contrib.auth.models import User


class NotificationType(models.TextChoices):
    ORDER_STATUS = 'order_status', 'Order Status Update'
    PAYMENT = 'payment', 'Payment Notification'
    PROMOTION = 'promotion', 'Promotional'
    LOYALTY = 'loyalty', 'Loyalty Points'
    SUBSCRIPTION = 'subscription', 'Subscription'
    SYSTEM = 'system', 'System Notification'


class Notification(models.Model):
    """User notifications"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Related objects (optional)
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        help_text="Related order if notification is about an order"
    )
    payment = models.ForeignKey(
        'payments.Payment',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        help_text="Related payment if notification is about a payment"
    )
    
    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        from django.utils import timezone
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
    
    @classmethod
    def create_order_notification(cls, user, order, title, message):
        """Create an order-related notification"""
        return cls.objects.create(
            user=user,
            notification_type=NotificationType.ORDER_STATUS,
            title=title,
            message=message,
            order=order
        )
    
    @classmethod
    def create_payment_notification(cls, user, payment, title, message):
        """Create a payment-related notification"""
        return cls.objects.create(
            user=user,
            notification_type=NotificationType.PAYMENT,
            title=title,
            message=message,
            payment=payment
        )
    
    @classmethod
    def create_loyalty_notification(cls, user, title, message):
        """Create a loyalty points notification"""
        return cls.objects.create(
            user=user,
            notification_type=NotificationType.LOYALTY,
            title=title,
            message=message
        )
    
    @classmethod
    def create_promotion_notification(cls, user, title, message):
        """Create a promotional notification"""
        return cls.objects.create(
            user=user,
            notification_type=NotificationType.PROMOTION,
            title=title,
            message=message
        )
    
    @classmethod
    def get_unread_count(cls, user):
        """Get count of unread notifications for user"""
        return cls.objects.filter(user=user, is_read=False).count()
    
    @classmethod
    def mark_all_as_read(cls, user):
        """Mark all notifications as read for user"""
        from django.utils import timezone
        cls.objects.filter(user=user, is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )
