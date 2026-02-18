from django.test import TestCase
from django.urls import reverse
from apps.accounts.models import User

class AuthFlowTest(TestCase):
    def setUp(self):
        self.register_url = reverse('accounts:register')
        self.login_url = reverse('accounts:login')
        self.phone = '0700000000'
        self.password = 'testpass123'

    def test_registration_flow(self):
        # Register a new user
        response = self.client.post(self.register_url, {
            'phone_number': self.phone,
            'confirm_phone_number': self.phone,
            'password': self.password
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(phone_number=self.phone).exists())

    def test_duplicate_registration_fails(self):
        # Create user first
        User.objects.create_user(phone_number=self.phone, password=self.password)
        # Try to register again
        response = self.client.post(self.register_url, {
            'phone_number': self.phone,
            'confirm_phone_number': self.phone,
            'password': self.password
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "User with this Phone number already exists")

    def test_login_flow(self):
        # Create user
        User.objects.create_user(phone_number=self.phone, password=self.password)
        # Login
        response = self.client.post(self.login_url, {
            'phone_number': self.phone,
            'password': self.password
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.phone)

    def test_logout_url_exists(self):
        # Verify logout URL resolves
        url = reverse('accounts:logout')
        self.assertIsNotNone(url)
