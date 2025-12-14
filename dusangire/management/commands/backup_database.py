"""
Management command to backup the database
Supports SQLite (development) and PostgreSQL (production)
"""
import os
import subprocess
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path


class Command(BaseCommand):
    help = 'Backup the database to a file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=str,
            default='backups',
            help='Directory to save backup files (default: backups)',
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['sql', 'json'],
            default='sql',
            help='Backup format (default: sql)',
        )

    def handle(self, *args, **options):
        output_dir = Path(options['output_dir'])
        output_dir.mkdir(parents=True, exist_ok=True)
        
        db_settings = settings.DATABASES['default']
        db_engine = db_settings['ENGINE']
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if 'sqlite' in db_engine:
            # SQLite backup
            db_path = db_settings['NAME']
            backup_filename = f'db_backup_{timestamp}.sqlite3'
            backup_path = output_dir / backup_filename
            
            try:
                import shutil
                shutil.copy2(db_path, backup_path)
                self.stdout.write(self.style.SUCCESS(
                    f'[SUCCESS] SQLite database backed up to: {backup_path}'
                ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f'[ERROR] Failed to backup SQLite database: {str(e)}'
                ))
                return
        
        elif 'postgresql' in db_engine:
            # PostgreSQL backup using pg_dump
            db_name = db_settings['NAME']
            db_user = db_settings.get('USER', 'postgres')
            db_host = db_settings.get('HOST', 'localhost')
            db_port = db_settings.get('PORT', '5432')
            
            backup_filename = f'db_backup_{timestamp}.sql'
            backup_path = output_dir / backup_filename
            
            # Build pg_dump command
            pg_dump_cmd = [
                'pg_dump',
                '-h', db_host,
                '-p', str(db_port),
                '-U', db_user,
                '-F', 'c',  # Custom format
                '-f', str(backup_path),
                db_name,
            ]
            
            # Set PGPASSWORD if provided
            env = os.environ.copy()
            if 'PASSWORD' in db_settings:
                env['PGPASSWORD'] = db_settings['PASSWORD']
            
            try:
                result = subprocess.run(
                    pg_dump_cmd,
                    env=env,
                    capture_output=True,
                    text=True,
                    check=True
                )
                self.stdout.write(self.style.SUCCESS(
                    f'[SUCCESS] PostgreSQL database backed up to: {backup_path}'
                ))
            except subprocess.CalledProcessError as e:
                self.stdout.write(self.style.ERROR(
                    f'[ERROR] Failed to backup PostgreSQL database: {e.stderr}'
                ))
                self.stdout.write(self.style.WARNING(
                    'Make sure pg_dump is installed and accessible in PATH'
                ))
                return
            except FileNotFoundError:
                self.stdout.write(self.style.ERROR(
                    '[ERROR] pg_dump not found. Please install PostgreSQL client tools.'
                ))
                return
        
        else:
            self.stdout.write(self.style.ERROR(
                f'[ERROR] Unsupported database engine: {db_engine}'
            ))
            return
        
        # Display backup info
        file_size = backup_path.stat().st_size / (1024 * 1024)  # Size in MB
        self.stdout.write(
            f'\nBackup Details:'
            f'\n  File: {backup_path}'
            f'\n  Size: {file_size:.2f} MB'
            f'\n  Timestamp: {timestamp}'
        )
