from django.contrib import admin
from .models import SubscriptionPlan, UserSubscription, SubscriptionOrder


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'plan_type', 'price', 'discount_percentage', 'meals_per_cycle', 'duration_days', 'is_active', 'is_featured', 'is_popular', 'subscribers_count']
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


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'status', 'start_date', 'end_date', 'next_billing_date', 'is_active', 'created_at']
    list_filter = ['status', 'plan__plan_type', 'created_at']
    search_fields = ['user__username', 'user__email', 'plan__name']
    readonly_fields = ['created_at', 'updated_at', 'cancelled_at']
    fieldsets = (
        ('Subscription Information', {
            'fields': ('user', 'plan', 'status')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date', 'next_billing_date', 'paused_until')
        }),
        ('Preferences', {
            'fields': ('preferred_delivery_time', 'dietary_preferences', 'auto_order_enabled')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'cancelled_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SubscriptionOrder)
class SubscriptionOrderAdmin(admin.ModelAdmin):
    list_display = ['subscription', 'order', 'scheduled_date', 'created_at']
    list_filter = ['scheduled_date', 'created_at']
    search_fields = ['subscription__user__username', 'order__order_number']
    readonly_fields = ['created_at']
