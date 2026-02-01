"""
Admin configuration for Patients app
Provides comprehensive management interface for health profiles and outcomes
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    HealthProfile, MedicalPrescription, PatientNutritionStatus,
    RecoveryMetrics, PatientMealHistory, HealthOutcomeStudy
)


@admin.register(HealthProfile)
class HealthProfileAdmin(admin.ModelAdmin):
    """Admin interface for patient health profiles"""
    
    list_display = [
        'patient_name', 'age_gender', 'admission_type', 'primary_diagnosis',
        'bmi_status', 'hospital_stay_days', 'is_active'
    ]
    list_filter = [
        'admission_type', 'gender', 'ward_name', 'admission_date', 'is_active'
    ]
    search_fields = [
        'user__first_name', 'user__last_name', 'primary_diagnosis',
        'hospital_bed_number', 'doctor_name'
    ]
    readonly_fields = [
        'created_at', 'updated_at', 'age', 'bmi', 'hospital_stay_days',
        'is_malnourished'
    ]
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'date_of_birth', 'age', 'gender', 'blood_type',
                      'phone_number', 'emergency_contact')
        }),
        ('Hospital Information', {
            'fields': ('admission_date', 'hospital_stay_days', 'admission_type',
                      'hospital_bed_number', 'ward_name', 'doctor_name')
        }),
        ('Medical Information', {
            'fields': ('primary_diagnosis', 'secondary_diagnosis', 'medical_history',
                      'current_medications')
        }),
        ('Nutritional Information', {
            'fields': ('allergies', 'dietary_restrictions', 'height_cm', 'weight_kg',
                      'bmi', 'is_malnourished')
        }),
        ('Status & Metadata', {
            'fields': ('notes', 'is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def patient_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    patient_name.short_description = 'Patient Name'
    
    def age_gender(self, obj):
        return f"{obj.age} years, {obj.get_gender_display()}"
    age_gender.short_description = 'Age / Gender'
    
    def bmi_status(self, obj):
        bmi = obj.bmi
        if bmi is None:
            return "—"
        if bmi < 18.5:
            return format_html(
                '<span style="color: orange;"><b>BMI: {:.1f} (Low)</b></span>',
                bmi
            )
        elif 18.5 <= bmi <= 24.9:
            return format_html(
                '<span style="color: green;"><b>BMI: {:.1f} (Normal)</b></span>',
                bmi
            )
        elif 25 <= bmi < 30:
            return format_html(
                '<span style="color: orange;"><b>BMI: {:.1f} (Overweight)</b></span>',
                bmi
            )
        else:
            return format_html(
                '<span style="color: red;"><b>BMI: {:.1f} (Obese)</b></span>',
                bmi
            )
    bmi_status.short_description = 'BMI Status'


@admin.register(MedicalPrescription)
class MedicalPrescriptionAdmin(admin.ModelAdmin):
    """Admin interface for medical prescriptions"""
    
    list_display = [
        'patient', 'meal_type', 'calories_per_day', 'prescribed_by',
        'prescribed_date', 'is_current'
    ]
    list_filter = [
        'meal_type', 'prescribed_date', 'start_date', 'is_active'
    ]
    search_fields = [
        'patient__user__first_name', 'patient__user__last_name',
        'prescribed_by', 'meal_type'
    ]
    readonly_fields = ['prescribed_date', 'created_at', 'updated_at', 'is_current']
    
    fieldsets = (
        ('Prescription Details', {
            'fields': ('patient', 'prescribed_by', 'prescribed_date')
        }),
        ('Meal Requirements', {
            'fields': ('meal_type', 'calories_per_day', 'protein_grams',
                      'carbs_grams', 'fat_grams')
        }),
        ('Duration', {
            'fields': ('start_date', 'end_date', 'is_active', 'is_current')
        }),
        ('Special Instructions', {
            'fields': ('foods_to_avoid', 'additional_instructions')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PatientNutritionStatus)
class PatientNutritionStatusAdmin(admin.ModelAdmin):
    """Admin interface for nutrition status tracking"""
    
    list_display = [
        'patient', 'measurement_date', 'malnutrition_level_color',
        'weight_kg', 'meal_intake_percentage', 'is_improving'
    ]
    list_filter = [
        'malnutrition_level', 'measurement_date', 'assessment_method'
    ]
    search_fields = [
        'patient__user__first_name', 'patient__user__last_name',
        'assessed_by'
    ]
    readonly_fields = [
        'created_at', 'is_improving', 'measurement_date'
    ]
    
    def malnutrition_level_color(self, obj):
        colors = {
            'SEVERE': '#d32f2f',
            'MODERATE': '#ff9800',
            'MILD': '#ffc107',
            'NORMAL': '#4caf50',
        }
        color = colors.get(obj.malnutrition_level, '#000')
        return format_html(
            '<span style="color: white; background-color: {}; padding: 5px 10px; '
            'border-radius: 3px;"><b>{}</b></span>',
            color, obj.get_malnutrition_level_display()
        )
    malnutrition_level_color.short_description = 'Malnutrition Level'


@admin.register(RecoveryMetrics)
class RecoveryMetricsAdmin(admin.ModelAdmin):
    """Admin interface for recovery metrics tracking"""
    
    list_display = [
        'patient', 'measurement_date', 'days_in_hospital',
        'infection_status_color', 'mobility_level', 'discharge_status'
    ]
    list_filter = [
        'infection_status', 'measurement_date', 'has_surgical_wound',
        'discharge_status'
    ]
    search_fields = [
        'patient__user__first_name', 'patient__user__last_name',
        'assessed_by'
    ]
    readonly_fields = ['created_at', 'measurement_date']
    
    fieldsets = (
        ('Patient & Assessment', {
            'fields': ('patient', 'measurement_date', 'assessed_by')
        }),
        ('Hospital Metrics', {
            'fields': ('days_in_hospital', 'expected_discharge_date',
                      'discharge_date', 'discharge_status')
        }),
        ('Infection Monitoring', {
            'fields': ('infection_status', 'infection_date', 'antibiotic_treatment')
        }),
        ('Wound Healing', {
            'fields': ('has_surgical_wound', 'wound_healing_status', 'wound_notes'),
            'classes': ('collapse',)
        }),
        ('Vitals & Immunity', {
            'fields': ('temperature_celsius', 'blood_pressure', 'immune_markers')
        }),
        ('Recovery Progress', {
            'fields': ('mobility_level', 'general_condition')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def infection_status_color(self, obj):
        colors = {
            'NO_INFECTION': '#4caf50',
            'SUSPECTED': '#ff9800',
            'CONFIRMED': '#d32f2f',
            'TREATED': '#2196f3',
        }
        color = colors.get(obj.infection_status, '#000')
        return format_html(
            '<span style="color: white; background-color: {}; padding: 5px 10px; '
            'border-radius: 3px;"><b>{}</b></span>',
            color, obj.get_infection_status_display()
        )
    infection_status_color.short_description = 'Infection Status'


@admin.register(PatientMealHistory)
class PatientMealHistoryAdmin(admin.ModelAdmin):
    """Admin interface for patient meal history tracking"""
    
    list_display = [
        'patient', 'meal_date', 'meal_type', 'menu_item',
        'quantity_consumed_percentage', 'was_prescribed'
    ]
    list_filter = [
        'meal_type', 'meal_date', 'was_prescribed'
    ]
    search_fields = [
        'patient__user__first_name', 'patient__user__last_name',
        'menu_item__name'
    ]
    readonly_fields = ['created_at', 'meal_date']
    
    fieldsets = (
        ('Meal Details', {
            'fields': ('patient', 'menu_item', 'meal_date', 'meal_type')
        }),
        ('Consumption', {
            'fields': ('was_prescribed', 'quantity_consumed_percentage')
        }),
        ('Feedback', {
            'fields': ('patient_feedback', 'nutritionist_notes')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(HealthOutcomeStudy)
class HealthOutcomeStudyAdmin(admin.ModelAdmin):
    """Admin interface for health outcome studies"""
    
    list_display = [
        'patient', 'study_start_date', 'study_end_date',
        'malnutrition_improved', 'infection_prevented', 'recovered_successfully'
    ]
    list_filter = [
        'study_start_date', 'malnutrition_improved',
        'infection_prevented', 'recovered_successfully'
    ]
    search_fields = [
        'patient__user__first_name', 'patient__user__last_name'
    ]
    readonly_fields = [
        'created_at', 'updated_at', 'weight_change_kg', 'impact_summary'
    ]
    
    fieldsets = (
        ('Study Parameters', {
            'fields': ('patient', 'study_start_date', 'study_end_date')
        }),
        ('Pre-Service Status', {
            'fields': ('pre_service_weight_kg', 'pre_service_malnutrition_level',
                      'pre_service_infection_status', 'pre_service_hospital_stay_estimate')
        }),
        ('Post-Service Status', {
            'fields': ('post_service_weight_kg', 'post_service_malnutrition_level',
                      'post_service_infection_status', 'actual_hospital_stay_days')
        }),
        ('Outcomes', {
            'fields': ('weight_change_kg', 'malnutrition_improved', 'infection_prevented',
                      'recovered_successfully', 'impact_summary')
        }),
        ('Study Notes', {
            'fields': ('clinical_observations', 'researcher_notes'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
