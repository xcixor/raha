from django.test import TestCase
from django.urls import reverse
from apps.accounts.models import User
from ..models import ModelProfile

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
        profile = ModelProfile.objects.create(user=self.user, model_name="Test Model", pfp=pfp)
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('models:profile_detail', kwargs={'slug': profile.slug}))

    def test_nearby_locations_initially_hidden(self):
        """
        Behavior: The nearby locations container should be hidden before a primary location is selected.
        """
        self.client.force_login(self.user)
        response = self.client.get(reverse('models:onboarding'))
        self.assertEqual(response.status_code, 200)
        # Check that the container has the 'hidden' class
        self.assertContains(response, 'id=\"nearby-locations-container\" class=\"hidden\"')

class ModelDisplayTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number='0711111111', password='password')
        pfp = SimpleUploadedFile('test.jpg', b'dummydata', content_type='image/jpeg')
        self.active_profile = ModelProfile.objects.create(
            user=self.user, 
            model_name="Active Model", 
            pfp=pfp,
            is_active=True
        )
        self.inactive_profile = ModelProfile.objects.create(
            user=User.objects.create_user(phone_number='0722222222', password='password'),
            model_name="Inactive Model",
            pfp=pfp,
            is_active=False
        )

    def test_model_list_shows_only_active_models(self):
        url = reverse('models:list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Active Model")
        self.assertNotContains(response, "Inactive Model")

    def test_model_detail_view_publicly_accessible(self):
        url = reverse('models:profile_detail', kwargs={'slug': self.active_profile.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Active Model")
        # Ensure upload form is NOT visible to anonymous user
        self.assertNotContains(response, "Upload to Gallery")

    def test_model_detail_view_owner_sees_upload_form(self):
        self.client.force_login(self.user)
        url = reverse('models:profile_detail', kwargs={'slug': self.active_profile.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Upload to Gallery")
