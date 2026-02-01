from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import DailyHealthMetric, MealReview, PatientHealthGoal
from .services import HealthService


@receiver(post_save, sender=DailyHealthMetric)
def health_metric_saved(sender, instance, created, **kwargs):
    """Handle health metric creation/update"""
    if created:
        # Check for alerts
        if instance.is_in_alert_range:
            HealthService.detect_health_alerts(instance.user)


@receiver(post_save, sender=MealReview)
def meal_review_saved(sender, instance, created, **kwargs):
    """Handle meal review creation/update"""
    if created:
        # Update meal effectiveness score
        HealthService.analyze_meal_effectiveness(instance.meal)
        
        # Check for meal-related alerts
        if instance.overall_rating <= 2:
            from .models import HealthAlert
            HealthAlert.objects.create(
                user=instance.user,
                alert_type='health_trend',
                severity='info',
                title=f'Low Meal Rating: {instance.meal.name}',
                message=f'You rated {instance.meal.name} {instance.overall_rating}/5. Consider alternatives.',
                send_email=False
            )


@receiver(post_save, sender=PatientHealthGoal)
def goal_status_changed(sender, instance, created, **kwargs):
    """Handle goal creation/status change"""
    if not created and instance.status == 'completed':
        from .models import HealthAlert
        # Create completion alert for patient
        HealthAlert.objects.create(
            user=instance.user,
            alert_type='goal_achieved',
            severity='info',
            title=f'Congratulations! Goal Achieved',
            message=f'You have successfully achieved your goal: {instance.goal_name}',
            goal=instance,
            notify_nutritionist=True
        )
