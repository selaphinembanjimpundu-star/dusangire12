from django import forms
from .models import Category, DietaryTag, MenuItem


class MenuFilterForm(forms.Form):
    """Form for filtering menu items"""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search menu items...',
            'id': 'menu-search'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        empty_label='All Categories',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    dietary_tags = forms.ModelMultipleChoiceField(
        queryset=DietaryTag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label='Dietary Requirements'
    )
    
    min_price = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min price',
            'step': '0.01',
            'min': '0'
        })
    )
    
    max_price = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max price',
            'step': '0.01',
            'min': '0'
        })
    )
    
    # Nutrition filters
    max_calories = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max calories',
            'min': '0'
        }),
        label='Max Calories'
    )
    
    min_protein = forms.DecimalField(
        required=False,
        max_digits=5,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min protein (g)',
            'step': '0.1',
            'min': '0'
        }),
        label='Min Protein (g)'
    )
    
    max_carbs = forms.DecimalField(
        required=False,
        max_digits=5,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max carbs (g)',
            'step': '0.1',
            'min': '0'
        }),
        label='Max Carbs (g)'
    )
    
    max_fat = forms.DecimalField(
        required=False,
        max_digits=5,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max fat (g)',
            'step': '0.1',
            'min': '0'
        }),
        label='Max Fat (g)'
    )





