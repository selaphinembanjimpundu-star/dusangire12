from django.contrib import admin
from .models import AdminLog


@admin.register(AdminLog)
class AdminLogAdmin(admin.ModelAdmin):
    """Admin interface for AdminLog model"""
    
    list_display = (
        'id',
        'admin_user',
        'action',
        'model_name',
        'status',
        'timestamp',
    )
    
    list_filter = (
        'action',
        'status',
        'timestamp',
        'admin_user',
        'model_name',
    )
    
    search_fields = (
        'description',
        'model_name',
        'admin_user__username',
        'error_message',
    )
    
    readonly_fields = (
        'admin_user',
        'action',
        'model_name',
        'object_id',
        'description',
        'old_values',
        'new_values',
        'ip_address',
        'user_agent',
        'status',
        'error_message',
        'timestamp',
        'duration_ms',
    )
    
    fieldsets = (
        ('Action Information', {
            'fields': ('admin_user', 'action', 'timestamp')
        }),
        ('Object Information', {
            'fields': ('model_name', 'object_id', 'description')
        }),
        ('Changes', {
            'fields': ('old_values', 'new_values'),
            'classes': ('collapse',)
        }),
        ('Request Information', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('status', 'error_message', 'duration_ms'),
        }),
    )
    
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)
    
    def has_add_permission(self, request):
        """Prevent manual creation of logs"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete logs"""
        return request.user.is_superuser
