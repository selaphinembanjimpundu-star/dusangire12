from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserRole(models.TextChoices):
    CUSTOMER = 'customer', 'Customer'
    STAFF = 'staff', 'Staff'
    ADMIN = 'admin', 'Admin'
    NUTRITIONIST = 'nutritionist', 'Nutritionist'


class Profile(models.Model):
    """Extended user profile with additional information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.CUSTOMER
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Dietary preferences (comma-separated or JSON field)
    dietary_preferences = models.TextField(blank=True, help_text="Dietary preferences or restrictions")
    
    # Light status - only customers without light can register
    has_light = models.BooleanField(
        default=False,
        help_text="Whether customer has light. Only customers without light can register."
    )
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
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
