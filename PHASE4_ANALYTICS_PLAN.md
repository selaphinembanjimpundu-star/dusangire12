# Phase 4: Advanced Analytics & Revenue Dashboard - Implementation Plan

**Date**: January 22, 2026  
**Status**: Building comprehensive analytics layer  
**Scope**: Integrate all existing systems with professional dashboards

---

## 📊 PHASE 4 OVERVIEW

### What We're Building
A comprehensive **analytics and business intelligence layer** that aggregates data from all existing systems (Phase 1-3) and provides real-time insights for business decision-making.

### Systems to Integrate
✅ Orders (Phase 3)  
✅ Payments (Phase 2.1)  
✅ VIP & Loyalty (Phase 2.2)  
✅ Subscriptions (Phase 2)  
✅ Corporate (Phase 4)  
✅ Catering (Phase 4)  
✅ Nutritionist (Phase 4)  
✅ Support (Phase 4)  
✅ Health Profiles (Phase 1)  
✅ Delivery (Phase 1)  

---

## 🎯 PHASE 4 OBJECTIVES

### 1. **Analytics Dashboard** (Executive View)
- Revenue tracking (daily, weekly, monthly, yearly)
- Customer metrics (acquisition, retention, lifetime value)
- Discount impact analysis
- Payment method breakdown
- Order trends

### 2. **Revenue Stream Analysis**
Track revenue from:
- Direct meal orders
- Subscription plans
- VIP tier upgrades
- Corporate contracts
- Catering services
- Referral bonuses
- Loyalty redemptions

### 3. **Customer Insights Dashboard**
- Customer segmentation (by VIP tier, subscription status, spending)
- Churn analysis
- Repeat purchase rate
- Average order value trends
- Loyalty program effectiveness

### 4. **Operational Metrics**
- Kitchen efficiency
- Delivery performance
- Nutritionist consultation bookings
- Support ticket resolution
- Staff performance

### 5. **Campaign Management**
- Promotional effectiveness
- A/B testing for discounts
- Email campaign tracking
- Referral program tracking
- Corporate contract performance

---

## 📁 NEW MODELS TO CREATE

### analytics/models.py

```python
# Dashboard snapshots for historical tracking
class DailyAnalyticsSnapshot(models.Model):
    """Daily snapshot of key metrics"""
    date = models.DateField(unique=True, auto_now_add=True)
    total_orders = models.IntegerField()
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2)
    total_discount = models.DecimalField(max_digits=12, decimal_places=2)
    unique_customers = models.IntegerField()
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2)
    vip_orders = models.IntegerField()
    subscription_orders = models.IntegerField()
    cash_orders = models.IntegerField()
    mobile_money_orders = models.IntegerField()
    bank_transfer_orders = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

# Revenue tracking by channel
class RevenueStream(models.Model):
    """Track revenue by different channels"""
    CHANNEL_CHOICES = [
        ('direct_order', 'Direct Meal Orders'),
        ('subscription', 'Subscription Plans'),
        ('vip_upgrade', 'VIP Tier Upgrade'),
        ('corporate', 'Corporate Contracts'),
        ('catering', 'Catering Services'),
        ('referral', 'Referral Bonuses'),
        ('loyalty', 'Loyalty Redemptions'),
    ]
    
    date = models.DateField()
    channel = models.CharField(max_length=50, choices=CHANNEL_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_count = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('date', 'channel')

# Customer metrics tracking
class CustomerMetrics(models.Model):
    """Track customer behavior and value"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='metrics')
    total_orders = models.IntegerField(default=0)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    last_order_date = models.DateTimeField(null=True, blank=True)
    first_order_date = models.DateTimeField(null=True, blank=True)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    lifetime_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    days_since_last_order = models.IntegerField(default=0)
    churn_risk = models.BooleanField(default=False)
    vip_tier_current = models.CharField(max_length=20, blank=True)
    subscription_active = models.BooleanField(default=False)
    loyalty_points_earned = models.IntegerField(default=0)
    loyalty_points_redeemed = models.IntegerField(default=0)
    referral_count = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

# Campaign tracking
class Campaign(models.Model):
    """Track promotional campaigns"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    discount_type = models.CharField(max_length=50)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    target_audience = models.CharField(max_length=100)
    budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# Campaign performance tracking
class CampaignPerformance(models.Model):
    """Track campaign effectiveness"""
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='performance')
    orders_influenced = models.IntegerField(default=0)
    revenue_generated = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    customers_reached = models.IntegerField(default=0)
    conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    roi = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    tracked_at = models.DateTimeField(auto_now=True)
```

---

## 🔧 NEW VIEWS & LOGIC

### analytics/views.py

#### 1. Main Analytics Dashboard
```python
def analytics_dashboard(request):
    """Main analytics dashboard with key metrics"""
    # Time period selection
    period = request.GET.get('period', 'month')  # day, week, month, year
    
    # Get date range
    if period == 'day':
        start_date = today() - timedelta(days=1)
    elif period == 'week':
        start_date = today() - timedelta(days=7)
    elif period == 'month':
        start_date = today() - timedelta(days=30)
    else:
        start_date = today() - timedelta(days=365)
    
    # Revenue analytics
    revenue_data = get_revenue_analytics(start_date)
    customer_metrics = get_customer_metrics(start_date)
    discount_impact = get_discount_impact(start_date)
    payment_breakdown = get_payment_breakdown(start_date)
    
    context = {
        'revenue_data': revenue_data,
        'customer_metrics': customer_metrics,
        'discount_impact': discount_impact,
        'payment_breakdown': payment_breakdown,
        'period': period,
    }
    return render(request, 'analytics/dashboard.html', context)
```

#### 2. Revenue Stream Analysis
```python
def revenue_streams(request):
    """Track revenue by channel"""
    streams = RevenueStream.objects.filter(
        date__gte=today() - timedelta(days=30)
    ).values('channel').annotate(
        total=Sum('amount'),
        count=Sum('transaction_count')
    ).order_by('-total')
    
    context = {
        'revenue_streams': streams,
        'chart_data': format_for_chart(streams),
    }
    return render(request, 'analytics/revenue_streams.html', context)
```

#### 3. Customer Analytics
```python
def customer_analytics(request):
    """Customer behavior and segmentation"""
    # VIP tier distribution
    vip_distribution = CustomerMetrics.objects.values(
        'vip_tier_current'
    ).annotate(count=Count('id'))
    
    # Churn analysis
    churn_risk_customers = CustomerMetrics.objects.filter(churn_risk=True)
    
    # Lifetime value segments
    ltv_segments = CustomerMetrics.objects.values().annotate(
        ltv_segment=Case(
            When(lifetime_value__lt=10000, then=Value('0-10K')),
            When(lifetime_value__lt=50000, then=Value('10-50K')),
            When(lifetime_value__gte=50000, then=Value('50K+')),
        )
    ).values('ltv_segment').annotate(count=Count('id'))
    
    context = {
        'vip_distribution': vip_distribution,
        'churn_risk_customers': churn_risk_customers,
        'ltv_segments': ltv_segments,
    }
    return render(request, 'analytics/customer_analytics.html', context)
```

#### 4. Campaign Management
```python
def campaigns(request):
    """View and manage promotional campaigns"""
    campaigns = Campaign.objects.all().prefetch_related('performance')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        campaigns = campaigns.filter(status=status)
    
    context = {
        'campaigns': campaigns,
        'total_budget': campaigns.aggregate(Sum('budget')),
    }
    return render(request, 'analytics/campaigns.html', context)

def campaign_detail(request, campaign_id):
    """Campaign performance details"""
    campaign = Campaign.objects.get(id=campaign_id)
    performance = campaign.performance.latest('tracked_at')
    
    context = {
        'campaign': campaign,
        'performance': performance,
    }
    return render(request, 'analytics/campaign_detail.html', context)
```

---

## 📊 ANALYTICS SERVICES

### analytics/services.py

```python
class AnalyticsService:
    """Service for calculating analytics metrics"""
    
    @staticmethod
    def calculate_daily_snapshot():
        """Calculate daily metrics snapshot"""
        today = timezone.now().date()
        
        orders = Order.objects.filter(created_at__date=today)
        
        snapshot = DailyAnalyticsSnapshot.objects.create(
            date=today,
            total_orders=orders.count(),
            total_revenue=orders.aggregate(Sum('total'))['total__sum'],
            total_discount=orders.aggregate(Sum('discount_amount'))['discount_amount__sum'],
            unique_customers=orders.values('user').distinct().count(),
            average_order_value=orders.aggregate(Avg('total'))['total__avg'],
            vip_orders=orders.filter(user__viptier__isnull=False).count(),
            subscription_orders=orders.filter(user__subscription__status='ACTIVE').count(),
            cash_orders=orders.filter(payment_method='cash_on_delivery').count(),
            mobile_money_orders=orders.filter(
                payment_method__in=['mtn_mobile_money', 'airtel_money']
            ).count(),
            bank_transfer_orders=orders.filter(payment_method='bank_transfer').count(),
        )
        return snapshot
    
    @staticmethod
    def update_customer_metrics(user):
        """Update customer metrics for a user"""
        orders = Order.objects.filter(user=user, status='delivered')
        
        metrics, created = CustomerMetrics.objects.get_or_create(user=user)
        metrics.total_orders = orders.count()
        metrics.total_spent = orders.aggregate(Sum('total'))['total__sum'] or 0
        metrics.first_order_date = orders.order_by('created_at').first().created_at
        metrics.last_order_date = orders.order_by('-created_at').first().created_at
        metrics.average_order_value = orders.aggregate(Avg('total'))['total__avg'] or 0
        metrics.lifetime_value = metrics.total_spent
        
        # Churn detection
        days_since_order = (timezone.now() - metrics.last_order_date).days
        metrics.days_since_last_order = days_since_order
        metrics.churn_risk = days_since_order > 60  # No order in 60+ days
        
        # VIP tier
        try:
            metrics.vip_tier_current = user.viptier.get_tier_level_display()
        except:
            metrics.vip_tier_current = None
        
        # Subscription status
        metrics.subscription_active = user.subscription_set.filter(
            status='ACTIVE'
        ).exists()
        
        metrics.save()
        return metrics
    
    @staticmethod
    def track_revenue_stream(channel, amount):
        """Track revenue by channel"""
        today = timezone.now().date()
        stream, created = RevenueStream.objects.get_or_create(
            date=today,
            channel=channel
        )
        stream.amount += amount
        stream.transaction_count += 1
        stream.save()
```

---

## 📈 MANAGEMENT COMMANDS

### analytics/management/commands/update_analytics.py

```python
from django.core.management.base import BaseCommand
from analytics.services import AnalyticsService

class Command(BaseCommand):
    help = 'Update analytics metrics'
    
    def handle(self, *args, **options):
        self.stdout.write("Updating analytics...")
        
        # Daily snapshot
        AnalyticsService.calculate_daily_snapshot()
        
        # Customer metrics
        from accounts.models import User
        for user in User.objects.filter(is_active=True):
            AnalyticsService.update_customer_metrics(user)
        
        self.stdout.write(self.style.SUCCESS('Analytics updated successfully'))
```

---

## 🎨 DASHBOARD TEMPLATES

### templates/analytics/dashboard.html
- Key metrics cards (Revenue, Orders, Customers, AOV)
- Revenue trends chart (line graph)
- Order status breakdown (pie chart)
- Payment method distribution
- Top 10 items sold
- Recent orders table
- Customer acquisition vs retention

### templates/analytics/revenue_streams.html
- Revenue by channel (bar chart)
- Channel comparison
- Monthly trend for each channel
- Performance metrics per channel

### templates/analytics/customer_analytics.html
- VIP tier distribution
- Churn risk customers list
- Lifetime value segments
- Retention rate trend
- Repeat purchase rate

### templates/analytics/campaigns.html
- Active campaigns list
- Campaign ROI comparison
- Campaign performance metrics
- Create/edit campaign form

---

## 🔗 INTEGRATION WITH EXISTING SYSTEMS

### Signal Handlers (signals.py)

```python
@receiver(post_save, sender=Order)
def track_order_revenue(sender, instance, created, **kwargs):
    """Track revenue when order is created"""
    if created and instance.payment_status == 'completed':
        AnalyticsService.track_revenue_stream(
            'direct_order',
            instance.total
        )

@receiver(post_save, sender=Payment)
def update_customer_after_payment(sender, instance, **kwargs):
    """Update customer metrics after payment"""
    if instance.status == 'completed':
        AnalyticsService.update_customer_metrics(instance.user)
```

---

## 📋 URLS

### analytics/urls.py

```python
urlpatterns = [
    path('dashboard/', views.analytics_dashboard, name='dashboard'),
    path('revenue-streams/', views.revenue_streams, name='revenue_streams'),
    path('customers/', views.customer_analytics, name='customer_analytics'),
    path('campaigns/', views.campaigns, name='campaigns'),
    path('campaigns/<int:campaign_id>/', views.campaign_detail, name='campaign_detail'),
    path('api/metrics/', views.api_metrics, name='api_metrics'),
]
```

---

## 📊 ANALYTICS CALCULATIONS

### Key Metrics to Track

1. **Revenue Metrics**
   - Daily/Weekly/Monthly/Yearly total
   - Revenue by channel
   - Revenue by VIP tier
   - Revenue by payment method

2. **Customer Metrics**
   - Total customers
   - New customers (per period)
   - Returning customers
   - Average order value
   - Customer lifetime value
   - Churn rate (no orders in 60 days)

3. **Order Metrics**
   - Total orders
   - Average order value
   - Order growth rate
   - Most popular items
   - Orders by payment method

4. **Discount Metrics**
   - Total discounts given
   - Discount by type (VIP, Referral, etc.)
   - Discount as % of revenue
   - Discount effectiveness (conversion rate)

5. **VIP Metrics**
   - VIP customer count per tier
   - VIP revenue contribution
   - VIP growth rate
   - Tier progression rate

6. **Loyalty Metrics**
   - Points issued vs redeemed
   - Redemption rate
   - Loyalty revenue impact
   - Active loyalty participants

---

## ✅ IMPLEMENTATION CHECKLIST

- [ ] Create `analytics` app: `python manage.py startapp analytics`
- [ ] Create models (DailyAnalyticsSnapshot, RevenueStream, etc.)
- [ ] Create service layer (AnalyticsService)
- [ ] Create views (dashboard, revenue_streams, customer_analytics, campaigns)
- [ ] Create templates (dashboard.html, revenue_streams.html, etc.)
- [ ] Create management command (update_analytics)
- [ ] Create URL patterns
- [ ] Add signal handlers for automatic tracking
- [ ] Run migrations: `python manage.py migrate`
- [ ] Create test data and verify calculations
- [ ] Add to navigation/menus
- [ ] Document for staff

---

## 🎯 PHASE 4 SUCCESS CRITERIA

✅ All metrics calculating correctly  
✅ Dashboard responsive on mobile  
✅ Charts rendering properly  
✅ Real-time data updates  
✅ Historical data tracked  
✅ Campaign management working  
✅ User permissions enforced  
✅ Performance optimized  
✅ Documentation complete  

---

**Next**: Implement all analytics components and integrate with existing systems.
