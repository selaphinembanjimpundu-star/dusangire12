from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from menu.models import MenuItem
from django.db.models import Avg
import uuid
from django.utils import timezone



class PlanType(models.TextChoices):
    DAILY = 'daily', 'Daily'
    WEEKLY = 'weekly', 'Weekly'
    MONTHLY = 'monthly', 'Monthly'


class SubscriptionStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    PAUSED = 'paused', 'Paused'
    CANCELLED = 'cancelled', 'Cancelled'
    EXPIRED = 'expired', 'Expired'


class PlanCategory(models.TextChoices):
    GENERAL = 'general', 'General'
    DETOX = 'detox', 'Detox'
    KETO = 'keto', 'Keto'
    DIABETIC = 'diabetic', 'Diabetic-Friendly'
    VEGAN = 'vegan', 'Vegan'
    ATHLETE = 'athlete', 'Athlete/Performance'


class SubscriptionPlan(models.Model):
    """Subscription meal plan templates"""
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    category = models.CharField(
        max_length=20,
        choices=PlanCategory.choices,
        default=PlanCategory.GENERAL
    )
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


class Subscription(models.Model):
    """User's active subscription - Professional subscription management"""
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
    dietary_preferences = models.TextField(
        blank=True, 
        help_text="Dietary preferences for meal selection (e.g., vegetarian, diabetic-friendly)"
    )
    
    # Meal preferences
    preferred_meals = models.ManyToManyField(
        MenuItem,
        blank=True,
        related_name='preferred_subscriptions',
        help_text="User's preferred meals for this subscription"
    )
    
    # Auto-order settings
    auto_order_enabled = models.BooleanField(
        default=True, 
        help_text="Automatically create orders"
    )
    auto_renewal_enabled = models.BooleanField(
        default=False,
        help_text="Automatically renew subscription when it expires"
    )
    
    # Delivery address (cached for performance)
    delivery_address_id = models.IntegerField(null=True, blank=True, help_text="Cached delivery address ID")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status', '-created_at']),
            models.Index(fields=['status', 'end_date']),
            models.Index(fields=['auto_order_enabled', 'status']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"
    
    def is_active(self):
        """Check if subscription is currently active"""
        today = timezone.now().date()
        return (
            self.status == SubscriptionStatus.ACTIVE and
            self.start_date <= today <= self.end_date
        )
    
    def days_remaining(self):
        """Calculate days remaining in subscription"""
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
        self.status = SubscriptionStatus.CANCELLED
        self.cancelled_at = timezone.now()
        self.auto_renewal_enabled = False
        self.save()
        
        # Update plan subscriber count
        self.plan.subscribers_count = max(0, self.plan.subscribers_count - 1)
        self.plan.save(update_fields=['subscribers_count'])
    
    def renew(self):
        """Renew subscription for another period"""
        from datetime import timedelta
        if self.status != SubscriptionStatus.ACTIVE:
            raise ValueError("Can only renew active subscriptions")
        
        # Extend end date by plan duration
        new_end_date = self.end_date + timedelta(days=self.plan.duration_days)
        self.end_date = new_end_date
        self.next_billing_date = new_end_date
        self.save()
        
        return self


class SubscriptionOrder(models.Model):
    """Orders generated from subscriptions"""
    subscription = models.ForeignKey(
        Subscription,  # CHANGED FROM UserSubscription TO Subscription
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


# ========================= PHASE 2.2 MODELS =========================


class VIPTierLevel(models.TextChoices):
    """VIP tier progression"""
    BRONZE = 'bronze', 'Bronze'
    SILVER = 'silver', 'Silver'
    GOLD = 'gold', 'Gold'
    PLATINUM = 'platinum', 'Platinum'


class VIPTier(models.Model):
    """VIP tier system for customer loyalty"""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='vip_tier'
    )
    
    tier_level = models.CharField(
        max_length=20,
        choices=VIPTierLevel.choices,
        default=VIPTierLevel.BRONZE
    )
    
    # Spending tracking (Year-to-Date)
    spending_ytd = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Year-to-date spending in RWF"
    )
    spending_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Total lifetime spending"
    )
    
    # Loyalty promotion
    promotion_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Extra loyalty points percentage (e.g., 5 for +5%)"
    )
    
    # Access level
    access_level = models.PositiveIntegerField(
        default=1,
        help_text="1=Bronze, 2=Silver, 3=Gold, 4=Platinum"
    )
    
    # Status tracking
    achieved_at = models.DateField(help_text="When tier was achieved")
    next_tier_threshold = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Spending needed for next tier"
    )
    
    # Benefits JSON
    benefits_list = models.JSONField(
        default=dict,
        blank=True,
        help_text="Tier benefits (JSON)"
    )
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "VIP Tiers"
    
    def __str__(self):
        return f"{self.user.username} - {self.get_tier_level_display()}"
    
    def get_tier_display_color(self):
        """Get color for tier display"""
        colors = {
            'bronze': '#CD7F32',
            'silver': '#C0C0C0',
            'gold': '#FFD700',
            'platinum': '#E5E4E2',
        }
        return colors.get(self.tier_level, '#999999')
    
    def get_benefits(self):
        """Get tier benefits"""
        benefits_map = {
            VIPTierLevel.BRONZE: {
                'loyalty_bonus': 2,
                'discount': 0,
                'perks': ['Early access to new meals', 'Monthly newsletter']
            },
            VIPTierLevel.SILVER: {
                'loyalty_bonus': 5,
                'discount': 5,
                'perks': ['5% subscription discount', 'Priority support', 'Quarterly health review']
            },
            VIPTierLevel.GOLD: {
                'loyalty_bonus': 10,
                'discount': 10,
                'perks': ['10% subscription discount', 'VIP support hotline', 'Free monthly consultation', 'Exclusive meals']
            },
            VIPTierLevel.PLATINUM: {
                'loyalty_bonus': 15,
                'discount': 15,
                'perks': ['15% subscription discount', '24/7 concierge', 'Free bi-weekly consultation', 'Exclusive meals', 'Birthday bonus (RWF 50K)']
            },
        }
        return benefits_map.get(self.tier_level, {})


class LoyaltyPoints(models.Model):
    """Customer loyalty points system - 1 point = RWF 100"""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='subscription_loyalty_points'
    )
    
    # Points balance
    balance = models.PositiveIntegerField(
        default=0,
        help_text="Current loyalty points balance"
    )
    earned_total = models.PositiveIntegerField(
        default=0,
        help_text="Total points earned (lifetime)"
    )
    redeemed_total = models.PositiveIntegerField(
        default=0,
        help_text="Total points redeemed (lifetime)"
    )
    
    # Bonus settings
    subscription_bonus_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.0,
        help_text="Multiplier for earning points (1.0 = 1pt per 100RWF, 1.05 = 5% bonus)"
    )
    
    # Expiration
    expires_at = models.DateField(
        null=True,
        blank=True,
        help_text="Points expiration date (null = no expiration)"
    )
    
    # Tracking
    last_activity_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Loyalty Points"
    
    def __str__(self):
        return f"{self.user.username} - {self.balance} points (RWF {self.balance * 100})"
    
    def add_points(self, amount, reason=''):
        """Add loyalty points"""
        self.balance += amount
        self.earned_total += amount
        self.save()
        
        LoyaltyTransaction.objects.create(
            user=self.user,
            transaction_type='EARN',
            points_amount=amount,
            description=reason,
            balance_before=self.balance - amount,
            balance_after=self.balance
        )
    
    def redeem_points(self, amount, reason=''):
        """Redeem loyalty points"""
        if self.balance < amount:
            raise ValueError("Insufficient loyalty points")
        
        self.balance -= amount
        self.redeemed_total += amount
        self.save()
        
        LoyaltyTransaction.objects.create(
            user=self.user,
            transaction_type='REDEEM',
            points_amount=amount,
            description=reason,
            balance_before=self.balance + amount,
            balance_after=self.balance
        )
    
    @property
    def value_in_rwf(self):
        """Get point value in RWF (1 point = 100 RWF)"""
        return self.balance * 100


class LoyaltyTransaction(models.Model):
    """Loyalty points transaction history"""
    
    TRANSACTION_TYPES = [
        ('EARN', 'Points Earned'),
        ('REDEEM', 'Points Redeemed'),
        ('BONUS', 'Bonus Points'),
        ('ADJUSTMENT', 'Admin Adjustment'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='loyalty_transactions'
    )
    
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES
    )
    
    points_amount = models.PositiveIntegerField()
    description = models.TextField()
    
    # Related objects
    related_subscription = models.ForeignKey(
        Subscription,  # CHANGED FROM UserSubscription TO Subscription
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    related_payment = models.ForeignKey(
        'payments.Payment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Balance tracking
    balance_before = models.PositiveIntegerField()
    balance_after = models.PositiveIntegerField()
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['transaction_type', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_transaction_type_display()} - {self.points_amount} points"


class ReferralProgram(models.Model):
    """Customer referral program"""
    
    REFERRAL_STATUS = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('EXPIRED', 'Expired'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    referrer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='referrals_given'
    )
    
    referee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='referrals_received',
        null=True,
        blank=True
    )
    
    # Referral link
    referral_code = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text="Unique referral code"
    )
    referral_link = models.URLField(blank=True)
    
    # Bonuses
    referrer_bonus_rwf = models.PositiveIntegerField(
        default=10000,
        help_text="Bonus for referrer in RWF"
    )
    referrer_bonus_points = models.PositiveIntegerField(
        default=100,
        help_text="Bonus points for referrer"
    )
    
    referee_discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10,
        help_text="Discount for referee on first purchase (%)"
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=REFERRAL_STATUS,
        default='PENDING'
    )
    
    # Completion tracking
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(help_text="When referral link expires")
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['referrer', 'status']),
            models.Index(fields=['referral_code']),
        ]
    
    def __str__(self):
        return f"{self.referrer.username} referral - {self.referral_code}"
    
    def generate_referral_link(self):
        """Generate shareable referral link"""
        base_url = "https://dusangire.rw"
        self.referral_link = f"{base_url}/refer/{self.referral_code}"
        return self.referral_link


class SubscriptionAutoRenewal(models.Model):
    """Auto-renewal configuration for subscriptions"""
    
    subscription = models.OneToOneField(
        Subscription,  # CHANGED FROM UserSubscription TO Subscription
        on_delete=models.CASCADE,
        related_name='auto_renewal'
    )
    
    auto_renew_enabled = models.BooleanField(default=False)
    
    # Payment settings
    payment_method_id = models.CharField(
        max_length=50,
        blank=True,
        help_text="Saved payment method ID"
    )
    
    # Renewal schedule
    renewal_date = models.DateField(help_text="Next scheduled renewal date")
    renewal_interval_days = models.PositiveIntegerField(
        default=30,
        help_text="Days between renewals"
    )
    
    # Notification
    notification_sent = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When reminder notification was sent"
    )
    notification_days_before = models.PositiveIntegerField(
        default=3,
        help_text="Days before renewal to send notification"
    )
    
    # Retry logic
    failure_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of failed renewal attempts"
    )
    max_retries = models.PositiveIntegerField(
        default=3,
        help_text="Maximum retry attempts"
    )
    next_retry_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When to retry if failed"
    )
    
    # Status
    last_renewal_status = models.CharField(
        max_length=50,
        blank=True,
        help_text="Status of last renewal attempt"
    )
    last_renewal_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When last renewal was processed"
    )
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Subscription Auto-Renewals"
    
    def __str__(self):
        return f"Auto-renewal for {self.subscription.user.username}"
    
    def is_renewal_due(self):
        """Check if renewal is due"""
        return timezone.now().date() >= self.renewal_date
    
    def should_send_notification(self):
        """Check if reminder notification should be sent"""
        from datetime import timedelta
        days_until_renewal = (self.renewal_date - timezone.now().date()).days
        return (
            0 < days_until_renewal <= self.notification_days_before and
            self.notification_sent is None
        )