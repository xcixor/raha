from django.test import TestCase
from django.urls import reverse
from ..models import County, LocationGroup, Location

class LocationHierarchyTest(TestCase):
    def setUp(self):
        self.county = County.objects.create(name='Nairobi', slug='nairobi')
        self.group_cbd = LocationGroup.objects.create(name='CBD Area', county=self.county, slug='cbd-area')
        self.group_west = LocationGroup.objects.create(name='Westlands Area', county=self.county, slug='westlands-area')
        
        self.loc_cbd1 = Location.objects.create(name='Nairobi CBD', slug='nairobi-cbd', group=self.group_cbd)
        self.loc_cbd2 = Location.objects.create(name='Ngara', slug='ngara', group=self.group_cbd)
        self.loc_west1 = Location.objects.create(name='Westlands', slug='westlands', group=self.group_west)

    def test_location_hierarchy_integrity(self):
        """
        Behavior: Verify that a Location correctly resolves to its Group and County.
        """
        self.assertEqual(self.loc_cbd1.group, self.group_cbd)
        self.assertEqual(self.loc_cbd1.group.county, self.county)

    def test_htmx_returns_locations_in_same_group(self):
        """
        Behavior: HTMX endpoint should return locations belonging to the same group as the primary location.
        """
        url = reverse('models:nearby_locations_htmx')
        response = self.client.get(url, {'primary_location_id': self.loc_cbd1.pk})
        
        self.assertEqual(response.status_code, 200)
        # Should include Ngara (same group)
        self.assertContains(response, 'Ngara')
        # Should NOT include Westlands (different group)
        self.assertNotContains(response, 'Westlands')

    def test_nearby_locations_exclude_primary(self):
        """
        Behavior: The list of nearby options should not include the primary location itself.
        """
        url = reverse('models:nearby_locations_htmx')
        response = self.client.get(url, {'primary_location_id': self.loc_cbd1.pk})
        
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Nairobi CBD')
