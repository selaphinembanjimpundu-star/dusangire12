from django.contrib import admin
from .models import DeliveryZone, DeliveryAddress


@admin.register(DeliveryZone)
class DeliveryZoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'delivery_charge', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active', 'delivery_charge']


@admin.register(DeliveryAddress)
class DeliveryAddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'label', 'get_full_address', 'zone', 'is_default', 'created_at']
    list_filter = ['zone', 'is_default', 'created_at']
    search_fields = ['user__username', 'label', 'address_line1', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'label', 'is_default')
        }),
        ('Contact Information', {
            'fields': ('full_name', 'phone')
        }),
        ('Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'zone')
        }),
        ('Additional Information', {
            'fields': ('delivery_instructions',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_full_address(self, obj):
        return obj.get_full_address()
    get_full_address.short_description = 'Full Address'
