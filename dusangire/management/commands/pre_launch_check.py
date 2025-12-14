"""
Management command to run comprehensive pre-launch checks
Tests all critical functionality before production deployment
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db import connection
from django.conf import settings
import sys

User = get_user_model()


class Command(BaseCommand):
    help = 'Run comprehensive pre-launch checks and tests'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-tests',
            action='store_true',
            help='Skip running Django test suite',
        )
        parser.add_argument(
            '--skip-security',
            action='store_true',
            help='Skip security checks',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS('NOURISH LINK - Pre-Launch Checklist'))
        self.stdout.write(self.style.SUCCESS('='*70 + '\n'))

        errors = []
        warnings = []

        # 1. Django System Check
        self.stdout.write('1. Running Django system checks...')
        try:
            call_command('check', verbosity=0)
            self.stdout.write(self.style.SUCCESS('   ✓ System checks passed'))
        except SystemExit:
            errors.append('Django system checks failed')
            self.stdout.write(self.style.ERROR('   ✗ System checks failed'))
        except Exception as e:
            errors.append(f'System check error: {str(e)}')
            self.stdout.write(self.style.ERROR(f'   ✗ System check error: {str(e)}'))

        # 2. Security Check
        if not options['skip_security']:
            self.stdout.write('\n2. Running security checks...')
            try:
                call_command('check', '--deploy', verbosity=0)
                self.stdout.write(self.style.SUCCESS('   ✓ Security checks passed'))
            except SystemExit:
                warnings.append('Security checks failed - review settings')
                self.stdout.write(self.style.WARNING('   ⚠ Security checks failed - review production settings'))
            except Exception as e:
                warnings.append(f'Security check error: {str(e)}')
                self.stdout.write(self.style.WARNING(f'   ⚠ Security check error: {str(e)}'))
        else:
            self.stdout.write('\n2. Skipping security checks...')
            self.stdout.write(self.style.WARNING('   ⚠ Security checks skipped'))

        # 3. Database Connection
        self.stdout.write('\n3. Testing database connection...')
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
            if result:
                self.stdout.write(self.style.SUCCESS('   ✓ Database connection successful'))
        except Exception as e:
            errors.append(f'Database connection failed: {str(e)}')
            self.stdout.write(self.style.ERROR(f'   ✗ Database connection failed: {str(e)}'))

        # 4. Check Migrations
        self.stdout.write('\n4. Checking database migrations...')
        try:
            call_command('showmigrations', '--plan', verbosity=0)
            # Check for unapplied migrations
            from django.core.management import call_command
            from io import StringIO
            out = StringIO()
            call_command('showmigrations', '--plan', stdout=out, verbosity=0)
            output = out.getvalue()
            if '[ ]' in output:
                warnings.append('Unapplied migrations detected')
                self.stdout.write(self.style.WARNING('   ⚠ Unapplied migrations detected - run migrate'))
            else:
                self.stdout.write(self.style.SUCCESS('   ✓ All migrations applied'))
        except Exception as e:
            warnings.append(f'Migration check error: {str(e)}')
            self.stdout.write(self.style.WARNING(f'   ⚠ Migration check error: {str(e)}'))

        # 5. Static Files
        self.stdout.write('\n5. Checking static files...')
        try:
            import os
            from django.conf import settings
            static_root = settings.STATIC_ROOT
            if static_root and os.path.exists(static_root):
                static_files = sum([len(files) for r, d, files in os.walk(static_root)])
                if static_files > 0:
                    self.stdout.write(self.style.SUCCESS(f'   ✓ Static files collected ({static_files} files)'))
                else:
                    warnings.append('Static files directory is empty - run collectstatic')
                    self.stdout.write(self.style.WARNING('   ⚠ Static files directory is empty - run collectstatic'))
            else:
                warnings.append('Static files not collected - run collectstatic')
                self.stdout.write(self.style.WARNING('   ⚠ Static files not collected - run collectstatic'))
        except Exception as e:
            warnings.append(f'Static files check error: {str(e)}')
            self.stdout.write(self.style.WARNING(f'   ⚠ Static files check error: {str(e)}'))

        # 6. Environment Variables
        self.stdout.write('\n6. Checking critical environment variables...')
        critical_vars = ['SECRET_KEY']
        if not settings.DEBUG:
            critical_vars.extend(['ALLOWED_HOSTS', 'DATABASE_URL'])
        
        missing_vars = []
        for var in critical_vars:
            if var == 'SECRET_KEY':
                if not hasattr(settings, 'SECRET_KEY') or not settings.SECRET_KEY:
                    missing_vars.append(var)
            elif var == 'ALLOWED_HOSTS':
                if not hasattr(settings, 'ALLOWED_HOSTS') or not settings.ALLOWED_HOSTS:
                    missing_vars.append(var)
            elif var == 'DATABASE_URL':
                db = settings.DATABASES['default']
                if not db.get('NAME'):
                    missing_vars.append('DATABASE_NAME')
        
        if missing_vars:
            errors.append(f'Missing environment variables: {", ".join(missing_vars)}')
            self.stdout.write(self.style.ERROR(f'   ✗ Missing variables: {", ".join(missing_vars)}'))
        else:
            self.stdout.write(self.style.SUCCESS('   ✓ Critical environment variables set'))

        # 7. Test Suite
        if not options['skip_tests']:
            self.stdout.write('\n7. Running test suite...')
            try:
                call_command('test', verbosity=1, interactive=False)
                self.stdout.write(self.style.SUCCESS('   ✓ All tests passed'))
            except SystemExit:
                errors.append('Test suite failed')
                self.stdout.write(self.style.ERROR('   ✗ Test suite failed'))
            except Exception as e:
                errors.append(f'Test error: {str(e)}')
                self.stdout.write(self.style.ERROR(f'   ✗ Test error: {str(e)}'))
        else:
            self.stdout.write('\n7. Skipping test suite...')
            self.stdout.write(self.style.WARNING('   ⚠ Test suite skipped'))

        # 8. Check Required Models
        self.stdout.write('\n8. Checking required models and data...')
        try:
            from menu.models import Category, MenuItem
            from subscriptions.models import SubscriptionPlan
            from delivery.models import DeliveryZone
            
            category_count = Category.objects.count()
            menu_count = MenuItem.objects.count()
            plan_count = SubscriptionPlan.objects.count()
            zone_count = DeliveryZone.objects.count()
            
            if category_count == 0:
                warnings.append('No categories found - run seed_menu command')
                self.stdout.write(self.style.WARNING('   ⚠ No categories found'))
            else:
                self.stdout.write(self.style.SUCCESS(f'   ✓ {category_count} categories found'))
            
            if menu_count == 0:
                warnings.append('No menu items found - run seed_menu command')
                self.stdout.write(self.style.WARNING('   ⚠ No menu items found'))
            else:
                self.stdout.write(self.style.SUCCESS(f'   ✓ {menu_count} menu items found'))
            
            if plan_count == 0:
                warnings.append('No subscription plans found - run seed_initial_data command')
                self.stdout.write(self.style.WARNING('   ⚠ No subscription plans found'))
            else:
                self.stdout.write(self.style.SUCCESS(f'   ✓ {plan_count} subscription plans found'))
            
            if zone_count == 0:
                warnings.append('No delivery zones found - run seed_initial_data command')
                self.stdout.write(self.style.WARNING('   ⚠ No delivery zones found'))
            else:
                self.stdout.write(self.style.SUCCESS(f'   ✓ {zone_count} delivery zones found'))
                
        except Exception as e:
            warnings.append(f'Model check error: {str(e)}')
            self.stdout.write(self.style.WARNING(f'   ⚠ Model check error: {str(e)}'))

        # 9. Check Superuser
        self.stdout.write('\n9. Checking superuser account...')
        try:
            superuser_count = User.objects.filter(is_superuser=True).count()
            if superuser_count == 0:
                warnings.append('No superuser found - run createsuperuser command')
                self.stdout.write(self.style.WARNING('   ⚠ No superuser found'))
            else:
                self.stdout.write(self.style.SUCCESS(f'   ✓ {superuser_count} superuser(s) found'))
        except Exception as e:
            warnings.append(f'Superuser check error: {str(e)}')
            self.stdout.write(self.style.WARNING(f'   ⚠ Superuser check error: {str(e)}'))

        # 10. Settings Check
        self.stdout.write('\n10. Checking production settings...')
        if settings.DEBUG:
            errors.append('DEBUG is True - must be False in production')
            self.stdout.write(self.style.ERROR('   ✗ DEBUG is True - must be False in production'))
        else:
            self.stdout.write(self.style.SUCCESS('   ✓ DEBUG is False'))
        
        if not hasattr(settings, 'ALLOWED_HOSTS') or not settings.ALLOWED_HOSTS:
            errors.append('ALLOWED_HOSTS not configured')
            self.stdout.write(self.style.ERROR('   ✗ ALLOWED_HOSTS not configured'))
        else:
            self.stdout.write(self.style.SUCCESS(f'   ✓ ALLOWED_HOSTS configured: {settings.ALLOWED_HOSTS}'))

        # Summary
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('Pre-Launch Check Summary'))
        self.stdout.write('='*70)
        
        if errors:
            self.stdout.write(self.style.ERROR(f'\n✗ ERRORS: {len(errors)}'))
            for error in errors:
                self.stdout.write(self.style.ERROR(f'   - {error}'))
        
        if warnings:
            self.stdout.write(self.style.WARNING(f'\n⚠ WARNINGS: {len(warnings)}'))
            for warning in warnings:
                self.stdout.write(self.style.WARNING(f'   - {warning}'))
        
        if not errors and not warnings:
            self.stdout.write(self.style.SUCCESS('\n✓ All checks passed! Ready for launch.'))
        elif not errors:
            self.stdout.write(self.style.WARNING('\n⚠ Checks passed with warnings. Review warnings before launch.'))
        else:
            self.stdout.write(self.style.ERROR('\n✗ Checks failed. Fix errors before launch.'))
            sys.exit(1)
        
        self.stdout.write('\n')
