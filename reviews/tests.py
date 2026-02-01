from django.test import TestCase, Client
from django.contrib.auth.models import User
from menu.models import MenuItem, Category
from orders.models import Order
from .models import Review, ReviewHelpful


class ReviewsTestCase(TestCase):
	def setUp(self):
		self.client = Client()
		self.user = User.objects.create_user(username='tester', password='pass')
		self.cat = Category.objects.create(name='Test', slug='test')
		self.item = MenuItem.objects.create(
			name='Test Item', description='Delicious', category=self.cat, price=10.00
		)

	def test_add_review(self):
		self.client.login(username='tester', password='pass')
		resp = self.client.post(f'/reviews/item/{self.item.id}/add/', {
			'rating': 5,
			'title': 'Great',
			'comment': 'Really good meal.'
		})
		self.assertEqual(resp.status_code, 302)
		self.assertTrue(Review.objects.filter(user=self.user, menu_item=self.item).exists())

	def test_mark_helpful(self):
		# create review
		review = Review.objects.create(user=self.user, menu_item=self.item, rating=4, comment='Nice food')
		self.client.login(username='tester', password='pass')
		resp = self.client.post(f'/reviews/{review.id}/helpful/')
		self.assertIn(resp.status_code, (200, 302))
		self.assertTrue(ReviewHelpful.objects.filter(review=review, user=self.user).exists())
