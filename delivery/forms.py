from django import forms
from .models import DeliveryAddress, DeliveryZone


class DeliveryAddressForm(forms.ModelForm):
    """Form for creating/editing delivery addresses"""
    
    class Meta:
        model = DeliveryAddress
        fields = [
            'label', 'full_name', 'phone',
            'address_line1', 'address_line2', 'city', 'zone',
            'delivery_instructions', 'is_default'
        ]
        widgets = {
            'label': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Home, Work, Ward 3'
            }),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line1': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ward, Room, Building, etc.'
            }),
            'address_line2': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Additional address details (optional)'
            }),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'zone': forms.Select(attrs={'class': 'form-select'}),
            'delivery_instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Special delivery instructions (optional)'
            }),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Filter zones to only active ones
        self.fields['zone'].queryset = DeliveryZone.objects.filter(is_active=True)
        self.fields['zone'].empty_label = "Select zone (optional)"
        
        # Set default city
        if not self.instance.pk:
            self.fields['city'].initial = 'Kigali'
        
        # Pre-fill with user info if available
        if user and not self.instance.pk:
            if hasattr(user, 'profile') and user.profile.phone:
                self.fields['phone'].initial = user.profile.phone
            self.fields['full_name'].initial = user.get_full_name() or user.username

















