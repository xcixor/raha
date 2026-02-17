from django.test import TestCase
from django.urls import reverse
from .models import User

class RegistrationBehaviorTest(TestCase):
    def test_user_can_register_with_phone_and_password(self):
        response = self.client.post(reverse('accounts:register'), {
            'phone_number': '0712345678',
            'password': 'testpassword123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(phone_number='0712345678').exists())

    def test_phone_number_must_be_unique(self):
        User.objects.create_user(phone_number='0712345678', password='password1')
        
        response = self.client.post(reverse('accounts:register'), {
            'phone_number': '0712345678',
            'password': 'password2'
        })
        
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('phone_number', form.errors)
