from django import forms
from .models import SubscriptionPlan, UserSubscription, PlanType, SubscriptionStatus
from delivery.models import DeliveryAddress


class SubscriptionForm(forms.ModelForm):
    """Form for subscribing to a plan"""
    delivery_address = forms.ModelChoiceField(
        queryset=DeliveryAddress.objects.none(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Select delivery address for subscription orders"
    )
    
    preferred_delivery_time = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time'
        }),
        help_text="Preferred delivery time (optional)"
    )
    
    dietary_preferences = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Any dietary preferences or restrictions...'
        })
    )
    
    class Meta:
        model = UserSubscription
        fields = ['delivery_address', 'preferred_delivery_time', 'dietary_preferences', 'auto_order_enabled']
        widgets = {
            'auto_order_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['delivery_address'].queryset = DeliveryAddress.objects.filter(user=user)


class SubscriptionUpdateForm(forms.ModelForm):
    """Form for updating subscription"""
    
    class Meta:
        model = UserSubscription
        fields = ['preferred_delivery_time', 'dietary_preferences', 'auto_order_enabled']
        widgets = {
            'preferred_delivery_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'dietary_preferences': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'auto_order_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

