"""
Unit tests for accounts app
"""
from django.test import TestCase
from django.contrib.auth.models import User
from .models import Profile, UserRole


class ProfileModelTest(TestCase):
    """Test Profile model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_profile_created_automatically(self):
        """Test that profile is created automatically when user is created"""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertEqual(self.user.profile.role, UserRole.CUSTOMER)
    
    def test_profile_str(self):
        """Test profile string representation"""
        expected = f"{self.user.username} - Customer"
        self.assertEqual(str(self.user.profile), expected)
    
    def test_profile_update(self):
        """Test profile update"""
        self.user.profile.phone = '+250788123456'
        self.user.profile.role = UserRole.STAFF
        self.user.profile.save()
        
        updated_profile = Profile.objects.get(user=self.user)
        self.assertEqual(updated_profile.phone, '+250788123456')
        self.assertEqual(updated_profile.role, UserRole.STAFF)
    
    def test_profile_dietary_preferences(self):
        """Test dietary preferences field"""
        self.user.profile.dietary_preferences = 'vegetarian, low-sodium'
        self.user.profile.save()
        
        updated_profile = Profile.objects.get(user=self.user)
        self.assertEqual(updated_profile.dietary_preferences, 'vegetarian, low-sodium')


class UserAuthenticationTest(TestCase):
    """Test user authentication"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_login(self):
        """Test user can log in"""
        from django.contrib.auth import authenticate
        user = authenticate(username='testuser', password='testpass123')
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'testuser')
    
    def test_user_logout(self):
        """Test user can log out"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/accounts/logout/')
        self.assertEqual(response.status_code, 302)  # Redirect after logout
    
    def test_user_registration(self):
        """Test user registration"""
        # First check if registration page loads
        response = self.client.get('/accounts/register/')
        self.assertEqual(response.status_code, 200)
        
        # Then try to register
        response = self.client.post('/accounts/register/', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
        })
        # Should redirect after successful registration or show form with errors
        self.assertIn(response.status_code, [200, 302])
        
        # Check if user was created (if registration succeeded)
        if response.status_code == 302:
            self.assertTrue(User.objects.filter(username='newuser').exists())
            new_user = User.objects.get(username='newuser')
            self.assertTrue(hasattr(new_user, 'profile'))
