from django.test import TestCase
from django.urls import reverse
from ..models import User

class RegistrationBehaviorTest(TestCase):
    def test_user_can_register_with_phone_and_password(self):
        """
        Behavior: A user can create an account using their phone and password.
        """
        response = self.client.post(reverse('accounts:register'), {
            'phone_number': '0711111111',
            'confirm_phone_number': '0711111111',
            'password': 'securepassword123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(phone_number='0711111111').exists())
