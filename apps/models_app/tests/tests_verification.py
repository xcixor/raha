from django.test import TestCase
from ..models import ModelProfile, Location
from ..services_verification import VerificationService
from apps.accounts.models import User

class VerificationServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number='0799999999', password='password')
        self.loc = Location.objects.create(name='Nairobi', slug='nairobi')
        self.profile = ModelProfile.objects.create(
            user=self.user, 
            model_name="Verified Model", 
            primary_location=self.loc
        )

    def test_verify_profile_marks_active_and_verified(self):
        VerificationService.verify_profile(self.profile.id)
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.is_verified)
        self.assertTrue(self.profile.is_active)

    def test_reject_profile_marks_inactive_and_unverified(self):
        self.profile.is_verified = True
        self.profile.is_active = True
        self.profile.save()
        
        VerificationService.reject_profile(self.profile.id)
        self.profile.refresh_from_db()
        self.assertFalse(self.profile.is_verified)
        self.assertFalse(self.profile.is_active)
