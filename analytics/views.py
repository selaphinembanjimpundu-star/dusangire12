from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum, Avg, Count, Q
from datetime import timedelta
from .models import (
    DailyAnalyticsSnapshot,
    RevenueStream,
    CustomerMetrics,
    Campaign,
    CampaignPerformance,
    PageViewAnalytics,
    ConversionEvent
)
from .services import AnalyticsService


def is_staff(user):
    """Check if user is staff"""
    return user.is_staff


@login_required
@user_passes_test(is_staff)
def analytics_dashboard(request):
    """Main analytics dashboard with KPIs"""
    
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    # Today's metrics
    today_snapshot = DailyAnalyticsSnapshot.objects.filter(date=today).first()
    
    # Monthly metrics
    month_snapshots = DailyAnalyticsSnapshot.objects.filter(
        date__gte=thirty_days_ago,
        date__lte=today
    )
    
    month_totals = month_snapshots.aggregate(
        total_revenue=Sum('total_revenue'),
        total_orders=Sum('total_orders'),
        total_discount=Sum('total_discount'),
        avg_order_value=Avg('average_order_value'),
    )
    
    # Customer segments
    customer_segments = AnalyticsService.get_customer_segments()
    
    # Revenue by payment method (today)
    payment_methods = {}
    if today_snapshot:
        payment_methods = {
            'cash': today_snapshot.cash_orders,
            'mobile_money': today_snapshot.mobile_money_orders,
            'bank_transfer': today_snapshot.bank_transfer_orders,
            'card': today_snapshot.card_orders,
        }
    
    # Active campaigns
    active_campaigns = Campaign.objects.filter(status='active').count()
    completed_campaigns = Campaign.objects.filter(status='completed').count()
    
    context = {
        'today_snapshot': today_snapshot,
        'month_totals': month_totals,
        'customer_segments': customer_segments,
        'payment_methods': payment_methods,
        'active_campaigns': active_campaigns,
        'completed_campaigns': completed_campaigns,
        'recent_orders': month_snapshots[:10],  # Last 10 days
    }
    
    return render(request, 'analytics/dashboard.html', context)


@login_required
@user_passes_test(is_staff)
def revenue_streams(request):
    """Analyze revenue by channel/stream"""
    
    today = timezone.now().date()
    
    # Time filter
    days = request.GET.get('days', 30)
    try:
        days = int(days)
    except ValueError:
        days = 30
    
    start_date = today - timedelta(days=days)
    
    # Get revenue streams
    streams = RevenueStream.objects.filter(
        date__gte=start_date
    ).values('channel').annotate(
        total_amount=Sum('amount'),
        total_transactions=Sum('transaction_count'),
        avg_transaction=Avg('amount')
    ).order_by('-total_amount')
    
    # Calculate totals
    total_revenue = sum(s['total_amount'] for s in streams)
    
    # Add percentages
    for stream in streams:
        if total_revenue > 0:
            stream['percentage'] = (stream['total_amount'] / total_revenue) * 100
        else:
            stream['percentage'] = 0
    
    # Daily trends (last 30 days)
    daily_revenue = DailyAnalyticsSnapshot.objects.filter(
        date__gte=start_date
    ).values('date').annotate(
        revenue=Sum('total_revenue')
    ).order_by('date')
    
    # VIP vs Regular revenue
    thirty_days_ago = today - timedelta(days=30)
    vip_revenue = DailyAnalyticsSnapshot.objects.filter(
        date__gte=thirty_days_ago
    ).aggregate(Sum('vip_discounts_given'))['vip_discounts_given__sum'] or 0
    
    context = {
        'streams': streams,
        'total_revenue': total_revenue,
        'daily_revenue': daily_revenue,
        'vip_revenue': vip_revenue,
        'days_selected': days,
    }
    
    return render(request, 'analytics/revenue_streams.html', context)


@login_required
@user_passes_test(is_staff)
def customer_analytics(request):
    """Customer segmentation and behavior analysis"""
    
    # Get all customers with metrics
    customers = CustomerMetrics.objects.all().order_by('-lifetime_value')
    
    # Segmentation
    segments = {
        'vip': CustomerMetrics.objects.filter(vip_tier_current__isnull=False).count(),
        'subscribed': CustomerMetrics.objects.filter(subscription_active=True).count(),
        'high_value': CustomerMetrics.objects.filter(lifetime_value__gte=500000).count(),
        'churn_risk': CustomerMetrics.objects.filter(churn_risk=True).count(),
        'inactive': CustomerMetrics.objects.filter(days_since_last_order__gte=30).count(),
        'new': CustomerMetrics.objects.filter(days_since_last_order__lte=7).count(),
    }
    
    # Top customers
    top_customers = customers[:10]
    
    # At-risk customers
    at_risk = CustomerMetrics.objects.filter(churn_risk=True).order_by('-lifetime_value')[:10]
    
    # Loyalty performance
    loyalty_stats = customers.aggregate(
        total_points_earned=Sum('loyalty_points_earned'),
        total_points_redeemed=Sum('loyalty_points_redeemed'),
        total_loyalty_value=Sum('loyalty_value_redeemed'),
        avg_redemption_rate=Avg('loyalty_points_redeemed'),
    )
    
    # Referral performance
    referral_stats = customers.aggregate(
        total_referrals=Sum('referral_count'),
        total_referral_earnings=Sum('referral_earnings'),
        avg_referrals_per_customer=Avg('referral_count'),
    )
    
    context = {
        'segments': segments,
        'top_customers': top_customers,
        'at_risk_customers': at_risk,
        'loyalty_stats': loyalty_stats,
        'referral_stats': referral_stats,
        'total_customers': customers.count(),
    }
    
    return render(request, 'analytics/customer_analytics.html', context)


@login_required
@user_passes_test(is_staff)
def campaigns(request):
    """Campaign management and performance tracking"""
    
    status_filter = request.GET.get('status', '')
    
    campaigns_qs = Campaign.objects.all().order_by('-start_date')
    
    if status_filter:
        campaigns_qs = campaigns_qs.filter(status=status_filter)
    
    # Get performance data for each campaign
    campaign_data = []
    for campaign in campaigns_qs:
        performance = CampaignPerformance.objects.filter(campaign=campaign).last()
        campaign_data.append({
            'campaign': campaign,
            'performance': performance,
        })
    
    # Campaign statistics
    stats = {
        'total_campaigns': Campaign.objects.count(),
        'active_campaigns': Campaign.objects.filter(status='active').count(),
        'completed_campaigns': Campaign.objects.filter(status='completed').count(),
        'draft_campaigns': Campaign.objects.filter(status='draft').count(),
    }
    
    context = {
        'campaign_data': campaign_data,
        'stats': stats,
        'status_filter': status_filter,
    }
    
    return render(request, 'analytics/campaigns.html', context)


@login_required
@user_passes_test(is_staff)
def campaign_detail(request, campaign_id):
    """Detailed campaign performance analysis"""
    
    campaign = get_object_or_404(Campaign, id=campaign_id)
    
    # Get performance history
    performance_history = CampaignPerformance.objects.filter(
        campaign=campaign
    ).order_by('-tracked_at')
    
    # Current performance
    current_performance = performance_history.first()
    
    # Performance trend (last 7 days)
    seven_days_ago = timezone.now() - timedelta(days=7)
    performance_trend = performance_history.filter(
        tracked_at__gte=seven_days_ago
    ).order_by('tracked_at')
    
    # Conversion data
    conversions = ConversionEvent.objects.filter(
        metadata__campaign_id=campaign.id
    ).values('event_type').annotate(
        count=Count('id')
    )
    
    context = {
        'campaign': campaign,
        'current_performance': current_performance,
        'performance_history': performance_history[:30],
        'performance_trend': performance_trend,
        'conversions': conversions,
    }
    
    return render(request, 'analytics/campaign_detail.html', context)


@login_required
@user_passes_test(is_staff)
def api_daily_revenue(request):
    """API endpoint for daily revenue data (for charts)"""
    
    days = request.GET.get('days', 30)
    try:
        days = int(days)
    except ValueError:
        days = 30
    
    today = timezone.now().date()
    start_date = today - timedelta(days=days)
    
    data = DailyAnalyticsSnapshot.objects.filter(
        date__gte=start_date
    ).values('date').annotate(
        revenue=Sum('total_revenue'),
        orders=Count('id')
    ).order_by('date')
    
    return JsonResponse({
        'dates': [str(d['date']) for d in data],
        'revenue': [float(d['revenue'] or 0) for d in data],
        'orders': [d['orders'] for d in data],
    })


@login_required
@user_passes_test(is_staff)
def api_customer_segments(request):
    """API endpoint for customer segment data"""
    
    segments = AnalyticsService.get_customer_segments()
    
    return JsonResponse(segments)
