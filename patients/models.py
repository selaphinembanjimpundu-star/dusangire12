"""
Patients App Models
Handles patient health profiles, nutrition tracking, and recovery metrics
Aligns with Business Model Canvas: Health Profile Management & Health Impact Tracking
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal


class HealthProfile(models.Model):
    """Patient health profile with medical history and dietary needs"""
    
    BLOOD_TYPE_CHOICES = [
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
    ]
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    ADMISSION_TYPE_CHOICES = [
        ('INPATIENT', 'Inpatient'),
        ('OUTPATIENT', 'Outpatient'),
        ('EMERGENCY', 'Emergency'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    
    # Personal Information
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    
    # Hospital Information
    admission_date = models.DateField()
    admission_type = models.CharField(max_length=10, choices=ADMISSION_TYPE_CHOICES)
    hospital_bed_number = models.CharField(max_length=50, blank=True)
    ward_name = models.CharField(max_length=100, blank=True)
    doctor_name = models.CharField(max_length=100, blank=True)
    
    # Medical Information
    primary_diagnosis = models.CharField(max_length=255)
    secondary_diagnosis = models.TextField(blank=True)
    medical_history = models.TextField(
        blank=True,
        help_text="Chronic conditions, previous surgeries, etc."
    )
    current_medications = models.TextField(blank=True)
    
    # Nutritional Information
    allergies = models.TextField(
        blank=True,
        help_text="Food allergies and intolerances (comma-separated)"
    )
    dietary_restrictions = models.TextField(
        blank=True,
        help_text="Religious, cultural, or preference-based restrictions"
    )
    
    # Nutritional Status
    height_cm = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('50'))],
        help_text="Height in centimeters"
    )
    weight_kg = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('10'))],
        help_text="Current weight in kilograms"
    )
    
    # Additional Information
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Patient Health Profile"
        verbose_name_plural = "Patient Health Profiles"
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['admission_date']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.primary_diagnosis}"
    
    @property
    def age(self):
        """Calculate patient age"""
        today = timezone.now().date()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    @property
    def bmi(self):
        """Calculate Body Mass Index"""
        height_m = self.height_cm / 100
        if height_m > 0:
            return round(float(self.weight_kg) / (height_m ** 2), 1)
        return None
    
    @property
    def hospital_stay_days(self):
        """Calculate days in hospital"""
        return (timezone.now().date() - self.admission_date).days
    
    @property
    def is_malnourished(self):
        """Check if patient shows signs of malnutrition"""
        if self.bmi is None:
            return False
        # BMI < 18.5 or > 40 indicates potential malnutrition
        return self.bmi < 18.5 or self.bmi > 40


class MedicalPrescription(models.Model):
    """Doctor-prescribed meal requirements for patient"""
    
    MEAL_TYPE_CHOICES = [
        ('DIABETIC', 'Diabetic Meal'),
        ('LOW_SODIUM', 'Low Sodium'),
        ('HIGH_PROTEIN', 'High Protein'),
        ('POST_SURGERY', 'Post-Surgery'),
        ('RENAL', 'Renal Diet'),
        ('CARDIAC', 'Cardiac Diet'),
        ('LIQUID', 'Liquid Diet'),
        ('SOFT', 'Soft Diet'),
        ('REGULAR', 'Regular Diet'),
    ]
    
    patient = models.ForeignKey(HealthProfile, on_delete=models.CASCADE, related_name='prescriptions')
    prescribed_by = models.CharField(max_length=100)  # Doctor name
    prescribed_date = models.DateField(auto_now_add=True)
    
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES)
    calories_per_day = models.IntegerField(
        validators=[MinValueValidator(500), MaxValueValidator(5000)],
        help_text="Target daily calories"
    )
    protein_grams = models.IntegerField(
        null=True,
        blank=True,
        help_text="Daily protein target in grams"
    )
    carbs_grams = models.IntegerField(
        null=True,
        blank=True,
        help_text="Daily carbohydrates target in grams"
    )
    fat_grams = models.IntegerField(
        null=True,
        blank=True,
        help_text="Daily fat target in grams"
    )
    
    # Timing
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Specific restrictions
    foods_to_avoid = models.TextField(blank=True)
    additional_instructions = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = "Medical Prescription"
        verbose_name_plural = "Medical Prescriptions"
    
    def __str__(self):
        return f"{self.patient} - {self.get_meal_type_display()}"
    
    @property
    def is_current(self):
        """Check if prescription is currently active"""
        today = timezone.now().date()
        if self.end_date:
            return self.start_date <= today <= self.end_date and self.is_active
        return self.start_date <= today and self.is_active


class PatientNutritionStatus(models.Model):
    """Track patient nutrition status improvements over time"""
    
    MALNUTRITION_LEVEL_CHOICES = [
        ('SEVERE', 'Severe'),
        ('MODERATE', 'Moderate'),
        ('MILD', 'Mild'),
        ('NORMAL', 'Normal'),
    ]
    
    patient = models.ForeignKey(HealthProfile, on_delete=models.CASCADE, related_name='nutrition_status')
    measurement_date = models.DateField(auto_now_add=True)
    
    # Nutrition Assessment
    malnutrition_level = models.CharField(
        max_length=20,
        choices=MALNUTRITION_LEVEL_CHOICES,
        default='MODERATE'
    )
    weight_kg = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('10'))],
        help_text="Weight at time of measurement"
    )
    mid_arm_circumference_cm = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Mid-arm circumference in cm"
    )
    serum_albumin_level = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Serum albumin level (g/dL)"
    )
    
    # Intake Assessment
    meal_intake_percentage = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage of prescribed meals consumed"
    )
    
    # Clinical Observations
    observations = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    
    # Assessment By
    assessed_by = models.CharField(max_length=100, blank=True)
    assessment_method = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g., Visual inspection, BMI calculation, Nutritionist review"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-measurement_date']
        verbose_name = "Patient Nutrition Status"
        verbose_name_plural = "Patient Nutrition Statuses"
        indexes = [
            models.Index(fields=['patient', '-measurement_date']),
        ]
    
    def __str__(self):
        return f"{self.patient} - {self.measurement_date} ({self.malnutrition_level})"
    
    @property
    def is_improving(self):
        """Check if nutrition status is improving"""
        # Get previous assessment
        previous = PatientNutritionStatus.objects.filter(
            patient=self.patient,
            measurement_date__lt=self.measurement_date
        ).order_by('-measurement_date').first()
        
        if not previous:
            return None  # No comparison data
        
        # Check if malnutrition level improved
        level_order = ['SEVERE', 'MODERATE', 'MILD', 'NORMAL']
        return level_order.index(self.malnutrition_level) > level_order.index(previous.malnutrition_level)


class RecoveryMetrics(models.Model):
    """Track patient recovery progress and health outcomes"""
    
    INFECTION_STATUS_CHOICES = [
        ('NO_INFECTION', 'No Infection'),
        ('SUSPECTED', 'Suspected Infection'),
        ('CONFIRMED', 'Confirmed Infection'),
        ('TREATED', 'Treated & Resolved'),
    ]
    
    WOUND_HEALING_CHOICES = [
        ('EXCELLENT', 'Excellent'),
        ('GOOD', 'Good'),
        ('FAIR', 'Fair'),
        ('POOR', 'Poor'),
    ]
    
    patient = models.ForeignKey(HealthProfile, on_delete=models.CASCADE, related_name='recovery_metrics')
    measurement_date = models.DateField(auto_now_add=True)
    
    # Hospital Stay Metrics
    days_in_hospital = models.IntegerField(validators=[MinValueValidator(0)])
    
    # Infection Monitoring
    infection_status = models.CharField(
        max_length=20,
        choices=INFECTION_STATUS_CHOICES,
        default='NO_INFECTION'
    )
    infection_date = models.DateField(null=True, blank=True)
    antibiotic_treatment = models.TextField(blank=True)
    
    # Wound Healing (if applicable)
    has_surgical_wound = models.BooleanField(default=False)
    wound_healing_status = models.CharField(
        max_length=20,
        choices=WOUND_HEALING_CHOICES,
        null=True,
        blank=True
    )
    wound_notes = models.TextField(blank=True)
    
    # Immunity & Vitals
    temperature_celsius = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Body temperature in Celsius"
    )
    blood_pressure = models.CharField(
        max_length=10,
        blank=True,
        help_text="e.g., 120/80"
    )
    immune_markers = models.TextField(
        blank=True,
        help_text="WBC count, CRP levels, other immune markers"
    )
    
    # Recovery Progress
    mobility_level = models.CharField(
        max_length=50,
        blank=True,
        help_text="e.g., Bed-ridden, Limited mobility, Ambulatory"
    )
    general_condition = models.TextField(
        blank=True,
        help_text="Overall patient condition and progress"
    )
    
    # Prognosis
    expected_discharge_date = models.DateField(null=True, blank=True)
    discharge_date = models.DateField(null=True, blank=True)
    discharge_status = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g., Recovered, Stable, Referral, etc."
    )
    
    # Assessment By
    assessed_by = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-measurement_date']
        verbose_name = "Recovery Metrics"
        verbose_name_plural = "Recovery Metrics"
        indexes = [
            models.Index(fields=['patient', '-measurement_date']),
        ]
    
    def __str__(self):
        return f"{self.patient} - Recovery ({self.measurement_date})"
    
    @property
    def is_recovered(self):
        """Check if patient is recovered"""
        return self.discharge_date is not None and self.discharge_status == 'Recovered'
    
    @property
    def had_complications(self):
        """Check if patient had any complications"""
        return self.infection_status != 'NO_INFECTION' or self.has_surgical_wound


class PatientMealHistory(models.Model):
    """Track meals delivered and consumed by patient"""
    
    patient = models.ForeignKey(HealthProfile, on_delete=models.CASCADE, related_name='meal_history')
    menu_item = models.ForeignKey('menu.MenuItem', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Meal Details
    meal_date = models.DateField(auto_now_add=True)
    meal_type = models.CharField(
        max_length=20,
        choices=[
            ('BREAKFAST', 'Breakfast'),
            ('LUNCH', 'Lunch'),
            ('DINNER', 'Dinner'),
            ('SNACK', 'Snack'),
        ]
    )
    
    # Prescribed vs Actual
    was_prescribed = models.BooleanField(default=True)
    quantity_consumed_percentage = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=100,
        help_text="Percentage of meal consumed"
    )
    
    # Feedback
    patient_feedback = models.TextField(blank=True)
    nutritionist_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-meal_date']
        verbose_name = "Patient Meal History"
        verbose_name_plural = "Patient Meal Histories"
        indexes = [
            models.Index(fields=['patient', '-meal_date']),
        ]
    
    def __str__(self):
        return f"{self.patient} - {self.meal_date} {self.meal_type}"


class HealthOutcomeStudy(models.Model):
    """Document health outcomes for research and impact tracking"""
    
    patient = models.ForeignKey(HealthProfile, on_delete=models.CASCADE, related_name='outcome_studies')
    
    # Study Parameters
    study_start_date = models.DateField(auto_now_add=True)
    study_end_date = models.DateField(null=True, blank=True)
    
    # Pre-Service Status
    pre_service_weight_kg = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text="Weight before starting meal service"
    )
    pre_service_malnutrition_level = models.CharField(
        max_length=20,
        choices=[
            ('SEVERE', 'Severe'),
            ('MODERATE', 'Moderate'),
            ('MILD', 'Mild'),
            ('NORMAL', 'Normal'),
        ]
    )
    pre_service_infection_status = models.CharField(
        max_length=20,
        blank=True,
        help_text="Initial infection status"
    )
    pre_service_hospital_stay_estimate = models.IntegerField(
        null=True,
        blank=True,
        help_text="Estimated days in hospital at start of service"
    )
    
    # Post-Service Status
    post_service_weight_kg = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Weight after meal service"
    )
    post_service_malnutrition_level = models.CharField(
        max_length=20,
        choices=[
            ('SEVERE', 'Severe'),
            ('MODERATE', 'Moderate'),
            ('MILD', 'Mild'),
            ('NORMAL', 'Normal'),
        ],
        null=True,
        blank=True
    )
    post_service_infection_status = models.CharField(
        max_length=20,
        blank=True,
        help_text="Final infection status"
    )
    actual_hospital_stay_days = models.IntegerField(
        null=True,
        blank=True,
        help_text="Actual days spent in hospital"
    )
    
    # Outcomes
    weight_change_kg = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Weight change during service"
    )
    malnutrition_improved = models.BooleanField(null=True, blank=True)
    infection_prevented = models.BooleanField(default=True)
    recovered_successfully = models.BooleanField(null=True, blank=True)
    
    # Study Notes
    clinical_observations = models.TextField(blank=True)
    researcher_notes = models.TextField(blank=True)
    
    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-study_start_date']
        verbose_name = "Health Outcome Study"
        verbose_name_plural = "Health Outcome Studies"
    
    def __str__(self):
        return f"Outcome Study: {self.patient} ({self.study_start_date})"
    
    @property
    def impact_summary(self):
        """Generate summary of health impact"""
        if not self.post_service_weight_kg:
            return "Study in progress"
        
        impacts = []
        if self.weight_change_kg and self.weight_change_kg > 0:
            impacts.append(f"Weight gain: +{self.weight_change_kg}kg")
        if self.malnutrition_improved:
            impacts.append("Malnutrition improved")
        if self.infection_prevented:
            impacts.append("Infection prevented")
        if self.recovered_successfully:
            impacts.append("Successfully recovered")
        
        return " | ".join(impacts) if impacts else "No significant improvements recorded"
