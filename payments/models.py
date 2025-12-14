from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from orders.models import Order


class PaymentMethod(models.TextChoices):
    CASH_ON_DELIVERY = 'cash_on_delivery', 'Cash on Delivery'
    MTN_MOBILE_MONEY = 'mtn_mobile_money', 'MTN Mobile Money'
    AIRTEL_MONEY = 'airtel_money', 'Airtel Money'
    BANK_TRANSFER = 'bank_transfer', 'Bank Transfer'
    CARD = 'card', 'Card Payment'


class PaymentStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    PROCESSING = 'processing', 'Processing'
    COMPLETED = 'completed', 'Completed'
    FAILED = 'failed', 'Failed'
    CANCELLED = 'cancelled', 'Cancelled'
    REFUNDED = 'refunded', 'Refunded'


class Payment(models.Model):
    """Payment record for orders"""
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    payment_method = models.CharField(
        max_length=50,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CASH_ON_DELIVERY
    )
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )
    
    # Payment details
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    # Transaction details (for mobile money, bank transfer, etc.)
    transaction_id = models.CharField(max_length=100, blank=True, help_text="Transaction ID or reference number")
    phone_number = models.CharField(max_length=20, blank=True, help_text="Phone number for mobile money")
    account_number = models.CharField(max_length=50, blank=True, help_text="Account number for bank transfer")
    
    # Payment notes
    notes = models.TextField(blank=True, help_text="Additional payment notes or instructions")
    
    # Gateway integration fields
    gateway_response = models.JSONField(null=True, blank=True, help_text="Response from payment gateway")
    payment_link = models.URLField(blank=True, help_text="Payment link for redirect-based payments")
    gateway_name = models.CharField(max_length=50, blank=True, help_text="Payment gateway used")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment for Order {self.order.order_number} - {self.get_payment_method_display()}"
    
    def get_status_display_class(self):
        """Return Bootstrap class for status badge"""
        status_classes = {
            PaymentStatus.PENDING: 'warning',
            PaymentStatus.PROCESSING: 'info',
            PaymentStatus.COMPLETED: 'success',
            PaymentStatus.FAILED: 'danger',
            PaymentStatus.CANCELLED: 'secondary',
            PaymentStatus.REFUNDED: 'secondary',
        }
        return status_classes.get(self.status, 'secondary')
    
    def mark_as_completed(self):
        """Mark payment as completed"""
        from django.utils import timezone
        self.status = PaymentStatus.COMPLETED
        self.paid_at = timezone.now()
        self.save()
    
    def mark_as_failed(self):
        """Mark payment as failed"""
        self.status = PaymentStatus.FAILED
        self.save()
