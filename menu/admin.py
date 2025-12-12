from django.contrib import admin
from .models import Category, DietaryTag, MenuItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(DietaryTag)
class DietaryTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon']
    search_fields = ['name']


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_available', 'is_featured', 'created_at']
    list_filter = ['category', 'is_available', 'is_featured', 'dietary_tags', 'created_at']
    search_fields = ['name', 'description']
    filter_horizontal = ['dietary_tags']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category', 'price', 'image')
        }),
        ('Nutrition Information', {
            'fields': ('calories', 'protein', 'carbs', 'fat')
        }),
        ('Tags and Availability', {
            'fields': ('dietary_tags', 'is_available', 'is_featured')
        }),
    )
