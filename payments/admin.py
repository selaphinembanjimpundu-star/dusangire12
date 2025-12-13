from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'payment_method', 'status', 'amount', 'transaction_id', 'created_at']
    list_filter = ['payment_method', 'status', 'created_at']
    search_fields = ['order__order_number', 'transaction_id', 'phone_number', 'account_number']
    readonly_fields = ['created_at', 'updated_at', 'paid_at']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order',)
        }),
        ('Payment Details', {
            'fields': ('payment_method', 'status', 'amount')
        }),
        ('Transaction Information', {
            'fields': ('transaction_id', 'phone_number', 'account_number', 'notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'paid_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_completed', 'mark_as_failed']
    
    def mark_as_completed(self, request, queryset):
        """Mark selected payments as completed"""
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} payment(s) marked as completed.')
    mark_as_completed.short_description = 'Mark selected payments as completed'
    
    def mark_as_failed(self, request, queryset):
        """Mark selected payments as failed"""
        updated = queryset.update(status='failed')
        self.message_user(request, f'{updated} payment(s) marked as failed.')
    mark_as_failed.short_description = 'Mark selected payments as failed'
