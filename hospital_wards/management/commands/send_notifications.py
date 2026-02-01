"""
Django management command to send pending notifications
Usage: python manage.py send_notifications
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from hospital_wards.models import PatientNotification, NotificationTemplate
from datetime import datetime


class Command(BaseCommand):
    help = 'Send pending patient notifications (email/SMS)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--send-emails',
            action='store_true',
            help='Send email notifications'
        )
        parser.add_argument(
            '--send-sms',
            action='store_true',
            help='Send SMS notifications (requires SMS service configured)'
        )

    def handle(self, *args, **options):
        self.stdout.write('📬 Processing pending notifications...')
        
        # Get pending notifications
        pending = PatientNotification.objects.filter(
            is_read=False,
            email_sent=False
        ).select_related('recipient', 'patient', 'admission')
        
        if not pending.exists():
            self.stdout.write(self.style.WARNING('No pending notifications to send'))
            return
        
        email_sent = 0
        sms_sent = 0
        errors = 0
        
        for notification in pending:
            try:
                # Send Email
                if notification.send_email and options['send_emails']:
                    self.send_email_notification(notification)
                    email_sent += 1
                    notification.email_sent = True
                
                # Send SMS
                if notification.send_sms and options['send_sms']:
                    self.send_sms_notification(notification)
                    sms_sent += 1
                    notification.sms_sent = True
                
                notification.save()
                
            except Exception as e:
                errors += 1
                self.stdout.write(
                    self.style.ERROR(f'Error sending notification {notification.id}: {str(e)}')
                )
        
        # Summary
        self.stdout.write(self.style.SUCCESS('✅ Notification processing complete'))
        self.stdout.write(f'📧 Emails sent: {email_sent}')
        self.stdout.write(f'📱 SMS sent: {sms_sent}')
        if errors:
            self.stdout.write(self.style.ERROR(f'❌ Errors: {errors}'))

    def send_email_notification(self, notification):
        """Send email notification"""
        template = NotificationTemplate.objects.filter(
            notification_type=notification.notification_type,
            is_active=True
        ).first()
        
        if not template:
            return
        
        # Prepare context
        context = {
            'recipient_name': notification.recipient.get_full_name() or notification.recipient.username,
            'patient_name': notification.patient.get_full_name() if notification.patient else 'N/A',
            'bed_number': notification.admission.bed.bed_number if notification.admission else 'N/A',
            'ward_name': notification.admission.bed.ward.name if notification.admission else 'N/A',
            'message': notification.message,
        }
        
        # Render email body with template variables
        email_body = template.email_body
        for key, value in context.items():
            email_body = email_body.replace(f'{{{{{key}}}}}', str(value))
        
        # Send email
        send_mail(
            subject=template.email_subject,
            message=email_body,
            from_email='noreply@dusangirehosp ital.com',
            recipient_list=[notification.recipient.email],
            fail_silently=False,
        )

    def send_sms_notification(self, notification):
        """Send SMS notification"""
        template = NotificationTemplate.objects.filter(
            notification_type=notification.notification_type,
            is_active=True
        ).first()
        
        if not template:
            return
        
        # Prepare context
        context = {
            'patient_name': notification.patient.get_full_name() if notification.patient else 'N/A',
            'bed_number': notification.admission.bed.bed_number if notification.admission else 'N/A',
            'ward_name': notification.admission.bed.ward.name if notification.admission else 'N/A',
        }
        
        # Render SMS body with template variables
        sms_body = template.sms_body
        for key, value in context.items():
            sms_body = sms_body.replace(f'{{{{{key}}}}}', str(value))
        
        # SMS sending would be implemented here with actual SMS service
        # For now, just log it
        self.stdout.write(f'📱 SMS to {notification.recipient.username}: {sms_body}')
