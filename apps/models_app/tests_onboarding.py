from django.test import TestCase
from django.urls import reverse
from apps.accounts.models import User
from .models import ModelProfile, Location, Service
from django.core.files.uploadedfile import SimpleUploadedFile
import io
from PIL import Image

def get_valid_image_file():
    file = io.BytesIO()
    image = Image.new('RGBA', size=(100, 100), color=(155, 0, 0))
    image.save(file, 'png')
    file.name = 'test.png'
    file.seek(0)
    return file

class OnboardingBehaviorTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number='0712345678', password='password')
        self.location = Location.objects.create(name="Nairobi", slug="nairobi")
        self.service = Service.objects.create(name="Massage", slug="massage")
        self.url = reverse('models:onboarding')
        self.client.force_login(self.user)

    def test_onboarding_requires_short_summary(self):
        image_content = get_valid_image_file().read()
        pfp = SimpleUploadedFile('test.png', image_content, content_type='image/png')
        data = {
            'model_name': 'Test Model',
            'pfp': pfp,
            'orientation': 'straight',
            'description': 'A long description',
            'primary_location': self.location.id,
            'services': [self.service.id],
            'privacy_protection': 'none',
            'short_summary': ''  # Empty
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIn('short_summary', form.errors)
        self.assertEqual(form.errors['short_summary'], ['This field is required.'])

    def test_onboarding_short_summary_max_length(self):
        image_content = get_valid_image_file().read()
        pfp = SimpleUploadedFile('test.png', image_content, content_type='image/png')
        long_summary = "a" * 41
        data = {
            'model_name': 'Test Model',
            'pfp': pfp,
            'orientation': 'straight',
            'description': 'A long description',
            'primary_location': self.location.id,
            'services': [self.service.id],
            'privacy_protection': 'none',
            'short_summary': long_summary
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIn('short_summary', form.errors)
        self.assertIn('Ensure this value has at most 40 characters', form.errors['short_summary'][0])

    def test_onboarding_success_with_short_summary(self):
        image_content = get_valid_image_file().read()
        pfp = SimpleUploadedFile('test.png', image_content, content_type='image/png')
        data = {
            'model_name': 'Valid Model',
            'pfp': pfp,
            'orientation': 'straight',
            'description': 'A long description',
            'primary_location': self.location.id,
            'services': [self.service.id],
            'privacy_protection': 'none',
            'short_summary': 'Hottest model in town'
        }
        response = self.client.post(self.url, data)
        # Check for successful redirection
        self.assertEqual(response.status_code, 302)
        profile = ModelProfile.objects.get(model_name='Valid Model')
        self.assertEqual(profile.short_summary, 'Hottest model in town')
