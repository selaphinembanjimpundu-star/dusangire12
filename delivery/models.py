from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class DeliveryZone(models.Model):
    """Delivery zones (inside hospital, outside hospital, etc.)"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    delivery_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Delivery charge for this zone"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - ${self.delivery_charge}"


class DeliveryAddress(models.Model):
    """User delivery addresses"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='delivery_addresses')
    label = models.CharField(
        max_length=50,
        help_text="Address label (e.g., Home, Work, Ward 3)"
    )
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    
    # Address details
    address_line1 = models.CharField(max_length=200, help_text="Ward, Room, Building, etc.")
    address_line2 = models.CharField(max_length=200, blank=True, help_text="Additional address details")
    city = models.CharField(max_length=100, default="Kigali")
    zone = models.ForeignKey(
        DeliveryZone,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='addresses',
        help_text="Delivery zone (auto-detected or manual)"
    )
    
    # Additional info
    delivery_instructions = models.TextField(blank=True, help_text="Special delivery instructions")
    is_default = models.BooleanField(default=False, help_text="Set as default delivery address")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Delivery Addresses"
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        return f"{self.label} - {self.user.username}"
    
    def get_full_address(self):
        """Get formatted full address"""
        parts = [self.address_line1]
        if self.address_line2:
            parts.append(self.address_line2)
        parts.append(self.city)
        return ", ".join(parts)
    
    def get_delivery_charge(self):
        """Get delivery charge for this address"""
        if self.zone:
            return self.zone.delivery_charge
        return Decimal('2000.00')  # Default charge in RWF
    
    def save(self, *args, **kwargs):
        # Ensure only one default address per user
        if self.is_default:
            DeliveryAddress.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
