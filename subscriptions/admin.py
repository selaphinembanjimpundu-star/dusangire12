from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count, Q
from django.utils import timezone
from .models import (
    SubscriptionPlan, Subscription, SubscriptionOrder,
    VIPTier, LoyaltyPoints, LoyaltyTransaction, ReferralProgram,
    SubscriptionAutoRenewal
)


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'plan_type', 'price', 'discount_badge', 'meals_per_cycle', 'duration_days', 'active_badge', 'popular_badge', 'subscribers_count']
    list_filter = ['plan_type', 'is_active', 'is_featured', 'is_popular', 'created_at']
    search_fields = ['name', 'description']
    filter_horizontal = ['menu_items']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'plan_type')
        }),
        ('Pricing', {
            'fields': ('price', 'discount_percentage', 'meals_per_cycle', 'duration_days')
        }),
        ('Menu Items', {
            'fields': ('menu_items',),
            'description': 'Select specific menu items for this plan (leave empty for all items)'
        }),
        ('Marketing', {
            'fields': ('is_active', 'is_featured', 'is_popular', 'subscribers_count')
        }),
    )
    
    def discount_badge(self, obj):
        """Display discount with badge"""
        if obj.discount_percentage > 0:
            return format_html(
                '<span style="background-color: #FFD700; color: black; padding: 5px 10px; border-radius: 3px;"><b>-{}%</b></span>',
                obj.discount_percentage
            )
        return "No discount"
    discount_badge.short_description = 'Discount'
    
    def active_badge(self, obj):
        """Display active status"""
        if obj.is_active:
            return format_html('<span style="color: green;"><b>✓ Active</b></span>')
        return format_html('<span style="color: red;"><b>✗ Inactive</b></span>')
    active_badge.short_description = 'Status'
    
    def popular_badge(self, obj):
        """Display popular status"""
        if obj.is_popular:
            return format_html('<span style="color: #FF6B6B;"><b>★ Popular</b></span>')
        return "—"
    popular_badge.short_description = 'Popular'


@admin.register(Subscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user_name', 'plan_name', 'status_badge', 'start_date', 'end_date', 'days_remaining', 'auto_renewal_status', 'created_at']
    list_filter = ['status', 'plan__plan_type', 'auto_order_enabled', 'auto_renewal_enabled', ('created_at', admin.DateFieldListFilter)]
    search_fields = ['user__username', 'user__email', 'plan__name']
    readonly_fields = ['created_at', 'updated_at', 'cancelled_at']
    
    fieldsets = (
        ('Subscription Information', {
            'fields': ('user', 'plan', 'status')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date', 'next_billing_date', 'paused_until')
        }),
        ('Auto Features', {
            'fields': ('auto_order_enabled', 'auto_renewal_enabled'),
            'classes': ('collapse',)
        }),
        ('Preferences', {
            'fields': ('preferred_delivery_time', 'dietary_preferences', 'preferred_meals'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'cancelled_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['pause_subscriptions', 'resume_subscriptions', 'enable_auto_renewal']
    
    def user_name(self, obj):
        return obj.user.username
    user_name.short_description = 'Customer'
    
    def plan_name(self, obj):
        return obj.plan.name
    plan_name.short_description = 'Plan'
    
    def status_badge(self, obj):
        """Display status with color"""
        colors = {
            'active': '#28A745',
            'paused': '#FFC107',
            'cancelled': '#DC3545',
            'expired': '#6C757D',
        }
        color = colors.get(obj.status, '#999999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;"><b>{}</b></span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def days_remaining(self, obj):
        """Display remaining days"""
        days = obj.days_remaining()
        if days > 0:
            return format_html('<b>{} days</b>', days)
        return format_html('<span style="color: red;"><b>Expired</b></span>')
    days_remaining.short_description = 'Remaining'
    
    def auto_renewal_status(self, obj):
        """Display auto-renewal status"""
        if obj.auto_renewal_enabled:
            return format_html('<span style="color: green;"><b>✓ Enabled</b></span>')
        return format_html('<span style="color: red;"><b>✗ Disabled</b></span>')
    auto_renewal_status.short_description = 'Auto-Renewal'
    
    def pause_subscriptions(self, request, queryset):
        count = queryset.update(status='paused')
        self.message_user(request, f'{count} subscription(s) paused.')
    pause_subscriptions.short_description = '⏸ Pause Selected'
    
    def resume_subscriptions(self, request, queryset):
        for sub in queryset:
            if sub.status == 'paused':
                sub.resume()
        self.message_user(request, f'Subscriptions resumed.')
    resume_subscriptions.short_description = '▶ Resume Selected'
    
    def enable_auto_renewal(self, request, queryset):
        count = queryset.update(auto_renewal_enabled=True)
        self.message_user(request, f'Auto-renewal enabled for {count} subscription(s).')
    enable_auto_renewal.short_description = '↻ Enable Auto-Renewal'


@admin.register(VIPTier)
class VIPTierAdmin(admin.ModelAdmin):
    """VIP tier management"""
    
    list_display = ['user_name', 'tier_badge', 'spending_ytd_display', 'spending_total_display', 'discount_display', 'achieved_at']
    list_filter = ['tier_level', 'achieved_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at', 'spending_total_display']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Tier Information', {
            'fields': ('tier_level', 'access_level', 'achieved_at')
        }),
        ('Spending Tracking', {
            'fields': ('spending_ytd', 'spending_total_display', 'next_tier_threshold')
        }),
        ('Benefits', {
            'fields': ('promotion_percentage', 'benefits_list'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_name(self, obj):
        return obj.user.username
    user_name.short_description = 'Customer'
    
    def tier_badge(self, obj):
        """Display tier with color and icon"""
        colors = {
            'bronze': ('#CD7F32', '🥉'),
            'silver': ('#C0C0C0', '🥈'),
            'gold': ('#FFD700', '🥇'),
            'platinum': ('#E5E4E2', '💎'),
        }
        color, icon = colors.get(obj.tier_level, ('#999999', '•'))
        return format_html(
            '<span style="background-color: {}; color: #000; padding: 5px 10px; border-radius: 3px;"><b>{} {}</b></span>',
            color,
            icon,
            obj.get_tier_level_display()
        )
    tier_badge.short_description = 'Tier'
    
    def spending_ytd_display(self, obj):
        return f"RWF {obj.spending_ytd:,.0f}"
    spending_ytd_display.short_description = 'YTD Spending'
    
    def spending_total_display(self, obj):
        return f"RWF {obj.spending_total:,.0f}"
    spending_total_display.short_description = 'Total Spending'
    
    def discount_display(self, obj):
        if obj.promotion_percentage > 0:
            return format_html('<b>+{}% bonus</b>', obj.promotion_percentage)
        return "—"
    discount_display.short_description = 'Bonus'


@admin.register(LoyaltyPoints)
class LoyaltyPointsAdmin(admin.ModelAdmin):
    """Loyalty points management"""
    
    list_display = ['user_name', 'balance_display', 'earned_total_display', 'redeemed_total_display', 'bonus_rate_display', 'last_activity_at']
    list_filter = [('last_activity_at', admin.DateFieldListFilter)]
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['earned_total', 'redeemed_total', 'last_activity_at', 'created_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Points Balance', {
            'fields': ('balance', 'earned_total', 'redeemed_total')
        }),
        ('Bonus Settings', {
            'fields': ('subscription_bonus_rate',),
            'description': 'Multiplier for earning points (1.0 = normal, 1.05 = 5% bonus)'
        }),
        ('Expiration', {
            'fields': ('expires_at',),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_activity_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_name(self, obj):
        return obj.user.username
    user_name.short_description = 'Customer'
    
    def balance_display(self, obj):
        """Display balance with RWF value"""
        return format_html(
            '<b>{} pts</b><br><small>RWF {:,}</small>',
            obj.balance,
            obj.value_in_rwf
        )
    balance_display.short_description = 'Current Balance'
    
    def earned_total_display(self, obj):
        return f"{obj.earned_total} pts"
    earned_total_display.short_description = 'Earned (Lifetime)'
    
    def redeemed_total_display(self, obj):
        return f"{obj.redeemed_total} pts"
    redeemed_total_display.short_description = 'Redeemed (Lifetime)'
    
    def bonus_rate_display(self, obj):
        bonus_pct = (obj.subscription_bonus_rate - 1.0) * 100
        if bonus_pct > 0:
            return format_html('<b>+{}%</b>', bonus_pct)
        return "None"
    bonus_rate_display.short_description = 'Bonus Rate'


@admin.register(LoyaltyTransaction)
class LoyaltyTransactionAdmin(admin.ModelAdmin):
    """Loyalty points transaction history"""
    
    list_display = ['user_name', 'transaction_type_display', 'points_amount', 'balance_change', 'created_at']
    list_filter = ['transaction_type', ('created_at', admin.DateFieldListFilter)]
    search_fields = ['user__username', 'description']
    readonly_fields = ['user', 'created_at', 'balance_tracking']
    
    fieldsets = (
        ('Transaction Information', {
            'fields': ('user', 'transaction_type', 'points_amount', 'description')
        }),
        ('Balance Tracking', {
            'fields': ('balance_before', 'balance_after'),
        }),
        ('Related Objects', {
            'fields': ('related_subscription', 'related_payment'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def user_name(self, obj):
        return obj.user.username
    user_name.short_description = 'Customer'
    
    def transaction_type_display(self, obj):
        """Display transaction type with icon"""
        icons = {
            'EARN': '+',
            'REDEEM': '-',
            'BONUS': '★',
            'ADJUSTMENT': '⚙',
        }
        icon = icons.get(obj.transaction_type, '•')
        return f"{icon} {obj.get_transaction_type_display()}"
    transaction_type_display.short_description = 'Type'
    
    def balance_change(self, obj):
        """Display balance change"""
        change = obj.balance_after - obj.balance_before
        if change > 0:
            return format_html('<span style="color: green;"><b>+{}</b></span>', change)
        elif change < 0:
            return format_html('<span style="color: red;"><b>{}</b></span>', change)
        return "—"
    balance_change.short_description = 'Change'
    
    def balance_tracking(self, obj):
        """Display before/after balance"""
        return f"{obj.balance_before} → {obj.balance_after}"
    balance_tracking.short_description = 'Balance'


@admin.register(ReferralProgram)
class ReferralProgramAdmin(admin.ModelAdmin):
    """Referral program management"""
    
    list_display = ['referrer_name', 'status_badge', 'referee_name', 'bonus_display', 'completed_at', 'created_at']
    list_filter = ['status', ('created_at', admin.DateFieldListFilter), ('completed_at', admin.DateFieldListFilter)]
    search_fields = ['referrer__username', 'referee__username', 'referral_code']
    readonly_fields = ['referral_code', 'referral_link', 'created_at']
    
    fieldsets = (
        ('Referral Information', {
            'fields': ('referrer', 'referee', 'referral_code', 'referral_link')
        }),
        ('Bonuses', {
            'fields': ('referrer_bonus_rwf', 'referrer_bonus_points', 'referee_discount_percent')
        }),
        ('Status', {
            'fields': ('status', 'completed_at', 'expires_at')
        }),
    )
    
    def referrer_name(self, obj):
        return obj.referrer.username
    referrer_name.short_description = 'Referrer'
    
    def referee_name(self, obj):
        return obj.referee.username if obj.referee else "—"
    referee_name.short_description = 'Referee'
    
    def status_badge(self, obj):
        """Display status with color"""
        colors = {
            'PENDING': '#FFC107',
            'COMPLETED': '#28A745',
            'EXPIRED': '#6C757D',
            'CANCELLED': '#DC3545',
        }
        color = colors.get(obj.status, '#999999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;"><b>{}</b></span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def bonus_display(self, obj):
        """Display bonus amounts"""
        return format_html(
            '<b>RWF {:,}</b> + {} pts<br><small>(-{}% discount)</small>',
            obj.referrer_bonus_rwf,
            obj.referrer_bonus_points,
            obj.referee_discount_percent
        )
    bonus_display.short_description = 'Bonuses'


@admin.register(SubscriptionAutoRenewal)
class SubscriptionAutoRenewalAdmin(admin.ModelAdmin):
    """Auto-renewal configuration"""
    
    list_display = ['subscription_user', 'enabled_badge', 'renewal_date', 'failure_status', 'last_renewal_at']
    list_filter = ['auto_renew_enabled', 'renewal_date', ('last_renewal_at', admin.DateFieldListFilter)]
    search_fields = ['subscription__user__username']
    readonly_fields = ['created_at', 'updated_at', 'last_renewal_status', 'last_renewal_at']
    
    fieldsets = (
        ('Subscription Information', {
            'fields': ('subscription',)
        }),
        ('Auto-Renewal Settings', {
            'fields': ('auto_renew_enabled', 'renewal_date', 'renewal_interval_days', 'payment_method_id')
        }),
        ('Notification', {
            'fields': ('notification_sent', 'notification_days_before'),
            'classes': ('collapse',)
        }),
        ('Retry Logic', {
            'fields': ('failure_count', 'max_retries', 'next_retry_at'),
            'classes': ('collapse',)
        }),
        ('Last Renewal', {
            'fields': ('last_renewal_status', 'last_renewal_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['enable_auto_renewal', 'disable_auto_renewal', 'retry_failed_renewal']
    
    def subscription_user(self, obj):
        return obj.subscription.user.username
    subscription_user.short_description = 'Customer'
    
    def enabled_badge(self, obj):
        """Display enabled status"""
        if obj.auto_renew_enabled:
            return format_html('<span style="color: green;"><b>✓ Enabled</b></span>')
        return format_html('<span style="color: red;"><b>✗ Disabled</b></span>')
    enabled_badge.short_description = 'Status'
    
    def failure_status(self, obj):
        """Display failure count"""
        if obj.failure_count == 0:
            return format_html('<span style="color: green;">No failures</span>')
        elif obj.failure_count >= obj.max_retries:
            return format_html('<span style="color: red;"><b>Max retries exceeded</b></span>')
        else:
            return format_html('<span style="color: #FFC107;">{}/{} failures</span>', obj.failure_count, obj.max_retries)
    failure_status.short_description = 'Failures'
    
    def enable_auto_renewal(self, request, queryset):
        count = queryset.update(auto_renew_enabled=True)
        self.message_user(request, f'Auto-renewal enabled for {count} subscription(s).')
    enable_auto_renewal.short_description = '✓ Enable Auto-Renewal'
    
    def disable_auto_renewal(self, request, queryset):
        count = queryset.update(auto_renew_enabled=False)
        self.message_user(request, f'Auto-renewal disabled for {count} subscription(s).')
    disable_auto_renewal.short_description = '✗ Disable Auto-Renewal'
    
    def retry_failed_renewal(self, request, queryset):
        count = queryset.filter(failure_count__gt=0).update(
            failure_count=0,
            next_retry_at=None,
            last_renewal_status='RETRY_QUEUED'
        )
        self.message_user(request, f'Retry queued for {count} failed renewal(s).')
    retry_failed_renewal.short_description = '↻ Retry Failed Renewals'


@admin.register(SubscriptionOrder)
class SubscriptionOrderAdmin(admin.ModelAdmin):
    list_display = ['subscription', 'order', 'scheduled_date', 'created_at']
    list_filter = ['scheduled_date', 'created_at']
    search_fields = ['subscription__user__username', 'order__order_number']
    readonly_fields = ['created_at']
