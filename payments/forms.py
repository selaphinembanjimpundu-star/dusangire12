from django import forms
from django.core.exceptions import ValidationError
from .models import Payment, PaymentMethod, PaymentStatus
from accounts.validators import (
    validate_uganda_phone_number,
    format_uganda_phone_number,
    validate_payment_method_details
)


class PaymentForm(forms.ModelForm):
    """Professional payment form with comprehensive validation"""
    
    payment_method = forms.ChoiceField(
        choices=PaymentMethod.choices,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        required=True,
        help_text="Select your preferred payment method"
    )
    
    # Mobile money fields
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 0781234567 or +256781234567',
            'pattern': r'^(\+?256|0)?[7][0-9]{8}$'
        }),
        help_text="Required for mobile money payments. Format: 0781234567 or +256781234567"
    )
    
    # Bank transfer fields
    account_number = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Account number or reference',
            'pattern': r'^[A-Za-z0-9\s\-]+$'
        }),
        help_text="Required for bank transfer. Enter your account number or reference."
    )
    
    # Transaction ID (for completed payments)
    transaction_id = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Transaction ID or reference number'
        }),
        help_text="Enter transaction ID if payment is already completed"
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Additional payment notes (optional)',
            'maxlength': 500
        }),
        help_text="Optional notes or instructions for payment processing"
    )
    
    class Meta:
        model = Payment
        fields = ['payment_method', 'phone_number', 'account_number', 'transaction_id', 'notes']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields conditionally required based on payment method
        self.fields['phone_number'].widget.attrs['data-required-for'] = 'mtn_mobile_money,airtel_money'
        self.fields['account_number'].widget.attrs['data-required-for'] = 'bank_transfer'
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number', '').strip()
        if not phone_number:
            return phone_number
        
        # Validate format
        if not validate_uganda_phone_number(phone_number):
            raise ValidationError(
                "Invalid phone number format. Please use format: 0781234567 or +256781234567"
            )
        
        # Format to standard format
        return format_uganda_phone_number(phone_number) or phone_number
    
    def clean_account_number(self):
        account_number = self.cleaned_data.get('account_number', '').strip()
        if not account_number:
            return account_number
        
        # Validate length
        if len(account_number) < 5:
            raise ValidationError(
                "Account number must be at least 5 characters long."
            )
        
        # Validate characters (alphanumeric, spaces, hyphens only)
        import re
        if not re.match(r'^[A-Za-z0-9\s\-]+$', account_number):
            raise ValidationError(
                "Account number contains invalid characters. Use only letters, numbers, spaces, and hyphens."
            )
        
        return account_number
    
    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        phone_number = cleaned_data.get('phone_number', '').strip()
        account_number = cleaned_data.get('account_number', '').strip()
        
        # Professional validation using validator
        validation_result = validate_payment_method_details(
            payment_method,
            phone_number if phone_number else None,
            account_number if account_number else None
        )
        
        if not validation_result['valid']:
            errors = {}
            for error in validation_result['errors']:
                if 'phone number' in error.lower():
                    errors['phone_number'] = error
                elif 'account number' in error.lower():
                    errors['account_number'] = error
                else:
                    # General error
                    raise ValidationError(validation_result['errors'])
            
            if errors:
                raise ValidationError(errors)
        
        return cleaned_data

















