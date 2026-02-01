from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from nutritionist_dashboard.models import NutritionistProfile, ClientAssignment
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Management command to seed nutritionist data for testing/demo purposes
    Usage: python manage.py seed_nutritionists [--clear]
    """
    help = 'Seeds the database with sample nutritionist data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing nutritionists and their data before seeding'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing nutritionists...'))
            NutritionistProfile.objects.all().delete()
            # Find and delete all nutritionist users
            nutritionist_users = User.objects.filter(
                username__startswith='nutritionist_demo_'
            )
            nutritionist_users.delete()

        nutritionists_data = [
            {
                'username': 'nutritionist_demo_1',
                'email': 'marie.durand@dusangire.rw',
                'first_name': 'Marie',
                'last_name': 'Durand',
                'bio': 'Certified nutritionist with 8 years of experience in sports nutrition and weight management.',
                'specialization': 'Sports Nutrition & Weight Management',
                'license_number': 'RW-NUT-2024-001',
                'phone_number': '+250788123456',
                'max_clients': 50,
            },
            {
                'username': 'nutritionist_demo_2',
                'email': 'jean.mutoni@dusangire.rw',
                'first_name': 'Jean',
                'last_name': 'Mutoni',
                'bio': 'Specialist in diabetes management and chronic disease nutrition. Passionate about community health.',
                'specialization': 'Diabetes Care & Clinical Nutrition',
                'license_number': 'RW-NUT-2024-002',
                'phone_number': '+250789234567',
                'max_clients': 40,
            },
            {
                'username': 'nutritionist_demo_3',
                'email': 'alice.rukundo@dusangire.rw',
                'first_name': 'Alice',
                'last_name': 'Rukundo',
                'bio': 'Pediatric and family nutrition expert. Dedicated to promoting healthy eating habits in children.',
                'specialization': 'Pediatric Nutrition & Family Health',
                'license_number': 'RW-NUT-2024-003',
                'phone_number': '+250790345678',
                'max_clients': 35,
            },
            {
                'username': 'nutritionist_demo_4',
                'email': 'robert.uwizeye@dusangire.rw',
                'first_name': 'Robert',
                'last_name': 'Uwizeye',
                'bio': 'Focuses on plant-based nutrition and sustainable dietary practices for optimal health.',
                'specialization': 'Vegan & Plant-Based Nutrition',
                'license_number': 'RW-NUT-2024-004',
                'phone_number': '+250791456789',
                'max_clients': 45,
            },
            {
                'username': 'nutritionist_demo_5',
                'email': 'grace.habimana@dusangire.rw',
                'first_name': 'Grace',
                'last_name': 'Habimana',
                'bio': 'Experienced in food allergy management and digestive health. Tailors nutrition plans to individual needs.',
                'specialization': 'Allergy Management & Digestive Health',
                'license_number': 'RW-NUT-2024-005',
                'phone_number': '+250792567890',
                'max_clients': 40,
            },
        ]

        created_count = 0
        for nut_data in nutritionists_data:
            try:
                # Extract profile-specific data
                profile_data = {
                    'bio': nut_data.pop('bio'),
                    'specialization': nut_data.pop('specialization'),
                    'license_number': nut_data.pop('license_number'),
                    'phone_number': nut_data.pop('phone_number'),
                    'max_clients': nut_data.pop('max_clients'),
                }

                # Create user
                user, created = User.objects.get_or_create(
                    username=nut_data['username'],
                    defaults={
                        'email': nut_data['email'],
                        'first_name': nut_data['first_name'],
                        'last_name': nut_data['last_name'],
                    }
                )

                # Create profile
                profile, profile_created = NutritionistProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        **profile_data,
                        'status': 'active',
                    }
                )

                if profile_created or created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Created nutritionist: {user.get_full_name()} ({user.email})'
                        )
                    )
                    logger.info(f'Created nutritionist profile for user {user.id}')
                else:
                    self.stdout.write(
                        f'• Nutritionist already exists: {user.get_full_name()}'
                    )

            except Exception as e:
                error_msg = f"Error creating nutritionist {nut_data.get('username')}: {str(e)}"
                self.stdout.write(self.style.ERROR(f'✗ {error_msg}'))
                logger.error(error_msg)
                raise CommandError(error_msg)

        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Seeding completed! {created_count} nutritionist(s) created/verified.'
            )
        )
        self.stdout.write(
            self.style.WARNING(
                '\nNext steps:\n'
                '1. Verify nutritionists in admin: http://localhost:8000/admin/nutritionist_dashboard/nutritionistprofile/\n'
                '2. Create client assignments as needed\n'
                '3. Test the nutritionist dashboard\n'
            )
        )
