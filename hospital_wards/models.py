"""
Hospital Ward Management Models
Handles ward & bed management, delivery scheduling, nutrition info, and patient education
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal


class Ward(models.Model):
    """Hospital ward/department"""
    name = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=255, help_text="Ward location/building")
    capacity = models.PositiveIntegerField(help_text="Total number of beds in ward")
    description = models.TextField(blank=True, help_text="Ward description and specialties")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_available_beds_count(self):
        """Get number of available beds"""
        return self.capacity - self.beds.filter(status='occupied').count()
    
    def get_occupancy_percentage(self):
        """Get ward occupancy percentage"""
        occupied = self.beds.filter(status='occupied').count()
        if self.capacity == 0:
            return 0
        return (occupied / self.capacity) * 100


class WardBed(models.Model):
    """Individual bed in a ward"""
    BED_STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Maintenance'),
        ('reserved', 'Reserved'),
    ]
    
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE, related_name='beds')
    bed_number = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=BED_STATUS_CHOICES, default='available')
    patient = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='hospital_bed')
    assigned_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['ward', 'bed_number']
        ordering = ['ward', 'bed_number']
    
    def __str__(self):
        return f"{self.ward.name} - Bed {self.bed_number}"
    
    def assign_patient(self, patient):
        """Assign patient to bed"""
        if self.status != 'available':
            raise ValueError(f"Bed {self.bed_number} is not available")
        self.patient = patient
        self.status = 'occupied'
        self.assigned_at = timezone.now()
        self.save()
    
    def release_patient(self):
        """Release patient from bed"""
        self.patient = None
        self.status = 'available'
        self.assigned_at = None
        self.save()


class WardDeliveryRoute(models.Model):
    """Delivery route/schedule for a ward"""
    MEAL_TYPE_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
        ('supplement', 'Supplement'),
    ]
    
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE, related_name='delivery_routes')
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES)
    scheduled_time = models.TimeField(help_text="Typical delivery time for this meal")
    average_delivery_minutes = models.PositiveIntegerField(
        default=30,
        help_text="Average minutes to deliver all meals in ward"
    )
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['ward', 'meal_type']
        ordering = ['ward', 'scheduled_time']
    
    def __str__(self):
        return f"{self.ward.name} - {self.get_meal_type_display()} ({self.scheduled_time})"


class WardAvailability(models.Model):
    """Real-time availability tracking for ward beds"""
    ward = models.OneToOneField(Ward, on_delete=models.CASCADE, related_name='availability')
    available_beds = models.PositiveIntegerField(default=0)
    occupied_beds = models.PositiveIntegerField(default=0)
    maintenance_beds = models.PositiveIntegerField(default=0)
    reserved_beds = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Ward Availabilities"
    
    def __str__(self):
        return f"{self.ward.name} - {self.available_beds}/{self.ward.capacity} available"
    
    def update_counts(self):
        """Update availability counts from actual bed statuses"""
        self.available_beds = self.ward.beds.filter(status='available').count()
        self.occupied_beds = self.ward.beds.filter(status='occupied').count()
        self.maintenance_beds = self.ward.beds.filter(status='maintenance').count()
        self.reserved_beds = self.ward.beds.filter(status='reserved').count()
        self.save()


class MealNutritionInfo(models.Model):
    """Detailed nutrition information for meals"""
    from menu.models import MenuItem
    
    menu_item = models.OneToOneField('menu.MenuItem', on_delete=models.CASCADE, related_name='nutrition_info')
    
    # Macronutrients (per serving)
    calories = models.PositiveIntegerField(help_text="Calories per serving")
    protein_g = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Protein in grams"
    )
    carbohydrates_g = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Carbohydrates in grams"
    )
    fat_g = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Fat in grams"
    )
    fiber_g = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Dietary fiber in grams"
    )
    
    # Micronutrients
    sodium_mg = models.PositiveIntegerField(
        default=0,
        help_text="Sodium in milligrams"
    )
    potassium_mg = models.PositiveIntegerField(
        default=0,
        help_text="Potassium in milligrams"
    )
    calcium_mg = models.PositiveIntegerField(
        default=0,
        help_text="Calcium in milligrams"
    )
    iron_mg = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Iron in milligrams"
    )
    
    # Allergen information
    contains_gluten = models.BooleanField(default=False)
    contains_dairy = models.BooleanField(default=False)
    contains_nuts = models.BooleanField(default=False)
    contains_shellfish = models.BooleanField(default=False)
    contains_eggs = models.BooleanField(default=False)
    contains_soy = models.BooleanField(default=False)
    allergen_warnings = models.TextField(
        blank=True,
        help_text="Additional allergen warnings (comma-separated)"
    )
    
    # Additional info
    key_ingredients = models.TextField(
        blank=True,
        help_text="Key ingredients (comma-separated)"
    )
    suitable_for_diets = models.CharField(
        max_length=255,
        blank=True,
        help_text="Suitable diet types: diabetic, low-sodium, high-protein, vegetarian, vegan, etc."
    )
    preparation_notes = models.TextField(blank=True)
    serving_size = models.CharField(
        max_length=100,
        default="1 plate",
        help_text="Standard serving size"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Meal Nutrition Info"
        verbose_name_plural = "Meal Nutrition Info"
    
    def __str__(self):
        return f"Nutrition Info - {self.menu_item.name}"
    
    def get_allergen_list(self):
        """Get list of allergens present in meal"""
        allergens = []
        if self.contains_gluten:
            allergens.append("Gluten")
        if self.contains_dairy:
            allergens.append("Dairy")
        if self.contains_nuts:
            allergens.append("Nuts")
        if self.contains_shellfish:
            allergens.append("Shellfish")
        if self.contains_eggs:
            allergens.append("Eggs")
        if self.contains_soy:
            allergens.append("Soy")
        if self.allergen_warnings:
            allergens.extend([a.strip() for a in self.allergen_warnings.split(',')])
        return allergens


class DeliveryScheduleSlot(models.Model):
    """Available delivery time slots for meal booking"""
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE, related_name='delivery_slots')
    meal_type = models.CharField(
        max_length=20,
        choices=[
            ('breakfast', 'Breakfast'),
            ('lunch', 'Lunch'),
            ('dinner', 'Dinner'),
            ('snack', 'Snack'),
        ]
    )
    date = models.DateField()
    start_time = models.TimeField(help_text="Time slot starts at")
    end_time = models.TimeField(help_text="Time slot ends at")
    max_bookings = models.PositiveIntegerField(default=50)
    current_bookings = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['ward', 'date', 'meal_type', 'start_time']
        ordering = ['date', 'start_time']
    
    def __str__(self):
        return f"{self.ward.name} - {self.date} {self.meal_type} ({self.start_time})"
    
    def has_availability(self):
        """Check if slot has available bookings"""
        return self.current_bookings < self.max_bookings and self.is_available
    
    def book_slot(self):
        """Book a slot"""
        if not self.has_availability():
            raise ValueError("Slot is fully booked")
        self.current_bookings += 1
        self.save()
    
    def release_slot(self):
        """Release a booked slot"""
        if self.current_bookings > 0:
            self.current_bookings -= 1
            self.save()


class PatientEducationCategory(models.Model):
    """Categories for patient education materials"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Icon class or emoji")
    ordering = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Patient Education Categories"
        ordering = ['ordering', 'name']
    
    def __str__(self):
        return self.name


class PatientEducationContent(models.Model):
    """Educational content for patients"""
    CONTENT_TYPE_CHOICES = [
        ('diet_info', 'Diet Information'),
        ('recovery_guide', 'Recovery Guide'),
        ('health_tip', 'Health Tip'),
        ('medication_info', 'Medication Information'),
        ('exercise_guide', 'Exercise Guide'),
        ('video_guide', 'Video Guide'),
        ('infographic', 'Infographic'),
    ]
    
    TARGET_ROLE_CHOICES = [
        ('patient', 'Patient'),
        ('caregiver', 'Caregiver'),
        ('both', 'Both Patient & Caregiver'),
    ]
    
    DIET_TYPE_CHOICES = [
        ('diabetic', 'Diabetic Diet'),
        ('low_sodium', 'Low Sodium Diet'),
        ('high_protein', 'High Protein Diet'),
        ('low_fat', 'Low Fat Diet'),
        ('renal', 'Renal Diet'),
        ('cardiac', 'Cardiac Diet'),
        ('ulcer', 'Ulcer Diet'),
        ('general', 'General Diet'),
        ('all', 'All Diet Types'),
    ]
    
    category = models.ForeignKey(
        PatientEducationCategory,
        on_delete=models.CASCADE,
        related_name='contents'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    content = models.TextField(help_text="Main educational content")
    content_type = models.CharField(max_length=50, choices=CONTENT_TYPE_CHOICES)
    target_role = models.CharField(max_length=20, choices=TARGET_ROLE_CHOICES, default='both')
    
    # Link to diet types
    applicable_diet_types = models.CharField(
        max_length=100,
        choices=DIET_TYPE_CHOICES,
        default='general',
        help_text="Which diet types this content applies to"
    )
    
    # Metadata
    image = models.ImageField(
        upload_to='education/',
        blank=True,
        null=True,
        help_text="Educational image or infographic"
    )
    video_url = models.URLField(blank=True, help_text="Link to educational video")
    pdf_file = models.FileField(
        upload_to='education/pdfs/',
        blank=True,
        null=True,
        help_text="PDF document"
    )
    
    # Publishing
    is_published = models.BooleanField(default=True)
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='education_contents'
    )
    
    ordering = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Patient Education Content"
        verbose_name_plural = "Patient Education Contents"
        ordering = ['category', 'ordering', '-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_content_type_display()})"


class PatientEducationProgress(models.Model):
    """Track which educational content patient has accessed"""
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='education_progress'
    )
    content = models.ForeignKey(
        PatientEducationContent,
        on_delete=models.CASCADE,
        related_name='patient_progress'
    )
    first_accessed = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)
    view_count = models.PositiveIntegerField(default=1)
    completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['patient', 'content']
        verbose_name = "Patient Education Progress"
        verbose_name_plural = "Patient Education Progress"
    
    def __str__(self):
        return f"{self.patient.username} - {self.content.title}"


class CaregiverNotification(models.Model):
    """Notifications for caregivers/relatives about orders and meals"""
    NOTIFICATION_TYPE_CHOICES = [
        ('order_placed', 'Order Placed'),
        ('order_confirmed', 'Order Confirmed'),
        ('order_preparing', 'Order Preparing'),
        ('order_ready', 'Order Ready'),
        ('order_delivered', 'Order Delivered'),
        ('meal_scheduled', 'Meal Scheduled'),
        ('nutrition_info', 'Nutrition Information'),
        ('education_assigned', 'Education Material Assigned'),
        ('appointment_reminder', 'Appointment Reminder'),
        ('custom_message', 'Custom Message'),
    ]
    
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='caregiver_notifications'
    )
    caregiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_notifications'
    )
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    # Related objects
    related_order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='caregiver_notifications'
    )
    related_education = models.ForeignKey(
        PatientEducationContent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='caregiver_notifications'
    )
    
    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['caregiver', '-created_at']),
            models.Index(fields=['is_read', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.patient.username}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
