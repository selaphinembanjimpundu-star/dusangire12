from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserRole(models.TextChoices):
    """User roles based on DUSANGIRE Business Model Canvas"""
    # Customers / Patients
    PATIENT = 'patient', 'Patient'
    CAREGIVER = 'caregiver', 'Caregiver'
    
    # Healthcare & Nutrition
    NUTRITIONIST = 'nutritionist', 'Nutritionist'
    MEDICAL_STAFF = 'medical_staff', 'Medical Staff'
    
    # Operations & Delivery
    CHEF = 'chef', 'Chef'
    KITCHEN_STAFF = 'kitchen_staff', 'Kitchen Staff'
    DELIVERY_PERSON = 'delivery_person', 'Delivery Person'
    SUPPORT_STAFF = 'support_staff', 'Support Staff'
    
    # Management & Admin
    HOSPITAL_MANAGER = 'hospital_manager', 'Hospital Manager'
    ADMIN = 'admin', 'System Administrator'


class Profile(models.Model):
    """Extended user profile with role-specific information based on Business Model Canvas"""
    
    # Core User Information
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Role and Permissions
    role = models.CharField(
        max_length=30,
        choices=UserRole.choices,
        default=UserRole.PATIENT,
        help_text="User role determining dashboard and permissions"
    )
    
    # Status Management
    is_active = models.BooleanField(
        default=True,
        help_text="Whether user account is active"
    )
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('pending_verification', 'Pending Verification'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        help_text="Account status"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # ==================== PATIENT/CUSTOMER FIELDS ====================
    # Dietary preferences (comma-separated or JSON field)
    dietary_preferences = models.TextField(blank=True, help_text="Dietary preferences or restrictions")
    
    # Medical alerts
    medical_alerts = models.TextField(blank=True, help_text="Critical medical alerts or allergies")
    
    # Light status - only customers without light can register
    has_light = models.BooleanField(
        default=False,
        help_text="Whether customer has light. Only customers without light can register."
    )
    
    # ==================== HEALTHCARE PROVIDER FIELDS ====================
    # For Nutritionists and Medical Staff
    license_number = models.CharField(
        max_length=50,
        blank=True,
        help_text="Professional license number (for nutritionists and medical staff)"
    )
    
    specialization = models.CharField(
        max_length=200,
        blank=True,
        help_text="Professional specialization"
    )
    
    years_experience = models.IntegerField(
        null=True,
        blank=True,
        help_text="Years of professional experience"
    )
    
    # ==================== STAFF FIELDS ====================
    # For Kitchen Staff, Delivery, Support, etc.
    department = models.CharField(
        max_length=50,
        blank=True,
        help_text="Department assignment (e.g., Kitchen, Delivery, Support)"
    )
    
    employee_id = models.CharField(
        max_length=50,
        blank=True,
        unique=True,
        null=True,
        help_text="Employee ID for staff members"
    )
    
    manager = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        limit_choices_to={'role__in': ['hospital_manager', 'admin']},
        help_text="Direct manager for this staff member"
    )
    
    # ==================== DELIVERY PERSON FIELDS ====================
    vehicle_registration = models.CharField(
        max_length=50,
        blank=True,
        help_text="Vehicle registration number for delivery personnel"
    )
    
    delivery_zones = models.CharField(
        max_length=500,
        blank=True,
        help_text="Comma-separated list of delivery zones"
    )
    
    is_available_for_delivery = models.BooleanField(
        default=True,
        help_text="Whether delivery person is available for orders"
    )
    
    # ==================== CAREGIVER FIELDS ====================
    patient_relationship = models.CharField(
        max_length=50,
        blank=True,
        help_text="Relationship to patient (parent, spouse, sibling, etc.)"
    )
    
    assigned_patient = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='caregivers',
        limit_choices_to={'profile__role': 'patient'},
        help_text="Patient this caregiver is assigned to"
    )
    
    # ==================== NOTIFICATIONS & PREFERENCES ====================
    email_notifications = models.BooleanField(
        default=True,
        help_text="Receive notifications via email"
    )
    
    sms_notifications = models.BooleanField(
        default=True,
        help_text="Receive notifications via SMS"
    )
    
    push_notifications = models.BooleanField(
        default=True,
        help_text="Receive push notifications"
    )
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.get_role_display()}"
    
    def is_healthcare_provider(self):
        """Check if user is a healthcare provider (nutritionist or medical staff)"""
        return self.role in [UserRole.NUTRITIONIST, UserRole.MEDICAL_STAFF]
    
    def is_staff_member(self):
        """Check if user is a staff member"""
        return self.role in [
            UserRole.CHEF,
            UserRole.KITCHEN_STAFF,
            UserRole.DELIVERY_PERSON,
            UserRole.SUPPORT_STAFF,
            UserRole.HOSPITAL_MANAGER
        ]
    
    def is_patient_or_caregiver(self):
        """Check if user is a patient or caregiver"""
        return self.role in [UserRole.PATIENT, UserRole.CAREGIVER]
    
    def is_admin(self):
        """Check if user is system admin"""
        return self.role == UserRole.ADMIN
    
    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"
        indexes = [
            models.Index(fields=['role', 'is_active']),
            models.Index(fields=['user', 'role']),
        ]
    
    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create profile when user is created"""
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Automatically save profile when user is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()
