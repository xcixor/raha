from django.test import TestCase
from django.urls import reverse
from ..models import Location, Service, ModelProfile
from apps.accounts.models import User

class UniqueConstraintTest(TestCase):
    def setUp(self):
        self.loc = Location.objects.create(name="Test", slug="test")

    def test_model_name_must_be_unique(self):
        """Behavior: Two profiles cannot have the same model name."""
        user1 = User.objects.create_user(phone_number='0711111111', password='pass')
        user2 = User.objects.create_user(phone_number='0722222222', password='pass')
        
        ModelProfile.objects.create(user=user1, model_name="UniqueName", primary_location=self.loc)
        
        with self.assertRaises(Exception): # Specific IntegrityError expected
            ModelProfile.objects.create(user=user2, model_name="UniqueName", primary_location=self.loc)
