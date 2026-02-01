"""
Management command to seed the database with initial data for production launch
Includes: subscription plans, delivery zones, and payment method configurations
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from subscriptions.models import SubscriptionPlan, PlanType
from delivery.models import DeliveryZone
from payments.models import PaymentMethod


class Command(BaseCommand):
    help = 'Seed the database with initial subscription plans, delivery zones, and other launch data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing initial data...'))
            SubscriptionPlan.objects.all().delete()
            DeliveryZone.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Cleared existing data.'))

        # Create Delivery Zones
        self.stdout.write('\nCreating delivery zones...')
        zones_data = [
            {
                'name': 'CHUB Internal (Wards)',
                'description': 'Direct delivery to patients and staff within CHUB hospital wards',
                'delivery_charge': Decimal('0.00'),
                'is_active': True,
            },
            {
                'name': 'CHUB Campus',
                'description': 'Delivery within CHUB hospital grounds, parking, and administrative buildings',
                'delivery_charge': Decimal('500.00'),
                'is_active': True,
            },
            {
                'name': 'Butare Central (0-2km)',
                'description': 'Delivery within the central Butare area near CHUB',
                'delivery_charge': Decimal('1000.00'),
                'is_active': True,
            },
            {
                'name': 'Butare Suburban (2-5km)',
                'description': 'Delivery to suburban areas of Butare, Rwanda',
                'delivery_charge': Decimal('2000.00'),
                'is_active': True,
            },
            {
                'name': 'Outside Butare',
                'description': 'Extended delivery services beyond Butare city limits',
                'delivery_charge': Decimal('3500.00'),
                'is_active': True,
            },
        ]

        zones_created = 0
        for zone_data in zones_data:
            zone, created = DeliveryZone.objects.get_or_create(
                name=zone_data['name'],
                defaults=zone_data
            )
            if created:
                zones_created += 1
                self.stdout.write(self.style.SUCCESS(f'  [OK] Created zone: {zone.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'  [-] Zone already exists: {zone.name}'))

        # Create Subscription Plans
        self.stdout.write('\nCreating subscription plans...')
        plans_data = [
            {
                'name': 'Daily Breakfast Plan',
                'description': 'Get a nutritious breakfast delivered daily. Perfect for patients and staff who want a healthy start to their day.',
                'plan_type': PlanType.DAILY,
                'price': Decimal('3000.00'),
                'meals_per_cycle': 1,
                'duration_days': 30,
                'is_active': True,
                'is_featured': True,
                'is_popular': True,
                'discount_percentage': Decimal('10.00'),
            },
            {
                'name': 'Daily Lunch Plan',
                'description': 'Enjoy a balanced lunch meal every day. Ideal for maintaining consistent nutrition during recovery.',
                'plan_type': PlanType.DAILY,
                'price': Decimal('5000.00'),
                'meals_per_cycle': 1,
                'duration_days': 30,
                'is_active': True,
                'is_featured': True,
                'is_popular': True,
                'discount_percentage': Decimal('10.00'),
            },
            {
                'name': 'Daily Dinner Plan',
                'description': 'Receive a hearty dinner meal daily. Great for evening nutrition and recovery support.',
                'plan_type': PlanType.DAILY,
                'price': Decimal('5000.00'),
                'meals_per_cycle': 1,
                'duration_days': 30,
                'is_active': True,
                'is_featured': False,
                'is_popular': False,
                'discount_percentage': Decimal('10.00'),
            },
            {
                'name': 'Complete Daily Plan',
                'description': 'Get breakfast, lunch, and dinner delivered daily. The most comprehensive nutrition plan for full recovery support.',
                'plan_type': PlanType.DAILY,
                'price': Decimal('12000.00'),
                'meals_per_cycle': 3,
                'duration_days': 30,
                'is_active': True,
                'is_featured': True,
                'is_popular': True,
                'discount_percentage': Decimal('15.00'),
            },
            {
                'name': 'Weekly Meal Plan',
                'description': 'Get 7 meals delivered throughout the week. Flexible meal selection with weekly billing.',
                'plan_type': PlanType.WEEKLY,
                'price': Decimal('30000.00'),
                'meals_per_cycle': 7,
                'duration_days': 28,
                'is_active': True,
                'is_featured': True,
                'is_popular': False,
                'discount_percentage': Decimal('12.00'),
            },
            {
                'name': 'Monthly Meal Plan',
                'description': 'Get 30 meals delivered throughout the month. Best value for long-term nutrition support.',
                'plan_type': PlanType.MONTHLY,
                'price': Decimal('120000.00'),
                'meals_per_cycle': 30,
                'duration_days': 30,
                'is_active': True,
                'is_featured': True,
                'is_popular': True,
                'discount_percentage': Decimal('20.00'),
            },
            {
                'name': 'Post-Surgery Recovery Plan',
                'description': 'Specialized meal plan designed for post-surgery recovery. Includes soft foods and high-protein options.',
                'plan_type': PlanType.DAILY,
                'price': Decimal('6000.00'),
                'meals_per_cycle': 2,
                'duration_days': 14,
                'is_active': True,
                'is_featured': True,
                'is_popular': False,
                'discount_percentage': Decimal('15.00'),
            },
            {
                'name': 'Diabetic-Friendly Weekly Plan',
                'description': 'Weekly meal plan with diabetic-friendly options. Low sugar, balanced nutrition.',
                'plan_type': PlanType.WEEKLY,
                'price': Decimal('35000.00'),
                'meals_per_cycle': 7,
                'duration_days': 28,
                'is_active': True,
                'is_featured': False,
                'is_popular': False,
                'discount_percentage': Decimal('10.00'),
            },
        ]

        plans_created = 0
        for plan_data in plans_data:
            plan, created = SubscriptionPlan.objects.get_or_create(
                name=plan_data['name'],
                defaults=plan_data
            )
            if created:
                plans_created += 1
                self.stdout.write(self.style.SUCCESS(f'  [OK] Created plan: {plan.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'  [-] Plan already exists: {plan.name}'))

        # Summary
        self.stdout.write(self.style.SUCCESS(
            f'\n[SUCCESS] Successfully seeded initial data!'
            f'\n  - Delivery Zones: {zones_created} new zones created'
            f'\n  - Subscription Plans: {plans_created} new plans created'
            f'\n\nNext steps:'
            f'\n  1. Run: python manage.py seed_menu (to add menu items)'
            f'\n  2. Create superuser: python manage.py createsuperuser'
            f'\n  3. Review and customize plans/zones in admin panel'
        ))
