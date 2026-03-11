import json
import os
import tempfile
from django.test import TestCase
from django.core.management import call_command
from io import StringIO
from apps.models_app.models.location import County, LocationGroup, Location
from apps.models_app.models.service import Service

# Test data mimicking what the scraper produces
MOCK_SCRAPER_DATA = {
    "locations": [
        {"county": "Nairobi", "group": "General", "name": "Kilimani"},
        {"county": "Nairobi", "group": "General", "name": "Westlands"},
        {"county": "Kiambu", "group": "General", "name": "Ruaka"}
    ],
    "services": [
        "Massage", "Incall"
    ]
}

class TestScraperSeeder(TestCase):

    def setUp(self):
        # Create a temporary JSON file with mock data
        self.temp_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json')
        json.dump(MOCK_SCRAPER_DATA, self.temp_file)
        self.temp_file.close()

    def tearDown(self):
        # Remove the temp file
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)

    def test_seed_nairobihot_command(self):
        """Test the seeder management command using mock JSON."""
        out = StringIO()
        
        # Run the command
        call_command('seed_nairobihot', file=self.temp_file.name, stdout=out)
        
        output = out.getvalue()
        
        # Assert output messages
        self.assertIn("Seeding Complete!", output)
        self.assertIn("Created 2 new Services", output)
        
        # Assert DB State - Services
        self.assertEqual(Service.objects.count(), 2)
        self.assertTrue(Service.objects.filter(name="Massage").exists())
        self.assertTrue(Service.objects.filter(name="Incall").exists())
        
        # Assert DB State - Counties
        self.assertEqual(County.objects.count(), 2)
        self.assertTrue(County.objects.filter(name="Nairobi").exists())
        self.assertTrue(County.objects.filter(name="Kiambu").exists())
        
        # Assert DB State - Groups
        self.assertEqual(LocationGroup.objects.count(), 2)
        self.assertTrue(LocationGroup.objects.filter(name="Nairobi - General", county__name="Nairobi").exists())
        
        # Assert DB State - Locations
        self.assertEqual(Location.objects.count(), 3)
        self.assertTrue(Location.objects.filter(name="Kilimani", group__county__name="Nairobi").exists())
        self.assertTrue(Location.objects.filter(name="Ruaka", group__county__name="Kiambu").exists())

    def test_seed_nairobihot_idempotent(self):
        """Ensure running the seeder multiple times does not duplicate records."""
        out = StringIO()
        call_command('seed_nairobihot', file=self.temp_file.name, stdout=out)
        call_command('seed_nairobihot', file=self.temp_file.name, stdout=out)
        
        # Record counts should be the same as if it ran once
        self.assertEqual(Service.objects.count(), 2)
        self.assertEqual(County.objects.count(), 2)
        self.assertEqual(Location.objects.count(), 3)
