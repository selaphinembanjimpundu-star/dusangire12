from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import (
    Payment, PaymentTransaction, Invoice, PaymentReconciliation,
    RefundRequest, AirtelMoneyProvider, MTNMobileMoneyProvider,
    BankTransferProvider
)


@admin.register(AirtelMoneyProvider)
class AirtelMoneyProviderAdmin(admin.ModelAdmin):
    list_display = ['merchant_id', 'status_badge', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Gateway Configuration', {
            'fields': ('merchant_id', 'api_key', 'api_secret', 'base_url', 'webhook_url')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        """Display status badge"""
        if obj.is_active:
            return format_html('<span style="color: green;"><b>✓ Active</b></span>')
        return format_html('<span style="color: red;"><b>✗ Inactive</b></span>')
    status_badge.short_description = 'Status'


@admin.register(MTNMobileMoneyProvider)
class MTNMobileMoneyProviderAdmin(admin.ModelAdmin):
    list_display = ['merchant_id', 'status_badge', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Gateway Configuration', {
            'fields': ('merchant_id', 'api_key', 'subscription_key', 'base_url', 'webhook_url')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        """Display status badge"""
        if obj.is_active:
            return format_html('<span style="color: green;"><b>✓ Active</b></span>')
        return format_html('<span style="color: red;"><b>✗ Inactive</b></span>')
    status_badge.short_description = 'Status'


@admin.register(BankTransferProvider)
class BankTransferProviderAdmin(admin.ModelAdmin):
    list_display = ['bank_name', 'account_number', 'status_badge']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Bank Details', {
            'fields': ('bank_name', 'account_number', 'account_holder', 'swift_code', 'branch_code')
        }),
        ('Customer Instructions', {
            'fields': ('instructions',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        """Display status badge"""
        if obj.is_active:
            return format_html('<span style="color: green;"><b>✓ Active</b></span>')
        return format_html('<span style="color: red;"><b>✗ Inactive</b></span>')
    status_badge.short_description = 'Status'


class PaymentTransactionInline(admin.TabularInline):
    """Inline transaction history"""
    model = PaymentTransaction
    extra = 0
    can_delete = False
    readonly_fields = ['gateway_name', 'request_type', 'status', 'request_at', 'response_at', 'processing_time_ms']
    fields = ['gateway_name', 'request_type', 'status', 'request_at', 'response_at', 'processing_time_ms']


class InvoiceInline(admin.TabularInline):
    """Inline invoice display"""
    model = Invoice
    extra = 0
    can_delete = False
    readonly_fields = ['invoice_number', 'issued_date', 'total_amount', 'is_paid', 'sent_to_customer']
    fields = ['invoice_number', 'issued_date', 'total_amount', 'is_paid', 'sent_to_customer']


class RefundRequestInline(admin.TabularInline):
    """Inline refund requests"""
    model = RefundRequest
    extra = 0
    can_delete = False
    readonly_fields = ['status', 'refund_amount', 'created_at', 'approved_at']
    fields = ['status', 'refund_amount', 'reason', 'created_at', 'approved_at']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Professional payment management interface"""
    
    list_display = [
        'payment_id_short', 'customer_info', 'amount_display', 
        'method_badge', 'status_badge', 'gateway_name', 'created_at_short'
    ]
    list_filter = [
        'payment_method', 'status', 'transaction_status', 'payment_type',
        ('created_at', admin.DateFieldListFilter),
        'reconciled', 'gateway_name'
    ]
    search_fields = [
        'payment_id', 'transaction_id', 'phone_number', 'account_number',
        'order__order_number', 'invoice_number', 'transaction_reference'
    ]
    readonly_fields = [
        'payment_id', 'created_at', 'updated_at', 'paid_at', 'processing_started_at',
        'invoice_number', 'gateway_response_display', 'transaction_details'
    ]
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('payment_id', 'payment_type', 'amount', 'currency')
        }),
        ('Linked Records', {
            'fields': ('order', 'subscription'),
            'classes': ('collapse',)
        }),
        ('Payment Method', {
            'fields': ('payment_method', 'phone_number', 'account_number', 'bank_provider')
        }),
        ('Transaction Details', {
            'fields': ('transaction_id', 'transaction_reference', 'transaction_status', 'gateway_name'),
            'classes': ('collapse',)
        }),
        ('Payment Status', {
            'fields': ('status', 'invoice_number', 'invoice_generated')
        }),
        ('Gateway Response', {
            'fields': ('gateway_response_display', 'payment_link'),
            'classes': ('collapse',)
        }),
        ('Reconciliation', {
            'fields': ('reconciled', 'reconciled_at'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes', 'customer_notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'paid_at', 'processing_started_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [PaymentTransactionInline, InvoiceInline, RefundRequestInline]
    
    actions = [
        'mark_as_completed', 'mark_as_failed', 'generate_invoices',
        'mark_as_reconciled', 'send_payment_reminders'
    ]
    
    def get_queryset(self, request):
        """Optimize queries with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('order', 'subscription', 'bank_provider')
    
    # Display methods
    def payment_id_short(self, obj):
        """Display shortened payment ID"""
        return str(obj.payment_id)[:8]
    payment_id_short.short_description = 'Payment ID'
    
    def customer_info(self, obj):
        """Display customer information"""
        if obj.order:
            return f"Order: {obj.order.order_number}"
        elif obj.subscription:
            return f"Subscription: {obj.subscription.id}"
        return "—"
    customer_info.short_description = 'Customer'
    
    def amount_display(self, obj):
        """Display amount with currency"""
        return f"{obj.currency} {obj.amount:,.2f}"
    amount_display.short_description = 'Amount'
    
    def method_badge(self, obj):
        """Display payment method badge"""
        colors = {
            'mtn_mobile_money': '#FFCC00',
            'airtel_money': '#FF0000',
            'bank_transfer': '#0099FF',
            'cash_on_delivery': '#999999',
            'card': '#006600',
        }
        color = colors.get(obj.payment_method, '#999999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;"><b>{}</b></span>',
            color,
            obj.get_payment_method_display()
        )
    method_badge.short_description = 'Method'
    
    def status_badge(self, obj):
        """Display status badge with color"""
        colors = {
            'pending': '#FFC107',
            'processing': '#17A2B8',
            'completed': '#28A745',
            'failed': '#DC3545',
            'cancelled': '#6C757D',
            'refunded': '#FFC107',
        }
        color = colors.get(obj.status, '#999999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;"><b>{}</b></span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def created_at_short(self, obj):
        """Display created date in short format"""
        return obj.created_at.strftime('%Y-%m-%d %H:%M')
    created_at_short.short_description = 'Created'
    
    def gateway_response_display(self, obj):
        """Display gateway response as formatted JSON"""
        if obj.gateway_response:
            import json
            try:
                formatted = json.dumps(obj.gateway_response, indent=2)
                return format_html('<pre>{}</pre>', formatted)
            except:
                return str(obj.gateway_response)
        return "—"
    gateway_response_display.short_description = 'Gateway Response'
    
    def transaction_details(self, obj):
        """Display detailed transaction information"""
        details = f"""
        <b>Transaction ID:</b> {obj.transaction_id}<br>
        <b>Reference:</b> {obj.transaction_reference or '—'}<br>
        <b>Gateway:</b> {obj.gateway_name or '—'}<br>
        <b>Phone:</b> {obj.phone_number or '—'}<br>
        <b>Account:</b> {obj.account_number or '—'}<br>
        <b>Status:</b> {obj.get_transaction_status_display()}
        """
        return format_html(details)
    transaction_details.short_description = 'Transaction Details'
    
    # Actions
    def mark_as_completed(self, request, queryset):
        """Mark payments as completed"""
        count = 0
        for payment in queryset:
            payment.mark_as_completed()
            count += 1
        self.message_user(request, f'{count} payment(s) marked as completed.')
    mark_as_completed.short_description = '✓ Mark as Completed'
    
    def mark_as_failed(self, request, queryset):
        """Mark payments as failed"""
        count = 0
        for payment in queryset:
            payment.mark_as_failed()
            count += 1
        self.message_user(request, f'{count} payment(s) marked as failed.')
    mark_as_failed.short_description = '✗ Mark as Failed'
    
    def generate_invoices(self, request, queryset):
        """Generate invoices for completed payments"""
        count = 0
        for payment in queryset.filter(status='completed', invoice_generated=False):
            if not payment.invoice_number:
                payment.generate_invoice_number()
                payment.invoice_generated = True
                payment.save()
                count += 1
        self.message_user(request, f'{count} invoice(s) generated.')
    generate_invoices.short_description = '📄 Generate Invoices'
    
    def mark_as_reconciled(self, request, queryset):
        """Mark payments as reconciled"""
        count = queryset.update(reconciled=True, reconciled_at=timezone.now())
        self.message_user(request, f'{count} payment(s) marked as reconciled.')
    mark_as_reconciled.short_description = '✓ Mark as Reconciled'
    
    def send_payment_reminders(self, request, queryset):
        """Send payment reminders for pending payments"""
        count = queryset.filter(status='pending').count()
        self.message_user(request, f'Payment reminders queued for {count} payment(s).')
    send_payment_reminders.short_description = '📧 Send Payment Reminders'


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    """Transaction audit log"""
    
    list_display = ['payment_short', 'gateway_name', 'request_type', 'status_badge', 'request_at']
    list_filter = ['gateway_name', 'request_type', 'status', 'success', ('request_at', admin.DateFieldListFilter)]
    search_fields = ['transaction_id', 'payment__payment_id']
    readonly_fields = ['request_at', 'response_at', 'request_data_display', 'response_data_display']
    
    fieldsets = (
        ('Transaction Information', {
            'fields': ('payment', 'transaction_id', 'gateway_name', 'request_type')
        }),
        ('Request Details', {
            'fields': ('request_data_display', 'request_at'),
            'classes': ('collapse',)
        }),
        ('Response Details', {
            'fields': ('response_data_display', 'response_code', 'response_message', 'response_at', 'processing_time_ms'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('status', 'success')
        }),
        ('Error Details', {
            'fields': ('error_code', 'error_message'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('payment')
    
    def payment_short(self, obj):
        return str(obj.payment.payment_id)[:8]
    payment_short.short_description = 'Payment'
    
    def status_badge(self, obj):
        colors = {
            'initiated': '#999999',
            'sent_to_gateway': '#17A2B8',
            'gateway_accepted': '#28A745',
            'awaiting_confirmation': '#FFC107',
            'confirmed': '#28A745',
            'timeout': '#FF6B6B',
            'failed': '#DC3545',
        }
        color = colors.get(obj.status, '#999999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;"><b>{}</b></span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def request_data_display(self, obj):
        import json
        try:
            formatted = json.dumps(obj.request_data, indent=2)
            return format_html('<pre>{}</pre>', formatted)
        except:
            return str(obj.request_data)
    request_data_display.short_description = 'Request Data'
    
    def response_data_display(self, obj):
        if not obj.response_data:
            return "—"
        import json
        try:
            formatted = json.dumps(obj.response_data, indent=2)
            return format_html('<pre>{}</pre>', formatted)
        except:
            return str(obj.response_data)
    response_data_display.short_description = 'Response Data'


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """Invoice management"""
    
    list_display = ['invoice_number', 'payment_short', 'total_amount', 'status_badge', 'issued_date']
    list_filter = [('issued_date', admin.DateFieldListFilter), 'is_paid', 'sent_to_customer']
    search_fields = ['invoice_number', 'payment__payment_id']
    readonly_fields = ['issued_date', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Invoice Details', {
            'fields': ('invoice_number', 'payment', 'issued_date', 'due_date')
        }),
        ('Amounts', {
            'fields': ('subtotal', 'tax_amount', 'total_amount')
        }),
        ('Status', {
            'fields': ('is_paid', 'paid_date', 'sent_to_customer', 'sent_at')
        }),
        ('Document', {
            'fields': ('pdf_file',),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def payment_short(self, obj):
        return str(obj.payment.payment_id)[:8]
    payment_short.short_description = 'Payment'
    
    def status_badge(self, obj):
        if obj.is_paid:
            return format_html('<span style="color: green;"><b>✓ Paid</b></span>')
        return format_html('<span style="color: red;"><b>Unpaid</b></span>')
    status_badge.short_description = 'Status'


@admin.register(PaymentReconciliation)
class PaymentReconciliationAdmin(admin.ModelAdmin):
    """Payment reconciliation tracking"""
    
    list_display = ['file_name', 'provider', 'statement_date', 'status_badge', 'discrepancy_display']
    list_filter = ['provider', 'status', ('statement_date', admin.DateFieldListFilter)]
    search_fields = ['file_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('File Information', {
            'fields': ('file_name', 'file_upload', 'provider')
        }),
        ('Statement Period', {
            'fields': ('statement_date', 'statement_period_start', 'statement_period_end')
        }),
        ('Summary', {
            'fields': ('total_transactions', 'total_amount', 'matched_count', 'unmatched_count', 'discrepancy_amount')
        }),
        ('Status', {
            'fields': ('status', 'reconciled_by', 'reconciled_at')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        colors = {
            'PENDING': '#FFC107',
            'IN_PROGRESS': '#17A2B8',
            'COMPLETE': '#28A745',
            'DISCREPANCY': '#FF6B6B',
            'RESOLVED': '#28A745',
        }
        color = colors.get(obj.status, '#999999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;"><b>{}</b></span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def discrepancy_display(self, obj):
        if obj.discrepancy_amount == 0:
            return format_html('<span style="color: green;"><b>RWF {:.2f}</b></span>', obj.discrepancy_amount)
        return format_html('<span style="color: red;"><b>RWF {:.2f}</b></span>', obj.discrepancy_amount)
    discrepancy_display.short_description = 'Discrepancy'


@admin.register(RefundRequest)
class RefundRequestAdmin(admin.ModelAdmin):
    """Refund request management"""
    
    list_display = ['payment_short', 'refund_amount', 'status_badge', 'created_at']
    list_filter = ['status', ('created_at', admin.DateFieldListFilter), ('approved_at', admin.DateFieldListFilter)]
    search_fields = ['payment__payment_id']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Refund Request', {
            'fields': ('payment', 'reason', 'refund_amount')
        }),
        ('Status', {
            'fields': ('status', 'approved_by', 'approved_at')
        }),
        ('Processing', {
            'fields': ('refund_transaction_id', 'response_notes', 'refund_completed_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_refund', 'reject_refund']
    
    def payment_short(self, obj):
        return str(obj.payment.payment_id)[:8]
    payment_short.short_description = 'Payment'
    
    def status_badge(self, obj):
        colors = {
            'REQUESTED': '#FFC107',
            'APPROVED': '#28A745',
            'PROCESSING': '#17A2B8',
            'COMPLETED': '#28A745',
            'REJECTED': '#DC3545',
        }
        color = colors.get(obj.status, '#999999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;"><b>{}</b></span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def approve_refund(self, request, queryset):
        count = queryset.filter(status='REQUESTED').update(
            status='APPROVED',
            approved_by=request.user,
            approved_at=timezone.now()
        )
        self.message_user(request, f'{count} refund request(s) approved.')
    approve_refund.short_description = '✓ Approve Refund'
    
    def reject_refund(self, request, queryset):
        count = queryset.filter(status='REQUESTED').update(status='REJECTED')
        self.message_user(request, f'{count} refund request(s) rejected.')
    reject_refund.short_description = '✗ Reject Refund'

