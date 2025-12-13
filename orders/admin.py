from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem, OrderStatus


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_item_count', 'get_total', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_item_count(self, obj):
        return obj.get_item_count()
    get_item_count.short_description = 'Items'
    
    def get_total(self, obj):
        return f"${obj.get_total()}"
    get_total.short_description = 'Total'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'menu_item', 'quantity', 'get_subtotal', 'created_at']
    list_filter = ['created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_subtotal(self, obj):
        return f"${obj.get_subtotal()}"
    get_subtotal.short_description = 'Subtotal'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'customer_name', 'status', 'total', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'user__username', 'customer_name', 'customer_phone']
    readonly_fields = ['order_number', 'created_at', 'updated_at', 'delivered_at']
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status')
        }),
        ('Customer Information', {
            'fields': ('customer_name', 'customer_phone', 'delivery_address', 'delivery_instructions')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'delivery_charge', 'total')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'delivered_at')
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'menu_item', 'quantity', 'price', 'subtotal']
    list_filter = ['order__status', 'order__created_at']
    search_fields = ['order__order_number', 'menu_item__name']
