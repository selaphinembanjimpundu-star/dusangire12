from django import forms
from .models import SupportTicket, SupportMessage
from orders.models import Order


class SupportTicketForm(forms.ModelForm):
    """Form for creating support tickets"""
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Describe your issue or question...'
        }),
        label='Message'
    )
    
    class Meta:
        model = SupportTicket
        fields = ['subject', 'message', 'order', 'priority']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief subject line'
            }),
            'order': forms.Select(attrs={
                'class': 'form-select'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'subject': 'Subject',
            'order': 'Related Order (optional)',
            'priority': 'Priority',
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Only show user's orders
            self.fields['order'].queryset = Order.objects.filter(
                user=user
            ).order_by('-created_at')[:20]
            self.fields['order'].required = False


class SupportMessageForm(forms.ModelForm):
    """Form for adding messages to tickets"""
    
    class Meta:
        model = SupportMessage
        fields = ['message', 'is_internal']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Type your message here...'
            }),
            'is_internal': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'message': 'Message',
            'is_internal': 'Internal note (staff only)',
        }


class FeedbackForm(forms.Form):
    """Public feedback form (doesn't require login)"""
    FEEDBACK_TYPES = [
        ('general', 'General Feedback'),
        ('suggestion', 'Feature Suggestion'),
        ('bug', 'Bug Report'),
        ('compliment', 'Compliment'),
        ('complaint', 'Complaint'),
    ]
    
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your name'
        }),
        required=True
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@example.com'
        }),
        required=True
    )
    feedback_type = forms.ChoiceField(
        choices=FEEDBACK_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        required=True
    )
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Brief subject'
        }),
        required=True
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6,
            'placeholder': 'Your feedback, suggestion, or question...'
        }),
        required=True
    )
