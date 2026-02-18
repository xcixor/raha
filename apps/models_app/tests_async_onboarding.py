from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.accounts.models import User
from .models import Location, Service

class AsyncOnboardingTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number='0755555555', password='password')
        self.client.force_login(self.user)
        self.loc = Location.objects.create(name='Test Loc', slug='test-loc')
        self.svc = Service.objects.create(name='Test Svc', slug='test-svc')
        self.url = reverse('models:onboarding')

    def test_htmx_onboarding_returns_redirect_header(self):
        """
        Behavior: When onboarding is submitted via HTMX, the response should 
        contain the 'HX-Redirect' header instead of a standard 302 redirect.
        """
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        pfp = SimpleUploadedFile('test.gif', small_gif, content_type='image/gif')

        data = {
            'model_name': 'AsyncModel',
            'pfp': pfp,
            'orientation': 'straight',
            'description': 'Hello world',
            'primary_location': self.loc.pk,
            'nearby_locations': [self.loc.pk],
            'services': [self.svc.pk],
            'privacy_protection': 'none'
        }
        
        # Simulate HTMX request
        response = self.client.post(self.url, data, HTTP_HX_REQUEST='true')
        
        # Check for HTMX Redirect header
        self.assertEqual(response.status_code, 200)
        self.assertIn('HX-Redirect', response)
        self.assertEqual(response['HX-Redirect'], reverse('root'))

    def test_onboarding_form_has_indicator(self):
        """
        Behavior: The onboarding template must contain the full-screen loader indicator.
        """
        response = self.client.get(self.url)
        self.assertContains(response, 'id="onboarding-loader"')
        self.assertContains(response, 'hx-indicator="#onboarding-loader"')
