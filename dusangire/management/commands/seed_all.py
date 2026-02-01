"""
Master management command to seed all initial data for production launch.
This command orchestrates all seeding operations for a complete initial setup.
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Seed all initial data for production launch (menu, subscriptions, delivery zones, etc.)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )
        parser.add_argument(
            '--menu-only',
            action='store_true',
            help='Only seed menu data',
        )
        parser.add_argument(
            '--subscriptions-only',
            action='store_true',
            help='Only seed subscription plans and delivery zones',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('Dusangire - Initial Data Seeding'))
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))

        clear_flag = ['--clear'] if options['clear'] else []

        if options['menu_only']:
            self.stdout.write('Seeding menu data only...\n')
            call_command('seed_menu', *clear_flag)
        elif options['subscriptions_only']:
            self.stdout.write('Seeding subscription plans and delivery zones only...\n')
            call_command('seed_initial_data', *clear_flag)
        else:
            # Seed everything
            self.stdout.write('Step 1/2: Seeding menu data (categories, dietary tags, menu items)...\n')
            call_command('seed_menu', *clear_flag)
            
            self.stdout.write('\n' + '-'*60 + '\n')
            
            self.stdout.write('Step 2/2: Seeding subscription plans and delivery zones...\n')
            call_command('seed_initial_data', *clear_flag)

        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('Initial Data Seeding Complete!'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write('\nNext steps:')
        self.stdout.write('  1. Create superuser: python manage.py createsuperuser')
        self.stdout.write('  2. Review and customize data in admin panel')
        self.stdout.write('  3. Add menu item images if needed')
        self.stdout.write('  4. Configure payment gateway credentials')
        self.stdout.write('  5. Test the application thoroughly\n')
