from django import forms
from django.core.exceptions import ValidationError
from .models import Review


class ReviewForm(forms.ModelForm):
    """Professional form for creating/editing reviews with validation"""
    order_id = forms.IntegerField(required=False, widget=forms.HiddenInput())
    
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment', 'order_id']
        widgets = {
            'rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 5,
                'required': True,
                'step': 1
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Review title (optional)',
                'maxlength': 200
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Write your review here (minimum 10 characters)...',
                'required': True,
                'maxlength': 2000,
                'minlength': 10
            }),
        }
        labels = {
            'rating': 'Rating (1-5 stars)',
            'title': 'Title (optional)',
            'comment': 'Your Review',
        }
        help_texts = {
            'rating': 'Rate this item from 1 (poor) to 5 (excellent)',
            'comment': 'Share your experience with this item (minimum 10 characters)',
        }
    
    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating is None:
            raise forms.ValidationError("Rating is required.")
        if rating < 1 or rating > 5:
            raise forms.ValidationError("Rating must be between 1 and 5.")
        return int(rating)
    
    def clean_comment(self):
        comment = self.cleaned_data.get('comment')
        if not comment:
            raise forms.ValidationError("Review comment is required.")
        
        # Remove extra whitespace
        comment = comment.strip()
        
        # Check minimum length
        if len(comment) < 10:
            raise forms.ValidationError(
                "Review comment must be at least 10 characters long. "
                "Please provide more details about your experience."
            )
        
        # Check maximum length
        if len(comment) > 2000:
            raise forms.ValidationError(
                "Review comment is too long. Maximum 2000 characters allowed."
            )
        
        return comment
    
    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if title and len(title) < 3:
            raise forms.ValidationError(
                "Title must be at least 3 characters long if provided."
            )
        return title
    
    def clean(self):
        cleaned_data = super().clean()
        # Additional cross-field validation can be added here
        return cleaned_data

















