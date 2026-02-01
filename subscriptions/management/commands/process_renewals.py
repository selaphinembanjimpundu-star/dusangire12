from django.core.management.base import BaseCommand
from django.utils import timezone
from subscriptions.services import SubscriptionRenewalService

class Command(BaseCommand):
    help = 'Process subscription auto-renewals'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting auto-renewal process...'))
        
        try:
            results = SubscriptionRenewalService.process_auto_renewals()
            
            self.stdout.write(self.style.SUCCESS(f"Processed: {results['processed']}"))
            self.stdout.write(self.style.SUCCESS(f"Success: {results['success']}"))
            self.stdout.write(self.style.WARNING(f"Failed: {results['failed']}"))
            self.stdout.write(self.style.WARNING(f"Retried: {results['retried']}"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error processing renewals: {str(e)}"))
            import traceback
            traceback.print_exc()
