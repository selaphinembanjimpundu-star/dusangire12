from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    NutritionistProfile, ClientAssignment, Consultation, 
    MealPlan, DietRecommendation, ClientNote, NutritionistAvailability
)

@admin.register(NutritionistAvailability)
class NutritionistAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('nutritionist', 'day_of_week', 'start_time', 'end_time', 'is_active')
    list_filter = ('day_of_week', 'is_active', 'nutritionist')
    search_fields = ('nutritionist__username', 'nutritionist__first_name', 'nutritionist__last_name')

@admin.register(NutritionistProfile)
class NutritionistProfileAdmin(admin.ModelAdmin):
    """
    Admin interface for nutritionist profiles
    """
    list_display = (
        'get_full_name',
        'get_email',
        'specialization',
        'status',
        'get_current_client_count_display',
        'max_clients',
        'created_at'
    )
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = (
        'user__first_name',
        'user__last_name',
        'user__email',
        'license_number',
        'specialization'
    )
    readonly_fields = ('created_at', 'updated_at', 'get_current_client_count_display')
    
    fieldsets = (
        (_('User Information'), {
            'fields': ('user',)
        }),
        (_('Professional Details'), {
            'fields': (
                'bio',
                'specialization',
                'license_number',
                'phone_number'
            )
        }),
        (_('Status & Capacity'), {
            'fields': (
                'status',
                'max_clients',
                'get_current_client_count_display'
            )
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['activate_nutritionists', 'deactivate_nutritionists', 'mark_on_leave']

    def get_full_name(self, obj):
        """Display nutritionist's full name"""
        return obj.user.get_full_name() or obj.user.email
    get_full_name.short_description = _('Name')
    get_full_name.admin_order_field = 'user__first_name'

    def get_email(self, obj):
        """Display nutritionist's email"""
        return obj.user.email
    get_email.short_description = _('Email')
    get_email.admin_order_field = 'user__email'

    def get_current_client_count_display(self, obj):
        """Display current active client count"""
        if hasattr(obj, 'current_client_count'):
            count = obj.current_client_count
        elif hasattr(obj, 'clients'):
            count = obj.clients.count() if hasattr(obj.clients, 'count') else 0
        else:
            count = 0
        
        return f"{count} / {obj.max_clients}"
    get_current_client_count_display.short_description = _('Active Clients / Max Capacity')

    def activate_nutritionists(self, request, queryset):
        """Bulk action to activate nutritionists"""
        updated = queryset.update(status='active')
        self.message_user(request, _(f'{updated} nutritionist(s) activated.'))
    activate_nutritionists.short_description = _('Activate selected nutritionists')

    def deactivate_nutritionists(self, request, queryset):
        """Bulk action to deactivate nutritionists"""
        updated = queryset.update(status='inactive')
        self.message_user(request, _(f'{updated} nutritionist(s) deactivated.'))
    deactivate_nutritionists.short_description = _('Deactivate selected nutritionists')

    def mark_on_leave(self, request, queryset):
        """Bulk action to mark as on leave"""
        updated = queryset.update(status='on_leave')
        self.message_user(request, _(f'{updated} nutritionist(s) marked as on leave.'))
    mark_on_leave.short_description = _('Mark as on leave')


@admin.register(ClientAssignment)
class ClientAssignmentAdmin(admin.ModelAdmin):
    """
    Admin interface for client assignments
    """
    list_display = (
        'get_client_name',
        'get_nutritionist_name',
        'status',
        'start_date',
        'end_date',
        'is_active_display',
        'created_at'
    )
    list_filter = ('status', 'start_date', 'end_date', 'created_at')
    search_fields = (
        'client__first_name',
        'client__last_name',
        'client__email',
        'nutritionist__first_name',
        'nutritionist__last_name',
        'nutritionist__email'
    )
    readonly_fields = ('created_at', 'updated_at', 'start_date')
    
    fieldsets = (
        (_('Assignment Details'), {
            'fields': ('nutritionist', 'client', 'start_date', 'end_date')
        }),
        (_('Status'), {
            'fields': ('status',)
        }),
        (_('Notes'), {
            'fields': ('notes',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_active', 'mark_paused', 'mark_completed', 'terminate_assignments']

    def get_client_name(self, obj):
        """Display client's full name"""
        return obj.client.get_full_name() or obj.client.email
    get_client_name.short_description = _('Client')
    get_client_name.admin_order_field = 'client__first_name'

    def get_nutritionist_name(self, obj):
        """Display nutritionist's full name"""
        return obj.nutritionist.get_full_name() or obj.nutritionist.email
    get_nutritionist_name.short_description = _('Nutritionist')
    get_nutritionist_name.admin_order_field = 'nutritionist__first_name'

    def is_active_display(self, obj):
        """Display if assignment is currently active"""
        return obj.status == 'active'
    is_active_display.short_description = _('Currently Active')
    is_active_display.boolean = True

    def mark_active(self, request, queryset):
        """Bulk action to mark assignments as active"""
        updated = queryset.update(status='active', end_date=None)
        self.message_user(request, _(f'{updated} assignment(s) marked as active.'))
    mark_active.short_description = _('Mark as active')

    def mark_paused(self, request, queryset):
        """Bulk action to mark assignments as paused"""
        updated = queryset.update(status='paused')
        self.message_user(request, _(f'{updated} assignment(s) marked as paused.'))
    mark_paused.short_description = _('Mark as paused')

    def mark_completed(self, request, queryset):
        """Bulk action to mark assignments as completed"""
        updated = queryset.update(status='completed')
        self.message_user(request, _(f'{updated} assignment(s) marked as completed.'))
    mark_completed.short_description = _('Mark as completed')

    def terminate_assignments(self, request, queryset):
        """Bulk action to terminate assignments"""
        from datetime import date
        updated = queryset.update(status='terminated', end_date=date.today())
        self.message_user(request, _(f'{updated} assignment(s) terminated.'))
    terminate_assignments.short_description = _('Terminate selected assignments')

@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('client', 'nutritionist', 'consultation_type', 'scheduled_at', 'status')
    list_filter = ('status', 'consultation_type', 'scheduled_at')
    search_fields = ('client__username', 'nutritionist__username')

@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'client', 'nutritionist', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'start_date')
    search_fields = ('title', 'client__username', 'nutritionist__username')

@admin.register(DietRecommendation)
class DietRecommendationAdmin(admin.ModelAdmin):
    list_display = ('title', 'client', 'nutritionist', 'status', 'priority')
    list_filter = ('status', 'priority')
    search_fields = ('title', 'client__username')

@admin.register(ClientNote)
class ClientNoteAdmin(admin.ModelAdmin):
    list_display = ('client', 'nutritionist', 'is_private', 'created_at')
    list_filter = ('is_private', 'created_at')
    search_fields = ('client__username', 'nutritionist__username')