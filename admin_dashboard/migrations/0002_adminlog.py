# Generated migration for AdminLog model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('CREATE', 'Create'), ('UPDATE', 'Update'), ('DELETE', 'Delete'), ('VIEW', 'View'), ('EXPORT', 'Export'), ('IMPORT', 'Import'), ('APPROVE', 'Approve'), ('REJECT', 'Reject'), ('ASSIGN', 'Assign'), ('UNASSIGN', 'Unassign'), ('PAYMENT_PROCESS', 'Payment Process'), ('ORDER_UPDATE', 'Order Update'), ('USER_ACTION', 'User Action'), ('SYSTEM_ACTION', 'System Action'), ('REPORT_GENERATE', 'Report Generate'), ('CONFIG_CHANGE', 'Config Change'), ('LOGIN', 'Login'), ('LOGOUT', 'Logout'), ('OTHER', 'Other')], default='OTHER', max_length=20)),
                ('model_name', models.CharField(help_text='Name of the model affected (e.g., Order, Payment, User)', max_length=100)),
                ('object_id', models.IntegerField(blank=True, help_text='ID of the affected object', null=True)),
                ('description', models.TextField(help_text='Detailed description of the action')),
                ('old_values', models.JSONField(blank=True, help_text='Previous values of changed fields', null=True)),
                ('new_values', models.JSONField(blank=True, help_text='New values of changed fields', null=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True, help_text='Browser/client information')),
                ('status', models.CharField(choices=[('SUCCESS', 'Success'), ('FAILED', 'Failed'), ('PENDING', 'Pending'), ('WARNING', 'Warning')], default='SUCCESS', max_length=20)),
                ('error_message', models.TextField(blank=True, help_text='Error message if action failed')),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('duration_ms', models.IntegerField(blank=True, help_text='Time taken to complete action in milliseconds', null=True)),
                ('admin_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='admin_logs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Admin Log',
                'verbose_name_plural': 'Admin Logs',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.AddIndex(
            model_name='adminlog',
            index=models.Index(fields=['-timestamp'], name='admin_dash_timestamp_idx'),
        ),
        migrations.AddIndex(
            model_name='adminlog',
            index=models.Index(fields=['admin_user', '-timestamp'], name='admin_dash_user_timestamp_idx'),
        ),
        migrations.AddIndex(
            model_name='adminlog',
            index=models.Index(fields=['action', '-timestamp'], name='admin_dash_action_timestamp_idx'),
        ),
        migrations.AddIndex(
            model_name='adminlog',
            index=models.Index(fields=['model_name', '-timestamp'], name='admin_dash_model_timestamp_idx'),
        ),
    ]
