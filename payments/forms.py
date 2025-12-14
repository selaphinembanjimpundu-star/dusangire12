from django import forms
from .models import Payment, PaymentMethod, PaymentStatus


class PaymentForm(forms.ModelForm):
    """Form for payment method selection and details"""
    
    payment_method = forms.ChoiceField(
        choices=PaymentMethod.choices,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        required=True
    )
    
    # Mobile money fields
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 0781234567'
        }),
        help_text="Required for mobile money payments"
    )
    
    # Bank transfer fields
    account_number = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Account number or reference'
        }),
        help_text="Required for bank transfer"
    )
    
    # Transaction ID (for completed payments)
    transaction_id = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Transaction ID or reference number'
        })
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Additional payment notes (optional)'
        })
    )
    
    class Meta:
        model = Payment
        fields = ['payment_method', 'phone_number', 'account_number', 'transaction_id', 'notes']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields conditionally required based on payment method
        self.fields['phone_number'].widget.attrs['data-required-for'] = 'mtn_mobile_money,airtel_money'
        self.fields['account_number'].widget.attrs['data-required-for'] = 'bank_transfer'
    
    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        phone_number = cleaned_data.get('phone_number')
        account_number = cleaned_data.get('account_number')
        
        # Validate mobile money
        if payment_method in [PaymentMethod.MTN_MOBILE_MONEY, PaymentMethod.AIRTEL_MONEY]:
            if not phone_number:
                raise forms.ValidationError({
                    'phone_number': 'Phone number is required for mobile money payments.'
                })
        
        # Validate bank transfer
        if payment_method == PaymentMethod.BANK_TRANSFER:
            if not account_number:
                raise forms.ValidationError({
                    'account_number': 'Account number is required for bank transfer.'
                })
        
        return cleaned_data



