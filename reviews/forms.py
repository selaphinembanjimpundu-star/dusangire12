from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    """Form for creating/editing reviews"""
    order_id = forms.IntegerField(required=False, widget=forms.HiddenInput())
    
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment', 'order_id']
        widgets = {
            'rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 5,
                'required': True
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Review title (optional)'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Write your review here...',
                'required': True
            }),
        }
        labels = {
            'rating': 'Rating (1-5 stars)',
            'title': 'Title (optional)',
            'comment': 'Your Review',
        }
    
    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating and (rating < 1 or rating > 5):
            raise forms.ValidationError("Rating must be between 1 and 5.")
        return rating

