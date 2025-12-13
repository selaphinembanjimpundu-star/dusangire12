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
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING
    )
    
    # Customer information (can be different from user profile)
    customer_name = models.CharField(max_length=200)
    customer_phone = models.CharField(max_length=20)
    delivery_address = models.TextField()
    delivery_instructions = models.TextField(blank=True)
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.order_number} - {self.user.username}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate unique order number using timestamp + random
            import random
            import string
            from django.utils import timezone
            prefix = 'ORD'
            # Use timestamp (YYYYMMDD) + random 6 digits for better uniqueness
            timestamp = timezone.now().strftime('%Y%m%d')
            random_part = ''.join(random.choices(string.digits, k=6))
            self.order_number = f"{prefix}{timestamp}{random_part}"
            
            # Ensure uniqueness (retry if collision)
            max_retries = 10
            retry_count = 0
            while Order.objects.filter(order_number=self.order_number).exists() and retry_count < max_retries:
                random_part = ''.join(random.choices(string.digits, k=6))
                self.order_number = f"{prefix}{timestamp}{random_part}"
                retry_count += 1
            
            if retry_count >= max_retries:
                # Fallback to UUID-based if still collision
                import uuid
                self.order_number = f"{prefix}{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)
    
    def get_status_display_class(self):
        """Return Bootstrap class for status badge"""
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
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Store price at time of order
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name} - Order {self.order.order_number}"
    
    def save(self, *args, **kwargs):
        # Calculate subtotal before saving
        self.subtotal = self.price * self.quantity
        super().save(*args, **kwargs)
