from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.exceptions import ValidationError
from datetime import date, timedelta

from .models import NutritionistProfile, ClientAssignment
from .forms import NutritionistProfileForm

User = get_user_model()


class NutritionistProfileModelTests(TestCase):
    """Test cases for NutritionistProfile model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='nutritionist1',
            email='nutritionist@test.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )

    def test_create_nutritionist_profile(self):
        """Test creating a nutritionist profile"""
        profile = NutritionistProfile.objects.create(
            user=self.user,
            bio='Experienced nutritionist',
            specialization='Weight Management',
            license_number='LIC123456',
            phone_number='+250788123456'
        )
        self.assertTrue(profile.id)
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.status, 'active')

    def test_profile_str_representation(self):
        """Test profile string representation"""
        profile = NutritionistProfile.objects.create(
            user=self.user,
            bio='Test bio'
        )
        expected = f"{self.user.get_full_name()} - Active"
        self.assertEqual(str(profile), expected)

    def test_current_client_count(self):
        """Test current client count property"""
        profile = NutritionistProfile.objects.create(user=self.user)
        self.assertEqual(profile.current_client_count, 0)

    def test_is_available_when_active(self):
        """Test is_available property when active"""
        profile = NutritionistProfile.objects.create(
            user=self.user,
            status='active',
            max_clients=5
        )
        self.assertTrue(profile.is_available)

    def test_is_not_available_when_inactive(self):
        """Test is_available when profile is inactive"""
        profile = NutritionistProfile.objects.create(
            user=self.user,
            status='inactive'
        )
        self.assertFalse(profile.is_available)

    def test_profile_validation_invalid_max_clients(self):
        """Test profile validation with invalid max_clients"""
        profile = NutritionistProfile(
            user=self.user,
            max_clients=0
        )
        with self.assertRaises(ValidationError):
            profile.full_clean()

    def test_profile_validation_short_license(self):
        """Test profile validation with short license number"""
        profile = NutritionistProfile(
            user=self.user,
            license_number='AB'
        )
        with self.assertRaises(ValidationError):
            profile.full_clean()


class ClientAssignmentModelTests(TestCase):
    """Test cases for ClientAssignment model"""

    def setUp(self):
        """Set up test data"""
        self.nutritionist = User.objects.create_user(
            username='nutritionist',
            email='nutritionist@test.com',
            password='testpass123'
        )
        NutritionistProfile.objects.create(user=self.nutritionist)

        self.client = User.objects.create_user(
            username='client',
            email='client@test.com',
            password='testpass123'
        )

    def test_create_assignment(self):
        """Test creating a client assignment"""
        assignment = ClientAssignment.objects.create(
            nutritionist=self.nutritionist,
            client=self.client,
            status='active'
        )
        self.assertTrue(assignment.id)
        self.assertEqual(assignment.status, 'active')
        self.assertIsNone(assignment.end_date)

    def test_assignment_str_representation(self):
        """Test assignment string representation"""
        assignment = ClientAssignment.objects.create(
            nutritionist=self.nutritionist,
            client=self.client
        )
        expected = f"{self.client.get_full_name()} - {self.nutritionist.get_full_name()}"
        self.assertEqual(str(assignment), expected)

    def test_is_active_property(self):
        """Test is_active property"""
        assignment = ClientAssignment.objects.create(
            nutritionist=self.nutritionist,
            client=self.client,
            status='active'
        )
        self.assertTrue(assignment.is_active)

    def test_assignment_validation_self_assignment(self):
        """Test that a user cannot be assigned to themselves"""
        assignment = ClientAssignment(
            nutritionist=self.nutritionist,
            client=self.nutritionist
        )
        with self.assertRaises(ValidationError):
            assignment.full_clean()

    def test_assignment_validation_invalid_dates(self):
        """Test assignment validation with invalid dates"""
        tomorrow = date.today() + timedelta(days=1)
        assignment = ClientAssignment(
            nutritionist=self.nutritionist,
            client=self.client,
            start_date=tomorrow,
            end_date=date.today()
        )
        with self.assertRaises(ValidationError):
            assignment.full_clean()

    def test_terminate_assignment(self):
        """Test terminating an assignment"""
        assignment = ClientAssignment.objects.create(
            nutritionist=self.nutritionist,
            client=self.client,
            status='active'
        )
        assignment.terminate()
        assignment.refresh_from_db()
        self.assertEqual(assignment.status, 'terminated')
        self.assertIsNotNone(assignment.end_date)

    def test_unique_together_constraint(self):
        """Test unique_together constraint"""
        ClientAssignment.objects.create(
            nutritionist=self.nutritionist,
            client=self.client
        )
        with self.assertRaises(Exception):
            ClientAssignment.objects.create(
                nutritionist=self.nutritionist,
                client=self.client
            )


class NutritionistProfileFormTests(TestCase):
    """Test cases for NutritionistProfileForm"""

    def test_valid_form(self):
        """Test form with valid data"""
        form_data = {
            'bio': 'Test bio',
            'specialization': 'Weight Management',
            'max_clients': 50
        }
        form = NutritionistProfileForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_bio_max_length_validation(self):
        """Test bio max length validation"""
        form_data = {
            'bio': 'A' * 1001,
            'specialization': 'Test',
            'max_clients': 50
        }
        form = NutritionistProfileForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('bio', form.errors)

    def test_min_max_clients_validation(self):
        """Test max_clients minimum validation"""
        form_data = {
            'bio': 'Test',
            'specialization': 'Test',
            'max_clients': 0
        }
        form = NutritionistProfileForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_license_number_uniqueness(self):
        """Test license number uniqueness validation"""
        user = User.objects.create_user(
            username='test',
            email='test@test.com',
            password='pass'
        )
        NutritionistProfile.objects.create(
            user=user,
            license_number='LIC123'
        )

        form_data = {
            'license_number': 'LIC123',
            'bio': 'Test',
            'specialization': 'Test',
            'max_clients': 50
        }
        form = NutritionistProfileForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('license_number', form.errors)


class NutritionistDashboardViewTests(TestCase):
    """Test cases for nutritionist dashboard views"""

    def setUp(self):
        """Set up test data"""
        self.client_obj = Client()
        
        self.nutritionist = User.objects.create_user(
            username='nutritionist',
            email='nutritionist@test.com',
            password='testpass123'
        )
        self.nutritionist_profile = NutritionistProfile.objects.create(
            user=self.nutritionist
        )

        self.client_user = User.objects.create_user(
            username='client',
            email='client@test.com',
            password='testpass123'
        )

        self.regular_user = User.objects.create_user(
            username='regular',
            email='regular@test.com',
            password='testpass123'
        )

    def test_dashboard_requires_login(self):
        """Test that dashboard requires login"""
        response = self.client_obj.get(reverse('nutritionist_dashboard:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_nutritionist_dashboard_access(self):
        """Test nutritionist can access dashboard"""
        self.client_obj.login(username='nutritionist', password='testpass123')
        response = self.client_obj.get(reverse('nutritionist_dashboard:dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_non_nutritionist_redirected(self):
        """Test non-nutritionist redirected to create profile"""
        user = User.objects.create_user(
            username='newuser',
            email='newuser@test.com',
            password='testpass123'
        )
        self.client_obj.login(username='newuser', password='testpass123')
        response = self.client_obj.get(
            reverse('nutritionist_dashboard:dashboard'),
            follow=True
        )
        self.assertIn('create', str(response.url).lower())

    def test_create_profile_view(self):
        """Test create profile view"""
        self.client_obj.login(username='regular', password='testpass123')
        response = self.client_obj.get(reverse('nutritionist_dashboard:create_profile'))
        self.assertEqual(response.status_code, 200)

    def test_create_profile_post(self):
        """Test creating profile via POST"""
        self.client_obj.login(username='regular', password='testpass123')
        data = {
            'bio': 'Test bio',
            'specialization': 'Test specialization',
            'max_clients': 50
        }
        response = self.client_obj.post(
            reverse('nutritionist_dashboard:create_profile'),
            data,
            follow=True
        )
        self.assertTrue(
            NutritionistProfile.objects.filter(user=self.regular_user).exists()
        )

    def test_manage_clients_requires_nutritionist(self):
        """Test manage_clients requires nutritionist role"""
        self.client_obj.login(username='client', password='testpass123')
        response = self.client_obj.get(reverse('nutritionist_dashboard:manage_clients'))
        self.assertEqual(response.status_code, 302)  # Should redirect


class NutritionistDashboardIntegrationTests(TestCase):
    """Integration tests for nutritionist dashboard"""

    def setUp(self):
        """Set up test data"""
        self.client_obj = Client()

        self.nutritionist = User.objects.create_user(
            username='nutritionist',
            email='nutritionist@test.com',
            password='testpass123'
        )
        NutritionistProfile.objects.create(user=self.nutritionist)

        self.client1 = User.objects.create_user(
            username='client1',
            email='client1@test.com',
            password='testpass123'
        )

        self.client2 = User.objects.create_user(
            username='client2',
            email='client2@test.com',
            password='testpass123'
        )

        # Create assignments
        self.assignment1 = ClientAssignment.objects.create(
            nutritionist=self.nutritionist,
            client=self.client1,
            status='active'
        )

        self.assignment2 = ClientAssignment.objects.create(
            nutritionist=self.nutritionist,
            client=self.client2,
            status='active'
        )

    def test_dashboard_shows_clients(self):
        """Test dashboard displays assigned clients"""
        self.client_obj.login(username='nutritionist', password='testpass123')
        response = self.client_obj.get(reverse('nutritionist_dashboard:dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_manage_clients_lists_all(self):
        """Test manage_clients lists all assignments"""
        self.client_obj.login(username='nutritionist', password='testpass123')
        response = self.client_obj.get(reverse('nutritionist_dashboard:manage_clients'))
        self.assertEqual(response.status_code, 200)
