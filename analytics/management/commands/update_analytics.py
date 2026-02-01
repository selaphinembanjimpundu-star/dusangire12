from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta
from analytics.services import AnalyticsService
from analytics.models import DailyAnalyticsSnapshot


class Command(BaseCommand):
    help = 'Update daily analytics snapshots and customer metrics'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=1,
            help='Number of days to process (default: 1 for today)'
        )
        parser.add_argument(
            '--backfill',
            action='store_true',
            help='Backfill analytics for the last 30 days'
        )

    def handle(self, *args, **options):
        if options['backfill']:
            # Backfill last 30 days
            today = timezone.now().date()
            for i in range(30):
                date = today - timedelta(days=i)
                self.stdout.write(f'Processing {date}...')
                AnalyticsService.calculate_daily_snapshot(date)
            self.stdout.write(self.style.SUCCESS('Backfill completed for last 30 days'))
        else:
            # Process specified number of days (default: today)
            days = options['days']
            today = timezone.now().date()
            
            for i in range(days):
                date = today - timedelta(days=i)
                self.stdout.write(f'Processing {date}...')
                snapshot = AnalyticsService.calculate_daily_snapshot(date)
                self.stdout.write(f'  Orders: {snapshot.total_orders}, Revenue: RWF {snapshot.total_revenue}')
        
        # Update customer metrics for all users
        self.stdout.write('Updating customer metrics...')
        users = User.objects.all()
        updated_count = 0
        
        for user in users:
            AnalyticsService.update_customer_metrics(user)
            updated_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated analytics for {updated_count} customers')
        )
