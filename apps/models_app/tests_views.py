from django.test import TestCase
from django.urls import reverse
from apps.accounts.models import User
from .models import ModelProfile

from django.core.files.uploadedfile import SimpleUploadedFile

class RootRedirectTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number='0733333333', password='password')
        self.url = reverse('root')

    def test_authenticated_user_without_profile_redirects_to_onboarding(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('models:onboarding'))

    def test_authenticated_user_with_profile_redirects_to_profile(self):
        pfp = SimpleUploadedFile('test.jpg', b'dummydata', content_type='image/jpeg')
        ModelProfile.objects.create(user=self.user, model_name="Test Model", pfp=pfp)
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('models:profile_detail'))

    def test_nearby_locations_initially_hidden(self):
        """
        Behavior: The nearby locations container should be hidden before a primary location is selected.
        """
        self.client.force_login(self.user)
        response = self.client.get(reverse('models:onboarding'))
        self.assertEqual(response.status_code, 200)
        # Check that the container has the 'hidden' class
        self.assertContains(response, 'id=\"nearby-locations-container\" class=\"hidden\"')
