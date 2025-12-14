"""
Unit tests for menu app
"""
from django.test import TestCase
from decimal import Decimal
from .models import Category, DietaryTag, MenuItem


class CategoryModelTest(TestCase):
    """Test Category model"""
    
    def setUp(self):
        """Set up test data"""
        self.category = Category.objects.create(
            name='Breakfast',
            description='Morning meals',
            slug='breakfast',
            is_active=True
        )
    
    def test_category_creation(self):
        """Test category creation"""
        self.assertEqual(self.category.name, 'Breakfast')
        self.assertEqual(self.category.slug, 'breakfast')
        self.assertTrue(self.category.is_active)
    
    def test_category_str(self):
        """Test category string representation"""
        self.assertEqual(str(self.category), 'Breakfast')
    
    def test_category_ordering(self):
        """Test category ordering"""
        Category.objects.create(name='Dinner', slug='dinner')
        Category.objects.create(name='Lunch', slug='lunch')
        
        categories = list(Category.objects.all())
        self.assertEqual(categories[0].name, 'Breakfast')
        self.assertEqual(categories[1].name, 'Dinner')
        self.assertEqual(categories[2].name, 'Lunch')


class DietaryTagModelTest(TestCase):
    """Test DietaryTag model"""
    
    def setUp(self):
        """Set up test data"""
        self.tag = DietaryTag.objects.create(
            name='Vegetarian',
            description='No meat products',
            icon='🥬'
        )
    
    def test_dietary_tag_creation(self):
        """Test dietary tag creation"""
        self.assertEqual(self.tag.name, 'Vegetarian')
        self.assertEqual(self.tag.icon, '🥬')
    
    def test_dietary_tag_str(self):
        """Test dietary tag string representation"""
        self.assertEqual(str(self.tag), 'Vegetarian')


class MenuItemModelTest(TestCase):
    """Test MenuItem model"""
    
    def setUp(self):
        """Set up test data"""
        self.category = Category.objects.create(
            name='Breakfast',
            slug='breakfast'
        )
        self.menu_item = MenuItem.objects.create(
            name='Scrambled Eggs',
            description='Fresh eggs scrambled to perfection',
            category=self.category,
            price=Decimal('2500.00'),
            calories=300,
            protein=Decimal('20.00'),
            carbs=Decimal('2.00'),
            fat=Decimal('22.00'),
            is_available=True
        )
    
    def test_menu_item_creation(self):
        """Test menu item creation"""
        self.assertEqual(self.menu_item.name, 'Scrambled Eggs')
        self.assertEqual(self.menu_item.price, Decimal('2500.00'))
        self.assertEqual(self.menu_item.category, self.category)
        self.assertTrue(self.menu_item.is_available)
    
    def test_menu_item_str(self):
        """Test menu item string representation"""
        expected = f"Scrambled Eggs - {self.category.name}"
        self.assertEqual(str(self.menu_item), expected)
    
    def test_menu_item_with_dietary_tags(self):
        """Test menu item with dietary tags"""
        tag1 = DietaryTag.objects.create(name='Vegetarian')
        tag2 = DietaryTag.objects.create(name='High Protein')
        
        self.menu_item.dietary_tags.add(tag1, tag2)
        
        self.assertEqual(self.menu_item.dietary_tags.count(), 2)
        self.assertIn(tag1, self.menu_item.dietary_tags.all())
        self.assertIn(tag2, self.menu_item.dietary_tags.all())
    
    def test_menu_item_price_validation(self):
        """Test menu item price must be positive"""
        from django.core.exceptions import ValidationError
        from django.db import IntegrityError
        
        # Price must be at least 0.01
        with self.assertRaises(ValidationError):
            item = MenuItem(
                name='Test Item',
                description='Test',
                category=self.category,
                price=Decimal('0.00')
            )
            item.full_clean()
    
    def test_menu_item_get_thumbnail_url(self):
        """Test get_thumbnail_url method"""
        # Without image, should return None
        self.assertIsNone(self.menu_item.get_thumbnail_url())


class MenuViewsTest(TestCase):
    """Test menu views"""
    
    def setUp(self):
        """Set up test data"""
        self.category = Category.objects.create(
            name='Breakfast',
            slug='breakfast'
        )
        self.menu_item = MenuItem.objects.create(
            name='Scrambled Eggs',
            description='Fresh eggs',
            category=self.category,
            price=Decimal('2500.00'),
            is_available=True
        )
    
    def test_menu_list_view(self):
        """Test menu list view"""
        response = self.client.get('/menu/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Scrambled Eggs')
    
    def test_menu_detail_view(self):
        """Test menu detail view"""
        response = self.client.get(f'/menu/item/{self.menu_item.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Scrambled Eggs')
        self.assertContains(response, 'RWF 2500')
    
    def test_menu_list_with_filter(self):
        """Test menu list with category filter"""
        response = self.client.get(f'/menu/?category={self.category.id}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Scrambled Eggs')
    
    def test_menu_list_with_search(self):
        """Test menu list with search"""
        response = self.client.get('/menu/?search=eggs')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Scrambled Eggs')
