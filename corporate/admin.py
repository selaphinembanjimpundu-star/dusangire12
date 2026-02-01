from django.contrib import admin
from .models import CorporatePartner, CorporateContract, CorporateEmployee

@admin.register(CorporatePartner)
class CorporatePartnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'partner_type', 'contact_person', 'is_active', 'created_at')
    list_filter = ('partner_type', 'is_active')
    search_fields = ('name', 'contact_person', 'contact_email')

@admin.register(CorporateContract)
class CorporateContractAdmin(admin.ModelAdmin):
    list_display = ('contract_number', 'partner', 'start_date', 'end_date', 'discount_percentage', 'is_active')
    list_filter = ('is_active', 'billing_cycle')
    search_fields = ('contract_number', 'partner__name')

'''@admin.register(CorporateEmployee)
class CorporateEmployeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'partner', 'employee_id', 'department', 'is_active')
    list_filter = ('partner', 'is_active')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'employee_id')'''
