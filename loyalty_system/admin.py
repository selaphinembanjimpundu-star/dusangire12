from django.contrib import admin
from django.utils.html import format_html
from .models import (SubscriptionTier, EnhancedSubscription, LoyaltyPoints, 
                     VIPMembership, VIPBenefit, ReferralBonus)

@admin.register(SubscriptionTier)
class SubscriptionTierAdmin(admin.ModelAdmin):
    list_display = ('name', 'frequency', 'price_display', 'meals_per_period', 'discount_percentage', 'is_active_badge')
    list_filter = ('frequency', 'is_active', 'includes_delivery', 'includes_consultation')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Tier Information', {
            'fields': ('name', 'frequency', 'meals_per_period', 'is_active')
        }),
        ('Pricing', {
            'fields': ('price_rwf', 'discount_percentage')
        }),
        ('Benefits', {
            'fields': ('includes_delivery', 'includes_consultation')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('System Information', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def price_display(self, obj):
        return format_html(
            '<span style="color: green; font-weight: bold;">{} RWF</span>',
            f"{obj.price_rwf:,.2f}"
        )
    price_display.short_description = 'Price'
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background-color: green; color: white; padding: 3px 10px; border-radius: 3px;">Active</span>'
            )
        return format_html(
            '<span style="background-color: red; color: white; padding: 3px 10px; border-radius: 3px;">Inactive</span>'
        )
    is_active_badge.short_description = 'Status'
    
    ordering = ['frequency', 'price_rwf']


@admin.register(EnhancedSubscription)
class EnhancedSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user_display', 'tier', 'status_badge', 'start_date', 'end_date', 'auto_renewal_badge')
    list_filter = ('status', 'tier__frequency', 'auto_renewal', 'start_date')
    search_fields = ('user__first_name', 'user__last_name', 'user__username')
    readonly_fields = ('created_at', 'updated_at', 'is_active_display')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'is_active_display')
        }),
        ('Subscription Details', {
            'fields': ('tier', 'status', 'auto_renewal')
        }),
        ('Duration', {
            'fields': ('start_date', 'end_date', 'renewal_date')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def user_display(self, obj):
        return obj.user.get_full_name() or obj.user.username
    user_display.short_description = 'User'
    
    def status_badge(self, obj):
        colors = {
            'ACTIVE': 'green',
            'PAUSED': 'orange',
            'CANCELLED': 'red',
            'EXPIRED': 'gray',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def auto_renewal_badge(self, obj):
        if obj.auto_renewal:
            return format_html(
                '<span style="background-color: blue; color: white; padding: 3px 10px; border-radius: 3px;">✓ Auto-Renewal</span>'
            )
        return format_html(
            '<span style="background-color: gray; color: white; padding: 3px 10px; border-radius: 3px;">Manual</span>'
        )
    auto_renewal_badge.short_description = 'Renewal'
    
    def is_active_display(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">✓ Active</span>')
        return format_html('<span style="color: red;">✗ Inactive</span>')
    is_active_display.short_description = 'Currently Active'
    
    ordering = ['-start_date']


@admin.register(LoyaltyPoints)
class LoyaltyPointsAdmin(admin.ModelAdmin):
    list_display = ('user_display', 'points_display', 'transaction_type', 'rwf_value_display', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'user__username', 'description')
    readonly_fields = ('created_at', 'rwf_value_display')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Points Transaction', {
            'fields': ('points', 'transaction_type', 'rwf_value_display')
        }),
        ('Details', {
            'fields': ('description', 'related_order')
        }),
        ('System Information', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def user_display(self, obj):
        return obj.user.get_full_name() or obj.user.username
    user_display.short_description = 'User'
    
    def points_display(self, obj):
        color = 'green' if obj.points > 0 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.points
        )
    points_display.short_description = 'Points'
    
    def rwf_value_display(self, obj):
        return format_html(
            '<span style="color: green; font-weight: bold;">{} RWF</span>',
            f"{obj.rwf_value:,.0f}"
        )
    rwf_value_display.short_description = 'RWF Value'
    
    ordering = ['-created_at']


@admin.register(VIPBenefit)
class VIPBenefitAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon')
    search_fields = ('name', 'description')


@admin.register(VIPMembership)
class VIPMembershipAdmin(admin.ModelAdmin):
    list_display = ('user_display', 'tier_badge', 'discount_percentage', 'is_active_badge', 'enrolled_date')
    list_filter = ('tier', 'is_active', 'enrolled_date')
    search_fields = ('user__first_name', 'user__last_name', 'user__username')
    readonly_fields = ('enrolled_date',)
    filter_horizontal = ('benefits',)
    
    fieldsets = (
        ('Member Information', {
            'fields': ('user', 'is_active')
        }),
        ('VIP Tier', {
            'fields': ('tier', 'discount_percentage')
        }),
        ('Benefits', {
            'fields': ('benefits',)
        }),
        ('Tier History', {
            'fields': ('enrolled_date', 'tier_upgrade_date')
        })
    )
    
    def user_display(self, obj):
        return obj.user.get_full_name() or obj.user.username
    user_display.short_description = 'Member'
    
    def tier_badge(self, obj):
        colors = {
            'BRONZE': '#8B4513',
            'SILVER': '#C0C0C0',
            'GOLD': '#FFD700',
            'PLATINUM': '#E5E4E2',
        }
        text_color = 'black' if obj.tier in ['GOLD', 'PLATINUM'] else 'white'
        color = colors.get(obj.tier, 'gray')
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 5px 15px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, text_color, obj.get_tier_display()
        )
    tier_badge.short_description = 'VIP Tier'
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background-color: green; color: white; padding: 3px 10px; border-radius: 3px;">Active</span>'
            )
        return format_html(
            '<span style="background-color: red; color: white; padding: 3px 10px; border-radius: 3px;">Inactive</span>'
        )
    is_active_badge.short_description = 'Status'
    
    ordering = ['-enrolled_date']


@admin.register(ReferralBonus)
class ReferralBonusAdmin(admin.ModelAdmin):
    list_display = ('referrer_display', 'referred_display', 'referral_code', 'bonus_points', 'status_badge', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('referrer__first_name', 'referrer__last_name', 'referrer__username', 
                     'referred_user__first_name', 'referred_user__last_name', 'referral_code')
    readonly_fields = ('created_at', 'conversion_date', 'referral_code')
    
    fieldsets = (
        ('Referral Information', {
            'fields': ('referrer', 'referred_user', 'referral_code')
        }),
        ('Bonus Details', {
            'fields': ('bonus_points', 'status')
        }),
        ('System Information', {
            'fields': ('created_at', 'conversion_date'),
            'classes': ('collapse',)
        })
    )
    
    def referrer_display(self, obj):
        return obj.referrer.get_full_name() or obj.referrer.username
    referrer_display.short_description = 'Referrer'
    
    def referred_display(self, obj):
        if obj.referred_user:
            return obj.referred_user.get_full_name() or obj.referred_user.username
        return '—'
    referred_display.short_description = 'Referred User'
    
    def status_badge(self, obj):
        colors = {
            'PENDING': 'orange',
            'COMPLETED': 'green',
            'FAILED': 'red',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    ordering = ['-created_at']
