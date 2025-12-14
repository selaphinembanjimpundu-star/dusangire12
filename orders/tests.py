"""
Unit tests for orders app
"""
from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
from menu.models import Category, MenuItem
from .models import Cart, CartItem, Order, OrderItem, OrderStatus


class CartModelTest(TestCase):
    """Test Cart model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Breakfast', slug='breakfast')
        self.menu_item = MenuItem.objects.create(
            name='Scrambled Eggs',
            description='Fresh eggs',
            category=self.category,
            price=Decimal('2500.00'),
            is_available=True
        )
        self.cart = Cart.objects.create(user=self.user)
    
    def test_cart_creation(self):
        """Test cart creation"""
        self.assertEqual(self.cart.user, self.user)
        self.assertEqual(self.cart.get_item_count(), 0)
        self.assertEqual(self.cart.get_total(), Decimal('0.00'))
    
    def test_cart_get_total(self):
        """Test cart total calculation"""
        CartItem.objects.create(
            cart=self.cart,
            menu_item=self.menu_item,
            quantity=2
        )
        
        expected_total = Decimal('2500.00') * 2
        self.assertEqual(self.cart.get_total(), expected_total)
    
    def test_cart_get_item_count(self):
        """Test cart item count"""
        CartItem.objects.create(
            cart=self.cart,
            menu_item=self.menu_item,
            quantity=3
        )
        
        self.assertEqual(self.cart.get_item_count(), 3)


class CartItemModelTest(TestCase):
    """Test CartItem model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Breakfast', slug='breakfast')
        self.menu_item = MenuItem.objects.create(
            name='Scrambled Eggs',
            description='Fresh eggs',
            category=self.category,
            price=Decimal('2500.00'),
            is_available=True
        )
        self.cart = Cart.objects.create(user=self.user)
    
    def test_cart_item_creation(self):
        """Test cart item creation"""
        cart_item = CartItem.objects.create(
            cart=self.cart,
            menu_item=self.menu_item,
            quantity=2
        )
        
        self.assertEqual(cart_item.cart, self.cart)
        self.assertEqual(cart_item.menu_item, self.menu_item)
        self.assertEqual(cart_item.quantity, 2)
    
    def test_cart_item_get_subtotal(self):
        """Test cart item subtotal calculation"""
        cart_item = CartItem.objects.create(
            cart=self.cart,
            menu_item=self.menu_item,
            quantity=3
        )
        
        expected_subtotal = Decimal('2500.00') * 3
        self.assertEqual(cart_item.get_subtotal(), expected_subtotal)


class OrderModelTest(TestCase):
    """Test Order model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Breakfast', slug='breakfast')
        self.menu_item = MenuItem.objects.create(
            name='Scrambled Eggs',
            description='Fresh eggs',
            category=self.category,
            price=Decimal('2500.00'),
            is_available=True
        )
    
    def test_order_creation(self):
        """Test order creation"""
        order = Order.objects.create(
            user=self.user,
            order_number='ORD-001',
            status=OrderStatus.PENDING,
            customer_name='Test User',
            customer_phone='+250788123456',
            delivery_address='123 Test St',
            subtotal=Decimal('2500.00'),
            delivery_charge=Decimal('500.00'),
            total=Decimal('3000.00')
        )
        
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.status, OrderStatus.PENDING)
        self.assertEqual(order.total, Decimal('3000.00'))
    
    def test_order_with_items(self):
        """Test order with items"""
        order = Order.objects.create(
            user=self.user,
            order_number='ORD-002',
            status=OrderStatus.PENDING,
            customer_name='Test User',
            customer_phone='+250788123456',
            delivery_address='123 Test St',
            subtotal=Decimal('2500.00'),
            delivery_charge=Decimal('500.00'),
            total=Decimal('3000.00')
        )
        
        order_item = OrderItem.objects.create(
            order=order,
            menu_item=self.menu_item,
            quantity=1,
            price=Decimal('2500.00')
        )
        
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order_item.order, order)
        self.assertEqual(order_item.menu_item, self.menu_item)


class OrderViewsTest(TestCase):
    """Test order views"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Breakfast', slug='breakfast')
        self.menu_item = MenuItem.objects.create(
            name='Scrambled Eggs',
            description='Fresh eggs',
            category=self.category,
            price=Decimal('2500.00'),
            is_available=True
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_cart_view(self):
        """Test cart view"""
        response = self.client.get('/orders/cart/')
        self.assertEqual(response.status_code, 200)
    
    def test_add_to_cart(self):
        """Test add to cart"""
        response = self.client.post(f'/orders/cart/add/{self.menu_item.id}/', {
            'quantity': 2
        })
        # Should redirect after adding to cart
        self.assertEqual(response.status_code, 302)
        
        # Check cart item was created
        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.items.count(), 1)
        self.assertEqual(cart.items.first().quantity, 2)
    
    def test_order_history_view(self):
        """Test order history view"""
        response = self.client.get('/orders/history/')
        self.assertEqual(response.status_code, 200)
