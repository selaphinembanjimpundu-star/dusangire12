"""
Management command to update cached ratings for all menu items
Run this after adding the average_rating and total_reviews fields
"""

from django.core.management.base import BaseCommand
from menu.models import MenuItem


class Command(BaseCommand):
    help = 'Update cached average ratings and review counts for all menu items'

    def handle(self, *args, **options):
        self.stdout.write('Updating ratings for all menu items...')
        
        menu_items = MenuItem.objects.all()
        total = menu_items.count()
        updated = 0
        
        for menu_item in menu_items:
            menu_item.update_average_rating()
            updated += 1
            if updated % 10 == 0:
                self.stdout.write(f'Updated {updated}/{total} items...')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated ratings for {updated} menu items'
            )
        )













