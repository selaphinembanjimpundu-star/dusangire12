from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Ward, WardBed, WardDeliveryRoute, WardAvailability,
    MealNutritionInfo, DeliveryScheduleSlot,
    PatientEducationCategory, PatientEducationContent, PatientEducationProgress,
    CaregiverNotification, PatientAdmission, PatientDischarge, PatientTransfer,
    BedMaintenanceSchedule, BulkOperation, PatientNotification, NotificationTemplate
)


class WardBedInline(admin.TabularInline):
    """Inline for ward beds"""
    model = WardBed
    extra = 5
    fields = ['bed_number', 'status', 'patient', 'notes', 'assigned_at']
    readonly_fields = ['assigned_at', 'created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('patient')


class WardDeliveryRouteInline(admin.TabularInline):
    """Inline for delivery routes"""
    model = WardDeliveryRoute
    extra = 3
    fields = ['meal_type', 'scheduled_time', 'average_delivery_minutes', 'is_active']


class WardAvailabilityInline(admin.StackedInline):
    """Inline for ward availability"""
    model = WardAvailability
    extra = 0
    fields = ['available_beds', 'occupied_beds', 'maintenance_beds', 'reserved_beds', 'last_updated']
    readonly_fields = ['last_updated']


@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    """Admin for Ward model"""
    list_display = ['name', 'location', 'capacity', 'available_beds', 'occupancy_badge', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'location', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Ward Information', {
            'fields': ('name', 'location', 'capacity', 'description')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [WardBedInline, WardDeliveryRouteInline, WardAvailabilityInline]
    
    def available_beds(self, obj):
        """Display available beds count"""
        return obj.get_available_beds_count()
    available_beds.short_description = "Available Beds"
    
    def occupancy_badge(self, obj):
        """Display occupancy percentage with color"""
        occupancy = float(obj.get_occupancy_percentage())
        if occupancy < 50:
            color = '#28a745'  # green
        elif occupancy < 80:
            color = '#ffc107'  # yellow
        else:
            color = '#dc3545'  # red
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{:.0f}%</span>',
            color,
            occupancy
        )
    occupancy_badge.short_description = "Occupancy"


@admin.register(WardBed)
class WardBedAdmin(admin.ModelAdmin):
    """Admin for Ward Bed model"""
    list_display = ['bed_display', 'ward', 'status_badge', 'patient', 'assigned_at', 'is_active']
    list_filter = ['ward', 'status', 'is_active', 'assigned_at']
    search_fields = ['bed_number', 'patient__username', 'ward__name']
    readonly_fields = ['assigned_at', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Bed Information', {
            'fields': ('ward', 'bed_number', 'status', 'is_active')
        }),
        ('Patient Assignment', {
            'fields': ('patient', 'assigned_at')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def bed_display(self, obj):
        """Display bed number and ward"""
        return f"{obj.ward.name} - {obj.bed_number}"
    bed_display.short_description = "Bed"
    
    def status_badge(self, obj):
        """Display status with color badge"""
        colors = {
            'available': '#28a745',
            'occupied': '#ffc107',
            'maintenance': '#dc3545',
            'reserved': '#17a2b8',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = "Status"


@admin.register(WardDeliveryRoute)
class WardDeliveryRouteAdmin(admin.ModelAdmin):
    """Admin for Ward Delivery Route"""
    list_display = ['ward', 'meal_type', 'scheduled_time', 'average_delivery_minutes', 'is_active']
    list_filter = ['ward', 'meal_type', 'is_active']
    search_fields = ['ward__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Delivery Route', {
            'fields': ('ward', 'meal_type', 'scheduled_time', 'average_delivery_minutes')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(WardAvailability)
class WardAvailabilityAdmin(admin.ModelAdmin):
    """Admin for Ward Availability"""
    list_display = ['ward', 'available_beds', 'occupied_beds', 'maintenance_beds', 'reserved_beds', 'last_updated']
    list_filter = ['last_updated']
    search_fields = ['ward__name']
    readonly_fields = ['available_beds', 'occupied_beds', 'maintenance_beds', 'reserved_beds', 'last_updated']
    
    def has_add_permission(self, request):
        return False


@admin.register(MealNutritionInfo)
class MealNutritionInfoAdmin(admin.ModelAdmin):
    """Admin for Meal Nutrition Info"""
    list_display = ['menu_item', 'calories', 'protein_g', 'carbs_display', 'fat_g', 'allergen_count', 'created_at']
    list_filter = ['created_at', 'contains_gluten', 'contains_dairy', 'contains_nuts']
    search_fields = ['menu_item__name', 'key_ingredients']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Menu Item', {
            'fields': ('menu_item',)
        }),
        ('Macronutrients (per serving)', {
            'fields': ('calories', 'protein_g', 'carbohydrates_g', 'fat_g', 'fiber_g', 'serving_size')
        }),
        ('Micronutrients', {
            'fields': ('sodium_mg', 'potassium_mg', 'calcium_mg', 'iron_mg'),
            'classes': ('collapse',)
        }),
        ('Allergens', {
            'fields': ('contains_gluten', 'contains_dairy', 'contains_nuts', 'contains_shellfish', 'contains_eggs', 'contains_soy', 'allergen_warnings')
        }),
        ('Additional Information', {
            'fields': ('key_ingredients', 'suitable_for_diets', 'preparation_notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def carbs_display(self, obj):
        return obj.carbohydrates_g
    carbs_display.short_description = "Carbs (g)"
    
    def allergen_count(self, obj):
        """Display count of allergens"""
        return len(obj.get_allergen_list())
    allergen_count.short_description = "Allergens"


@admin.register(DeliveryScheduleSlot)
class DeliveryScheduleSlotAdmin(admin.ModelAdmin):
    """Admin for Delivery Schedule Slots"""
    list_display = ['ward', 'date', 'meal_type', 'time_range', 'booking_status', 'is_available']
    list_filter = ['ward', 'date', 'meal_type', 'is_available']
    search_fields = ['ward__name']
    readonly_fields = ['created_at']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Schedule', {
            'fields': ('ward', 'date', 'meal_type', 'start_time', 'end_time')
        }),
        ('Capacity', {
            'fields': ('max_bookings', 'current_bookings')
        }),
        ('Status', {
            'fields': ('is_available',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def time_range(self, obj):
        """Display time slot"""
        return f"{obj.start_time} - {obj.end_time}"
    time_range.short_description = "Time Slot"
    
    def booking_status(self, obj):
        """Display booking status"""
        available = obj.has_availability()
        status_text = f"{obj.current_bookings}/{obj.max_bookings}"
        color = '#28a745' if available else '#dc3545'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            status_text
        )
    booking_status.short_description = "Bookings"


class PatientEducationContentInline(admin.TabularInline):
    """Inline for education contents"""
    model = PatientEducationContent
    extra = 2
    fields = ['title', 'content_type', 'is_published']


@admin.register(PatientEducationCategory)
class PatientEducationCategoryAdmin(admin.ModelAdmin):
    """Admin for Education Categories"""
    list_display = ['name', 'icon', 'is_active', 'ordering', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
    
    inlines = [PatientEducationContentInline]


@admin.register(PatientEducationContent)
class PatientEducationContentAdmin(admin.ModelAdmin):
    """Admin for Education Content"""
    list_display = ['title', 'category', 'content_type', 'target_role', 'is_published', 'view_count', 'created_at']
    list_filter = ['category', 'content_type', 'target_role', 'is_published', 'created_at']
    search_fields = ['title', 'description', 'content']
    readonly_fields = ['created_at', 'updated_at', 'view_count']
    
    fieldsets = (
        ('Content Information', {
            'fields': ('category', 'title', 'description', 'content')
        }),
        ('Content Type & Target', {
            'fields': ('content_type', 'target_role', 'applicable_diet_types')
        }),
        ('Media', {
            'fields': ('image', 'video_url', 'pdf_file'),
            'classes': ('collapse',)
        }),
        ('Publishing', {
            'fields': ('is_published', 'author', 'ordering', 'view_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def view_count(self, obj):
        """Get view count from progress"""
        return obj.patient_progress.filter(completed=True).count()
    view_count.short_description = "Completion Count"


@admin.register(PatientEducationProgress)
class PatientEducationProgressAdmin(admin.ModelAdmin):
    """Admin for Education Progress"""
    list_display = ['patient', 'content', 'view_count', 'completed', 'first_accessed', 'last_accessed']
    list_filter = ['completed', 'first_accessed', 'last_accessed']
    search_fields = ['patient__username', 'content__title']
    readonly_fields = ['first_accessed', 'last_accessed']
    
    fieldsets = (
        ('Progress', {
            'fields': ('patient', 'content', 'view_count', 'completed', 'completion_date')
        }),
        ('Access History', {
            'fields': ('first_accessed', 'last_accessed'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CaregiverNotification)
class CaregiverNotificationAdmin(admin.ModelAdmin):
    """Admin for Caregiver Notifications"""
    list_display = ['patient', 'caregiver', 'notification_type', 'is_read_badge', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['patient__username', 'caregiver__username', 'title']
    readonly_fields = ['created_at', 'read_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Notification Details', {
            'fields': ('patient', 'caregiver', 'notification_type', 'title', 'message')
        }),
        ('Related Objects', {
            'fields': ('related_order', 'related_education'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_read', 'read_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def is_read_badge(self, obj):
        """Display read status"""
        if obj.is_read:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 3px;">Read</span>'
            )
        return format_html(
            '<span style="background-color: #ffc107; color: white; padding: 3px 8px; border-radius: 3px;">Unread</span>'
        )
    is_read_badge.short_description = "Status"


class PatientAdmissionAdmin(admin.ModelAdmin):
    """Admin for patient admissions"""
    list_display = ['patient_name', 'admission_date', 'reason', 'bed_number', 'admitted_by']
    list_filter = ['reason', 'admission_date', 'is_active']
    search_fields = ['patient__first_name', 'patient__last_name', 'chief_complaint']
    readonly_fields = ['admission_date', 'created_at', 'updated_at']
    fieldsets = (
        ('Patient Information', {
            'fields': ('patient', 'bed', 'admitted_by')
        }),
        ('Admission Details', {
            'fields': ('reason', 'chief_complaint', 'admission_date')
        }),
        ('Medical History', {
            'fields': ('medical_history', 'allergies', 'current_medications'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def patient_name(self, obj):
        return obj.patient.get_full_name()
    patient_name.short_description = "Patient"
    
    def bed_number(self, obj):
        return obj.bed.bed_number if obj.bed else "N/A"
    bed_number.short_description = "Bed"


class PatientDischargeAdmin(admin.ModelAdmin):
    """Admin for patient discharges"""
    list_display = ['patient_name', 'discharge_date', 'discharge_status', 'discharged_by']
    list_filter = ['discharge_status', 'discharge_date']
    search_fields = ['admission__patient__first_name', 'admission__patient__last_name']
    readonly_fields = ['discharge_date', 'created_at']
    fieldsets = (
        ('Discharge Information', {
            'fields': ('admission', 'discharge_status', 'discharge_date', 'discharged_by')
        }),
        ('Instructions & Medications', {
            'fields': ('discharge_notes', 'follow_up_instructions', 'medications_prescribed')
        }),
        ('Follow Up', {
            'fields': ('restrictions', 'return_visit_date'),
            'classes': ('collapse',)
        }),
    )
    
    def patient_name(self, obj):
        return obj.admission.patient.get_full_name()
    patient_name.short_description = "Patient"


class PatientTransferAdmin(admin.ModelAdmin):
    """Admin for patient bed transfers"""
    list_display = ['patient_name', 'from_bed_number', 'to_bed_number', 'transfer_date']
    list_filter = ['transfer_date', 'is_completed']
    search_fields = ['patient__first_name', 'patient__last_name']
    readonly_fields = ['transfer_date']
    
    def patient_name(self, obj):
        return obj.patient.get_full_name()
    patient_name.short_description = "Patient"
    
    def from_bed_number(self, obj):
        return obj.from_bed.bed_number if obj.from_bed else "N/A"
    from_bed_number.short_description = "From Bed"
    
    def to_bed_number(self, obj):
        return obj.to_bed.bed_number if obj.to_bed else "N/A"
    to_bed_number.short_description = "To Bed"


class BedMaintenanceScheduleAdmin(admin.ModelAdmin):
    """Admin for bed maintenance"""
    list_display = ['bed_number', 'maintenance_type', 'scheduled_date', 'is_completed']
    list_filter = ['maintenance_type', 'scheduled_date', 'is_completed']
    search_fields = ['bed__bed_number']
    readonly_fields = ['completed_date'] if 'completed_date' in [f.name for f in BedMaintenanceSchedule._meta.fields] else []
    
    def bed_number(self, obj):
        return obj.bed.bed_number
    bed_number.short_description = "Bed"


# Register admin classes
admin.site.register(PatientAdmission, PatientAdmissionAdmin)
admin.site.register(PatientDischarge, PatientDischargeAdmin)
admin.site.register(PatientTransfer, PatientTransferAdmin)
admin.site.register(BedMaintenanceSchedule, BedMaintenanceScheduleAdmin)


@admin.register(BulkOperation)
class BulkOperationAdmin(admin.ModelAdmin):
    """Admin for bulk operations"""
    list_display = ['operation_type', 'status_badge', 'total_records', 'successful_records', 'initiated_by', 'created_at']
    list_filter = ['operation_type', 'status', 'created_at']
    search_fields = ['initiated_by__username']
    readonly_fields = ['total_records', 'successful_records', 'failed_records', 'created_at', 'started_at', 'completed_at', 'success_rate_display']
    
    fieldsets = (
        ('Operation Information', {
            'fields': ('operation_type', 'status', 'initiated_by')
        }),
        ('File Handling', {
            'fields': ('input_file', 'output_file')
        }),
        ('Statistics', {
            'fields': ('total_records', 'successful_records', 'failed_records', 'success_rate_display', 'error_message')
        }),
        ('Timeline', {
            'fields': ('created_at', 'started_at', 'completed_at')
        }),
    )
    
    def status_badge(self, obj):
        """Display status as colored badge"""
        colors = {
            'pending': '#FFA500',
            'processing': '#87CEEB',
            'completed': '#90EE90',
            'failed': '#FF6B6B'
        }
        color = colors.get(obj.status, '#808080')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def success_rate_display(self, obj):
        """Display success rate"""
        return f"{obj.success_rate:.1f}%"
    success_rate_display.short_description = 'Success Rate'


@admin.register(PatientNotification)
class PatientNotificationAdmin(admin.ModelAdmin):
    """Admin for patient notifications"""
    list_display = ['title', 'notification_type', 'recipient', 'read_status', 'created_at']
    list_filter = ['notification_type', 'is_read', 'send_email', 'send_sms', 'created_at']
    search_fields = ['title', 'message', 'recipient__username', 'patient__username']
    readonly_fields = ['created_at', 'read_at']
    
    fieldsets = (
        ('Notification Information', {
            'fields': ('notification_type', 'title', 'message', 'recipient', 'patient', 'admission')
        }),
        ('Delivery Methods', {
            'fields': ('send_email', 'send_sms', 'send_in_app', 'scheduled_for')
        }),
        ('Status', {
            'fields': ('is_read', 'read_at', 'email_sent', 'sms_sent')
        }),
        ('Timeline', {
            'fields': ('created_at',)
        }),
    )
    
    def read_status(self, obj):
        """Display read status"""
        if obj.is_read:
            return format_html('<span style="color: green;">✓ Read</span>')
        return format_html('<span style="color: red;">✗ Unread</span>')
    read_status.short_description = 'Status'


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    """Admin for notification templates"""
    list_display = ['name', 'notification_type', 'is_active', 'created_at']
    list_filter = ['notification_type', 'is_active', 'created_at']
    search_fields = ['name', 'email_subject']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Template Information', {
            'fields': ('name', 'notification_type', 'is_active')
        }),
        ('Email Template', {
            'fields': ('email_subject', 'email_body'),
            'description': 'Variables: {patient_name}, {bed_number}, {ward_name}'
        }),
        ('SMS Template', {
            'fields': ('sms_body',),
            'description': 'Keep under 160 characters'
        }),
        ('Timeline', {
            'fields': ('created_at', 'updated_at')
        }),
    )

