from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import date, time
import logging

logger = logging.getLogger(__name__)


class NutritionistProfile(models.Model):
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('inactive', _('Inactive')),
        ('on_leave', _('On Leave')),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='nutritionistprofile'
    )
    bio = models.TextField(blank=True, null=True)
    specialization = models.CharField(max_length=255, blank=True, null=True)
    license_number = models.CharField(max_length=100, blank=True, null=True, unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    max_clients = models.IntegerField(default=50)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Nutritionist Profile')
        verbose_name_plural = _('Nutritionist Profiles')

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_status_display()}"

    @property
    def current_client_count(self):
        # Count active client assignments for this nutritionist
        return self.user.assigned_clients.filter(status='active').count()

    @property
    def is_available(self):
        return self.status == 'active' and self.current_client_count < self.max_clients

    def clean(self):
        # Validate sensible max_clients and license length if provided
        errors = {}
        if self.max_clients is not None and self.max_clients < 1:
            errors['max_clients'] = _('Max clients must be at least 1')
        if self.license_number and len(self.license_number) < 3:
            errors['license_number'] = _('License number is too short')
        if errors:
            raise ValidationError(errors)


class NutritionistAvailability(models.Model):
    """Availability slots for nutritionists"""
    nutritionist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='availability_slots'
    )
    day_of_week = models.IntegerField(choices=[
        (0, _('Monday')),
        (1, _('Tuesday')),
        (2, _('Wednesday')),
        (3, _('Thursday')),
        (4, _('Friday')),
        (5, _('Saturday')),
        (6, _('Sunday')),
    ])
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Nutritionist Availability')
        verbose_name_plural = _('Nutritionist Availabilities')
        unique_together = ('nutritionist', 'day_of_week', 'start_time', 'end_time')

    def __str__(self):
        return f"{self.nutritionist.get_full_name()} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"


class ClientAssignment(models.Model):
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('paused', _('Paused')),
        ('completed', _('Completed')),
        ('terminated', _('Terminated')),
    ]

    nutritionist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assigned_clients'
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='nutritionist_assignments'
    )
    start_date = models.DateField(default=date.today)
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Client Assignment')
        verbose_name_plural = _('Client Assignments')
        unique_together = ('nutritionist', 'client')

    def __str__(self):
        return f"{self.client.get_full_name()} - {self.nutritionist.get_full_name()}"

    @property
    def is_active(self):
        return self.status == 'active'

    def terminate(self):
        """Terminate the assignment: set status and end_date."""
        self.status = 'terminated'
        if not self.end_date:
            self.end_date = date.today()
        self.save()

    def clean(self):
        errors = {}
        # Prevent assigning a user to themselves
        if self.nutritionist == self.client:
            errors['client'] = _('Nutritionist and client cannot be the same user.')

        # If both dates present, ensure start_date <= end_date
        if self.end_date and self.start_date and self.start_date > self.end_date:
            errors['start_date'] = _('Start date cannot be after end date.')

        if errors:
            raise ValidationError(errors)


class Consultation(models.Model):
    CONSULTATION_TYPE_CHOICES = [
        ('initial', _('Initial Assessment')),
        ('followup', _('Follow-up')),
        ('routine', _('Routine Check-in')),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', _('Scheduled')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]

    nutritionist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='nutritionist_consultations'
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='client_consultations'
    )
    consultation_type = models.CharField(
        max_length=20,
        choices=CONSULTATION_TYPE_CHOICES,
        default='routine'
    )
    scheduled_at = models.DateTimeField()
    duration_minutes = models.IntegerField(default=30)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Consultation')
        verbose_name_plural = _('Consultations')

    def __str__(self):
        return f"{self.client.get_full_name()} - {self.get_consultation_type_display()}"


class MealPlan(models.Model):
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('approved', _('Approved')),
        ('active', _('Active')),
        ('completed', _('Completed')),
    ]

    nutritionist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_meal_plans'
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assigned_meal_plans'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Meal Plan')
        verbose_name_plural = _('Meal Plans')

    def __str__(self):
        return f"{self.title} - {self.client.get_full_name()}"


class DietRecommendation(models.Model):
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
    ]

    nutritionist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='diet_recommendations'
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_recommendations'
    )
    meal_plan = models.ForeignKey(
        MealPlan,
        on_delete=models.CASCADE,
        related_name='recommendations',
        blank=True,
        null=True
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.IntegerField(default=1)
    target_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Diet Recommendation')
        verbose_name_plural = _('Diet Recommendations')

    def __str__(self):
        return f"{self.title} - {self.client.get_full_name()}"


class ClientNote(models.Model):
    nutritionist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='client_notes'
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='nutritionist_notes'
    )
    content = models.TextField()
    is_private = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Client Note')
        verbose_name_plural = _('Client Notes')

    def __str__(self):
        return f"Note for {self.client.get_full_name()}"