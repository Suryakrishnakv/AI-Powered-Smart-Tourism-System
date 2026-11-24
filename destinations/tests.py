from django.test import TestCase, Client
from django.urls import reverse
from django.core.management import call_command
from destinations.models import District, Category, Destination
from core.models import VerificationStatus


class ThiruvananthapuramDestinationsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Run the idempotent management command to populate Thiruvananthapuram destinations
        call_command('import_thiruvananthapuram_destinations')

    def setUp(self):
        self.client = Client()
        self.tvm_district = District.objects.get(slug='thiruvananthapuram')

    def test_01_all_inserted_destinations_exist(self):
        """1. Verify exactly 50 destinations exist in the database."""
        count = Destination.objects.count()
        self.assertEqual(count, 50)

    def test_02_every_destination_belongs_strictly_to_thiruvananthapuram(self):
        """2. Verify 100% of destinations belong only to Thiruvananthapuram district."""
        non_tvm = Destination.objects.exclude(district=self.tvm_district)
        self.assertEqual(non_tvm.count(), 0)

        # Check total for Thiruvananthapuram
        tvm_count = Destination.objects.filter(district=self.tvm_district).count()
        self.assertEqual(tvm_count, 50)

    def test_03_no_duplicate_destinations_exist(self):
        """3. Verify zero duplicates exist across slugs and name+district combinations."""
        slug_count = Destination.objects.values('slug').distinct().count()
        self.assertEqual(slug_count, 50)

        name_district_count = Destination.objects.values('name', 'district').distinct().count()
        self.assertEqual(name_district_count, 50)

    def test_04_coordinates_are_valid_and_within_district_bounds(self):
        """4. Verify every destination has valid Kerala coordinates within Thiruvananthapuram bounds."""
        for dest in Destination.objects.all():
            # Thiruvananthapuram roughly spans latitude 8.25 to 8.90 and longitude 76.60 to 77.35
            self.assertGreaterEqual(float(dest.latitude), 8.20, f"Latitude too low for {dest.name}")
            self.assertLessEqual(float(dest.latitude), 9.00, f"Latitude too high for {dest.name}")
            self.assertGreaterEqual(float(dest.longitude), 76.50, f"Longitude too low for {dest.name}")
            self.assertLessEqual(float(dest.longitude), 77.40, f"Longitude too high for {dest.name}")
            self.assertTrue(bool(dest.source_name), f"Missing source for {dest.name}")
            self.assertEqual(dest.verification_status, VerificationStatus.VERIFIED)

    def test_05_destination_categories_assigned_properly(self):
        """5. Verify all destination categories exist and have assigned destinations."""
        categories = Category.objects.all()
        self.assertGreaterEqual(categories.count(), 6)
        for cat in categories:
            d_count = Destination.objects.filter(category=cat).count()
            self.assertGreater(d_count, 0, f"Category {cat.name} has no destinations assigned")

    def test_06_display_image_url_returns_valid_url(self):
        """6. Verify display_image_url returns a valid string/url."""
        for dest in Destination.objects.all():
            img_url = dest.display_image_url
            self.assertTrue(img_url.startswith('http') or img_url.startswith('/media/'))

    def test_07_thiruvananthapuram_list_view_loads_with_markers(self):
        """7. Verify Explore Thiruvananthapuram page loads with HTTP 200 and map markers."""
        url = reverse('destinations:thiruvananthapuram_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Thiruvananthapuram Interactive Destination Map")
        self.assertContains(response, "Kovalam Beach")
        self.assertContains(response, "Varkala Beach")
        self.assertContains(response, "Ponmudi Hill Station")
        self.assertContains(response, "Sree Padmanabhaswamy Temple")
        self.assertEqual(len(response.context['map_markers']), 50)

    def test_08_search_and_category_filters(self):
        """8. Test category and text search filtering."""
        list_url = reverse('destinations:thiruvananthapuram_list')

        # Filter by beaches
        res_beach = self.client.get(list_url, {'category': 'beaches-and-coastal'})
        self.assertEqual(res_beach.status_code, 200)
        self.assertContains(res_beach, "Kovalam Beach")
        self.assertNotContains(res_beach, "Ponmudi Hill Station")

        # Search by term 'Ponmudi'
        res_search = self.client.get(list_url, {'q': 'Ponmudi'})
        self.assertEqual(res_search.status_code, 200)
        self.assertContains(res_search, "Ponmudi Hill Station")
        self.assertNotContains(res_search, "Kovalam Beach")

    def test_09_destination_detail_view(self):
        """9. Test destination detail page for Kovalam Beach."""
        url = reverse('destinations:destination_detail', kwargs={
            'district_slug': 'thiruvananthapuram',
            'slug': 'kovalam-beach'
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Kovalam Beach")
        self.assertContains(response, "Official Data Verification Record")
        self.assertContains(response, "destinationMap")
        self.assertContains(response, "Department of Tourism, Govt. of Kerala")

    def test_10_idempotent_import_does_not_duplicate(self):
        """10. Running import command again must preserve exactly 50 records without duplicates."""
        call_command('import_thiruvananthapuram_destinations')
        self.assertEqual(Destination.objects.count(), 50)
