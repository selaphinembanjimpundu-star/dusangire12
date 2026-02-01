"""
Management command to seed the database with sample menu items
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from menu.models import Category, DietaryTag, MenuItem
from decimal import Decimal


class Command(BaseCommand):
    help = 'Seed the database with sample menu items, categories, and dietary tags'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing menu items, categories, and dietary tags before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing menu data...'))
            MenuItem.objects.all().delete()
            Category.objects.all().delete()
            DietaryTag.objects.all().delete()

        # Create Categories
        self.stdout.write('Creating categories...')
        categories_data = [
            {'name': 'Breakfast', 'description': 'Start your day with nutritious breakfast options'},
            {'name': 'Lunch', 'description': 'Satisfying lunch meals for midday energy'},
            {'name': 'Dinner', 'description': 'Hearty dinner options for the evening'},
            {'name': 'Snacks', 'description': 'Light snacks and appetizers'},
            {'name': 'Beverages', 'description': 'Refreshing drinks and beverages'},
        ]
        
        categories = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'slug': slugify(cat_data['name']),
                    'description': cat_data['description'],
                    'is_active': True
                }
            )
            categories[cat_data['name']] = category
            if created:
                self.stdout.write(self.style.SUCCESS(f'  [OK] Created category: {category.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'  [-] Category already exists: {category.name}'))

        # Create Dietary Tags
        self.stdout.write('Creating dietary tags...')
        dietary_tags_data = [
            {'name': 'Diabetic-Friendly', 'description': 'Suitable for diabetic patients', 'icon': '🩺'},
            {'name': 'Low-Sodium', 'description': 'Low sodium content', 'icon': '🧂'},
            {'name': 'High-Protein', 'description': 'High protein content', 'icon': '💪'},
            {'name': 'Post-Surgery', 'description': 'Suitable for post-surgery recovery', 'icon': '🏥'},
            {'name': 'Vegetarian', 'description': 'Vegetarian option', 'icon': '🥗'},
            {'name': 'Soft Diet', 'description': 'Easy to chew and swallow', 'icon': '🍲'},
        ]
        
        dietary_tags = {}
        for tag_data in dietary_tags_data:
            tag, created = DietaryTag.objects.get_or_create(
                name=tag_data['name'],
                defaults={
                    'description': tag_data['description'],
                    'icon': tag_data['icon']
                }
            )
            dietary_tags[tag_data['name']] = tag
            if created:
                self.stdout.write(self.style.SUCCESS(f'  [OK] Created dietary tag: {tag.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'  [-] Dietary tag already exists: {tag.name}'))

        # Create Menu Items
        self.stdout.write('Creating menu items...')
        menu_items_data = [
            {
                'name': 'Scrambled Eggs with Toast',
                'description': 'Fresh scrambled eggs served with whole grain toast. High in protein and perfect for breakfast.',
                'category': 'Breakfast',
                'price': Decimal('8.99'),
                'calories': 350,
                'protein': Decimal('20.0'),
                'carbs': Decimal('25.0'),
                'fat': Decimal('18.0'),
                'dietary_tags': ['High-Protein', 'Vegetarian'],
                'is_featured': True,
            },
            {
                'name': 'Oatmeal with Fruits',
                'description': 'Warm oatmeal topped with fresh fruits. Great for a healthy start to your day.',
                'category': 'Breakfast',
                'price': Decimal('7.50'),
                'calories': 280,
                'protein': Decimal('8.0'),
                'carbs': Decimal('45.0'),
                'fat': Decimal('6.0'),
                'dietary_tags': ['Diabetic-Friendly', 'Vegetarian', 'Low-Sodium'],
                'is_featured': False,
            },
            {
                'name': 'Grilled Chicken Breast',
                'description': 'Tender grilled chicken breast served with steamed vegetables. High protein meal perfect for recovery.',
                'category': 'Lunch',
                'price': Decimal('12.99'),
                'calories': 320,
                'protein': Decimal('35.0'),
                'carbs': Decimal('5.0'),
                'fat': Decimal('12.0'),
                'dietary_tags': ['High-Protein', 'Post-Surgery', 'Low-Sodium'],
                'is_featured': True,
            },
            {
                'name': 'Vegetable Soup',
                'description': 'Homemade vegetable soup with fresh seasonal vegetables. Light and nutritious.',
                'category': 'Lunch',
                'price': Decimal('6.99'),
                'calories': 150,
                'protein': Decimal('5.0'),
                'carbs': Decimal('20.0'),
                'fat': Decimal('4.0'),
                'dietary_tags': ['Vegetarian', 'Soft Diet', 'Low-Sodium'],
                'is_featured': False,
            },
            {
                'name': 'Baked Salmon',
                'description': 'Fresh salmon baked to perfection with herbs and lemon. Rich in omega-3 fatty acids.',
                'category': 'Dinner',
                'price': Decimal('15.99'),
                'calories': 380,
                'protein': Decimal('30.0'),
                'carbs': Decimal('2.0'),
                'fat': Decimal('25.0'),
                'dietary_tags': ['High-Protein', 'Post-Surgery'],
                'is_featured': True,
            },
            {
                'name': 'Mashed Potatoes',
                'description': 'Creamy mashed potatoes made with fresh potatoes. Soft and easy to digest.',
                'category': 'Dinner',
                'price': Decimal('5.99'),
                'calories': 220,
                'protein': Decimal('4.0'),
                'carbs': Decimal('35.0'),
                'fat': Decimal('8.0'),
                'dietary_tags': ['Vegetarian', 'Soft Diet'],
                'is_featured': False,
            },
            {
                'name': 'Fresh Fruit Salad',
                'description': 'Mixed seasonal fruits served fresh. A healthy and refreshing snack option.',
                'category': 'Snacks',
                'price': Decimal('4.99'),
                'calories': 120,
                'protein': Decimal('2.0'),
                'carbs': Decimal('28.0'),
                'fat': Decimal('0.5'),
                'dietary_tags': ['Vegetarian', 'Diabetic-Friendly'],
                'is_featured': False,
            },
            {
                'name': 'Yogurt Parfait',
                'description': 'Layered yogurt with granola and fresh berries. High in protein and probiotics.',
                'category': 'Snacks',
                'price': Decimal('5.50'),
                'calories': 200,
                'protein': Decimal('12.0'),
                'carbs': Decimal('25.0'),
                'fat': Decimal('6.0'),
                'dietary_tags': ['High-Protein', 'Vegetarian'],
                'is_featured': False,
            },
            {
                'name': 'Herbal Tea',
                'description': 'Warm herbal tea selection. Soothing and caffeine-free.',
                'category': 'Beverages',
                'price': Decimal('2.99'),
                'calories': 5,
                'protein': Decimal('0.0'),
                'carbs': Decimal('1.0'),
                'fat': Decimal('0.0'),
                'dietary_tags': ['Vegetarian', 'Low-Sodium'],
                'is_featured': False,
            },
            {
                'name': 'Fresh Orange Juice',
                'description': 'Freshly squeezed orange juice. Rich in vitamin C.',
                'category': 'Beverages',
                'price': Decimal('3.50'),
                'calories': 110,
                'protein': Decimal('2.0'),
                'carbs': Decimal('26.0'),
                'fat': Decimal('0.5'),
                'dietary_tags': ['Vegetarian', 'Diabetic-Friendly'],
                'is_featured': False,
            },
        ]

        created_count = 0
        for item_data in menu_items_data:
            category = categories[item_data['category']]
            item_tags = [dietary_tags[tag] for tag in item_data['dietary_tags'] if tag in dietary_tags]
            
            # Remove dietary_tags from item_data before creating MenuItem
            item_data_copy = item_data.copy()
            item_data_copy.pop('category')
            item_data_copy.pop('dietary_tags')
            
            menu_item, created = MenuItem.objects.get_or_create(
                name=item_data['name'],
                defaults={
                    **item_data_copy,
                    'category': category,
                }
            )
            
            if created:
                # Add dietary tags
                menu_item.dietary_tags.set(item_tags)
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  [OK] Created menu item: {menu_item.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'  [-] Menu item already exists: {menu_item.name}'))

        self.stdout.write(self.style.SUCCESS(
            f'\n[SUCCESS] Successfully seeded database!'
            f'\n  - Categories: {len(categories)}'
            f'\n  - Dietary Tags: {len(dietary_tags)}'
            f'\n  - Menu Items: {created_count} new items created'
        ))



















