from django import forms
from django.utils.translation import gettext_lazy as _
from .models import NutritionistProfile, Consultation, MealPlan, DietRecommendation, ClientNote


class NutritionistProfileForm(forms.ModelForm):
    """Form for creating/updating nutritionist profile"""
    
    class Meta:
        model = NutritionistProfile
        # Exclude 'status' from the form so it uses the model default when omitted
        fields = ['bio', 'specialization', 'license_number', 'phone_number', 'max_clients']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter your professional biography...'}),
            'specialization': forms.TextInput(attrs={'placeholder': 'e.g., Pediatric Nutrition, Sports Nutrition'}),
            'license_number': forms.TextInput(attrs={'placeholder': 'Your professional license number'}),
            'phone_number': forms.TextInput(attrs={'placeholder': '+250 7XX XXX XXX'}),
        }


class ConsultationForm(forms.ModelForm):
    """Form for scheduling consultations"""
    
    class Meta:
        model = Consultation
        fields = ['client', 'consultation_type', 'scheduled_at', 'duration_minutes', 'notes']
        widgets = {
            'scheduled_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Any notes about this consultation...'}),
        }


class MealPlanForm(forms.ModelForm):
    """Form for creating meal plans"""
    
    class Meta:
        model = MealPlan
        fields = ['client', 'title', 'description', 'start_date', 'end_date', 'notes']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe this meal plan...'}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Additional notes...'}),
        }


class DietRecommendationForm(forms.ModelForm):
    """Form for creating diet recommendations"""
    
    class Meta:
        model = DietRecommendation
        fields = ['client', 'title', 'description', 'priority', 'target_date', 'notes']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe this recommendation...'}),
            'target_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Additional notes...'}),
        }


class ClientNoteForm(forms.ModelForm):
    """Form for adding client notes"""
    
    class Meta:
        model = ClientNote
        fields = ['content', 'is_private']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter your notes about this client...'}),
        }