from django.db.models import Sum, Avg, Count, Q
from django.utils import timezone
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import timedelta
from orders.models import Order
from .models import (
    DailyAnalyticsSnapshot,
    RevenueStream,
    CustomerMetrics,
    Campaign,
    CampaignPerformance,
    PageViewAnalytics,
    ConversionEvent
)


class AnalyticsService:
    """Service for analytics calculations and updates"""
    
    @staticmethod
    def calculate_daily_snapshot(date=None):
        """Calculate and store daily analytics snapshot"""
        if date is None:
            date = timezone.now().date()
        
        # Get orders for the day
        day_start = timezone.make_aware(timezone.datetime.combine(date, timezone.datetime.min.time()))
        day_end = timezone.make_aware(timezone.datetime.combine(date, timezone.datetime.max.time()))
        
        orders = Order.objects.filter(
            created_at__gte=day_start,
            created_at__lte=day_end,
            status__in=['completed', 'delivered']
        )
        
        # Calculate basic metrics
        total_orders = orders.count()
        unique_customers = orders.values('user_id').distinct().count()
        total_revenue = orders.aggregate(Sum('total_price'))['total_price__sum'] or Decimal('0.00')
        
        # Calculate discounts
        total_discount = (
            orders.aggregate(Sum('loyalty_discount_amount'))['loyalty_discount_amount__sum'] or Decimal('0.00')
        ) + (
            orders.aggregate(Sum('vip_discount_amount'))['vip_discount_amount__sum'] or Decimal('0.00')
        ) + (
            orders.aggregate(Sum('corporate_discount_amount'))['corporate_discount_amount__sum'] or Decimal('0.00')
        ) + (
            orders.aggregate(Sum('referral_discount_amount'))['referral_discount_amount__sum'] or Decimal('0.00')
        )
        
        # Calculate average order value
        average_order_value = (
            total_revenue / total_orders if total_orders > 0 else Decimal('0.00')
        )
        
        # Count order types
        vip_orders = orders.filter(user__customer_metrics__vip_tier_current__isnull=False).count()
        
        # Count payment methods
        cash_orders = orders.filter(payment_method='cash_on_delivery').count()
        mobile_money_orders = orders.filter(payment_method='mobile_money').count()
        bank_transfer_orders = orders.filter(payment_method='bank_transfer').count()
        card_orders = orders.filter(payment_method='card').count()
        
        # Create or update snapshot
        snapshot, created = DailyAnalyticsSnapshot.objects.update_or_create(
            date=date,
            defaults={
                'total_orders': total_orders,
                'unique_customers': unique_customers,
                'total_revenue': total_revenue,
                'total_discount': total_discount,
                'average_order_value': average_order_value,
                'vip_orders': vip_orders,
                'cash_orders': cash_orders,
                'mobile_money_orders': mobile_money_orders,
                'bank_transfer_orders': bank_transfer_orders,
                'card_orders': card_orders,
            }
        )
        
        return snapshot
    
    @staticmethod
    def update_customer_metrics(user):
        """Update customer metrics for a specific user"""
        orders = Order.objects.filter(user=user, status__in=['completed', 'delivered'])
        
        total_orders = orders.count()
        total_spent = orders.aggregate(Sum('total_price'))['total_price__sum'] or Decimal('0.00')
        
        # Calculate average order value
        average_order_value = (
            total_spent / total_orders if total_orders > 0 else Decimal('0.00')
        )
        
        # Get first and last order dates
        first_order = orders.order_by('created_at').first()
        last_order = orders.order_by('-created_at').first()
        
        first_order_date = first_order.created_at if first_order else None
        last_order_date = last_order.created_at if last_order else None
        
        # Calculate days since last order
        days_since_last_order = 0
        if last_order_date:
            days_since_last_order = (timezone.now() - last_order_date).days
        
        # Calculate churn risk (no order in 60+ days)
        churn_risk = days_since_last_order >= 60 and total_orders > 0
        
        # Calculate total discounts received
        total_discounts = (
            orders.aggregate(Sum('loyalty_discount_amount'))['loyalty_discount_amount__sum'] or Decimal('0.00')
        ) + (
            orders.aggregate(Sum('vip_discount_amount'))['vip_discount_amount__sum'] or Decimal('0.00')
        ) + (
            orders.aggregate(Sum('corporate_discount_amount'))['corporate_discount_amount__sum'] or Decimal('0.00')
        ) + (
            orders.aggregate(Sum('referral_discount_amount'))['referral_discount_amount__sum'] or Decimal('0.00')
        )
        
        metrics, created = CustomerMetrics.objects.update_or_create(
            user=user,
            defaults={
                'total_orders': total_orders,
                'total_spent': total_spent,
                'average_order_value': average_order_value,
                'first_order_date': first_order_date,
                'last_order_date': last_order_date,
                'days_since_last_order': days_since_last_order,
                'lifetime_value': total_spent,
                'churn_risk': churn_risk,
                'total_discounts_received': total_discounts,
            }
        )
        
        return metrics
    
    @staticmethod
    def track_revenue_stream(date=None, channel='direct_order', amount=Decimal('0.00'), transaction_count=1):
        """Track revenue by channel/stream"""
        if date is None:
            date = timezone.now().date()
        
        stream, created = RevenueStream.objects.update_or_create(
            date=date,
            channel=channel,
            defaults={
                'amount': amount,
                'transaction_count': transaction_count,
            }
        )
        
        return stream
    
    @staticmethod
    def get_revenue_summary(days=30):
        """Get revenue summary for last N days"""
        start_date = timezone.now().date() - timedelta(days=days)
        
        snapshots = DailyAnalyticsSnapshot.objects.filter(
            date__gte=start_date
        ).aggregate(
            total_revenue=Sum('total_revenue'),
            total_orders=Sum('total_orders'),
            total_discount=Sum('total_discount'),
            avg_order_value=Avg('average_order_value'),
        )
        
        return snapshots
    
    @staticmethod
    def get_customer_segments():
        """Get customer segmentation by metrics"""
        segments = {
            'vip_customers': CustomerMetrics.objects.filter(vip_tier_current__isnull=False).count(),
            'subscribed_customers': CustomerMetrics.objects.filter(subscription_active=True).count(),
            'churn_risk': CustomerMetrics.objects.filter(churn_risk=True).count(),
            'high_value': CustomerMetrics.objects.filter(lifetime_value__gte=500000).count(),  # RWF 500k+
            'inactive': CustomerMetrics.objects.filter(days_since_last_order__gte=30).count(),
        }
        
        return segments
    
    @staticmethod
    def get_campaign_roi(campaign):
        """Calculate and update campaign ROI"""
        performance = CampaignPerformance.objects.filter(campaign=campaign).last()
        
        if performance and campaign.budget and campaign.budget > 0:
            performance.roi = ((performance.revenue_generated - campaign.budget) / campaign.budget) * 100
            performance.save()
            return performance.roi
        
        return 0
    
    @staticmethod
    def get_dashboard_data():
        """Get comprehensive dashboard data"""
        today = timezone.now().date()
        
        # Today's snapshot
        today_snapshot = DailyAnalyticsSnapshot.objects.filter(date=today).first()
        
        # Last 30 days
        thirty_days_ago = today - timedelta(days=30)
        month_data = DailyAnalyticsSnapshot.objects.filter(
            date__gte=thirty_days_ago
        ).aggregate(
            total_revenue=Sum('total_revenue'),
            total_orders=Sum('total_orders'),
            total_discount=Sum('total_discount'),
        )
        
        # Customer segments
        segments = AnalyticsService.get_customer_segments()
        
        # Top campaigns
        active_campaigns = Campaign.objects.filter(status='active')
        
        # Revenue by channel (last 7 days)
        seven_days_ago = today - timedelta(days=7)
        revenue_streams = RevenueStream.objects.filter(
            date__gte=seven_days_ago
        ).values('channel').annotate(
            total=Sum('amount')
        ).order_by('-total')
        
        return {
            'today': today_snapshot,
            'month': month_data,
            'segments': segments,
            'active_campaigns': active_campaigns.count(),
            'revenue_streams': list(revenue_streams),
        }
    
    @staticmethod
    def record_conversion_event(user=None, event_type='view_menu', session_id=None, metadata=None):
        """Record a conversion event"""
        event = ConversionEvent.objects.create(
            user=user,
            event_type=event_type,
            session_id=session_id or '',
            metadata=metadata or {}
        )
        
        return event
    
    @staticmethod
    def get_conversion_funnel(days=7):
        """Get conversion funnel for last N days"""
        start_date = timezone.now() - timedelta(days=days)
        
        funnel = ConversionEvent.objects.filter(
            timestamp__gte=start_date
        ).values('event_type').annotate(
            count=Count('id'),
            unique_sessions=Count('session_id', distinct=True)
        ).order_by('event_type')
        
        return funnel
