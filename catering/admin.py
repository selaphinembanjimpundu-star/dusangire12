from django.contrib import admin
from .models import CateringPackage, CateringBooking

@admin.register(CateringPackage)
class CateringPackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_per_person', 'min_people', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')

@admin.register(CateringBooking)
class CateringBookingAdmin(admin.ModelAdmin):
    list_display = ('event_name', 'user', 'event_date', 'number_of_people', 'status', 'total_price')
    list_filter = ('status', 'event_date')
    search_fields = ('event_name', 'user__username', 'location')
    date_hierarchy = 'event_date'
