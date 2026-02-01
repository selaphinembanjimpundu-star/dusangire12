# Generated migration for payment system enhancements

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.core.validators
from decimal import Decimal
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_payment_gateway_name_payment_gateway_response_and_more'),
        ('subscriptions', '0001_initial'),
        ('orders', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Create provider models
        migrations.CreateModel(
            name='AirtelMoneyProvider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('merchant_id', models.CharField(max_length=100, unique=True)),
                ('api_key', models.CharField(max_length=500)),
                ('api_secret', models.CharField(max_length=500)),
                ('base_url', models.URLField(default='https://openapiuat.airtel.africa')),
                ('webhook_url', models.URLField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Airtel Money Providers',
            },
        ),
        migrations.CreateModel(
            name='MTNMobileMoneyProvider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('merchant_id', models.CharField(max_length=100, unique=True)),
                ('api_key', models.CharField(max_length=500)),
                ('subscription_key', models.CharField(max_length=500)),
                ('base_url', models.URLField(default='https://momoapi.mtn.com')),
                ('webhook_url', models.URLField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'MTN Mobile Money Providers',
            },
        ),
        migrations.CreateModel(
            name='BankTransferProvider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bank_name', models.CharField(max_length=100)),
                ('account_number', models.CharField(max_length=50)),
                ('account_holder', models.CharField(max_length=100)),
                ('swift_code', models.CharField(blank=True, max_length=20)),
                ('branch_code', models.CharField(blank=True, max_length=20)),
                ('instructions', models.TextField(help_text='Payment instructions for customers')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        # Add new fields to Payment model
        migrations.AddField(
            model_name='payment',
            name='payment_id',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=False),
        ),
        migrations.AddField(
            model_name='payment',
            name='currency',
            field=models.CharField(default='RWF', max_length=3),
        ),
        migrations.AddField(
            model_name='payment',
            name='payment_type',
            field=models.CharField(
                choices=[('order_payment', 'Order Payment'), ('subscription_payment', 'Subscription Payment'), 
                        ('loyalty_redemption', 'Loyalty Points Redemption'), ('refund', 'Refund')],
                default='order_payment',
                max_length=30
            ),
        ),
        migrations.AddField(
            model_name='payment',
            name='transaction_status',
            field=models.CharField(
                choices=[('initiated', 'Initiated'), ('sent_to_gateway', 'Sent to Gateway'), 
                        ('gateway_accepted', 'Gateway Accepted'), ('awaiting_confirmation', 'Awaiting Confirmation'),
                        ('confirmed', 'Confirmed'), ('timeout', 'Timed Out'), ('failed', 'Failed')],
                default='initiated',
                max_length=25
            ),
        ),
        migrations.AddField(
            model_name='payment',
            name='transaction_reference',
            field=models.CharField(blank=True, db_index=True, max_length=100),
        ),
        migrations.AddField(
            model_name='payment',
            name='invoice_number',
            field=models.CharField(blank=True, db_index=True, max_length=50, unique=False),
        ),
        migrations.AddField(
            model_name='payment',
            name='invoice_generated',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='payment',
            name='reconciled',
            field=models.BooleanField(default=False, help_text='Has payment been reconciled with bank?'),
        ),
        migrations.AddField(
            model_name='payment',
            name='reconciled_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='customer_notes',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='processing_started_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        # Add subscription relationship
        migrations.AddField(
            model_name='payment',
            name='subscription',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='subscriptions.usersubscription'),
        ),
        # Add bank provider relationship
        migrations.AddField(
            model_name='payment',
            name='bank_provider',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payments', to='payments.banktransferprovider'),
        ),
        # Update validators on phone_number
        migrations.AlterField(
            model_name='payment',
            name='phone_number',
            field=models.CharField(
                blank=True,
                max_length=20,
                validators=[django.core.validators.RegexValidator(r'^\+?[0-9]{9,15}$', 'Invalid phone number')],
                help_text='Phone number for mobile money'
            ),
        ),
        # Update transaction_id to be unique with db_index
        migrations.AlterField(
            model_name='payment',
            name='transaction_id',
            field=models.CharField(db_index=True, max_length=100, unique=False),
        ),
        # Create PaymentTransaction model
        migrations.CreateModel(
            name='PaymentTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_id', models.CharField(db_index=True, max_length=100)),
                ('gateway_name', models.CharField(max_length=50)),
                ('request_type', models.CharField(
                    choices=[('INITIATE', 'Initiate Payment'), ('QUERY', 'Query Status'), 
                            ('CONFIRM', 'Confirm Payment'), ('CANCEL', 'Cancel Payment'), ('REFUND', 'Refund Payment')],
                    max_length=50
                )),
                ('request_data', models.JSONField()),
                ('response_data', models.JSONField(blank=True, null=True)),
                ('response_code', models.CharField(blank=True, max_length=10)),
                ('response_message', models.TextField(blank=True)),
                ('status', models.CharField(
                    choices=[('initiated', 'Initiated'), ('sent_to_gateway', 'Sent to Gateway'), 
                            ('gateway_accepted', 'Gateway Accepted'), ('awaiting_confirmation', 'Awaiting Confirmation'),
                            ('confirmed', 'Confirmed'), ('timeout', 'Timed Out'), ('failed', 'Failed')],
                    max_length=25
                )),
                ('success', models.BooleanField(default=False)),
                ('request_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('response_at', models.DateTimeField(blank=True, null=True)),
                ('processing_time_ms', models.IntegerField(blank=True, null=True)),
                ('error_code', models.CharField(blank=True, max_length=50)),
                ('error_message', models.TextField(blank=True)),
                ('payment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='payments.payment')),
            ],
            options={
                'ordering': ['-request_at'],
            },
        ),
        # Create Invoice model
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_number', models.CharField(db_index=True, max_length=50, unique=True)),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=10)),
                ('tax_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('issued_date', models.DateField(auto_now_add=True)),
                ('due_date', models.DateField()),
                ('notes', models.TextField(blank=True)),
                ('pdf_file', models.FileField(blank=True, null=True, upload_to='invoices/')),
                ('is_paid', models.BooleanField(default=False)),
                ('paid_date', models.DateField(blank=True, null=True)),
                ('sent_to_customer', models.BooleanField(default=False)),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('payment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='invoice', to='payments.payment')),
            ],
            options={
                'ordering': ['-issued_date'],
            },
        ),
        # Create PaymentReconciliation model
        migrations.CreateModel(
            name='PaymentReconciliation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_name', models.CharField(max_length=255)),
                ('file_upload', models.FileField(upload_to='reconciliation_files/')),
                ('provider', models.CharField(
                    choices=[('AIRTEL', 'Airtel Money'), ('MTN', 'MTN Mobile Money'), ('BANK', 'Bank Transfer')],
                    max_length=50
                )),
                ('statement_date', models.DateField()),
                ('statement_period_start', models.DateField()),
                ('statement_period_end', models.DateField()),
                ('total_transactions', models.IntegerField()),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('matched_count', models.IntegerField(default=0)),
                ('unmatched_count', models.IntegerField(default=0)),
                ('discrepancy_amount', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('status', models.CharField(
                    choices=[('PENDING', 'Pending Review'), ('IN_PROGRESS', 'In Progress'), 
                            ('COMPLETE', 'Reconciliation Complete'), ('DISCREPANCY', 'Discrepancy Found'), ('RESOLVED', 'Resolved')],
                    default='PENDING',
                    max_length=20
                )),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('reconciled_at', models.DateTimeField(blank=True, null=True)),
                ('reconciled_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-statement_date'],
            },
        ),
        # Create RefundRequest model
        migrations.CreateModel(
            name='RefundRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.TextField()),
                ('refund_amount', models.DecimalField(
                    decimal_places=2,
                    max_digits=10,
                    validators=[django.core.validators.MinValueValidator(Decimal('0.01'))]
                )),
                ('status', models.CharField(
                    choices=[('REQUESTED', 'Requested'), ('APPROVED', 'Approved'), 
                            ('PROCESSING', 'Processing'), ('COMPLETED', 'Completed'), ('REJECTED', 'Rejected')],
                    default='REQUESTED',
                    max_length=20
                )),
                ('refund_transaction_id', models.CharField(blank=True, db_index=True, max_length=100)),
                ('response_notes', models.TextField(blank=True)),
                ('refund_completed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('approved_at', models.DateTimeField(blank=True, null=True)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_refunds', to=settings.AUTH_USER_MODEL)),
                ('payment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='refund_requests', to='payments.payment')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        # Add indexes to Payment model
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['-created_at'], name='payments_pa_created_idx'),
        ),
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['payment_method', 'status'], name='payments_pa_method_status_idx'),
        ),
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['reconciled', '-created_at'], name='payments_pa_reconciled_idx'),
        ),
        # Add indexes to PaymentTransaction
        migrations.AddIndex(
            model_name='paymenttransaction',
            index=models.Index(fields=['-request_at'], name='payments_pt_request_at_idx'),
        ),
        migrations.AddIndex(
            model_name='paymenttransaction',
            index=models.Index(fields=['payment', 'gateway_name'], name='payments_pt_payment_gateway_idx'),
        ),
    ]
