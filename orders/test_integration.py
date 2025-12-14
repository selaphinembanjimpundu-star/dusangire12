"""
Integration tests for order workflow
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from decimal import Decimal
from menu.models import Category, MenuItem
from orders.models import Cart, CartItem, Order, OrderItem, OrderStatus
from delivery.models import DeliveryAddress, DeliveryZone
from payments.models import Payment, PaymentMethod, PaymentStatus


class OrderWorkflowTest(TestCase):
    """Integration test for complete order workflow"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create category and menu item
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
        
        # Create delivery zone and address
        self.delivery_zone = DeliveryZone.objects.create(
            name='Inside Hospital',
            description='Delivery inside hospital premises',
            delivery_charge=Decimal('500.00'),
            is_active=True
        )
        self.delivery_address = DeliveryAddress.objects.create(
            user=self.user,
            label='Home',
            full_name='Test User',
            phone='+250788123456',
            address_line1='123 Test St',
            city='Kigali',
            zone=self.delivery_zone,
            is_default=True
        )
    
    def test_complete_order_workflow(self):
        """Test complete order workflow: login -> add to cart -> checkout -> order"""
        # 1. Login
        self.client.login(username='testuser', password='testpass123')
        
        # 2. Add item to cart
        response = self.client.post(f'/orders/cart/add/{self.menu_item.id}/', {
            'quantity': 2
        })
        self.assertEqual(response.status_code, 302)
        
        # Verify cart
        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.get_item_count(), 2)
        self.assertEqual(cart.get_total(), Decimal('5000.00'))
        
        # 3. Go to checkout
        response = self.client.get('/orders/checkout/')
        self.assertEqual(response.status_code, 200)
        
        # 4. Place order
        response = self.client.post('/orders/checkout/', {
            'use_saved_address': 'true',
            'saved_address_id': self.delivery_address.id,
            'payment_method': PaymentMethod.CASH_ON_DELIVERY,
            'customer_name': 'Test User',
            'customer_phone': '+250788123456',
        })
        
        # Should redirect to payment confirmation
        self.assertEqual(response.status_code, 302)
        
        # Verify order was created
        order = Order.objects.filter(user=self.user).latest('created_at')
        self.assertIsNotNone(order)
        self.assertEqual(order.status, OrderStatus.PENDING)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.total, Decimal('5500.00'))  # 5000 + 500 delivery
        
        # Verify payment was created
        payment = Payment.objects.filter(order=order).first()
        self.assertIsNotNone(payment)
        self.assertEqual(payment.payment_method, PaymentMethod.CASH_ON_DELIVERY)
        self.assertEqual(payment.status, PaymentStatus.PENDING)
        
        # Verify cart is empty after order
        cart.refresh_from_db()
        self.assertEqual(cart.get_item_count(), 0)

