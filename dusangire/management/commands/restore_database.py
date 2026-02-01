"""
Management command to restore the database from a backup
Supports SQLite (development) and PostgreSQL (production)
"""
import os
import subprocess
from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path


class Command(BaseCommand):
    help = 'Restore the database from a backup file'

    def add_arguments(self, parser):
        parser.add_argument(
            'backup_file',
            type=str,
            help='Path to the backup file to restore from',
        )
        parser.add_argument(
            '--backup-dir',
            type=str,
            default='backups',
            help='Directory where backup files are stored (default: backups)',
        )
        parser.add_argument(
            '--no-input',
            action='store_true',
            help='Skip confirmation prompt',
        )

    def handle(self, *args, **options):
        backup_file = options['backup_file']
        backup_dir = Path(options['backup_dir'])
        
        # If relative path, check in backup directory
        if not os.path.isabs(backup_file):
            backup_path = backup_dir / backup_file
        else:
            backup_path = Path(backup_file)
        
        if not backup_path.exists():
            self.stdout.write(self.style.ERROR(
                f'[ERROR] Backup file not found: {backup_path}'
            ))
            return
        
        # Confirmation
        if not options['no_input']:
            self.stdout.write(self.style.WARNING(
                f'\n⚠️  WARNING: This will replace the current database with the backup!'
            ))
            self.stdout.write(f'Backup file: {backup_path}')
            confirm = input('Are you sure you want to continue? (yes/no): ')
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.WARNING('Restore cancelled.'))
                return
        
        db_settings = settings.DATABASES['default']
        db_engine = db_settings['ENGINE']
        
        if 'sqlite' in db_engine:
            # SQLite restore
            db_path = db_settings['NAME']
            db_dir = os.path.dirname(db_path)
            
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
            
            try:
                import shutil
                # Backup current database first
                if os.path.exists(db_path):
                    current_backup = f"{db_path}.backup_before_restore"
                    shutil.copy2(db_path, current_backup)
                    self.stdout.write(self.style.WARNING(
                        f'Current database backed up to: {current_backup}'
                    ))
                
                # Restore from backup
                shutil.copy2(backup_path, db_path)
                self.stdout.write(self.style.SUCCESS(
                    f'[SUCCESS] SQLite database restored from: {backup_path}'
                ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f'[ERROR] Failed to restore SQLite database: {str(e)}'
                ))
                return
        
        elif 'postgresql' in db_engine:
            # PostgreSQL restore using pg_restore
            db_name = db_settings['NAME']
            db_user = db_settings.get('USER', 'postgres')
            db_host = db_settings.get('HOST', 'localhost')
            db_port = db_settings.get('PORT', '5432')
            
            # Check if backup is SQL dump or custom format
            if str(backup_path).endswith('.sql'):
                # SQL dump format
                restore_cmd = [
                    'psql',
                    '-h', db_host,
                    '-p', str(db_port),
                    '-U', db_user,
                    '-d', db_name,
                    '-f', str(backup_path),
                ]
            else:
                # Custom format
                restore_cmd = [
                    'pg_restore',
                    '-h', db_host,
                    '-p', str(db_port),
                    '-U', db_user,
                    '-d', db_name,
                    '--clean',
                    '--if-exists',
                    str(backup_path),
                ]
            
            # Set PGPASSWORD if provided
            env = os.environ.copy()
            if 'PASSWORD' in db_settings:
                env['PGPASSWORD'] = db_settings['PASSWORD']
            
            try:
                # Backup current database first
                self.stdout.write('Creating backup of current database before restore...')
                from django.core.management import call_command
                call_command('backup_database', verbosity=0)
                
                # Restore
                result = subprocess.run(
                    restore_cmd,
                    env=env,
                    capture_output=True,
                    text=True,
                    check=True
                )
                self.stdout.write(self.style.SUCCESS(
                    f'[SUCCESS] PostgreSQL database restored from: {backup_path}'
                ))
            except subprocess.CalledProcessError as e:
                self.stdout.write(self.style.ERROR(
                    f'[ERROR] Failed to restore PostgreSQL database: {e.stderr}'
                ))
                self.stdout.write(self.style.WARNING(
                    'Make sure psql/pg_restore is installed and accessible in PATH'
                ))
                return
            except FileNotFoundError:
                self.stdout.write(self.style.ERROR(
                    '[ERROR] psql/pg_restore not found. Please install PostgreSQL client tools.'
                ))
                return
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f'[ERROR] Restore error: {str(e)}'
                ))
                return
        
        else:
            self.stdout.write(self.style.ERROR(
                f'[ERROR] Unsupported database engine: {db_engine}'
            ))
            return
        
        # Display restore info
        file_size = backup_path.stat().st_size / (1024 * 1024)  # Size in MB
        self.stdout.write(
            f'\nRestore Details:'
            f'\n  Source: {backup_path}'
            f'\n  Size: {file_size:.2f} MB'
            f'\n  Database: {db_settings["NAME"]}'
        )
        
        self.stdout.write(self.style.SUCCESS(
            '\n✓ Database restore completed successfully!'
        ))
        self.stdout.write(self.style.WARNING(
            '\n⚠️  Next steps:'
            f'\n  1. Run migrations: python manage.py migrate'
            f'\n  2. Verify data: python manage.py shell'
            f'\n  3. Test application functionality'
        ))














