from django.contrib import admin
from .models import SupportTicket, SupportMessage


class SupportMessageInline(admin.TabularInline):
    model = SupportMessage
    extra = 0
    readonly_fields = ['created_at']
    fields = ['user', 'message', 'is_internal', 'created_at']


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'subject', 'status', 'priority', 'assigned_to', 'created_at']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['subject', 'message', 'user__username', 'order__order_number']
    readonly_fields = ['created_at', 'updated_at', 'resolved_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    inlines = [SupportMessageInline]
    
    fieldsets = (
        ('Ticket Information', {
            'fields': ('user', 'subject', 'message', 'order')
        }),
        ('Status', {
            'fields': ('status', 'priority', 'assigned_to')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'resolved_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_resolved', 'mark_closed', 'assign_to_me']
    
    def mark_resolved(self, request, queryset):
        for ticket in queryset:
            ticket.mark_resolved()
        self.message_user(request, f"{queryset.count()} ticket(s) marked as resolved.")
    mark_resolved.short_description = "Mark selected tickets as resolved"
    
    def mark_closed(self, request, queryset):
        queryset.update(status='closed')
        self.message_user(request, f"{queryset.count()} ticket(s) marked as closed.")
    mark_closed.short_description = "Mark selected tickets as closed"
    
    def assign_to_me(self, request, queryset):
        queryset.update(assigned_to=request.user)
        self.message_user(request, f"{queryset.count()} ticket(s) assigned to you.")
    assign_to_me.short_description = "Assign selected tickets to me"


@admin.register(SupportMessage)
class SupportMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'ticket', 'user', 'is_internal', 'created_at']
    list_filter = ['is_internal', 'created_at']
    search_fields = ['message', 'ticket__subject', 'user__username']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
