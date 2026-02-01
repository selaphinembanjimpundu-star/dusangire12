from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class AdminLog(models.Model):
    """
    Model to track all admin panel activities and actions.
    Provides audit trail for admin operations.
    """
    
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('VIEW', 'View'),
        ('EXPORT', 'Export'),
        ('IMPORT', 'Import'),
        ('APPROVE', 'Approve'),
        ('REJECT', 'Reject'),
        ('ASSIGN', 'Assign'),
        ('UNASSIGN', 'Unassign'),
        ('PAYMENT_PROCESS', 'Payment Process'),
        ('ORDER_UPDATE', 'Order Update'),
        ('USER_ACTION', 'User Action'),
        ('SYSTEM_ACTION', 'System Action'),
        ('REPORT_GENERATE', 'Report Generate'),
        ('CONFIG_CHANGE', 'Config Change'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('OTHER', 'Other'),
    ]
    
    # Who performed the action
    admin_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='admin_logs'
    )
    
    # What action was performed
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        default='OTHER'
    )
    
    # What model/object was affected
    model_name = models.CharField(
        max_length=100,
        help_text="Name of the model affected (e.g., Order, Payment, User)"
    )
    
    # ID of the affected object
    object_id = models.IntegerField(
        null=True,
        blank=True,
        help_text="ID of the affected object"
    )
    
    # Description of what happened
    description = models.TextField(
        help_text="Detailed description of the action"
    )
    
    # Previous values (JSON format for changed fields)
    old_values = models.JSONField(
        null=True,
        blank=True,
        help_text="Previous values of changed fields"
    )
    
    # New values (JSON format)
    new_values = models.JSONField(
        null=True,
        blank=True,
        help_text="New values of changed fields"
    )
    
    # IP address of the admin
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )
    
    # User agent/browser info
    user_agent = models.TextField(
        blank=True,
        help_text="Browser/client information"
    )
    
    # Status of the action
    status = models.CharField(
        max_length=20,
        choices=[
            ('SUCCESS', 'Success'),
            ('FAILED', 'Failed'),
            ('PENDING', 'Pending'),
            ('WARNING', 'Warning'),
        ],
        default='SUCCESS'
    )
    
    # Error message if failed
    error_message = models.TextField(
        blank=True,
        help_text="Error message if action failed"
    )
    
    # Timestamp
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )
    
    # Duration of the action (in milliseconds)
    duration_ms = models.IntegerField(
        null=True,
        blank=True,
        help_text="Time taken to complete action in milliseconds"
    )
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['admin_user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['model_name', '-timestamp']),
        ]
        verbose_name = 'Admin Log'
        verbose_name_plural = 'Admin Logs'
    
    def __str__(self):
        return f"{self.get_action_display()} by {self.admin_user} on {self.timestamp}"
