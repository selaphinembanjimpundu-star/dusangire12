"""
Hospital Ward Management Forms
Handles forms for patient admission, discharge, transfers, and bulk operations
"""

from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import (
    PatientAdmission, PatientDischarge, PatientTransfer,
    WardBed, Ward, BulkOperation
)
import csv
from io import StringIO


class PatientAdmissionForm(forms.ModelForm):
    """Form for admitting a patient to a bed"""
    
    class Meta:
        model = PatientAdmission
        fields = ['patient', 'bed', 'reason', 'chief_complaint', 'medical_history']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'bed': forms.Select(attrs={'class': 'form-control'}),
            'reason': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Admission reason'}),
            'chief_complaint': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'medical_history': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show available beds
        self.fields['bed'].queryset = WardBed.objects.filter(status='available')
        # Show all users who can be patients
        self.fields['patient'].queryset = User.objects.all()


class PatientDischargeForm(forms.ModelForm):
    """Form for discharging a patient"""
    
    class Meta:
        model = PatientDischarge
        fields = ['discharge_status', 'discharge_notes', 'follow_up_instructions', 'return_visit_date']
        widgets = {
            'discharge_status': forms.Select(attrs={'class': 'form-control'}),
            'discharge_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'follow_up_instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Instructions for follow-up care'}),
            'return_visit_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class PatientTransferForm(forms.ModelForm):
    """Form for transferring a patient between beds/wards"""
    
    class Meta:
        model = PatientTransfer
        fields = ['to_bed', 'reason']
        widgets = {
            'to_bed': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select destination bed'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Reason for transfer'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show available beds
        self.fields['to_bed'].queryset = WardBed.objects.filter(status='available')


class BulkPatientImportForm(forms.Form):
    """Form for bulk importing patients from CSV"""
    
    csv_file = forms.FileField(
        label='CSV File',
        help_text='Format: patient_id, first_name, last_name, email, phone, date_of_birth, gender',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.csv'})
    )
    
    def clean_csv_file(self):
        """Validate CSV file format"""
        file = self.cleaned_data.get('csv_file')
        if file:
            if not file.name.endswith('.csv'):
                raise ValidationError('File must be a CSV file.')
            
            # Read and validate
            try:
                decoded = file.read().decode('utf-8')
                reader = csv.DictReader(StringIO(decoded))
                
                expected_fields = ['patient_id', 'first_name', 'last_name', 'email', 'phone', 'date_of_birth', 'gender']
                if reader.fieldnames and not all(field in reader.fieldnames for field in expected_fields):
                    raise ValidationError(f'CSV must have columns: {", ".join(expected_fields)}')
            except Exception as e:
                raise ValidationError(f'Error reading CSV: {str(e)}')
        
        return file


class BulkPatientAssignmentForm(forms.Form):
    """Form for bulk assigning patients to beds"""
    
    csv_file = forms.FileField(
        label='CSV File',
        help_text='Format: patient_id, bed_id, reason, chief_complaint',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.csv'})
    )
    send_notifications = forms.BooleanField(
        required=False,
        initial=True,
        label='Send admission notifications',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def clean_csv_file(self):
        """Validate CSV file format"""
        file = self.cleaned_data.get('csv_file')
        if file:
            if not file.name.endswith('.csv'):
                raise ValidationError('File must be a CSV file.')
            
            try:
                decoded = file.read().decode('utf-8')
                reader = csv.DictReader(StringIO(decoded))
                
                expected_fields = ['patient_id', 'bed_id', 'reason', 'chief_complaint']
                if reader.fieldnames and not all(field in reader.fieldnames for field in expected_fields):
                    raise ValidationError(f'CSV must have columns: {", ".join(expected_fields)}')
            except Exception as e:
                raise ValidationError(f'Error reading CSV: {str(e)}')
        
        return file


class BulkDischargeForm(forms.Form):
    """Form for bulk discharging multiple patients"""
    
    admissions = forms.ModelMultipleChoiceField(
        queryset=PatientAdmission.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label='Select patients to discharge'
    )
    discharge_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'General discharge notes'}),
        label='General discharge notes (optional)'
    )
    send_notifications = forms.BooleanField(
        required=False,
        initial=True,
        label='Send discharge notifications',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class ExportReportForm(forms.Form):
    """Form for exporting hospital reports"""
    
    REPORT_TYPES = [
        ('occupancy', 'Occupancy Report'),
        ('patient_list', 'Patient List'),
        ('admission_discharge', 'Admission/Discharge Summary'),
        ('bed_utilization', 'Bed Utilization'),
    ]
    
    report_type = forms.ChoiceField(
        choices=REPORT_TYPES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Report Type'
    )
    
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Start Date (optional)'
    )
    
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='End Date (optional)'
    )
    
    ward = forms.ModelChoiceField(
        queryset=Ward.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Filter by Ward (optional)'
    )


class FilterBulkOperationForm(forms.Form):
    """Form for filtering bulk operations"""
    
    OPERATION_CHOICES = [('', 'All Operations')] + BulkOperation.OPERATION_TYPES
    STATUS_CHOICES = [('', 'All Statuses')] + BulkOperation.STATUS_CHOICES
    
    operation_type = forms.ChoiceField(
        choices=OPERATION_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Date From'
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Date To'
    )
