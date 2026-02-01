"""
Status Change Notifications System
Handles notifications for patient admissions, discharges, transfers, and bed status changes
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.utils import timezone
from django.db.models import Q
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import logging

from .models import (
    PatientAdmission, PatientDischarge, PatientTransfer,
    WardBed, PatientNotification, NotificationTemplate,
    CaregiverNotification
)

logger = logging.getLogger(__name__)


# ==================== NOTIFICATION TEMPLATES ====================

def get_or_create_templates():
    """Ensure all notification templates exist"""
    templates = {
        'patient_admitted': {
            'subject': 'Patient Admission Notification',
            'body': '''
Dear Caregiver,

Patient {{patient_name}} has been admitted to the hospital.

Admission Details:
- Patient: {{patient_name}}
- Bed: {{bed_number}} ({{ward_name}})
- Admission Date: {{admission_date}}
- Reason: {{reason}}
- Chief Complaint: {{chief_complaint}}

Please contact the hospital for more information.

Best regards,
Hospital Management System
            ''',
            'notification_type': 'admission'
        },
        'patient_discharged': {
            'subject': 'Patient Discharge Notification',
            'body': '''
Dear Caregiver,

Patient {{patient_name}} has been discharged from the hospital.

Discharge Details:
- Patient: {{patient_name}}
- Discharge Date: {{discharge_date}}
- Status: {{discharge_status}}
- Length of Stay: {{length_of_stay}} days
- Notes: {{discharge_notes}}

Please ensure follow-up care as recommended.

Best regards,
Hospital Management System
            ''',
            'notification_type': 'discharge'
        },
        'patient_transferred': {
            'subject': 'Patient Transfer Notification',
            'body': '''
Dear Caregiver,

Patient {{patient_name}} has been transferred to another bed/ward.

Transfer Details:
- Patient: {{patient_name}}
- From: {{old_bed}} ({{old_ward}})
- To: {{new_bed}} ({{new_ward}})
- Transfer Date: {{transfer_date}}
- Reason: {{transfer_reason}}

Please note the new location for visiting and communication.

Best regards,
Hospital Management System
            ''',
            'notification_type': 'transfer'
        },
        'bed_status_changed': {
            'subject': 'Bed Status Change Notification',
            'body': '''
Dear Staff,

Bed status has been updated.

Bed Details:
- Bed: {{bed_number}} ({{ward_name}})
- Previous Status: {{old_status}}
- New Status: {{new_status}}
- Changed At: {{status_change_time}}
- Changed By: {{changed_by}}

Please update records accordingly.

Best regards,
Hospital Management System
            ''',
            'notification_type': 'bed_status'
        },
        'bed_maintenance_scheduled': {
            'subject': 'Bed Maintenance Scheduled',
            'body': '''
Dear Staff,

Bed maintenance has been scheduled.

Maintenance Details:
- Bed: {{bed_number}} ({{ward_name}})
- Scheduled Date: {{maintenance_date}}
- Estimated Duration: {{maintenance_duration}}
- Status: {{bed_status}}

Please ensure patient is transferred if necessary.

Best regards,
Hospital Management System
            ''',
            'notification_type': 'maintenance'
        }
    }
    
    for key, data in templates.items():
        NotificationTemplate.objects.get_or_create(
            name=key,
            defaults={
                'subject': data['subject'],
                'body': data['body'],
                'notification_type': data['notification_type'],
                'is_active': True
            }
        )


# ==================== NOTIFICATION SENDING ====================

def send_admission_notification(admission):
    """Send notification when patient is admitted"""
    try:
        template = NotificationTemplate.objects.get(name='patient_admitted')
        
        # Prepare context
        context = {
            'patient_name': admission.patient.user.get_full_name(),
            'bed_number': admission.bed.bed_number,
            'ward_name': admission.bed.ward.name,
            'admission_date': admission.admission_date.strftime('%Y-%m-%d %H:%M'),
            'reason': admission.reason,
            'chief_complaint': admission.chief_complaint or 'N/A'
        }
        
        # Get caregivers (if tracking is implemented)
        # For now, send to patient's emergency contacts
        recipients = get_patient_contacts(admission.patient)
        
        if recipients:
            # Send email notifications
            for recipient in recipients:
                send_notification_email(
                    recipient,
                    template,
                    context,
                    'admission',
                    admission.patient.user
                )
            
            logger.info(f"Admission notifications sent for patient {admission.patient.id}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error sending admission notification: {str(e)}")
        return False


def send_discharge_notification(discharge):
    """Send notification when patient is discharged"""
    try:
        template = NotificationTemplate.objects.get(name='patient_discharged')
        admission = discharge.admission
        
        # Calculate length of stay
        length_of_stay = (discharge.created_at.date() - admission.admission_date.date()).days
        
        # Prepare context
        context = {
            'patient_name': admission.patient.user.get_full_name(),
            'discharge_date': discharge.created_at.strftime('%Y-%m-%d %H:%M'),
            'discharge_status': discharge.get_discharge_status_display(),
            'length_of_stay': length_of_stay,
            'discharge_notes': discharge.discharge_notes or 'None'
        }
        
        # Get caregivers
        recipients = get_patient_contacts(admission.patient)
        
        if recipients:
            for recipient in recipients:
                send_notification_email(
                    recipient,
                    template,
                    context,
                    'discharge',
                    admission.patient.user
                )
            
            logger.info(f"Discharge notifications sent for patient {admission.patient.id}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error sending discharge notification: {str(e)}")
        return False


def send_transfer_notification(transfer):
    """Send notification when patient is transferred"""
    try:
        template = NotificationTemplate.objects.get(name='patient_transferred')
        
        # Get previous admission
        previous_bed = transfer.previous_bed
        new_bed = transfer.new_bed
        
        # Prepare context
        context = {
            'patient_name': transfer.patient.user.get_full_name(),
            'old_bed': previous_bed.bed_number if previous_bed else 'N/A',
            'old_ward': previous_bed.ward.name if previous_bed else 'N/A',
            'new_bed': new_bed.bed_number,
            'new_ward': new_bed.ward.name,
            'transfer_date': transfer.transfer_date.strftime('%Y-%m-%d %H:%M'),
            'transfer_reason': transfer.reason or 'N/A'
        }
        
        # Get caregivers
        recipients = get_patient_contacts(transfer.patient)
        
        if recipients:
            for recipient in recipients:
                send_notification_email(
                    recipient,
                    template,
                    context,
                    'transfer',
                    transfer.patient.user
                )
            
            logger.info(f"Transfer notifications sent for patient {transfer.patient.id}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error sending transfer notification: {str(e)}")
        return False


def send_bed_status_notification(bed, old_status, new_status, changed_by=None):
    """Send notification when bed status changes"""
    try:
        template = NotificationTemplate.objects.get(name='bed_status_changed')
        
        # Prepare context
        context = {
            'bed_number': bed.bed_number,
            'ward_name': bed.ward.name,
            'old_status': old_status,
            'new_status': new_status,
            'status_change_time': timezone.now().strftime('%Y-%m-%d %H:%M'),
            'changed_by': changed_by.get_full_name() if changed_by else 'System'
        }
        
        # Get ward staff
        recipients = get_ward_staff(bed.ward)
        
        if recipients:
            for recipient in recipients:
                send_notification_email(
                    recipient,
                    template,
                    context,
                    'bed_status',
                    None
                )
            
            logger.info(f"Bed status notifications sent for bed {bed.id}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error sending bed status notification: {str(e)}")
        return False


# ==================== NOTIFICATION HELPERS ====================

def send_notification_email(recipient_email, template, context, notification_type, user=None):
    """Send email notification using template"""
    try:
        # Render subject and body with context
        subject = render_template_string(template.subject, context)
        body = render_template_string(template.body, context)
        
        # Send email
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            html_message=format_html_email(subject, body),
            fail_silently=False
        )
        
        # Create in-app notification if user exists
        if user:
            PatientNotification.objects.create(
                recipient=user,
                title=subject,
                message=body,
                notification_type=notification_type,
                related_object=None
            )
        
        logger.info(f"Notification email sent to {recipient_email}")
        return True
    
    except Exception as e:
        logger.error(f"Error sending notification email: {str(e)}")
        return False


def render_template_string(template_str, context):
    """Render template string with context"""
    from django.template import Template, Context
    template = Template(template_str)
    return template.render(Context(context))


def format_html_email(subject, body):
    """Format plain text body as HTML email"""
    html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #0066cc;">{subject}</h2>
                <div style="background: #f5f5f5; padding: 20px; border-left: 4px solid #0066cc;">
                    <pre style="font-family: Arial, sans-serif; white-space: pre-wrap;">
{body}
                    </pre>
                </div>
                <p style="color: #999; font-size: 12px; margin-top: 30px;">
                    This is an automated notification from Hospital Management System.
                    Please do not reply to this email.
                </p>
            </div>
        </body>
    </html>
    """
    return html


def get_patient_contacts(patient):
    """Get list of email addresses for patient contacts"""
    contacts = []
    
    # Add patient's own email
    if patient.user.email:
        contacts.append(patient.user.email)
    
    # TODO: Add emergency contacts when that model is created
    # For now, just return patient email
    
    return list(set(contacts))  # Remove duplicates


def get_ward_staff(ward):
    """Get list of email addresses for ward staff"""
    # Get users assigned to this ward with staff roles
    # This depends on staff assignment implementation
    # For now, return empty list - implement based on your staff model
    return []


# ==================== NOTIFICATION VIEWS ====================

@login_required
def notifications_dashboard(request):
    """Dashboard showing all notifications for current user"""
    notifications = PatientNotification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(notifications, 20)
    page = request.GET.get('page')
    notifications = paginator.get_page(page)
    
    context = {
        'notifications': notifications,
        'unread_count': PatientNotification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
    }
    
    return render(request, 'hospital_wards/notifications_dashboard.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def notification_preferences(request):
    """User notification preferences"""
    if request.method == 'POST':
        # Update preferences
        patient = request.user.patient_profile
        
        # Store preferences (implement based on your preference model)
        patient.notification_email = request.POST.get('email_enabled', False) == 'on'
        patient.notification_sms = request.POST.get('sms_enabled', False) == 'on'
        patient.notification_app = request.POST.get('app_enabled', False) == 'on'
        patient.save()
        
        messages.success(request, 'Notification preferences updated successfully')
        return redirect('hospital_wards:notification_preferences')
    
    context = {
        'patient': request.user.patient_profile if hasattr(request.user, 'patient_profile') else None
    }
    
    return render(request, 'hospital_wards/notification_preferences.html', context)


@login_required
@require_http_methods(["POST"])
def mark_notification_read(request, notification_id):
    """Mark notification as read"""
    notification = get_object_or_404(
        PatientNotification,
        id=notification_id,
        recipient=request.user
    )
    notification.is_read = True
    notification.read_at = timezone.now()
    notification.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'unread_count': PatientNotification.objects.filter(
                recipient=request.user,
                is_read=False
            ).count()
        })
    
    return redirect('hospital_wards:notifications_dashboard')


@login_required
@require_http_methods(["POST"])
def delete_notification(request, notification_id):
    """Delete notification"""
    notification = get_object_or_404(
        PatientNotification,
        id=notification_id,
        recipient=request.user
    )
    notification.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('hospital_wards:notifications_dashboard')


@login_required
@require_POST
def mark_all_read(request):
    """Mark all notifications as read"""
    PatientNotification.objects.filter(
        recipient=request.user,
        is_read=False
    ).update(
        is_read=True,
        read_at=timezone.now()
    )
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'unread_count': 0})
    
    return redirect('hospital_wards:notifications_dashboard')


@login_required
@require_POST
def clear_notifications(request):
    """Clear all notifications"""
    PatientNotification.objects.filter(recipient=request.user).delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('hospital_wards:notifications_dashboard')


@login_required
def notification_count(request):
    """Get unread notification count (AJAX)"""
    count = PatientNotification.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()
    
    return JsonResponse({'unread_count': count})


# ==================== NOTIFICATION SIGNALS ====================

def setup_notification_signals():
    """
    Connect signals to create notifications on model changes.
    Call this in apps.py ready() method
    """
    from django.db.models.signals import post_save
    from django.dispatch import receiver
    
    @receiver(post_save, sender=PatientAdmission)
    def patient_admitted_signal(sender, instance, created, **kwargs):
        """Send notification when patient is admitted"""
        if created:
            send_admission_notification(instance)
    
    @receiver(post_save, sender=PatientDischarge)
    def patient_discharged_signal(sender, instance, created, **kwargs):
        """Send notification when patient is discharged"""
        if created:
            send_discharge_notification(instance)
    
    @receiver(post_save, sender=PatientTransfer)
    def patient_transferred_signal(sender, instance, created, **kwargs):
        """Send notification when patient is transferred"""
        if created:
            send_transfer_notification(instance)


# ==================== NOTIFICATION STATS ====================

@login_required
def notification_stats(request):
    """Get notification statistics (AJAX)"""
    stats = {
        'total': PatientNotification.objects.filter(recipient=request.user).count(),
        'unread': PatientNotification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count(),
        'read': PatientNotification.objects.filter(
            recipient=request.user,
            is_read=True
        ).count(),
        'by_type': {}
    }
    
    # Count by notification type
    from django.db.models import Count
    type_counts = PatientNotification.objects.filter(
        recipient=request.user
    ).values('notification_type').annotate(count=Count('id'))
    
    for tc in type_counts:
        stats['by_type'][tc['notification_type']] = tc['count']
    
    return JsonResponse(stats)
