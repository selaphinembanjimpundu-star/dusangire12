from django import forms
from django.core.exceptions import ValidationError
from .models import SubscriptionPlan, Subscription, PlanType, SubscriptionStatus
from delivery.models import DeliveryAddress
from menu.models import MenuItem


class SubscriptionForm(forms.ModelForm):
    """Professional form for subscribing to a plan with validation"""
    delivery_address = forms.ModelChoiceField(
        queryset=DeliveryAddress.objects.none(),
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True
        }),
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
            'placeholder': 'Any dietary preferences or restrictions (e.g., vegetarian, diabetic-friendly, low-sodium)...',
            'maxlength': 500
        }),
        help_text="Optional: Describe any dietary preferences or restrictions"
    )
    
    preferred_meals = forms.ModelMultipleChoiceField(
        queryset=MenuItem.objects.filter(is_available=True),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        help_text="Optional: Select your preferred meals (we'll prioritize these in your orders)"
    )
    
    auto_renewal_enabled = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text="Automatically renew subscription when it expires"
    )
    
    class Meta:
        model = Subscription
        fields = ['delivery_address', 'preferred_delivery_time', 'dietary_preferences', 
                 'preferred_meals', 'auto_order_enabled', 'auto_renewal_enabled']
        widgets = {
            'auto_order_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        plan = kwargs.pop('plan', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['delivery_address'].queryset = DeliveryAddress.objects.filter(user=user)
        
        # Limit preferred meals to plan's menu items if plan has specific items
        if plan and plan.menu_items.exists():
            self.fields['preferred_meals'].queryset = plan.menu_items.filter(is_available=True)
        else:
            # Show top-rated items as suggestions
            from menu.models import MenuItem
            self.fields['preferred_meals'].queryset = MenuItem.objects.filter(
                is_available=True
            ).order_by('-average_rating', '-total_reviews')[:20]
    
    def clean_dietary_preferences(self):
        dietary = self.cleaned_data.get('dietary_preferences', '').strip()
        if dietary and len(dietary) > 500:
            raise ValidationError("Dietary preferences must be 500 characters or less.")
        return dietary


class SubscriptionUpdateForm(forms.ModelForm):
    """Professional form for updating subscription with validation"""
    
    preferred_meals = forms.ModelMultipleChoiceField(
        queryset=MenuItem.objects.filter(is_available=True),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        help_text="Update your preferred meals"
    )
    
    class Meta:
        model = Subscription
        fields = ['preferred_delivery_time', 'dietary_preferences', 'preferred_meals',
                 'auto_order_enabled', 'auto_renewal_enabled']
        widgets = {
            'preferred_delivery_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'dietary_preferences': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'maxlength': 500
            }),
            'auto_order_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'auto_renewal_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.plan:
            # Limit to plan's menu items if specified
            if self.instance.plan.menu_items.exists():
                self.fields['preferred_meals'].queryset = self.instance.plan.menu_items.filter(is_available=True)
        
        # Set initial preferred meals
        if self.instance.pk:
            self.fields['preferred_meals'].initial = self.instance.preferred_meals.all()
    
    def clean_dietary_preferences(self):
        dietary = self.cleaned_data.get('dietary_preferences', '').strip()
        if dietary and len(dietary) > 500:
            raise ValidationError("Dietary preferences must be 500 characters or less.")
        return dietary

















