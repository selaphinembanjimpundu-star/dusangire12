from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum, Avg, Count
from django.utils import timezone
from decimal import Decimal

class DailyAnalyticsSnapshot(models.Model):
    """Daily snapshot of key metrics for historical tracking"""
    date = models.DateField(unique=True, db_index=True)
    
    # Order metrics
    total_orders = models.IntegerField(default=0)
    unique_customers = models.IntegerField(default=0)
    
    # Revenue metrics
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_discount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Order breakdown
    vip_orders = models.IntegerField(default=0)
    subscription_orders = models.IntegerField(default=0)
    referral_orders = models.IntegerField(default=0)
    
    # Payment method breakdown
    cash_orders = models.IntegerField(default=0)
    mobile_money_orders = models.IntegerField(default=0)
    bank_transfer_orders = models.IntegerField(default=0)
    card_orders = models.IntegerField(default=0)
    
    # Discount tracking
    vip_discounts_given = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    loyalty_discounts_given = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    referral_discounts_given = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name = 'Daily Analytics Snapshot'
        verbose_name_plural = 'Daily Analytics Snapshots'
    
    def __str__(self):
        return f"Analytics for {self.date}"


class RevenueStream(models.Model):
    """Track revenue by different channels/sources"""
    CHANNEL_CHOICES = [
        ('direct_order', 'Direct Meal Orders'),
        ('subscription', 'Subscription Plans'),
        ('vip_upgrade', 'VIP Tier Upgrade'),
        ('corporate', 'Corporate Contracts'),
        ('catering', 'Catering Services'),
        ('referral', 'Referral Bonuses'),
        ('loyalty', 'Loyalty Redemptions'),
    ]
    
    date = models.DateField(db_index=True)
    channel = models.CharField(max_length=50, choices=CHANNEL_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_count = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('date', 'channel')
        ordering = ['-date', '-amount']
        indexes = [
            models.Index(fields=['-date', 'channel']),
        ]
    
    def __str__(self):
        return f"{self.get_channel_display()} - {self.date}: RWF {self.amount}"


class CustomerMetrics(models.Model):
    """Track customer behavior and lifetime value"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_metrics')
    
    # Order history
    total_orders = models.IntegerField(default=0)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Dates
    first_order_date = models.DateTimeField(null=True, blank=True)
    last_order_date = models.DateTimeField(null=True, blank=True)
    days_since_last_order = models.IntegerField(default=0)
    
    # Value metrics
    lifetime_value = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    churn_risk = models.BooleanField(default=False, help_text='No order in 60+ days')
    
    # VIP & Subscription
    vip_tier_current = models.CharField(max_length=20, blank=True, choices=[
        ('Bronze', 'Bronze'),
        ('Silver', 'Silver'),
        ('Gold', 'Gold'),
        ('Platinum', 'Platinum'),
    ])
    subscription_active = models.BooleanField(default=False)
    
    # Loyalty tracking
    loyalty_points_earned = models.IntegerField(default=0)
    loyalty_points_redeemed = models.IntegerField(default=0)
    loyalty_value_redeemed = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # Referral tracking
    referral_count = models.IntegerField(default=0)
    referral_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # Discount benefit tracking
    total_discounts_received = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    vip_discounts_received = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-lifetime_value']
        verbose_name = 'Customer Metrics'
        verbose_name_plural = 'Customer Metrics'
    
    def __str__(self):
        return f"{self.user.username} - LTV: RWF {self.lifetime_value}"
    
    @property
    def repeat_purchase_rate(self):
        """Calculate repeat purchase rate"""
        if self.total_orders <= 1:
            return 0
        return ((self.total_orders - 1) / self.total_orders) * 100


class Campaign(models.Model):
    """Track promotional campaigns"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Campaign details
    discount_type = models.CharField(max_length=50)  # percentage, fixed, etc.
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    target_audience = models.CharField(max_length=100)  # 'vip', 'new_customers', 'referrals', etc.
    
    # Dates
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    # Budget & ROI
    budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Campaign'
        verbose_name_plural = 'Campaigns'
    
    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"
    
    @property
    def is_active(self):
        """Check if campaign is currently active"""
        now = timezone.now()
        return self.status == 'active' and self.start_date <= now <= self.end_date


class CampaignPerformance(models.Model):
    """Track campaign effectiveness and ROI"""
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='performance_history')
    
    # Performance metrics
    orders_influenced = models.IntegerField(default=0)
    revenue_generated = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    customers_reached = models.IntegerField(default=0)
    customers_converted = models.IntegerField(default=0)
    
    # Rate calculations
    conversion_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('0.00'),
        help_text='Percentage of reached customers who converted'
    )
    roi = models.DecimalField(
        max_digits=8, decimal_places=2, default=Decimal('0.00'),
        help_text='Return on investment percentage'
    )
    
    tracked_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-campaign', '-tracked_at']
        verbose_name = 'Campaign Performance'
        verbose_name_plural = 'Campaign Performance'
    
    def __str__(self):
        return f"{self.campaign.name} - {self.tracked_at.date()}"
    
    def calculate_roi(self):
        """Calculate ROI based on budget and revenue"""
        if self.campaign.budget and self.campaign.budget > 0:
            self.roi = ((self.revenue_generated - self.campaign.budget) / self.campaign.budget) * 100
            self.save()


class PageViewAnalytics(models.Model):
    """Track page views for traffic analysis"""
    page_name = models.CharField(max_length=255)
    view_count = models.IntegerField(default=1)
    unique_visitors = models.IntegerField(default=0)
    date = models.DateField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('page_name', 'date')
        ordering = ['-date', '-view_count']
    
    def __str__(self):
        return f"{self.page_name} - {self.view_count} views"


class ConversionEvent(models.Model):
    """Track conversion events (add to cart, checkout, purchase, etc.)"""
    EVENT_TYPES = [
        ('view_menu', 'View Menu'),
        ('add_to_cart', 'Add to Cart'),
        ('start_checkout', 'Start Checkout'),
        ('complete_order', 'Complete Order'),
        ('subscribe', 'Subscribe'),
        ('referral_click', 'Referral Click'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    session_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    metadata = models.JSONField(default=dict, blank=True)  # For extra data
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Conversion Event'
        verbose_name_plural = 'Conversion Events'
        indexes = [
            models.Index(fields=['-timestamp', 'event_type']),
        ]
    
    def __str__(self):
        return f"{self.get_event_type_display()} - {self.timestamp}"
