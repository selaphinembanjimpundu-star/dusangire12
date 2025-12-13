from django.contrib import admin
from .models import LoyaltyPoints, PointsTransaction, PointsRedemption


@admin.register(LoyaltyPoints)
class LoyaltyPointsAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_points', 'lifetime_points', 'points_redeemed', 'updated_at']
    list_filter = ['updated_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-total_points']


@admin.register(PointsTransaction)
class PointsTransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'points', 'transaction_type', 'reason', 'order', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['user__username', 'reason', 'order__order_number']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']


@admin.register(PointsRedemption)
class PointsRedemptionAdmin(admin.ModelAdmin):
    list_display = ['name', 'points_required', 'discount_amount', 'discount_percentage', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['points_required']
