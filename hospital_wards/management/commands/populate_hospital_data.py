"""
Django management command to populate the hospital database with sample data
Creates realistic test data for development and testing
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from accounts.models import Profile
from hospital_wards.models import (
    Ward, WardBed, WardDeliveryRoute, PatientEducationContent,
    PatientEducationCategory, MealNutritionInfo, CaregiverNotification,
    PatientAdmission, PatientDischarge, PatientTransfer, BedMaintenanceSchedule
)
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Populate hospital database with sample data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before populating',
        )
        parser.add_argument(
            '--patients',
            type=int,
            default=20,
            help='Number of test patients to create (default: 20)',
        )
        parser.add_argument(
            '--wards',
            type=int,
            default=4,
            help='Number of wards to create (default: 4)',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('⚠️  Clearing existing data...'))
            self.clear_data()

        self.stdout.write(self.style.SUCCESS('🏥 Creating hospital data...'))

        num_wards = options['wards']
        num_patients = options['patients']

        # Create wards
        wards = self.create_wards(num_wards)
        self.stdout.write(self.style.SUCCESS(f'✅ Created {len(wards)} wards'))

        # Create beds
        beds = self.create_beds(wards)
        self.stdout.write(self.style.SUCCESS(f'✅ Created {len(beds)} beds'))

        # Create staff
        staff = self.create_staff()
        self.stdout.write(self.style.SUCCESS(f'✅ Created {len(staff)} staff members'))

        # Create patients and assign to beds
        patients = self.create_patients(num_patients)
        self.stdout.write(self.style.SUCCESS(f'✅ Created {num_patients} patients'))

        # Assign patients to beds
        assigned = self.assign_patients_to_beds(patients, beds)
        self.stdout.write(self.style.SUCCESS(f'✅ Assigned {assigned} patients to beds'))

        # Create education content
        education = self.create_education_content()
        self.stdout.write(self.style.SUCCESS(f'✅ Created {education} education materials'))

        self.stdout.write(self.style.SUCCESS('✨ Sample data generation complete!'))
        self.print_summary(wards, beds, patients, staff)

    def clear_data(self):
        """Clear existing data"""
        models = [
            CaregiverNotification, PatientEducationContent, PatientEducationCategory,
            WardDeliveryRoute, WardBed, Ward, Profile, User,
            PatientAdmission, PatientDischarge, PatientTransfer, BedMaintenanceSchedule,
            MealNutritionInfo
        ]
        for model in models:
            try:
                count = model.objects.count()
                model.objects.all().delete()
                if count > 0:
                    self.stdout.write(f'  Deleted {count} {model.__name__} records')
            except Exception as e:
                self.stdout.write(f'  Error deleting {model.__name__}: {e}')

    def create_wards(self, count):
        """Create ward records"""
        ward_data = [
            {'name': 'General Ward A', 'location': 'Building 1, 1st Floor', 'capacity': 20},
            {'name': 'General Ward B', 'location': 'Building 1, 2nd Floor', 'capacity': 20},
            {'name': 'ICU Ward', 'location': 'Building 2, 3rd Floor', 'capacity': 10},
            {'name': 'Pediatric Ward', 'location': 'Building 2, 1st Floor', 'capacity': 15},
            {'name': 'Maternity Ward', 'location': 'Building 3, 2nd Floor', 'capacity': 12},
        ]

        wards = []
        for i in range(min(count, len(ward_data))):
            data = ward_data[i]
            ward, created = Ward.objects.get_or_create(
                name=data['name'],
                defaults={
                    'location': data['location'],
                    'capacity': data['capacity'],
                    'is_active': True,
                }
            )
            wards.append(ward)

        return wards

    def create_beds(self, wards):
        """Create bed records"""
        beds = []
        bed_status = ['available', 'occupied', 'maintenance', 'reserved']

        for ward in wards:
            for bed_num in range(1, ward.capacity + 1):
                bed_number = f"{ward.name.split()[0]}-{bed_num:03d}"
                status = random.choice(bed_status)

                bed, created = WardBed.objects.get_or_create(
                    ward=ward,
                    bed_number=bed_number,
                    defaults={
                        'status': status,
                        'notes': f'Bed {bed_num} in {ward.name}' if status == 'maintenance' else '',
                        'is_active': True,
                    }
                )
                beds.append(bed)

        return beds

    def create_staff(self):
        """Create staff members with different roles"""
        staff_data = [
            ('doctor1', 'doctor@chub.rw', 'Dr.', 'James', 'Smith', 'medical_staff'),
            ('doctor2', 'dr.jane@chub.rw', 'Dr.', 'Jane', 'Kariuki', 'medical_staff'),
            ('nurse1', 'nurse.john@chub.rw', 'Nurse', 'John', 'Kipchoge', 'medical_staff'),
            ('chef1', 'chef.peter@chub.rw', 'Chef', 'Peter', 'Mwangi', 'chef'),
            ('chef2', 'chef.mary@chub.rw', 'Chef', 'Mary', 'Okonkwo', 'chef'),
            ('kitchen1', 'kitchen.samuel@chub.rw', 'Staff', 'Samuel', 'Mutua', 'kitchen_staff'),
            ('kitchen2', 'kitchen.rose@chub.rw', 'Staff', 'Rose', 'Ngugi', 'kitchen_staff'),
            ('delivery1', 'driver.paul@chub.rw', 'Driver', 'Paul', 'Ochieng', 'delivery_person'),
            ('support1', 'support.david@chub.rw', 'Technician', 'David', 'Kiplagat', 'support_staff'),
            ('manager1', 'manager.alice@chub.rw', 'Manager', 'Alice', 'Amina', 'hospital_manager'),
            ('nutritionist1', 'nutrition.ruth@chub.rw', 'Nutritionist', 'Ruth', 'Mwende', 'nutritionist'),
            ('admin1', 'admin@chub.rw', 'Admin', 'Admin', 'User', 'admin'),
        ]

        staff = []
        for username, email, prefix, first_name, last_name, role in staff_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'is_staff': True if role in ['admin', 'medical_staff'] else False,
                    'is_active': True,
                }
            )
            if created:
                user.set_password('testpass123')
                user.save()

            # Create or update profile
            Profile.objects.update_or_create(
                user=user,
                defaults={
                    'phone': f'+250788{random.randint(100000, 999999)}',
                    'role': role,
                    'status': 'active',
                    'is_active': True,
                }
            )
            staff.append(user)

        return staff

    def create_patients(self, count):
        """Create patient users"""
        patient_names = [
            ('John', 'Musyoka'), ('Jane', 'Kariuki'), ('Peter', 'Kipchoge'),
            ('Mary', 'Okonkwo'), ('James', 'Mwangi'), ('Alice', 'Amina'),
            ('David', 'Kiplagat'), ('Ruth', 'Mwende'), ('Samuel', 'Mutua'),
            ('Rose', 'Ngugi'), ('Paul', 'Ochieng'), ('Eve', 'Kidogo'),
            ('Mark', 'Kabuto'), ('Sarah', 'Okumu'), ('Thomas', 'Kiplagat'),
            ('Catherine', 'Nyambura'), ('Michael', 'Kipkemboi'), ('Diana', 'Kerubo'),
            ('Daniel', 'Kipyegon'), ('Elizabeth', 'Kiplagat'),
        ]

        patients = []
        for i in range(count):
            first, last = patient_names[i % len(patient_names)]
            username = f'patient{i+1}'
            email = f'patient{i+1}@chub.rw'

            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': f'{first}{i+1 if i >= len(patient_names) else ""}',
                    'last_name': last,
                    'is_active': True,
                }
            )
            if created:
                user.set_password('testpass123')
                user.save()

            # Create or update profile
            Profile.objects.update_or_create(
                user=user,
                defaults={
                    'phone': f'+250788{random.randint(100000, 999999)}',
                    'role': 'patient',
                    'status': 'active',
                    'is_active': True,
                }
            )
            patients.append(user)

        return patients

    def assign_patients_to_beds(self, patients, beds):
        """Assign patients to available beds"""
        assigned = 0
        available_beds = [b for b in beds if b.status == 'available']

        # Assign random patients to random available beds
        for patient in random.sample(patients, min(len(patients), len(available_beds))):
            bed = random.choice(available_beds)
            try:
                bed.assign_patient(patient)
                assigned += 1
                available_beds.remove(bed)
            except ValueError:
                continue

        return assigned

    def create_education_content(self):
        """Create patient education materials"""
        categories_data = [
            'Post-Operative Care',
            'Diabetes Management',
            'Heart Health',
            'Nutrition & Diet',
            'Medication Information',
            'Physical Therapy',
            'Mental Health',
        ]

        education_data = [
            ('Wound Care Instructions', 'Post-Operative Care', 'Learn how to properly care for your surgical wound'),
            ('Managing Diabetes Daily', 'Diabetes Management', 'Daily routine for managing blood sugar'),
            ('Heart-Healthy Eating', 'Heart Health', 'Foods that support cardiovascular health'),
            ('Medication Side Effects', 'Medication Information', 'Understanding common side effects'),
            ('Physical Therapy Exercises', 'Physical Therapy', 'Exercises to aid recovery'),
            ('Sleep & Recovery', 'Mental Health', 'Importance of sleep during recovery'),
            ('Balanced Nutrition', 'Nutrition & Diet', 'Creating balanced meals'),
        ]

        created = 0

        # Create categories
        for cat_name in categories_data:
            category, cat_created = PatientEducationCategory.objects.get_or_create(
                name=cat_name,
                defaults={'description': f'{cat_name} educational materials'}
            )

        # Create content
        for title, category_name, description in education_data:
            category = PatientEducationCategory.objects.get(name=category_name)
            content, is_created = PatientEducationContent.objects.get_or_create(
                title=title,
                defaults={
                    'category': category,
                    'description': description,
                    'content': description * 5,  # Repeat for length
                    'content_type': 'health_tip',
                    'target_role': 'both',
                    'applicable_diet_types': 'general',
                }
            )
            if is_created:
                created += 1

        return created

    def create_nutrition_info(self):
        """Create nutrition information"""
        nutrition_data = [
            {
                'name': 'Standard Diet',
                'description': 'Balanced nutrition for general recovery',
                'allergies': '',
                'restrictions': '',
                'is_active': True,
            },
            {
                'name': 'Diabetic Diet',
                'description': 'Low sugar, high fiber diet for diabetics',
                'allergies': '',
                'restrictions': 'High sugar foods',
                'is_active': True,
            },
            {
                'name': 'Low Sodium Diet',
                'description': 'Reduced salt intake for heart health',
                'allergies': '',
                'restrictions': 'Salty foods, processed meats',
                'is_active': True,
            },
            {
                'name': 'Soft Foods Diet',
                'description': 'Easy to swallow and digest',
                'allergies': '',
                'restrictions': 'Hard, crunchy foods',
                'is_active': True,
            },
        ]

        created = 0
        for data in nutrition_data:
            nutrition, is_created = MealNutritionInfo.objects.get_or_create(
                name=data['name'],
                defaults={
                    'description': data['description'],
                    'allergies': data['allergies'],
                    'restrictions': data['restrictions'],
                    'is_active': data['is_active'],
                }
            )
            if is_created:
                created += 1

        return created

    def create_notifications(self, patients):
        """Create sample notifications"""
        notification_messages = [
            'Your medication is due',
            'Time for physical therapy',
            'Check your meal schedule',
            'Doctor will visit soon',
            'Please complete your education module',
        ]

        created = 0
        for patient in random.sample(patients, min(5, len(patients))):
            for _ in range(random.randint(1, 3)):
                notification, is_created = CaregiverNotification.objects.get_or_create(
                    patient=patient,
                    title=random.choice(notification_messages),
                    defaults={
                        'message': 'This is an important notification for patient care',
                        'notification_type': random.choice(['alert', 'reminder', 'info']),
                        'is_read': random.choice([True, False]),
                        'sent_at': timezone.now() - timedelta(hours=random.randint(0, 24)),
                    }
                )
                if is_created:
                    created += 1

        return created

    def create_delivery_routes(self, wards):
        """Create delivery routes for wards"""
        created = 0
        for ward in wards:
            route, is_created = WardDeliveryRoute.objects.get_or_create(
                ward=ward,
                route_name=f'{ward.name} - Daily Route',
                defaults={
                    'start_time': timezone.now().replace(hour=8, minute=0),
                    'end_time': timezone.now().replace(hour=17, minute=0),
                    'frequency': 'daily',
                    'is_active': True,
                }
            )
            if is_created:
                created += 1

        return created

    def print_summary(self, wards, beds, patients, staff):
        """Print summary of created data"""
        occupied_beds = sum(1 for b in beds if b.status == 'occupied')
        available_beds = sum(1 for b in beds if b.status == 'available')

        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('📊 HOSPITAL DATA SUMMARY'))
        self.stdout.write('='*60)
        self.stdout.write(f'Wards Created:        {len(wards)}')
        self.stdout.write(f'Total Beds:           {len(beds)}')
        self.stdout.write(f'  └─ Occupied:        {occupied_beds}')
        self.stdout.write(f'  └─ Available:       {available_beds}')
        self.stdout.write(f'Patients Created:     {len(patients)}')
        self.stdout.write(f'Staff Members:        {len(staff)}')
        self.stdout.write('='*60)
        self.stdout.write(self.style.WARNING('Test Credentials (all use password: testpass123)'))
        self.stdout.write('  Doctor:       doctor1')
        self.stdout.write('  Chef:         chef1')
        self.stdout.write('  Manager:      manager1')
        self.stdout.write('  Patient:      patient1')
        self.stdout.write('  Admin:        admin1')
        self.stdout.write('='*60 + '\n')
