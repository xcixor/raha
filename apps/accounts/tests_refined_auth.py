from django.test import TestCase
from django.urls import reverse
from apps.accounts.models import User

class RefinedAuthFlowTest(TestCase):
    def setUp(self):
        self.register_url = reverse('accounts:register')

    def test_phone_number_validation_rules(self):
        """
        Behavior: Phone number must be exactly 10 digits starting with 07.
        """
        invalid_numbers = [
            '1234567890',  # Doesn't start with 0
            '071234567',   # 9 digits
            '07123456789', # 11 digits
            '0612345678',  # Doesn't start with 07
            'abcdefghij'   # Non-digits
        ]
        for phone in invalid_numbers:
            response = self.client.post(self.register_url, {
                'phone_number': phone,
                'confirm_phone_number': phone,
                'password': 'password123'
            })
            self.assertEqual(response.status_code, 200)
            form = response.context['form']
            self.assertIn('phone_number', form.errors)
            self.assertEqual(form.errors['phone_number'][0], 'Enter a valid 10-digit phone number starting with 07.')

    def test_phone_confirmation_must_match(self):
        """
        Behavior: phone_number and confirm_phone_number must match.
        """
        response = self.client.post(self.register_url, {
            'phone_number': '0712345678',
            'confirm_phone_number': '0712345679',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIn('confirm_phone_number', form.errors)
        self.assertEqual(form.errors['confirm_phone_number'][0], 'Phone numbers do not match.')

    def test_valid_registration_flow(self):
        """
        Behavior: Registration succeeds with valid 10-digit 07... number and matching confirmation.
        """
        response = self.client.post(self.register_url, {
            'phone_number': '0712345678',
            'confirm_phone_number': '0712345678',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(phone_number='0712345678').exists())
