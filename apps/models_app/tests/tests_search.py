from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.accounts.models import User
from apps.models_app.models import ModelProfile, Service, Location, LocationGroup, County

class ModelSearchTests(TestCase):
    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(phone_number='0711111111', password='password')
        self.user2 = User.objects.create_user(phone_number='0722222222', password='password')
        self.user3 = User.objects.create_user(phone_number='0733333333', password='password')
        
        # Create Services
        self.massage = Service.objects.create(name="Massage")
        self.escort = Service.objects.create(name="Escort")
        
        # Create Locations
        self.nairobi_county = County.objects.create(name="Nairobi")
        self.mombasa_county = County.objects.create(name="Mombasa")
        
        self.nairobi_group = LocationGroup.objects.create(county=self.nairobi_county, name="Nairobi Central")
        self.mombasa_group = LocationGroup.objects.create(county=self.mombasa_county, name="Mombasa Island")
        
        self.westlands = Location.objects.create(group=self.nairobi_group, name="Westlands")
        self.nyali = Location.objects.create(group=self.mombasa_group, name="Nyali")
        
        pfp = SimpleUploadedFile('test.jpg', b'dummydata', content_type='image/jpeg')

        # Create Models
        # Alice: Nairobi, Massage
        self.alice = ModelProfile.objects.create(
            user=self.user1,
            model_name="Alice",
            pfp=pfp,
            is_active=True,
            primary_location=self.westlands
        )
        self.alice.services.add(self.massage)
        
        # Bob: Mombasa, Escort
        self.bob = ModelProfile.objects.create(
            user=self.user2,
            model_name="Bob",
            pfp=pfp,
            is_active=True,
            primary_location=self.nyali
        )
        self.bob.services.add(self.escort)
        
        # Charlie: Nairobi, Massage + Escort
        self.charlie = ModelProfile.objects.create(
            user=self.user3,
            model_name="Charlie",
            pfp=pfp,
            is_active=True,
            primary_location=self.westlands
        )
        self.charlie.services.add(self.massage, self.escort)

    def test_search_by_name(self):
        url = reverse('models:list')
        response = self.client.get(url, {'q': 'Alice'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alice")
        self.assertNotContains(response, "Bob")
        self.assertNotContains(response, "Charlie")

    def test_search_by_service(self):
        url = reverse('models:list')
        response = self.client.get(url, {'q': 'Massage'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alice")
        self.assertContains(response, "Charlie")
        self.assertNotContains(response, "Bob")

    def test_search_by_county(self):
        url = reverse('models:list')
        response = self.client.get(url, {'q': 'Nairobi'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alice")
        self.assertContains(response, "Charlie")
        self.assertNotContains(response, "Bob")

    def test_search_by_location(self):
        url = reverse('models:list')
        response = self.client.get(url, {'q': 'Nyali'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bob")
        self.assertNotContains(response, "Alice")
        self.assertNotContains(response, "Charlie")

    def test_search_partial_match(self):
        url = reverse('models:list')
        response = self.client.get(url, {'q': 'ali'}) 
        self.assertContains(response, "Alice")
        self.assertNotContains(response, "Bob")

    def test_search_no_results(self):
        url = reverse('models:list')
        response = self.client.get(url, {'q': 'NonExistent'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Alice")
        self.assertNotContains(response, "Bob")
        self.assertNotContains(response, "Charlie")
