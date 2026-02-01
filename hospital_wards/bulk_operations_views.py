"""
Bulk Operations Views for Hospital Ward Management
Handles CSV import/export, batch operations, and bulk management
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db import transaction
from django.db.models import Q, Count
from datetime import datetime, timedelta
import csv
import io

from .models import (
    BulkOperation, PatientAdmission, PatientDischarge,
    WardBed, Ward, Patient, PatientTransfer
)
from .forms import (
    BulkPatientImportForm, BulkPatientAssignmentForm, BulkDischargeForm,
    ExportReportForm, FilterBulkOperationForm
)


@login_required
@require_http_methods(["GET", "POST"])
def bulk_import_patients(request):
    """Import patients from CSV file"""
    if request.method == 'POST':
        form = BulkPatientImportForm(request.POST, request.FILES)
        if form.is_valid():
            return handle_patient_import(request, form.cleaned_data['csv_file'])
    else:
        form = BulkPatientImportForm()
    
    context = {'form': form}
    return render(request, 'hospital_wards/bulk_import_patients.html', context)


def handle_patient_import(request, csv_file):
    """Process patient import CSV"""
    bulk_op = BulkOperation.objects.create(
        operation_type='import_patients',
        status='processing',
        initiated_by=request.user,
        total_records=0
    )
    
    try:
        decoded = csv_file.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(decoded))
        
        successful = 0
        failed = 0
        errors = []
        
        with transaction.atomic():
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (skip header)
                try:
                    # Validate and create patient
                    patient_id = row.get('patient_id', '').strip()
                    first_name = row.get('first_name', '').strip()
                    last_name = row.get('last_name', '').strip()
                    email = row.get('email', '').strip()
                    phone = row.get('phone', '').strip()
                    date_of_birth = row.get('date_of_birth', '').strip()
                    gender = row.get('gender', '').strip()
                    
                    if not all([first_name, last_name, email]):
                        errors.append(f"Row {row_num}: Missing required fields")
                        failed += 1
                        continue
                    
                    # Check if patient already exists
                    if Patient.objects.filter(user__email=email).exists():
                        errors.append(f"Row {row_num}: Patient with email {email} already exists")
                        failed += 1
                        continue
                    
                    # Create patient user account
                    from django.contrib.auth.models import User
                    user = User.objects.create_user(
                        username=email.split('@')[0] + str(datetime.now().timestamp()),
                        email=email,
                        first_name=first_name,
                        last_name=last_name
                    )
                    
                    # Create patient record
                    patient = Patient.objects.create(
                        user=user,
                        phone=phone,
                        date_of_birth=date_of_birth if date_of_birth else None,
                        gender=gender if gender in ['M', 'F', 'O'] else 'O'
                    )
                    
                    successful += 1
                
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
                    failed += 1
        
        # Update bulk operation record
        bulk_op.total_records = successful + failed
        bulk_op.successful_records = successful
        bulk_op.failed_records = failed
        bulk_op.status = 'completed' if failed == 0 else 'completed'
        bulk_op.completed_at = timezone.now()
        
        if errors:
            bulk_op.error_message = '\n'.join(errors[:20])  # Store first 20 errors
        
        bulk_op.save()
        
        messages.success(
            request,
            f'Import completed: {successful} patients created, {failed} failed'
        )
    
    except Exception as e:
        bulk_op.status = 'failed'
        bulk_op.error_message = str(e)
        bulk_op.completed_at = timezone.now()
        bulk_op.save()
        messages.error(request, f'Import failed: {str(e)}')
    
    return redirect('bulk_operations_list')


@login_required
@require_http_methods(["GET", "POST"])
def bulk_assign_patients(request):
    """Bulk assign patients to beds"""
    if request.method == 'POST':
        form = BulkPatientAssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            return handle_bulk_assignment(
                request,
                form.cleaned_data['csv_file'],
                form.cleaned_data.get('send_notifications', False)
            )
    else:
        form = BulkPatientAssignmentForm()
    
    context = {'form': form}
    return render(request, 'hospital_wards/bulk_assign_patients.html', context)


def handle_bulk_assignment(request, csv_file, send_notifications):
    """Process bulk patient assignment CSV"""
    bulk_op = BulkOperation.objects.create(
        operation_type='bulk_assignment',
        status='processing',
        initiated_by=request.user,
        total_records=0
    )
    
    try:
        decoded = csv_file.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(decoded))
        
        successful = 0
        failed = 0
        errors = []
        
        with transaction.atomic():
            for row_num, row in enumerate(reader, start=2):
                try:
                    patient_id = int(row.get('patient_id', 0))
                    bed_id = int(row.get('bed_id', 0))
                    reason = row.get('reason', '').strip()
                    chief_complaint = row.get('chief_complaint', '').strip()
                    
                    if not all([patient_id, bed_id, reason]):
                        errors.append(f"Row {row_num}: Missing required fields")
                        failed += 1
                        continue
                    
                    # Get patient and bed
                    patient = Patient.objects.get(id=patient_id)
                    bed = WardBed.objects.get(id=bed_id, status='available')
                    
                    # Create admission
                    admission = PatientAdmission.objects.create(
                        patient=patient,
                        bed=bed,
                        reason=reason,
                        chief_complaint=chief_complaint
                    )
                    
                    # Update bed status
                    bed.status = 'occupied'
                    bed.current_patient = patient
                    bed.save()
                    
                    successful += 1
                
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
                    failed += 1
        
        bulk_op.total_records = successful + failed
        bulk_op.successful_records = successful
        bulk_op.failed_records = failed
        bulk_op.status = 'completed'
        bulk_op.completed_at = timezone.now()
        
        if errors:
            bulk_op.error_message = '\n'.join(errors[:20])
        
        bulk_op.save()
        
        messages.success(
            request,
            f'Bulk assignment completed: {successful} patients assigned, {failed} failed'
        )
    
    except Exception as e:
        bulk_op.status = 'failed'
        bulk_op.error_message = str(e)
        bulk_op.completed_at = timezone.now()
        bulk_op.save()
        messages.error(request, f'Bulk assignment failed: {str(e)}')
    
    return redirect('bulk_operations_list')


@login_required
@require_http_methods(["GET", "POST"])
def bulk_discharge(request):
    """Bulk discharge multiple patients"""
    if request.method == 'POST':
        form = BulkDischargeForm(request.POST)
        if form.is_valid():
            return handle_bulk_discharge(
                request,
                form.cleaned_data['admissions'],
                form.cleaned_data.get('discharge_notes', ''),
                form.cleaned_data.get('send_notifications', False)
            )
    else:
        form = BulkDischargeForm()
    
    context = {'form': form}
    return render(request, 'hospital_wards/bulk_discharge.html', context)


def handle_bulk_discharge(request, admissions, discharge_notes, send_notifications):
    """Process bulk discharge"""
    bulk_op = BulkOperation.objects.create(
        operation_type='bulk_discharge',
        status='processing',
        initiated_by=request.user,
        total_records=len(admissions)
    )
    
    try:
        successful = 0
        failed = 0
        
        with transaction.atomic():
            for admission in admissions:
                try:
                    # Create discharge record
                    discharge = PatientDischarge.objects.create(
                        admission=admission,
                        discharge_notes=discharge_notes
                    )
                    
                    # Release bed
                    bed = admission.bed
                    bed.status = 'available'
                    bed.current_patient = None
                    bed.save()
                    
                    # Mark admission as inactive
                    admission.is_active = False
                    admission.save()
                    
                    successful += 1
                
                except Exception as e:
                    failed += 1
        
        bulk_op.successful_records = successful
        bulk_op.failed_records = failed
        bulk_op.status = 'completed'
        bulk_op.completed_at = timezone.now()
        bulk_op.save()
        
        messages.success(
            request,
            f'Bulk discharge completed: {successful} patients discharged, {failed} failed'
        )
    
    except Exception as e:
        bulk_op.status = 'failed'
        bulk_op.error_message = str(e)
        bulk_op.completed_at = timezone.now()
        bulk_op.save()
        messages.error(request, f'Bulk discharge failed: {str(e)}')
    
    return redirect('bulk_operations_list')


@login_required
@require_http_methods(["GET"])
def export_patients_csv(request):
    """Export patient list to CSV"""
    bulk_op = BulkOperation.objects.create(
        operation_type='export_patients',
        status='processing',
        initiated_by=request.user
    )
    
    try:
        # Get all patients with current admissions
        admissions = PatientAdmission.objects.filter(is_active=True).select_related(
            'patient__user', 'bed__ward'
        )
        
        # Create CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="patients_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Patient ID', 'Name', 'Email', 'Phone', 'Bed', 'Ward', 'Admission Date', 'Reason'])
        
        for admission in admissions:
            writer.writerow([
                admission.patient.id,
                admission.patient.user.get_full_name(),
                admission.patient.user.email,
                admission.patient.phone,
                admission.bed.bed_number,
                admission.bed.ward.name,
                admission.admission_date.strftime('%Y-%m-%d %H:%M'),
                admission.reason,
            ])
        
        bulk_op.total_records = admissions.count()
        bulk_op.successful_records = admissions.count()
        bulk_op.status = 'completed'
        bulk_op.completed_at = timezone.now()
        bulk_op.save()
        
        return response
    
    except Exception as e:
        bulk_op.status = 'failed'
        bulk_op.error_message = str(e)
        bulk_op.completed_at = timezone.now()
        bulk_op.save()
        messages.error(request, f'Export failed: {str(e)}')
        return redirect('bulk_operations_list')


@login_required
@require_http_methods(["GET", "POST"])
def export_report(request):
    """Generate and export hospital reports"""
    if request.method == 'POST':
        form = ExportReportForm(request.POST)
        if form.is_valid():
            return handle_report_export(request, form.cleaned_data)
    else:
        form = ExportReportForm()
    
    context = {'form': form}
    return render(request, 'hospital_wards/export_report.html', context)


def handle_report_export(request, data):
    """Process report export"""
    report_type = data.get('report_type')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    ward = data.get('ward')
    
    bulk_op = BulkOperation.objects.create(
        operation_type='export_report',
        status='processing',
        initiated_by=request.user
    )
    
    try:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{report_type}_report.csv"'
        writer = csv.writer(response)
        
        if report_type == 'occupancy':
            return export_occupancy_report(writer, ward, bulk_op)
        elif report_type == 'patient_list':
            return export_patient_list_report(writer, start_date, end_date, ward, bulk_op)
        elif report_type == 'admission_discharge':
            return export_admission_discharge_report(writer, start_date, end_date, ward, bulk_op)
        elif report_type == 'bed_utilization':
            return export_bed_utilization_report(writer, start_date, end_date, ward, bulk_op)
    
    except Exception as e:
        bulk_op.status = 'failed'
        bulk_op.error_message = str(e)
        bulk_op.completed_at = timezone.now()
        bulk_op.save()
        messages.error(request, f'Report export failed: {str(e)}')
        return redirect('bulk_operations_list')


def export_occupancy_report(writer, ward_filter, bulk_op):
    """Export occupancy report"""
    wards = Ward.objects.filter(is_active=True)
    if ward_filter:
        wards = wards.filter(id=ward_filter.id)
    
    writer.writerow(['Ward', 'Total Beds', 'Occupied', 'Available', 'Maintenance', 'Occupancy %'])
    
    total_occupied = 0
    total_beds = 0
    
    for ward in wards:
        total = ward.beds.count()
        occupied = ward.beds.filter(status='occupied').count()
        available = ward.beds.filter(status='available').count()
        maintenance = ward.beds.filter(status='maintenance').count()
        occupancy_pct = (occupied / total * 100) if total > 0 else 0
        
        writer.writerow([
            ward.name,
            total,
            occupied,
            available,
            maintenance,
            f'{occupancy_pct:.1f}%'
        ])
        
        total_occupied += occupied
        total_beds += total
    
    writer.writerow([])
    writer.writerow(['TOTAL', total_beds, total_occupied, '', '', f'{(total_occupied/total_beds*100):.1f}%' if total_beds > 0 else '0%'])
    
    bulk_op.total_records = wards.count()
    bulk_op.successful_records = wards.count()
    bulk_op.status = 'completed'
    bulk_op.completed_at = timezone.now()
    bulk_op.save()
    
    # Return response will be handled by caller
    return None  # Placeholder


def export_patient_list_report(writer, start_date, end_date, ward_filter, bulk_op):
    """Export patient list report"""
    admissions = PatientAdmission.objects.filter(is_active=True).select_related(
        'patient__user', 'bed__ward'
    )
    
    if ward_filter:
        admissions = admissions.filter(bed__ward=ward_filter)
    
    if start_date:
        admissions = admissions.filter(admission_date__gte=start_date)
    if end_date:
        admissions = admissions.filter(admission_date__lte=end_date)
    
    writer.writerow(['Patient ID', 'Name', 'Email', 'Phone', 'Bed', 'Ward', 'Admission Date', 'Days Admitted', 'Reason'])
    
    for admission in admissions:
        days = (timezone.now().date() - admission.admission_date.date()).days
        writer.writerow([
            admission.patient.id,
            admission.patient.user.get_full_name(),
            admission.patient.user.email,
            admission.patient.phone,
            admission.bed.bed_number,
            admission.bed.ward.name,
            admission.admission_date.strftime('%Y-%m-%d'),
            days,
            admission.reason,
        ])
    
    bulk_op.total_records = admissions.count()
    bulk_op.successful_records = admissions.count()
    bulk_op.status = 'completed'
    bulk_op.completed_at = timezone.now()
    bulk_op.save()
    
    return None


def export_admission_discharge_report(writer, start_date, end_date, ward_filter, bulk_op):
    """Export admission/discharge summary"""
    discharges = PatientDischarge.objects.select_related(
        'admission__patient__user', 'admission__bed__ward'
    )
    
    if ward_filter:
        discharges = discharges.filter(admission__bed__ward=ward_filter)
    
    if start_date:
        discharges = discharges.filter(created_at__gte=start_date)
    if end_date:
        discharges = discharges.filter(created_at__lte=end_date)
    
    writer.writerow(['Date', 'Patient', 'Ward', 'Admission Date', 'Discharge Date', 'Days Admitted', 'Status'])
    
    for discharge in discharges:
        days = (discharge.created_at.date() - discharge.admission.admission_date.date()).days
        writer.writerow([
            discharge.created_at.strftime('%Y-%m-%d'),
            discharge.admission.patient.user.get_full_name(),
            discharge.admission.bed.ward.name,
            discharge.admission.admission_date.strftime('%Y-%m-%d'),
            discharge.created_at.strftime('%Y-%m-%d'),
            days,
            discharge.discharge_status,
        ])
    
    bulk_op.total_records = discharges.count()
    bulk_op.successful_records = discharges.count()
    bulk_op.status = 'completed'
    bulk_op.completed_at = timezone.now()
    bulk_op.save()
    
    return None


def export_bed_utilization_report(writer, start_date, end_date, ward_filter, bulk_op):
    """Export bed utilization report"""
    beds = WardBed.objects.filter(is_active=True).select_related('ward')
    
    if ward_filter:
        beds = beds.filter(ward=ward_filter)
    
    writer.writerow(['Ward', 'Bed Number', 'Status', 'Current Patient', 'Assigned Since', 'Days Occupied'])
    
    for bed in beds:
        days = ''
        if bed.current_patient and bed.status == 'occupied':
            admission = PatientAdmission.objects.filter(
                bed=bed, is_active=True
            ).first()
            if admission:
                days = (timezone.now().date() - admission.admission_date.date()).days
        
        writer.writerow([
            bed.ward.name,
            bed.bed_number,
            bed.get_status_display(),
            bed.current_patient.user.get_full_name() if bed.current_patient else 'N/A',
            '',
            days if days != '' else '0',
        ])
    
    bulk_op.total_records = beds.count()
    bulk_op.successful_records = beds.count()
    bulk_op.status = 'completed'
    bulk_op.completed_at = timezone.now()
    bulk_op.save()
    
    return None


@login_required
def bulk_operations_list(request):
    """List all bulk operations"""
    operations = BulkOperation.objects.all().select_related('initiated_by')
    
    # Filter form
    form = FilterBulkOperationForm(request.GET)
    if form.is_valid():
        if form.cleaned_data.get('operation_type'):
            operations = operations.filter(operation_type=form.cleaned_data['operation_type'])
        if form.cleaned_data.get('status'):
            operations = operations.filter(status=form.cleaned_data['status'])
        if form.cleaned_data.get('date_from'):
            operations = operations.filter(created_at__gte=form.cleaned_data['date_from'])
        if form.cleaned_data.get('date_to'):
            operations = operations.filter(created_at__lte=form.cleaned_data['date_to'])
    
    context = {
        'operations': operations,
        'form': form,
    }
    return render(request, 'hospital_wards/bulk_operations_list.html', context)
