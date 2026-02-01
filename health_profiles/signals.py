from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import HealthCheck, ConsultantAvailability, AutoAssignmentLog
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=ConsultantAvailability)
def auto_assign_on_availability_change(sender, instance, created, update_fields, **kwargs):
    """
    When a consultant becomes available, automatically assign pending health checks.
    This provides real-time assignment instead of waiting for the management command.
    """
    # Only process if status changed to 'available'
    if update_fields and 'status' not in update_fields:
        return

    # Check if consultant has capacity
    if not instance.is_available:
        return

    logger.info(f"Consultant {instance.user.get_full_name()} is now available - checking for pending assignments")

    # Find pending health checks that match this consultant's specialization
    pending_checks = HealthCheck.objects.filter(
        status=HealthCheck.StatusChoices.PENDING,
        assigned_consultant__isnull=True
    )

    # Filter by specialization if needed
    if instance.specialization:
        # Match checks with similar types to specialization
        pending_checks = pending_checks.filter(
            check_type__in=instance.preferred_check_types.split(',') if instance.preferred_check_types else []
        )

    # Sort by priority (urgent first)
    priority_order = {HealthCheck.PriorityChoices.URGENT: 0, HealthCheck.PriorityChoices.HIGH: 1,
                      HealthCheck.PriorityChoices.NORMAL: 2, HealthCheck.PriorityChoices.LOW: 3}
    pending_checks = sorted(pending_checks, key=lambda x: priority_order.get(x.priority, 4))

    # Assign available slots
    available_slots = instance.available_slots
    assigned_count = 0

    for check in pending_checks[:available_slots]:
        try:
            check.assigned_consultant = instance.user
            check.auto_assigned = True
            check.status = HealthCheck.StatusChoices.ASSIGNED
            check.save()

            # Update consultant workload
            instance.current_assignments += 1
            instance.save()

            # Log the assignment
            AutoAssignmentLog.objects.create(
                health_check=check,
                assigned_consultant=instance.user,
                result=AutoAssignmentLog.ResultChoices.SUCCESS,
                message=f"Auto-assigned by real-time signal when consultant became available"
            )

            assigned_count += 1

            # Send notifications
            _notify_assignment(check, instance.user)

            logger.info(f"Auto-assigned health check #{check.id} to {instance.user.get_full_name()}")

        except Exception as e:
            logger.error(f"Error assigning health check: {e}")
            AutoAssignmentLog.objects.create(
                health_check=check,
                assigned_consultant=instance.user,
                result=AutoAssignmentLog.ResultChoices.ERROR,
                message=f"Error during auto-assignment: {str(e)}"
            )

    if assigned_count > 0:
        logger.info(f"Real-time auto-assignment complete: {assigned_count} checks assigned to {instance.user.get_full_name()}")


@receiver(pre_save, sender=HealthCheck)
def track_status_changes(sender, instance, **kwargs):
    """
    Track when health check status changes to update consultant workload.
    """
    try:
        old_instance = HealthCheck.objects.get(pk=instance.pk)

        # If status changed from assigned to completed, reduce consultant workload
        if old_instance.status != HealthCheck.StatusChoices.COMPLETED and \
           instance.status == HealthCheck.StatusChoices.COMPLETED:
            if instance.assigned_consultant:
                try:
                    availability = instance.assigned_consultant.consultant_availability
                    if availability.current_assignments > 0:
                        availability.current_assignments -= 1
                        availability.save()

                    # Update total completed checks
                    availability.total_completed_checks += 1
                    availability.save()

                    logger.info(f"Updated workload for {instance.assigned_consultant.get_full_name()}: "
                              f"current={availability.current_assignments}, total={availability.total_completed_checks}")
                except ConsultantAvailability.DoesNotExist:
                    logger.warning(f"No availability record for consultant {instance.assigned_consultant}")

        # If status changed from assigned to in_progress, notify patient
        if old_instance.status == HealthCheck.StatusChoices.ASSIGNED and \
           instance.status == HealthCheck.StatusChoices.IN_PROGRESS:
            _notify_consultation_started(instance)

    except HealthCheck.DoesNotExist:
        # This is a new instance, skip old instance comparison
        pass


@receiver(post_save, sender=HealthCheck)
def notify_on_completion(sender, instance, created, update_fields, **kwargs):
    """
    Send notifications when a health check is completed with recommendations.
    """
    if update_fields and 'status' not in update_fields:
        return

    if instance.status == HealthCheck.StatusChoices.COMPLETED:
        _notify_completion(instance)


def _notify_assignment(health_check, consultant):
    """
    Notify patient that a consultant has been assigned to their health check.
    """
    try:
        patient = health_check.patient
        
        # Send email notification
        context = {
            'patient_name': patient.get_full_name(),
            'consultant_name': consultant.get_full_name(),
            'check_type': health_check.get_check_type_display(),
            'check_id': health_check.id,
            'site_name': settings.SITE_NAME,
            'contact_email': settings.CONTACT_EMAIL,
        }

        html_message = render_to_string('emails/health_check_assigned.html', context)
        text_message = render_to_string('emails/health_check_assigned.txt', context)

        send_mail(
            subject=f"Health Check Assigned - Check #{health_check.id}",
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[patient.email],
            html_message=html_message,
            fail_silently=True
        )

        logger.info(f"Assignment notification sent to {patient.email}")

    except Exception as e:
        logger.error(f"Error sending assignment notification: {e}")


def _notify_consultation_started(health_check):
    """
    Notify patient that consultation has started.
    """
    try:
        patient = health_check.patient

        context = {
            'patient_name': patient.get_full_name(),
            'consultant_name': health_check.assigned_consultant.get_full_name(),
            'check_type': health_check.get_check_type_display(),
            'check_id': health_check.id,
            'site_name': settings.SITE_NAME,
        }

        html_message = render_to_string('emails/consultation_started.html', context)
        text_message = render_to_string('emails/consultation_started.txt', context)

        send_mail(
            subject=f"Consultation Started - Check #{health_check.id}",
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[patient.email],
            html_message=html_message,
            fail_silently=True
        )

        logger.info(f"Consultation started notification sent to {patient.email}")

    except Exception as e:
        logger.error(f"Error sending consultation started notification: {e}")


def _notify_completion(health_check):
    """
    Notify patient that consultation is complete with recommendations.
    """
    try:
        patient = health_check.patient

        context = {
            'patient_name': patient.get_full_name(),
            'consultant_name': health_check.assigned_consultant.get_full_name(),
            'check_type': health_check.get_check_type_display(),
            'recommendations': health_check.recommendations,
            'consultant_notes': health_check.consultant_notes,
            'check_id': health_check.id,
            'site_name': settings.SITE_NAME,
        }

        html_message = render_to_string('emails/consultation_completed.html', context)
        text_message = render_to_string('emails/consultation_completed.txt', context)

        send_mail(
            subject=f"Consultation Complete - Check #{health_check.id}",
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[patient.email],
            html_message=html_message,
            fail_silently=True
        )

        # Also notify consultant
        send_mail(
            subject=f"Consultation Recorded - Check #{health_check.id}",
            message=f"Your consultation for patient {patient.get_full_name()} has been recorded.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[health_check.assigned_consultant.email],
            fail_silently=True
        )

        logger.info(f"Completion notification sent to {patient.email}")

    except Exception as e:
        logger.error(f"Error sending completion notification: {e}")


# Ready function to initialize signals
def ready():
    """
    Initialize all signals when app is ready.
    """
    logger.info("Health check auto-assignment signals initialized")
