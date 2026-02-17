import tempfile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.accounts.models import User
from .models import Location, Service, ModelProfile

class OnboardingBehaviorTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number='0711111111', password='password')
        self.client.force_login(self.user)
        self.loc = Location.objects.create(name='Test Loc', slug='test-loc')
        self.svc = Service.objects.create(name='Test Svc', slug='test-svc')

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_model_can_complete_onboarding(self):
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        pfp = SimpleUploadedFile('test.gif', small_gif, content_type='image/gif')

        # Debugging the M2M issue: testing with a single location ID
        data = {
            'model_name': 'Hottie X',
            'pfp': pfp,
            'orientation': 'straight',
            'description': 'Hello world',
            'locations': [self.loc.pk],
            'services': [self.svc.pk]
        }
        
        response = self.client.post(reverse('models:onboarding'), data)

        # Check for form errors if redirect failed
        if response.status_code == 200:
            print(f"Form Errors: {response.context['form'].errors}")

        self.assertEqual(response.status_code, 302)
        profile = ModelProfile.objects.get(user=self.user)
        self.assertEqual(profile.locations.count(), 1)
