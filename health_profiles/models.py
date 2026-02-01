from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class HealthProfile(models.Model):
    """Track patient medical history, dietary restrictions, allergies"""
    
    BLOOD_TYPE_CHOICES = [
        ('O+', 'O+'), ('O-', 'O-'),
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='health_profile')
    date_of_birth = models.DateField()
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES, null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    height_cm = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    
    # Medical History
    medical_history = models.TextField(blank=True, help_text="Previous medical conditions")
    current_conditions = models.TextField(blank=True, help_text="Ongoing health conditions")
    medications = models.TextField(blank=True, help_text="Current medications")
    
    # Dietary Information
    allergies = models.TextField(blank=True, help_text="Food allergies (comma-separated)")
    dietary_restrictions = models.TextField(blank=True, help_text="Dietary restrictions")
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Health Profile - {self.user.get_full_name()}"
    
    def calculate_bmi(self):
        """Calculate Body Mass Index"""
        if self.height_cm and self.weight_kg:
            height_m = self.height_cm / 100
            return round(self.weight_kg / (height_m ** 2), 2)
        return None


class PatientNutritionStatus(models.Model):
    """Track malnutrition levels pre/post meal service"""
    
    STATUS_CHOICES = [
        ('MALNOURISHED', 'Malnourished'),
        ('AT_RISK', 'At Risk'),
        ('NORMAL', 'Normal'),
        ('OVERWEIGHT', 'Overweight'),
        ('OBESE', 'Obese'),
    ]
    
    ASSESSMENT_TYPE_CHOICES = [
        ('PRE_SERVICE', 'Pre-Service Assessment'),
        ('POST_SERVICE', 'Post-Service Assessment'),
        ('FOLLOW_UP', 'Follow-up Assessment'),
    ]
    
    health_profile = models.ForeignKey(HealthProfile, on_delete=models.CASCADE, related_name='nutrition_statuses')
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    muac_cm = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Mid-Upper Arm Circumference")
    nutritionist_notes = models.TextField(blank=True)
    
    assessed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='nutrition_assessments')
    assessment_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-assessment_date']
    
    def __str__(self):
        return f"{self.health_profile.user.username} - {self.assessment_type}"


class MedicalPrescription(models.Model):
    """Doctor-prescribed meal requirements per patient"""
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('COMPLETED', 'Completed'),
    ]
    
    health_profile = models.ForeignKey(HealthProfile, on_delete=models.CASCADE, related_name='medical_prescriptions')
    doctor_name = models.CharField(max_length=100)
    prescription_date = models.DateField()
    
    meal_requirements = models.TextField(help_text="Specific meal requirements prescribed by doctor")
    dietary_restrictions = models.TextField(blank=True, help_text="Additional dietary restrictions")
    calorie_target = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(0)], help_text="Daily calorie target")
    protein_target_grams = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])
    
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-prescription_date']
    
    def __str__(self):
        return f"Prescription for {self.health_profile.user.username} - {self.doctor_name}"


class RecoveryMetrics(models.Model):
    """Hospital stay duration, infection rates, outcome tracking"""
    
    OUTCOME_CHOICES = [
        ('RECOVERING', 'Recovering'),
        ('IMPROVED', 'Improved'),
        ('STABLE', 'Stable'),
        ('DECLINED', 'Declined'),
        ('DISCHARGED', 'Discharged'),
        ('TRANSFERRED', 'Transferred'),
    ]
    
    health_profile = models.ForeignKey(HealthProfile, on_delete=models.CASCADE, related_name='recovery_metrics')
    hospital_admission_date = models.DateField()
    hospital_discharge_date = models.DateField(blank=True, null=True)
    
    admission_reason = models.TextField()
    infection_status = models.BooleanField(default=False, help_text="Infection present during stay")
    infection_type = models.CharField(max_length=100, blank=True)
    
    current_outcome = models.CharField(max_length=20, choices=OUTCOME_CHOICES, default='RECOVERING')
    recovery_notes = models.TextField(blank=True)
    
    attending_physician = models.CharField(max_length=100, blank=True)
    nutrition_intervention_applied = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-hospital_admission_date']
    
    def __str__(self):
        return f"Recovery - {self.health_profile.user.username}"
    
    @property
    def hospital_stay_days(self):
        """Calculate hospital stay duration"""
        if self.hospital_discharge_date:
            return (self.hospital_discharge_date - self.hospital_admission_date).days
        from django.utils import timezone
        return (timezone.now().date() - self.hospital_admission_date).days


# ============ HEALTH CHECK & CONSULTATION AUTO-ASSIGNMENT ============

class HealthCheck(models.Model):
    """Health check appointment/consultation request with auto-assignment"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending - Awaiting Assignment'),
        ('assigned', 'Assigned - Consultant Assigned'),
        ('in_progress', 'In Progress - Consultation Ongoing'),
        ('completed', 'Completed - Consultation Done'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('urgent', 'Urgent - Immediate attention needed'),
        ('high', 'High - Within 24 hours'),
        ('normal', 'Normal - Within 3 days'),
        ('low', 'Low - Flexible scheduling'),
    ]
    
    TYPE_CHOICES = [
        ('initial', 'Initial Health Assessment'),
        ('follow_up', 'Follow-up Consultation'),
        ('nutrition', 'Nutrition Assessment'),
        ('medical', 'Medical Check'),
        ('wellness', 'Wellness Check'),
    ]
    
    # Patient/Customer Info
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='health_checks')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Check Details
    check_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='wellness')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    
    # Description
    description = models.TextField(help_text="Patient's health concerns or reason for check")
    medical_history = models.TextField(blank=True, help_text="Relevant medical history")
    current_symptoms = models.TextField(blank=True, help_text="Current symptoms if any")
    
    # Consultant Assignment
    assigned_consultant = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_health_checks'
    )
    
    # Scheduling
    requested_date = models.DateField(null=True, blank=True)
    requested_time_slot = models.CharField(max_length=50, blank=True, help_text="e.g., '09:00-10:00'")
    scheduled_datetime = models.DateTimeField(null=True, blank=True)
    completed_datetime = models.DateTimeField(null=True, blank=True)
    
    # Assignment Tracking
    auto_assigned = models.BooleanField(default=False, help_text="Auto-assigned by system")
    assigned_at = models.DateTimeField(null=True, blank=True)
    assignment_reason = models.CharField(max_length=200, blank=True)
    
    # Notes
    consultant_notes = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-priority', 'created_at']
        indexes = [
            models.Index(fields=['patient', 'status']),
            models.Index(fields=['status', 'assigned_consultant']),
        ]
    
    def __str__(self):
        return f"Health Check #{self.id} - {self.patient.get_full_name()}"
    
    @property
    def is_pending_assignment(self):
        return self.status == 'pending' and not self.assigned_consultant


class ConsultantAvailability(models.Model):
    """Track consultant availability for auto-assignment"""
    
    AVAILABILITY_STATUS = [
        ('available', 'Available - Can accept assignments'),
        ('busy', 'Busy - Currently in consultation'),
        ('break', 'On Break'),
        ('offline', 'Offline'),
    ]
    
    consultant = models.OneToOneField(User, on_delete=models.CASCADE, related_name='consultant_availability')
    
    # Status
    status = models.CharField(max_length=20, choices=AVAILABILITY_STATUS, default='offline')
    
    # Capacity
    max_concurrent_checks = models.IntegerField(default=3)
    current_assignments = models.IntegerField(default=0)
    
    # Specialization
    specialization = models.CharField(max_length=100, blank=True)
    preferred_check_types = models.CharField(max_length=200, blank=True, help_text="Comma-separated list")
    
    # Performance
    average_rating = models.FloatField(default=0.0)
    total_completed_checks = models.IntegerField(default=0)
    
    last_status_update = models.DateTimeField(auto_now=True)
    next_available_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['status', '-average_rating']
    
    def __str__(self):
        return f"{self.consultant.get_full_name()} - {self.status}"
    
    @property
    def is_available(self):
        """Check if consultant can accept new assignments"""
        return self.status == 'available' and self.current_assignments < self.max_concurrent_checks
    
    @property
    def available_slots(self):
        """Calculate available assignment slots"""
        return max(0, self.max_concurrent_checks - self.current_assignments)


class AutoAssignmentLog(models.Model):
    """Audit log for auto-assignment actions"""
    
    RESULT_CHOICES = [
        ('success', 'Successfully Assigned'),
        ('no_available', 'No Available Consultant'),
        ('error', 'Assignment Error'),
    ]
    
    health_check = models.ForeignKey(HealthCheck, on_delete=models.CASCADE, related_name='assignment_logs')
    assigned_consultant = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    result = models.CharField(max_length=20, choices=RESULT_CHOICES)
    message = models.TextField()
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Assignment #{self.id} - {self.result}"
