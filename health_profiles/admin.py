from django.contrib import admin
from django.utils.html import format_html
from .models import HealthProfile, PatientNutritionStatus, MedicalPrescription, RecoveryMetrics

@admin.register(HealthProfile)
class HealthProfileAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'age', 'blood_type', 'bmi_display', 'allergies_preview', 'created_at')
    list_filter = ('blood_type', 'created_at', 'updated_at')
    search_fields = ('user__first_name', 'user__last_name', 'user__username', 'allergies', 'dietary_restrictions')
    readonly_fields = ('created_at', 'updated_at', 'bmi_calculation', 'age_calculation')
    
    fieldsets = (
        ('Patient Information', {
            'fields': ('user', 'date_of_birth', 'age_calculation')
        }),
        ('Blood & Vital', {
            'fields': ('blood_type', 'weight_kg', 'height_cm', 'bmi_calculation')
        }),
        ('Medical History', {
            'fields': ('medical_history', 'current_conditions', 'medications')
        }),
        ('Dietary Information', {
            'fields': ('allergies', 'dietary_restrictions')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def patient_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    patient_name.short_description = 'Patient Name'
    
    def age_calculation(self, obj):
        from django.utils import timezone
        from dateutil.relativedelta import relativedelta
        
        age = relativedelta(timezone.now().date(), obj.date_of_birth).years
        return f"{age} years"
    age_calculation.short_description = 'Age'
    
    def bmi_calculation(self, obj):
        bmi = obj.calculate_bmi()
        if bmi:
            if bmi < 18.5:
                color = 'red'
                category = 'Underweight'
            elif bmi < 25:
                color = 'green'
                category = 'Normal'
            elif bmi < 30:
                color = 'orange'
                category = 'Overweight'
            else:
                color = 'darkred'
                category = 'Obese'
            
            return format_html(
                '<span style="color: {}; font-weight: bold;">{} ({})</span>',
                color, bmi, category
            )
        return 'N/A'
    bmi_calculation.short_description = 'BMI'
    
    def bmi_display(self, obj):
        bmi = obj.calculate_bmi()
        if bmi:
            return f"{bmi}"
        return 'N/A'
    bmi_display.short_description = 'BMI'
    
    def allergies_preview(self, obj):
        if obj.allergies:
            preview = obj.allergies[:50]
            return preview + '...' if len(obj.allergies) > 50 else preview
        return '—'
    allergies_preview.short_description = 'Allergies'
    
    def age(self, obj):
        from django.utils import timezone
        from dateutil.relativedelta import relativedelta
        
        return relativedelta(timezone.now().date(), obj.date_of_birth).years
    
    ordering = ['-created_at']


@admin.register(PatientNutritionStatus)
class PatientNutritionStatusAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'assessment_type', 'status_badge', 'weight_kg', 'assessed_by', 'assessment_date')
    list_filter = ('assessment_type', 'status', 'assessment_date')
    search_fields = ('health_profile__user__first_name', 'health_profile__user__last_name', 'nutritionist_notes')
    readonly_fields = ('assessment_date',)
    
    fieldsets = (
        ('Patient Information', {
            'fields': ('health_profile',)
        }),
        ('Assessment Details', {
            'fields': ('assessment_type', 'status', 'assessment_date', 'assessed_by')
        }),
        ('Measurements', {
            'fields': ('weight_kg', 'muac_cm')
        }),
        ('Notes', {
            'fields': ('nutritionist_notes',)
        })
    )
    
    def patient_name(self, obj):
        return obj.health_profile.user.get_full_name() or obj.health_profile.user.username
    patient_name.short_description = 'Patient'
    
    def status_badge(self, obj):
        colors = {
            'MALNOURISHED': 'darkred',
            'AT_RISK': 'orange',
            'NORMAL': 'green',
            'OVERWEIGHT': 'gold',
            'OBESE': 'red',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    ordering = ['-assessment_date']


@admin.register(MedicalPrescription)
class MedicalPrescriptionAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'doctor_name', 'prescription_date', 'status_badge', 'start_date', 'end_date')
    list_filter = ('status', 'prescription_date', 'start_date')
    search_fields = ('health_profile__user__first_name', 'health_profile__user__last_name', 'doctor_name', 'meal_requirements')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Patient Information', {
            'fields': ('health_profile',)
        }),
        ('Doctor Information', {
            'fields': ('doctor_name', 'prescription_date')
        }),
        ('Prescription Details', {
            'fields': ('meal_requirements', 'dietary_restrictions', 'calorie_target', 'protein_target_grams')
        }),
        ('Duration & Status', {
            'fields': ('start_date', 'end_date', 'status')
        }),
        ('Additional Notes', {
            'fields': ('notes',)
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def patient_name(self, obj):
        return obj.health_profile.user.get_full_name() or obj.health_profile.user.username
    patient_name.short_description = 'Patient'
    
    def status_badge(self, obj):
        colors = {
            'ACTIVE': 'green',
            'INACTIVE': 'gray',
            'COMPLETED': 'blue',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    ordering = ['-prescription_date']


@admin.register(RecoveryMetrics)
class RecoveryMetricsAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'hospital_admission_date', 'stay_duration', 'current_outcome_badge', 'infection_status_badge')
    list_filter = ('current_outcome', 'infection_status', 'hospital_admission_date')
    search_fields = ('health_profile__user__first_name', 'health_profile__user__last_name', 'admission_reason', 'attending_physician')
    readonly_fields = ('created_at', 'updated_at', 'stay_duration_display')
    
    fieldsets = (
        ('Patient Information', {
            'fields': ('health_profile',)
        }),
        ('Hospital Information', {
            'fields': ('hospital_admission_date', 'hospital_discharge_date', 'stay_duration_display', 'attending_physician')
        }),
        ('Admission Details', {
            'fields': ('admission_reason', 'nutrition_intervention_applied')
        }),
        ('Infection Status', {
            'fields': ('infection_status', 'infection_type')
        }),
        ('Recovery Status', {
            'fields': ('current_outcome', 'recovery_notes')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def patient_name(self, obj):
        return obj.health_profile.user.get_full_name() or obj.health_profile.user.username
    patient_name.short_description = 'Patient'
    
    def stay_duration(self, obj):
        return f"{obj.hospital_stay_days} days"
    stay_duration.short_description = 'Stay Duration'
    
    def stay_duration_display(self, obj):
        return f"{obj.hospital_stay_days} days"
    stay_duration_display.short_description = 'Hospital Stay Duration'
    
    def current_outcome_badge(self, obj):
        colors = {
            'RECOVERING': 'blue',
            'IMPROVED': 'green',
            'STABLE': 'gray',
            'DECLINED': 'orange',
            'DISCHARGED': 'darkgreen',
            'TRANSFERRED': 'purple',
        }
        color = colors.get(obj.current_outcome, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_current_outcome_display()
        )
    current_outcome_badge.short_description = 'Outcome'
    
    def infection_status_badge(self, obj):
        if obj.infection_status:
            return format_html(
                '<span style="background-color: red; color: white; padding: 3px 10px; border-radius: 3px;">Infected</span>'
            )
        return format_html(
            '<span style="background-color: green; color: white; padding: 3px 10px; border-radius: 3px;">Clear</span>'
        )
    infection_status_badge.short_description = 'Infection'
    
    ordering = ['-hospital_admission_date']


# ==================== HEALTH CHECK AUTO-ASSIGNMENT ADMIN ====================

from .models import HealthCheck, ConsultantAvailability, AutoAssignmentLog


@admin.register(HealthCheck)
class HealthCheckAdmin(admin.ModelAdmin):
    """Admin interface for managing health checks"""
    list_display = ('id', 'patient', 'check_type', 'status', 'priority', 'assigned_consultant', 'auto_assigned', 'created_at')
    list_filter = ('status', 'priority', 'check_type', 'created_at', 'auto_assigned')
    search_fields = ('patient__first_name', 'patient__email', 'assigned_consultant__first_name', 'assigned_consultant__email')
    readonly_fields = ('auto_assigned', 'created_at', 'assigned_at', 'completed_datetime')
    
    fieldsets = (
        ('Check Information', {
            'fields': ('patient', 'check_type', 'priority', 'status')
        }),
        ('Assignment', {
            'fields': ('assigned_consultant', 'auto_assigned', 'assigned_at')
        }),
        ('Details', {
            'fields': ('description', 'requested_date')
        }),
        ('Consultation', {
            'fields': ('scheduled_datetime', 'consultant_notes', 'recommendations', 'completed_datetime')
        }),
        ('Tracking', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """Optimize queries with select_related"""
        queryset = super().get_queryset(request)
        return queryset.select_related('patient', 'assigned_consultant')


@admin.register(ConsultantAvailability)
class ConsultantAvailabilityAdmin(admin.ModelAdmin):
    """Admin interface for managing consultant availability"""
    list_display = ('consultant', 'status', 'current_assignments', 'max_concurrent_checks', 'average_rating', 'total_completed_checks')
    list_filter = ('status',)
    search_fields = ('consultant__first_name', 'consultant__email')
    readonly_fields = ('total_completed_checks',)
    
    fieldsets = (
        ('Consultant', {
            'fields': ('consultant',)
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Capacity', {
            'fields': ('current_assignments', 'max_concurrent_checks')
        }),
        ('Specialization', {
            'fields': ('specialization', 'preferred_check_types')
        }),
        ('Performance', {
            'fields': ('average_rating', 'total_completed_checks')
        }),
    )


@admin.register(AutoAssignmentLog)
class AutoAssignmentLogAdmin(admin.ModelAdmin):
    """Admin interface for viewing assignment logs"""
    list_display = ('id', 'health_check', 'assigned_consultant', 'result', 'timestamp')
    list_filter = ('result', 'timestamp')
    search_fields = ('assigned_consultant__email', 'message', 'health_check__id')
    readonly_fields = ('timestamp', 'health_check', 'assigned_consultant', 'result', 'message')
    
    fieldsets = (
        ('Assignment', {
            'fields': ('health_check', 'assigned_consultant')
        }),
        ('Result', {
            'fields': ('result', 'message')
        }),
        ('Timestamp', {
            'fields': ('timestamp',)
        }),
    )

    def has_add_permission(self, request):
        """Prevent manual creation of logs"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of logs (audit trail)"""
        return False
