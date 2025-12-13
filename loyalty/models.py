from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class TransactionType(models.TextChoices):
    EARNED = 'earned', 'Earned'
    REDEEMED = 'redeemed', 'Redeemed'
    EXPIRED = 'expired', 'Expired'
    ADJUSTED = 'adjusted', 'Adjusted'


class LoyaltyPoints(models.Model):
    """User's loyalty points balance"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='loyalty_points'
    )
    total_points = models.PositiveIntegerField(
        default=0,
        help_text="Total points currently available"
    )
    lifetime_points = models.PositiveIntegerField(
        default=0,
        help_text="Total points earned over lifetime"
    )
    points_redeemed = models.PositiveIntegerField(
        default=0,
        help_text="Total points redeemed"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Loyalty Points"
        verbose_name_plural = "Loyalty Points"
        ordering = ['-total_points']
    
    def __str__(self):
        return f"{self.user.username} - {self.total_points} points"
    
    def add_points(self, points, reason="", order=None):
        """Add points to user's balance"""
        if points <= 0:
            return False
        
        self.total_points += points
        self.lifetime_points += points
        self.save()
        
        # Create transaction record
        PointsTransaction.objects.create(
            user=self.user,
            points=points,
            transaction_type=TransactionType.EARNED,
            reason=reason,
            order=order
        )
        return True
    
    def redeem_points(self, points, reason=""):
        """Redeem points from user's balance"""
        if points <= 0 or points > self.total_points:
            return False
        
        self.total_points -= points
        self.points_redeemed += points
        self.save()
        
        # Create transaction record
        PointsTransaction.objects.create(
            user=self.user,
            points=-points,  # Negative for redemption
            transaction_type=TransactionType.REDEEMED,
            reason=reason
        )
        return True
    
    def calculate_points_from_order(self, order_total):
        """Calculate points earned from order total
        Default: 1 point per 100 RWF spent
        """
        points_per_100 = 1  # Can be made configurable
        points = int(order_total / 100 * points_per_100)
        return max(0, points)  # Ensure non-negative


class PointsTransaction(models.Model):
    """Transaction history for loyalty points"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='points_transactions'
    )
    points = models.IntegerField(
        help_text="Points amount (positive for earned, negative for redeemed)"
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices,
        default=TransactionType.EARNED
    )
    reason = models.CharField(
        max_length=200,
        blank=True,
        help_text="Reason for transaction (e.g., 'Order completed', 'Points redeemed')"
    )
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='points_transactions',
        help_text="Related order if points earned from order"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        sign = "+" if self.points >= 0 else ""
        return f"{self.user.username} - {sign}{self.points} points - {self.get_transaction_type_display()}"
    
    @property
    def is_earned(self):
        """Check if this is an earned transaction"""
        return self.transaction_type == TransactionType.EARNED
    
    @property
    def is_redeemed(self):
        """Check if this is a redeemed transaction"""
        return self.transaction_type == TransactionType.REDEEMED


class PointsRedemption(models.Model):
    """Available redemption options for points"""
    name = models.CharField(max_length=200)
    description = models.TextField()
    points_required = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Points required for this redemption"
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Discount amount in RWF (if applicable)"
    )
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Discount percentage (if applicable)"
    )
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['points_required']
    
    def __str__(self):
        return f"{self.name} - {self.points_required} points"
    
    def apply_discount(self, order_total):
        """Apply discount to order total"""
        if self.discount_amount:
            return min(self.discount_amount, order_total)
        elif self.discount_percentage:
            discount = order_total * (self.discount_percentage / 100)
            return min(discount, order_total)
        return Decimal('0.00')
