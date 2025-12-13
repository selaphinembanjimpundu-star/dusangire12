from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from menu.models import MenuItem
from django.db.models import Avg


class PlanType(models.TextChoices):
    DAILY = 'daily', 'Daily'
    WEEKLY = 'weekly', 'Weekly'
    MONTHLY = 'monthly', 'Monthly'


class SubscriptionStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    PAUSED = 'paused', 'Paused'
    CANCELLED = 'cancelled', 'Cancelled'
    EXPIRED = 'expired', 'Expired'


class SubscriptionPlan(models.Model):
    """Subscription meal plan templates"""
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    plan_type = models.CharField(
        max_length=20,
        choices=PlanType.choices,
        default=PlanType.DAILY
    )
    
    # Pricing
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Price per billing cycle"
    )
    
    # Plan details
    meals_per_cycle = models.PositiveIntegerField(
        default=1,
        help_text="Number of meals per billing cycle"
    )
    duration_days = models.PositiveIntegerField(
        help_text="Duration of plan in days (e.g., 30 for monthly)"
    )
    
    # Menu items included (optional - can be specific items or categories)
    menu_items = models.ManyToManyField(
        MenuItem,
        blank=True,
        related_name='subscription_plans',
        help_text="Specific menu items included (leave empty for all items)"
    )
    
    # Availability
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional features
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Discount percentage (e.g., 10.00 for 10% off)"
    )
    is_popular = models.BooleanField(default=False, help_text="Mark as popular plan")
    subscribers_count = models.PositiveIntegerField(default=0, help_text="Number of active subscribers")
    
    class Meta:
        ordering = ['plan_type', 'price']
    
    def __str__(self):
        return f"{self.name} - {self.get_plan_type_display()}"
    
    def get_price_per_meal(self):
        """Calculate price per meal"""
        if self.meals_per_cycle > 0:
            return self.price / self.meals_per_cycle
        return self.price
    
    def calculate_savings(self, regular_price_per_meal=None):
        """Calculate savings compared to regular ordering"""
        if regular_price_per_meal is None:
            # Get average menu item price as baseline
            avg_price = MenuItem.objects.filter(is_available=True).aggregate(
                avg=Avg('price')
            )['avg'] or Decimal('5000.00')  # Default fallback
            regular_price_per_meal = avg_price
        
        subscription_price_per_meal = self.get_price_per_meal()
        savings_per_meal = regular_price_per_meal - subscription_price_per_meal
        savings_percentage = (savings_per_meal / regular_price_per_meal * 100) if regular_price_per_meal > 0 else 0
        
        cycles = self.duration_days // self.get_cycle_days() if self.get_cycle_days() > 0 else 1
        total_savings = savings_per_meal * self.meals_per_cycle * cycles
        
        return {
            'per_meal': savings_per_meal,
            'percentage': savings_percentage,
            'total_savings': total_savings
        }
    
    def get_cycle_days(self):
        """Get number of days per billing cycle"""
        if self.plan_type == PlanType.DAILY:
            return 1
        elif self.plan_type == PlanType.WEEKLY:
            return 7
        elif self.plan_type == PlanType.MONTHLY:
            return 30
        return 1
    
    def get_total_meals(self):
        """Get total meals in subscription duration"""
        cycles = self.duration_days // self.get_cycle_days()
        return cycles * self.meals_per_cycle
    
    def get_discounted_price(self):
        """Get price after discount"""
        if self.discount_percentage > 0:
            discount_amount = self.price * (self.discount_percentage / 100)
            return self.price - discount_amount
        return self.price


class UserSubscription(models.Model):
    """User's active subscription"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT, related_name='user_subscriptions')
    status = models.CharField(
        max_length=20,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.ACTIVE
    )
    
    # Dates
    start_date = models.DateField()
    end_date = models.DateField()
    next_billing_date = models.DateField(null=True, blank=True)
    paused_until = models.DateField(null=True, blank=True, help_text="Resume date if paused")
    
    # Custom preferences
    preferred_delivery_time = models.TimeField(null=True, blank=True, help_text="Preferred delivery time")
    dietary_preferences = models.TextField(blank=True, help_text="Dietary preferences for meal selection")
    
    # Auto-order settings
    auto_order_enabled = models.BooleanField(default=True, help_text="Automatically create orders")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"
    
    def is_active(self):
        """Check if subscription is currently active"""
        from django.utils import timezone
        today = timezone.now().date()
        return (
            self.status == SubscriptionStatus.ACTIVE and
            self.start_date <= today <= self.end_date
        )
    
    def days_remaining(self):
        """Calculate days remaining in subscription"""
        from django.utils import timezone
        today = timezone.now().date()
        if self.end_date > today:
            return (self.end_date - today).days
        return 0
    
    def pause(self):
        """Pause the subscription"""
        self.status = SubscriptionStatus.PAUSED
        self.save()
    
    def resume(self):
        """Resume a paused subscription"""
        if self.status == SubscriptionStatus.PAUSED:
            self.status = SubscriptionStatus.ACTIVE
            self.paused_until = None
            self.save()
    
    def cancel(self):
        """Cancel the subscription"""
        from django.utils import timezone
        self.status = SubscriptionStatus.CANCELLED
        self.cancelled_at = timezone.now()
        self.save()


class SubscriptionOrder(models.Model):
    """Orders generated from subscriptions"""
    subscription = models.ForeignKey(
        UserSubscription,
        on_delete=models.CASCADE,
        related_name='subscription_orders'
    )
    order = models.OneToOneField(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='subscription_order'
    )
    scheduled_date = models.DateField(help_text="Date this order was scheduled for")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-scheduled_date']
    
    def __str__(self):
        return f"Subscription Order for {self.subscription.user.username} - {self.scheduled_date}"
