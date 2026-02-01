"""
Signal handlers for nutritionist dashboard.
Handles audit logging and automatic actions.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
import logging

from .models import NutritionistProfile, ClientAssignment

logger = logging.getLogger(__name__)


@receiver(post_save, sender=NutritionistProfile)
def log_nutritionist_profile_change(sender, instance, created, **kwargs):
    """Log nutritionist profile creation or update"""
    action = "created" if created else "updated"
    logger.info(
        f"NutritionistProfile {action}: "
        f"user_id={instance.user_id}, "
        f"status={instance.status}, "
        f"timestamp={timezone.now().isoformat()}"
    )


@receiver(post_delete, sender=NutritionistProfile)
def log_nutritionist_profile_delete(sender, instance, **kwargs):
    """Log nutritionist profile deletion"""
    logger.warning(
        f"NutritionistProfile deleted: "
        f"user_id={instance.user_id}, "
        f"timestamp={timezone.now().isoformat()}"
    )


@receiver(post_save, sender=ClientAssignment)
def log_client_assignment_change(sender, instance, created, **kwargs):
    """Log client assignment creation or update"""
    action = "created" if created else "updated"
    logger.info(
        f"ClientAssignment {action}: "
        f"nutritionist_id={instance.nutritionist_id}, "
        f"client_id={instance.client_id}, "
        f"status={instance.status}, "
        f"timestamp={timezone.now().isoformat()}"
    )


@receiver(post_delete, sender=ClientAssignment)
def log_client_assignment_delete(sender, instance, **kwargs):
    """Log client assignment deletion"""
    logger.warning(
        f"ClientAssignment deleted: "
        f"nutritionist_id={instance.nutritionist_id}, "
        f"client_id={instance.client_id}, "
        f"timestamp={timezone.now().isoformat()}"
    )
