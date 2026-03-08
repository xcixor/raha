from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.accounts.models import User
from ..models import ModelProfile, Location, Service

class OnboardingIdempotencyTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number='0722222222', password='password')
        self.client.force_login(self.user)
        self.loc = Location.objects.create(name='Nairobi', slug='nairobi')
        self.svc = Service.objects.create(name='Massage', slug='massage')
        self.url = reverse('models:onboarding')

    def test_onboarding_twice_does_not_crash(self):
        """
        Behavior: If a user somehow submits the onboarding form twice, 
        it should update the existing profile instead of raising an IntegrityError.
        """
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        pfp = SimpleUploadedFile('test.gif', small_gif, content_type='image/gif')

        data = {
            'model_name': 'First Try',
            'short_summary': 'Summary 1',
            'orientation': 'straight',
            'description': 'Description 1',
            'primary_location': self.loc.pk,
            'nearby_locations': [self.loc.pk],
            'services': [self.svc.pk],
            'pfp': pfp,
            'privacy_protection': 'none'
        }
        # First submission
        resp1 = self.client.post(self.url, data)
        self.assertEqual(resp1.status_code, 302)
        self.assertEqual(ModelProfile.objects.count(), 1)
        
        # Second submission (maybe after a refresh or back button)
        pfp.seek(0)
        data['model_name'] = 'Second Try'
        data['pfp'] = pfp
        resp2 = self.client.post(self.url, data)
        self.assertEqual(resp2.status_code, 302)
        
        # Check that it updated the existing profile
        self.assertEqual(ModelProfile.objects.count(), 1)
        profile = ModelProfile.objects.get(user=self.user)
        self.assertEqual(profile.model_name, 'Second Try')
