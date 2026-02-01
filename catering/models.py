from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from decimal import Decimal

class CateringPackage(models.Model):
    """Pre-defined catering packages (e.g., Wedding, Corporate Lunch, Party)"""
    name = models.CharField(max_length=200)
    description = models.TextField()
    price_per_person = models.DecimalField(max_digits=10, decimal_places=2)
    min_people = models.PositiveIntegerField(default=10)
    image = models.ImageField(upload_to='catering/packages/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Catering Package')
        verbose_name_plural = _('Catering Packages')

    def __str__(self):
        return self.name

class CateringBooking(models.Model):
    """Bookings for catering services"""
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('confirmed', _('Confirmed')),
        ('cancelled', _('Cancelled')),
        ('completed', _('Completed')),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='catering_bookings')
    package = models.ForeignKey(CateringPackage, on_delete=models.SET_NULL, null=True, blank=True)
    event_name = models.CharField(max_length=200)
    event_date = models.DateField()
    event_time = models.TimeField()
    location = models.TextField()
    number_of_people = models.PositiveIntegerField()
    special_requests = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Catering Booking')
        verbose_name_plural = _('Catering Bookings')

    def __str__(self):
        return f"{self.event_name} - {self.event_date}"

    def save(self, *args, **kwargs):
        if self.package and not self.total_price:
            self.total_price = self.package.price_per_person * self.number_of_people
        super().save(*args, **kwargs)
