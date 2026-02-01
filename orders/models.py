from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from menu.models import MenuItem


class Cart(models.Model):
    """Shopping cart for a user"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart for {self.user.username}"
    
    def get_total(self):
        """Calculate total price of all items in cart"""
        return sum(item.get_subtotal() for item in self.items.all())
    
    def get_item_count(self):
        """Get total number of items in cart"""
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    """Individual item in shopping cart"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['cart', 'menu_item']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name}"
    
    def get_subtotal(self):
        """Calculate subtotal for this item"""
        return self.menu_item.price * self.quantity


class OrderStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    CONFIRMED = 'confirmed', 'Confirmed'
    PREPARING = 'preparing', 'Preparing'
    READY = 'ready', 'Ready'
    DELIVERED = 'delivered', 'Delivered'
    CANCELLED = 'cancelled', 'Cancelled'


class Order(models.Model):
    """Customer order"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    
    PAYMENT_METHOD_CHOICES = [
        ('cash_on_delivery', 'Cash on Delivery'),
        ('mtn_mobile_money', 'MTN Mobile Money'),
        ('airtel_money', 'Airtel Money'),
        ('bank_transfer', 'Bank Transfer'),
        ('card', 'Credit/Debit Card'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, default='cash_on_delivery')
    payment_notes = models.TextField(blank=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    account_number = models.CharField(max_length=100, blank=True)
    
    customer_name = models.CharField(max_length=200)
    customer_phone = models.CharField(max_length=20)
    delivery_address = models.TextField()
    delivery_instructions = models.TextField(blank=True)
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    loyalty_points_redeemed = models.PositiveIntegerField(default=0)
    loyalty_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    vip_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    corporate_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    referral_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    coupon_code = models.CharField(max_length=50, blank=True)
    
    # ✅ Corrected: use `total` instead of `total_amount`
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.order_number} - {self.user.username}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            import random, string, uuid
            from django.utils import timezone
            prefix = 'ORD'
            timestamp = timezone.now().strftime('%Y%m%d')
            random_part = ''.join(random.choices(string.digits, k=6))
            self.order_number = f"{prefix}{timestamp}{random_part}"
            
            for _ in range(10):
                if not Order.objects.filter(order_number=self.order_number).exists():
                    break
                random_part = ''.join(random.choices(string.digits, k=6))
                self.order_number = f"{prefix}{timestamp}{random_part}"
            else:
                self.order_number = f"{prefix}{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)
    
    def get_status_display_class(self):
        status_classes = {
            OrderStatus.PENDING: 'warning',
            OrderStatus.CONFIRMED: 'info',
            OrderStatus.PREPARING: 'primary',
            OrderStatus.READY: 'success',
            OrderStatus.DELIVERED: 'success',
            OrderStatus.CANCELLED: 'danger',
        }
        return status_classes.get(self.status, 'secondary')


class OrderItem(models.Model):
    """Individual item in an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # price at time of order
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name} - Order {self.order.order_number}"
    
    def save(self, *args, **kwargs):
        self.subtotal = self.price * self.quantity
        super().save(*args, **kwargs)
