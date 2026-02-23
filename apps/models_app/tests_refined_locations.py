from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.accounts.models import User
from .models import Location, Service, ModelProfile

class RefinedLocationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number='0711111111', password='password')
        self.client.force_login(self.user)
        self.loc1 = Location.objects.create(name='Westlands', slug='westlands')
        self.loc2 = Location.objects.create(name='Kilimani', slug='kilimani')
        self.loc3 = Location.objects.create(name='Lavington', slug='lavington')
        self.svc = Service.objects.create(name='Massage', slug='massage')
        self.url = reverse('models:onboarding')

    def test_onboarding_location_separation(self):
        """
        Behavior: A model selects one primary location and multiple nearby locations.
        """
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        pfp = SimpleUploadedFile('test.gif', small_gif, content_type='image/gif')

        data = {
            'model_name': 'Test Model',
            'pfp': pfp,
            'short_summary': 'Hottest in Westlands',
            'orientation': 'straight',
            'description': 'Description',
            'primary_location': self.loc1.pk,
            'nearby_locations': [self.loc2.pk, self.loc3.pk],
            'services': [self.svc.pk],
            'privacy_protection': 'none'
        }
        
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        
        profile = ModelProfile.objects.get(user=self.user)
        self.assertEqual(profile.primary_location, self.loc1)
        self.assertEqual(profile.nearby_locations.count(), 2)
        self.assertIn(self.loc2, profile.nearby_locations.all())
        self.assertIn(self.loc3, profile.nearby_locations.all())
