from django.contrib import admin
from .models import (
    DailyAnalyticsSnapshot,
    RevenueStream,
    CustomerMetrics,
    Campaign,
    CampaignPerformance,
    PageViewAnalytics,
    ConversionEvent
)


@admin.register(DailyAnalyticsSnapshot)
class DailyAnalyticsSnapshotAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_orders', 'unique_customers', 'total_revenue', 'total_discount')
    list_filter = ('date',)
    search_fields = ('date',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Date', {'fields': ('date',)}),
        ('Order Metrics', {
            'fields': ('total_orders', 'unique_customers', 'average_order_value')
        }),
        ('Revenue', {
            'fields': ('total_revenue', 'total_discount')
        }),
        ('Order Breakdown', {
            'fields': ('vip_orders', 'subscription_orders', 'referral_orders'),
            'classes': ('collapse',)
        }),
        ('Payment Methods', {
            'fields': ('cash_orders', 'mobile_money_orders', 'bank_transfer_orders', 'card_orders'),
            'classes': ('collapse',)
        }),
        ('Discount Details', {
            'fields': ('vip_discounts_given', 'loyalty_discounts_given', 'referral_discounts_given'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(RevenueStream)
class RevenueStreamAdmin(admin.ModelAdmin):
    list_display = ('date', 'channel', 'amount', 'transaction_count')
    list_filter = ('date', 'channel')
    search_fields = ('date', 'channel')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CustomerMetrics)
class CustomerMetricsAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_orders', 'lifetime_value', 'churn_risk', 'vip_tier_current')
    list_filter = ('churn_risk', 'vip_tier_current', 'subscription_active')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('updated_at',)
    
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Order History', {
            'fields': ('total_orders', 'total_spent', 'average_order_value', 'first_order_date', 'last_order_date')
        }),
        ('Churn Analysis', {
            'fields': ('days_since_last_order', 'churn_risk')
        }),
        ('VIP & Subscription', {
            'fields': ('vip_tier_current', 'subscription_active')
        }),
        ('Loyalty Program', {
            'fields': ('loyalty_points_earned', 'loyalty_points_redeemed', 'loyalty_value_redeemed')
        }),
        ('Referral Program', {
            'fields': ('referral_count', 'referral_earnings')
        }),
        ('Discount Analysis', {
            'fields': ('total_discounts_received', 'vip_discounts_received')
        }),
        ('Metadata', {
            'fields': ('lifetime_value', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'discount_type', 'start_date', 'end_date')
    list_filter = ('status', 'start_date', 'discount_type')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Campaign Details', {
            'fields': ('name', 'description', 'status')
        }),
        ('Discount', {
            'fields': ('discount_type', 'discount_value', 'target_audience')
        }),
        ('Schedule', {
            'fields': ('start_date', 'end_date')
        }),
        ('Budget', {
            'fields': ('budget',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CampaignPerformance)
class CampaignPerformanceAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'orders_influenced', 'revenue_generated', 'conversion_rate', 'roi')
    list_filter = ('campaign', 'tracked_at')
    search_fields = ('campaign__name',)
    readonly_fields = ('tracked_at',)
    
    fieldsets = (
        ('Campaign', {'fields': ('campaign',)}),
        ('Performance Metrics', {
            'fields': ('orders_influenced', 'revenue_generated', 'customers_reached', 'customers_converted')
        }),
        ('Rates & ROI', {
            'fields': ('conversion_rate', 'roi')
        }),
        ('Tracked At', {
            'fields': ('tracked_at',)
        }),
    )


@admin.register(PageViewAnalytics)
class PageViewAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('page_name', 'date', 'view_count', 'unique_visitors')
    list_filter = ('date', 'page_name')
    search_fields = ('page_name',)
    readonly_fields = ('created_at',)


@admin.register(ConversionEvent)
class ConversionEventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'user', 'timestamp')
    list_filter = ('event_type', 'timestamp')
    search_fields = ('user__username', 'session_id')
    readonly_fields = ('timestamp',)

