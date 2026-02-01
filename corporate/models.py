from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from django.core.validators import MinValueValidator

class CorporatePartner(models.Model):
    """Hospital, Clinic, or Company partner"""
    name = models.CharField(max_length=255, unique=True)
    address = models.TextField()
    contact_person = models.CharField(max_length=255)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    
    # Partner type
    PARTNER_TYPES = [
        ('hospital', _('Hospital')),
        ('clinic', _('Clinic')),
        ('corporate', _('Corporate Office')),
        ('other', _('Other')),
    ]
    partner_type = models.CharField(max_length=20, choices=PARTNER_TYPES, default='hospital')
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Corporate Partner')
        verbose_name_plural = _('Corporate Partners')

    def __str__(self):
        return self.name
    
    

class CorporateContract(models.Model):
    """Contract terms for a partner"""
    partner = models.ForeignKey(CorporatePartner, on_delete=models.CASCADE, related_name='contracts')
    contract_number = models.CharField(max_length=50, unique=True)
    
    # Dates
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Status field
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('active', _('Active')),
        ('expired', _('Expired')),
        ('terminated', _('Terminated')),
        ('pending_renewal', _('Pending Renewal')),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    
    # Keep is_active for backward compatibility or quick queries
    is_active = models.BooleanField(default=True)
    
    # Discounts
    discount_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    # Billing terms
    BILLING_CYCLE_CHOICES = [
        ('monthly', _('Monthly')),
        ('quarterly', _('Quarterly')),
        ('on_order', _('Per Order')),
    ]
    
    billing_cycle = models.CharField(
        max_length=20,
        choices=BILLING_CYCLE_CHOICES,
        default='monthly'
    )
    
    # Additional contract details
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Corporate Contract')
        verbose_name_plural = _('Corporate Contracts')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.partner.name} - {self.contract_number}"
    
    def save(self, *args, **kwargs):
        # Auto-update is_active based on status when saving
        if self.status == 'active':
            self.is_active = True
        elif self.status in ['expired', 'terminated']:
            self.is_active = False
        
        super().save(*args, **kwargs)
    
    @property
    def is_currently_active(self):
        """Check if contract is currently active based on dates"""
        from django.utils import timezone
        today = timezone.now().date()
        return (
            self.status == 'active' and
            self.start_date <= today <= self.end_date
        )
    
    @property
    def days_remaining(self):
        """Calculate days remaining until contract end"""
        from django.utils import timezone
        today = timezone.now().date()
        if self.end_date >= today:
            return (self.end_date - today).days
        return 0

class CorporateEmployee(models.Model):
    """Link between a User and a Corporate Partner"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='corporate_profile')
    partner = models.ForeignKey(CorporatePartner, on_delete=models.CASCADE, related_name='employees')
    employee_id = models.CharField(max_length=50, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Corporate Employee')
        verbose_name_plural = _('Corporate Employees')

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.partner.name})"