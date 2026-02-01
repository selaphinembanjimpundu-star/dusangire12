# Generated migration for RBAC system expansion
# This migration adds role-based access control fields to Profile model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0001_initial'),
    ]

    operations = [
        # Update UserRole choices to include 10 roles instead of 4
        migrations.AlterField(
            model_name='profile',
            name='role',
            field=models.CharField(
                choices=[
                    ('patient', 'Patient'),
                    ('caregiver', 'Caregiver'),
                    ('nutritionist', 'Nutritionist'),
                    ('medical_staff', 'Medical Staff'),
                    ('chef', 'Chef'),
                    ('kitchen_staff', 'Kitchen Staff'),
                    ('delivery_person', 'Delivery Person'),
                    ('support_staff', 'Support Staff'),
                    ('hospital_manager', 'Hospital Manager'),
                    ('admin', 'Admin'),
                    # Legacy aliases for backward compatibility
                    ('customer', 'Customer'),  # Alias for patient
                    ('staff', 'Staff'),  # Alias for support_staff
                ],
                default='patient',
                max_length=20,
            ),
        ),
        
        # Add new fields for status management
        migrations.AddField(
            model_name='profile',
            name='status',
            field=models.CharField(
                choices=[
                    ('active', 'Active'),
                    ('inactive', 'Inactive'),
                    ('suspended', 'Suspended'),
                    ('pending_verification', 'Pending Verification'),
                ],
                default='pending_verification',
                max_length=20,
                help_text='Account status: active, inactive, suspended, or pending verification'
            ),
        ),
        
        migrations.AddField(
            model_name='profile',
            name='is_active',
            field=models.BooleanField(
                default=True,
                help_text='Whether the user account is active'
            ),
        ),
        
        # Add healthcare provider fields
        migrations.AddField(
            model_name='profile',
            name='license_number',
            field=models.CharField(
                max_length=100,
                blank=True,
                null=True,
                help_text='Professional license number for healthcare providers'
            ),
        ),
        
        migrations.AddField(
            model_name='profile',
            name='specialization',
            field=models.CharField(
                max_length=100,
                blank=True,
                null=True,
                help_text='Healthcare provider specialization (e.g., Pediatrics, Cardiology)'
            ),
        ),
        
        migrations.AddField(
            model_name='profile',
            name='years_experience',
            field=models.IntegerField(
                blank=True,
                null=True,
                help_text='Years of professional experience'
            ),
        ),
        
        # Add staff fields
        migrations.AddField(
            model_name='profile',
            name='department',
            field=models.CharField(
                max_length=100,
                blank=True,
                null=True,
                help_text='Department or team assignment (e.g., Kitchen, Delivery, Support)'
            ),
        ),
        
        migrations.AddField(
            model_name='profile',
            name='employee_id',
            field=models.CharField(
                max_length=50,
                blank=True,
                null=True,
                unique=True,
                help_text='Unique employee identifier'
            ),
        ),
        
        migrations.AddField(
            model_name='profile',
            name='manager',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='accounts.profile',
                related_name='subordinates',
                help_text='Direct manager/supervisor'
            ),
        ),
        
        # Add delivery fields
        migrations.AddField(
            model_name='profile',
            name='vehicle_registration',
            field=models.CharField(
                max_length=50,
                blank=True,
                null=True,
                help_text='Vehicle registration number for delivery personnel'
            ),
        ),
        
        migrations.AddField(
            model_name='profile',
            name='delivery_zones',
            field=models.CharField(
                max_length=200,
                blank=True,
                null=True,
                help_text='Comma-separated list of delivery zones/areas'
            ),
        ),
        
        migrations.AddField(
            model_name='profile',
            name='is_available_for_delivery',
            field=models.BooleanField(
                default=False,
                help_text='Whether delivery person is currently available for deliveries'
            ),
        ),
        
        # Add caregiver fields
        migrations.AddField(
            model_name='profile',
            name='patient_relationship',
            field=models.CharField(
                max_length=50,
                blank=True,
                null=True,
                choices=[
                    ('parent', 'Parent'),
                    ('spouse', 'Spouse'),
                    ('sibling', 'Sibling'),
                    ('adult_child', 'Adult Child'),
                    ('other_family', 'Other Family Member'),
                    ('friend', 'Friend'),
                    ('professional_caregiver', 'Professional Caregiver'),
                ],
                help_text='Relationship to patient (for caregivers)'
            ),
        ),
        
        migrations.AddField(
            model_name='profile',
            name='assigned_patient',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
                related_name='caregivers',
                help_text='Patient assigned to this caregiver'
            ),
        ),
        
        # Add notification preferences
        migrations.AddField(
            model_name='profile',
            name='email_notifications',
            field=models.BooleanField(
                default=True,
                help_text='Enable email notifications'
            ),
        ),
        
        migrations.AddField(
            model_name='profile',
            name='sms_notifications',
            field=models.BooleanField(
                default=True,
                help_text='Enable SMS notifications'
            ),
        ),
        
        migrations.AddField(
            model_name='profile',
            name='push_notifications',
            field=models.BooleanField(
                default=True,
                help_text='Enable push notifications'
            ),
        ),
        
        # Add database indexes for optimization
        migrations.AddIndex(
            model_name='profile',
            index=models.Index(
                fields=['role', 'is_active'],
                name='profile_role_active_idx'
            ),
        ),
        
        migrations.AddIndex(
            model_name='profile',
            index=models.Index(
                fields=['user', 'role'],
                name='profile_user_role_idx'
            ),
        ),
    ]
