from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, RegexValidator
from django.utils import timezone
from decimal import Decimal
from orders.models import Order
from subscriptions.models import Subscription
import uuid


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


class PaymentType(models.TextChoices):
    """Type of payment transaction"""
    ORDER_PAYMENT = 'order_payment', 'Order Payment'
    SUBSCRIPTION_PAYMENT = 'subscription_payment', 'Subscription Payment'
    LOYALTY_REDEMPTION = 'loyalty_redemption', 'Loyalty Points Redemption'
    REFUND = 'refund', 'Refund'


class TransactionStatus(models.TextChoices):
    """Transaction status for real-time tracking"""
    INITIATED = 'initiated', 'Initiated'
    SENT_TO_GATEWAY = 'sent_to_gateway', 'Sent to Gateway'
    GATEWAY_ACCEPTED = 'gateway_accepted', 'Gateway Accepted'
    AWAITING_CONFIRMATION = 'awaiting_confirmation', 'Awaiting Confirmation'
    CONFIRMED = 'confirmed', 'Confirmed'
    TIMEOUT = 'timeout', 'Timed Out'
    FAILED = 'failed', 'Failed'


class AirtelMoneyProvider(models.Model):
    """Airtel Money gateway configuration"""
    merchant_id = models.CharField(max_length=100, unique=True)
    api_key = models.CharField(max_length=500)
    api_secret = models.CharField(max_length=500)
    base_url = models.URLField(default='https://openapiuat.airtel.africa')
    webhook_url = models.URLField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Airtel Money Providers"
    
    def __str__(self):
        return f"Airtel Money - {self.merchant_id}"


class MTNMobileMoneyProvider(models.Model):
    """MTN Mobile Money gateway configuration"""
    merchant_id = models.CharField(max_length=100, unique=True)
    api_key = models.CharField(max_length=500)
    subscription_key = models.CharField(max_length=500)
    base_url = models.URLField(default='https://momoapi.mtn.com')
    webhook_url = models.URLField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "MTN Mobile Money Providers"
    
    def __str__(self):
        return f"MTN Mobile Money - {self.merchant_id}"


class BankTransferProvider(models.Model):
    """Bank transfer configuration"""
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    account_holder = models.CharField(max_length=100)
    swift_code = models.CharField(max_length=20, blank=True)
    branch_code = models.CharField(max_length=20, blank=True)
    instructions = models.TextField(help_text="Payment instructions for customers")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.bank_name} - {self.account_number}"


class Payment(models.Model):
    """Payment record for orders and subscriptions - Professional payment tracking"""
    
    # Identifiers
    payment_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=False, db_index=True)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment', null=True, blank=True)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    
    # Payment details
    payment_method = models.CharField(
        max_length=50,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CASH_ON_DELIVERY,
        db_index=True
    )
    payment_type = models.CharField(
        max_length=30,
        choices=PaymentType.choices,
        default=PaymentType.ORDER_PAYMENT
    )
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        db_index=True
    )
    
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    # Currency
    currency = models.CharField(max_length=3, default='RWF')
    
    # Mobile money fields
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        validators=[RegexValidator(r'^\+?[0-9]{9,15}$', 'Invalid phone number')],
        help_text="Phone number for mobile money"
    )
    
    # Bank transfer fields
    account_number = models.CharField(max_length=50, blank=True, help_text="Account number for bank transfer")
    bank_provider = models.ForeignKey(
        BankTransferProvider,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments'
    )
    
    # Transaction tracking
    transaction_id = models.CharField(max_length=100, db_index=True, help_text="Gateway transaction ID")
    transaction_reference = models.CharField(max_length=100, blank=True, db_index=True, help_text="Customer-facing reference")
    transaction_status = models.CharField(
        max_length=25,
        choices=TransactionStatus.choices,
        default=TransactionStatus.INITIATED
    )
    
    # Gateway integration
    gateway_name = models.CharField(max_length=50, blank=True)
    gateway_response = models.JSONField(null=True, blank=True, help_text="Full gateway response")
    payment_link = models.URLField(blank=True, help_text="Redirect URL for hosted payment")
    
    # Invoice details
    invoice_number = models.CharField(max_length=50, db_index=True, blank=True)
    invoice_generated = models.BooleanField(default=False)
    
    # Reconciliation
    reconciled = models.BooleanField(default=False, help_text="Has payment been reconciled with bank?")
    reconciled_at = models.DateTimeField(null=True, blank=True)
    
    # Notes
    notes = models.TextField(blank=True, help_text="Internal payment notes")
    customer_notes = models.TextField(blank=True, help_text="Notes for customer")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    processing_started_at = models.DateTimeField(null=True, blank=True)
    
    @property
    def user(self):
        """Get the user associated with this payment"""
        if self.order:
            return self.order.user
        if self.subscription:
            return self.subscription.user
        return None

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['payment_method', 'status']),
            models.Index(fields=['reconciled', '-created_at']),
        ]
    
    def __str__(self):
        if self.order:
            return f"Payment {self.payment_id} - Order {self.order.order_number}"
        return f"Payment {self.payment_id} - {self.get_payment_method_display()}"
    
    def get_status_badge_color(self):
        """Bootstrap color for status display"""
        colors = {
            PaymentStatus.PENDING: 'warning',
            PaymentStatus.PROCESSING: 'info',
            PaymentStatus.COMPLETED: 'success',
            PaymentStatus.FAILED: 'danger',
            PaymentStatus.CANCELLED: 'secondary',
            PaymentStatus.REFUNDED: 'warning',
        }
        return colors.get(self.status, 'secondary')
    
    def generate_invoice_number(self):
        """Generate unique invoice number"""
        if not self.invoice_number:
            from django.utils import timezone
            prefix = 'INV'
            date_part = timezone.now().strftime('%Y%m%d')
            count = Payment.objects.filter(
                created_at__date=timezone.now().date(),
                invoice_number__startswith=prefix
            ).count() + 1
            self.invoice_number = f"{prefix}-{date_part}-{count:05d}"
    
    def mark_as_completed(self):
        """Mark payment as completed and generate invoice"""
        from django.utils import timezone
        self.status = PaymentStatus.COMPLETED
        self.transaction_status = TransactionStatus.CONFIRMED
        self.paid_at = timezone.now()
        if not self.invoice_number:
            self.generate_invoice_number()
        self.save()
    
    def mark_as_failed(self, error_message=''):
        """Mark payment as failed"""
        self.status = PaymentStatus.FAILED
        self.transaction_status = TransactionStatus.FAILED
        if error_message:
            self.notes += f"\n[FAILED] {error_message}"
        self.save()
    
    def mark_as_refunded(self, refund_reason=''):
        """Mark payment as refunded"""
        self.status = PaymentStatus.REFUNDED
        if refund_reason:
            self.notes += f"\n[REFUNDED] {refund_reason}"
        self.save()
    
    @property
    def is_paid(self):
        return self.status == PaymentStatus.COMPLETED
    
    @property
    def is_pending(self):
        return self.status in [PaymentStatus.PENDING, PaymentStatus.PROCESSING]


class PaymentTransaction(models.Model):
    """Detailed transaction log for payment gateway interactions"""
    
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='transactions')
    transaction_id = models.CharField(max_length=100, db_index=True)
    gateway_name = models.CharField(max_length=50)
    
    # Request details
    request_type = models.CharField(
        max_length=50,
        choices=[
            ('INITIATE', 'Initiate Payment'),
            ('QUERY', 'Query Status'),
            ('CONFIRM', 'Confirm Payment'),
            ('CANCEL', 'Cancel Payment'),
            ('REFUND', 'Refund Payment'),
        ]
    )
    request_data = models.JSONField(help_text="Sanitized request data sent to gateway")
    
    # Response details
    response_data = models.JSONField(null=True, blank=True, help_text="Full response from gateway")
    response_code = models.CharField(max_length=10, blank=True)
    response_message = models.TextField(blank=True)
    
    # Status tracking
    status = models.CharField(max_length=25, choices=TransactionStatus.choices)
    success = models.BooleanField(default=False)
    
    # Timestamps
    request_at = models.DateTimeField(auto_now_add=True, db_index=True)
    response_at = models.DateTimeField(null=True, blank=True)
    processing_time_ms = models.IntegerField(null=True, blank=True, help_text="Processing time in milliseconds")
    
    # Error tracking
    error_code = models.CharField(max_length=50, blank=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-request_at']
        indexes = [
            models.Index(fields=['-request_at']),
            models.Index(fields=['payment', 'gateway_name']),
        ]
    
    def __str__(self):
        return f"{self.gateway_name} - {self.request_type} - {self.transaction_id}"


class Invoice(models.Model):
    """Professional invoice generation and tracking"""
    
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='invoice')
    invoice_number = models.CharField(max_length=50, unique=True, db_index=True)
    
    # Invoice details
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Payment terms
    issued_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    notes = models.TextField(blank=True)
    
    # PDF storage
    pdf_file = models.FileField(upload_to='invoices/', blank=True, null=True)
    
    # Status
    is_paid = models.BooleanField(default=False)
    paid_date = models.DateField(null=True, blank=True)
    
    # Tracking
    sent_to_customer = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-issued_date']
    
    def __str__(self):
        return f"Invoice {self.invoice_number}"
    
    @property
    def is_overdue(self):
        from datetime import date
        return not self.is_paid and date.today() > self.due_date


class PaymentReconciliation(models.Model):
    """Payment reconciliation with bank/gateway statements"""
    
    # File details
    file_name = models.CharField(max_length=255)
    file_upload = models.FileField(upload_to='reconciliation_files/')
    
    # Provider
    provider = models.CharField(
        max_length=50,
        choices=[
            ('AIRTEL', 'Airtel Money'),
            ('MTN', 'MTN Mobile Money'),
            ('BANK', 'Bank Transfer'),
        ]
    )
    
    # Reconciliation period
    statement_date = models.DateField()
    statement_period_start = models.DateField()
    statement_period_end = models.DateField()
    
    # Summary
    total_transactions = models.IntegerField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    matched_count = models.IntegerField(default=0)
    unmatched_count = models.IntegerField(default=0)
    discrepancy_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Status
    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETE', 'Reconciliation Complete'),
        ('DISCREPANCY', 'Discrepancy Found'),
        ('RESOLVED', 'Resolved'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reconciled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    reconciled_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-statement_date']
    
    def __str__(self):
        return f"{self.provider} - {self.statement_date}"


class RefundRequest(models.Model):
    """Refund request and tracking"""
    
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refund_requests')
    
    # Refund details
    reason = models.TextField(help_text="Reason for refund")
    refund_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    # Status tracking
    STATUS_CHOICES = [
        ('REQUESTED', 'Requested'),
        ('APPROVED', 'Approved'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('REJECTED', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='REQUESTED')
    
    # Processing
    refund_transaction_id = models.CharField(max_length=100, blank=True, db_index=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_refunds')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Response
    response_notes = models.TextField(blank=True)
    refund_completed_at = models.DateTimeField(null=True, blank=True)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Refund - {self.payment.payment_id} - {self.status}"

