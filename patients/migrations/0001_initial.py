# Generated migration for patients app

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
from decimal import Decimal
import django.core.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('menu', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='HealthProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_of_birth', models.DateField()),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], max_length=1)),
                ('blood_type', models.CharField(blank=True, choices=[('O+', 'O+'), ('O-', 'O-'), ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-')], max_length=3)),
                ('phone_number', models.CharField(blank=True, max_length=20)),
                ('emergency_contact', models.CharField(blank=True, max_length=100)),
                ('admission_date', models.DateField()),
                ('admission_type', models.CharField(choices=[('INPATIENT', 'Inpatient'), ('OUTPATIENT', 'Outpatient'), ('EMERGENCY', 'Emergency')], max_length=10)),
                ('hospital_bed_number', models.CharField(blank=True, max_length=50)),
                ('ward_name', models.CharField(blank=True, max_length=100)),
                ('doctor_name', models.CharField(blank=True, max_length=100)),
                ('primary_diagnosis', models.CharField(max_length=255)),
                ('secondary_diagnosis', models.TextField(blank=True)),
                ('medical_history', models.TextField(blank=True, help_text='Chronic conditions, previous surgeries, etc.')),
                ('current_medications', models.TextField(blank=True)),
                ('allergies', models.TextField(blank=True, help_text='Food allergies and intolerances (comma-separated)')),
                ('dietary_restrictions', models.TextField(blank=True, help_text='Religious, cultural, or preference-based restrictions')),
                ('height_cm', models.DecimalField(decimal_places=2, help_text='Height in centimeters', max_digits=5, validators=[django.core.validators.MinValueValidator(Decimal('50'))])),
                ('weight_kg', models.DecimalField(decimal_places=2, help_text='Current weight in kilograms', max_digits=6, validators=[django.core.validators.MinValueValidator(Decimal('10'))])),
                ('notes', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='patient_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Patient Health Profile',
                'verbose_name_plural': 'Patient Health Profiles',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='MedicalPrescription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prescribed_by', models.CharField(max_length=100)),
                ('prescribed_date', models.DateField(auto_now_add=True)),
                ('meal_type', models.CharField(choices=[('DIABETIC', 'Diabetic Meal'), ('LOW_SODIUM', 'Low Sodium'), ('HIGH_PROTEIN', 'High Protein'), ('POST_SURGERY', 'Post-Surgery'), ('RENAL', 'Renal Diet'), ('CARDIAC', 'Cardiac Diet'), ('LIQUID', 'Liquid Diet'), ('SOFT', 'Soft Diet'), ('REGULAR', 'Regular Diet')], max_length=20)),
                ('calories_per_day', models.IntegerField(help_text='Target daily calories', validators=[django.core.validators.MinValueValidator(500), django.core.validators.MaxValueValidator(5000)])),
                ('protein_grams', models.IntegerField(blank=True, help_text='Daily protein target in grams', null=True)),
                ('carbs_grams', models.IntegerField(blank=True, help_text='Daily carbohydrates target in grams', null=True)),
                ('fat_grams', models.IntegerField(blank=True, help_text='Daily fat target in grams', null=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('foods_to_avoid', models.TextField(blank=True)),
                ('additional_instructions', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prescriptions', to='patients.healthprofile')),
            ],
            options={
                'verbose_name': 'Medical Prescription',
                'verbose_name_plural': 'Medical Prescriptions',
                'ordering': ['-start_date'],
            },
        ),
        migrations.CreateModel(
            name='RecoveryMetrics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('measurement_date', models.DateField(auto_now_add=True)),
                ('days_in_hospital', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('infection_status', models.CharField(choices=[('NO_INFECTION', 'No Infection'), ('SUSPECTED', 'Suspected Infection'), ('CONFIRMED', 'Confirmed Infection'), ('TREATED', 'Treated & Resolved')], default='NO_INFECTION', max_length=20)),
                ('infection_date', models.DateField(blank=True, null=True)),
                ('antibiotic_treatment', models.TextField(blank=True)),
                ('has_surgical_wound', models.BooleanField(default=False)),
                ('wound_healing_status', models.CharField(blank=True, choices=[('EXCELLENT', 'Excellent'), ('GOOD', 'Good'), ('FAIR', 'Fair'), ('POOR', 'Poor')], max_length=20, null=True)),
                ('wound_notes', models.TextField(blank=True)),
                ('temperature_celsius', models.DecimalField(blank=True, decimal_places=1, help_text='Body temperature in Celsius', max_digits=3, null=True)),
                ('blood_pressure', models.CharField(blank=True, help_text='e.g., 120/80', max_length=10)),
                ('immune_markers', models.TextField(blank=True, help_text='WBC count, CRP levels, other immune markers')),
                ('mobility_level', models.CharField(blank=True, help_text='e.g., Bed-ridden, Limited mobility, Ambulatory', max_length=50)),
                ('general_condition', models.TextField(blank=True, help_text='Overall patient condition and progress')),
                ('expected_discharge_date', models.DateField(blank=True, null=True)),
                ('discharge_date', models.DateField(blank=True, null=True)),
                ('discharge_status', models.CharField(blank=True, help_text='e.g., Recovered, Stable, Referral, etc.', max_length=100)),
                ('assessed_by', models.CharField(blank=True, max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recovery_metrics', to='patients.healthprofile')),
            ],
            options={
                'verbose_name': 'Recovery Metrics',
                'verbose_name_plural': 'Recovery Metrics',
                'ordering': ['-measurement_date'],
            },
        ),
        migrations.CreateModel(
            name='PatientNutritionStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('measurement_date', models.DateField(auto_now_add=True)),
                ('malnutrition_level', models.CharField(choices=[('SEVERE', 'Severe'), ('MODERATE', 'Moderate'), ('MILD', 'Mild'), ('NORMAL', 'Normal')], default='MODERATE', max_length=20)),
                ('weight_kg', models.DecimalField(decimal_places=2, help_text='Weight at time of measurement', max_digits=6, validators=[django.core.validators.MinValueValidator(Decimal('10'))])),
                ('mid_arm_circumference_cm', models.DecimalField(blank=True, decimal_places=1, help_text='Mid-arm circumference in cm', max_digits=4, null=True)),
                ('serum_albumin_level', models.DecimalField(blank=True, decimal_places=1, help_text='Serum albumin level (g/dL)', max_digits=3, null=True)),
                ('meal_intake_percentage', models.IntegerField(help_text='Percentage of prescribed meals consumed', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('observations', models.TextField(blank=True)),
                ('recommendations', models.TextField(blank=True)),
                ('assessed_by', models.CharField(blank=True, max_length=100)),
                ('assessment_method', models.CharField(blank=True, help_text='e.g., Visual inspection, BMI calculation, Nutritionist review', max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='nutrition_status', to='patients.healthprofile')),
            ],
            options={
                'verbose_name': 'Patient Nutrition Status',
                'verbose_name_plural': 'Patient Nutrition Statuses',
                'ordering': ['-measurement_date'],
            },
        ),
        migrations.CreateModel(
            name='PatientMealHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meal_date', models.DateField(auto_now_add=True)),
                ('meal_type', models.CharField(choices=[('BREAKFAST', 'Breakfast'), ('LUNCH', 'Lunch'), ('DINNER', 'Dinner'), ('SNACK', 'Snack')], max_length=20)),
                ('was_prescribed', models.BooleanField(default=True)),
                ('quantity_consumed_percentage', models.IntegerField(default=100, help_text='Percentage of meal consumed', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('patient_feedback', models.TextField(blank=True)),
                ('nutritionist_notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('menu_item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='menu.menuitem')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meal_history', to='patients.healthprofile')),
            ],
            options={
                'verbose_name': 'Patient Meal History',
                'verbose_name_plural': 'Patient Meal Histories',
                'ordering': ['-meal_date'],
            },
        ),
        migrations.CreateModel(
            name='HealthOutcomeStudy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('study_start_date', models.DateField(auto_now_add=True)),
                ('study_end_date', models.DateField(blank=True, null=True)),
                ('pre_service_weight_kg', models.DecimalField(decimal_places=2, help_text='Weight before starting meal service', max_digits=6)),
                ('pre_service_malnutrition_level', models.CharField(choices=[('SEVERE', 'Severe'), ('MODERATE', 'Moderate'), ('MILD', 'Mild'), ('NORMAL', 'Normal')], max_length=20)),
                ('pre_service_infection_status', models.CharField(blank=True, help_text='Initial infection status', max_length=20)),
                ('pre_service_hospital_stay_estimate', models.IntegerField(blank=True, help_text='Estimated days in hospital at start of service', null=True)),
                ('post_service_weight_kg', models.DecimalField(blank=True, decimal_places=2, help_text='Weight after meal service', max_digits=6, null=True)),
                ('post_service_malnutrition_level', models.CharField(blank=True, choices=[('SEVERE', 'Severe'), ('MODERATE', 'Moderate'), ('MILD', 'Mild'), ('NORMAL', 'Normal')], max_length=20, null=True)),
                ('post_service_infection_status', models.CharField(blank=True, help_text='Final infection status', max_length=20)),
                ('actual_hospital_stay_days', models.IntegerField(blank=True, help_text='Actual days spent in hospital', null=True)),
                ('weight_change_kg', models.DecimalField(blank=True, decimal_places=2, help_text='Weight change during service', max_digits=6, null=True)),
                ('malnutrition_improved', models.BooleanField(blank=True, null=True)),
                ('infection_prevented', models.BooleanField(default=True)),
                ('recovered_successfully', models.BooleanField(blank=True, null=True)),
                ('clinical_observations', models.TextField(blank=True)),
                ('researcher_notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outcome_studies', to='patients.healthprofile')),
            ],
            options={
                'verbose_name': 'Health Outcome Study',
                'verbose_name_plural': 'Health Outcome Studies',
                'ordering': ['-study_start_date'],
            },
        ),
        migrations.AddIndex(
            model_name='patientnutritionstatus',
            index=models.Index(fields=['patient', '-measurement_date'], name='patients_pat_patient_idx'),
        ),
        migrations.AddIndex(
            model_name='patientmealhistory',
            index=models.Index(fields=['patient', '-meal_date'], name='patients_pat_patient_meal_idx'),
        ),
        migrations.AddIndex(
            model_name='healthprofile',
            index=models.Index(fields=['user', '-created_at'], name='patients_hea_user_id_idx'),
        ),
        migrations.AddIndex(
            model_name='healthprofile',
            index=models.Index(fields=['admission_date'], name='patients_hea_admissi_idx'),
        ),
        migrations.AddIndex(
            model_name='recoverymetrics',
            index=models.Index(fields=['patient', '-measurement_date'], name='patients_rec_patient_idx'),
        ),
    ]
