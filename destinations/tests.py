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


class KollamDestinationsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('import_thiruvananthapuram_destinations')
        call_command('import_kollam_destinations')

    def setUp(self):
        self.client = Client()
        self.kollam_district = District.objects.get(slug='kollam')
        self.tvm_district = District.objects.get(slug='thiruvananthapuram')

    def test_01_kollam_has_50_verified_destinations_and_tvm_preserved(self):
        """1. Verify Kollam has 50 destinations and Thiruvananthapuram's 50 remain intact."""
        self.assertEqual(Destination.objects.filter(district=self.kollam_district).count(), 50)
        self.assertEqual(Destination.objects.filter(district=self.tvm_district).count(), 50)
        self.assertEqual(Destination.objects.count(), 100)

    def test_02_wrong_district_places_excluded_from_kollam(self):
        """2. Verify Alappuzha (Krishnapuram Palace) & Thiruvananthapuram (Kappil) places are excluded from Kollam."""
        kollam_names = set(
            Destination.objects.filter(district=self.kollam_district).values_list('name', flat=True)
        )
        self.assertNotIn("Krishnapuram Palace", kollam_names)
        self.assertNotIn("Kappil Beach", kollam_names)
        self.assertNotIn("Kappil Lake", kollam_names)
        self.assertIn("Mayyanad Subramanya Swamy Temple", kollam_names)
        self.assertIn("Sambranikodi Island", kollam_names)
        self.assertIn("Punalur Suspension Bridge", kollam_names)

    def test_03_kollam_coordinates_within_district_bounds(self):
        """3. Verify every Kollam destination has valid GPS coordinates strictly inside Kollam bounds."""
        for dest in Destination.objects.filter(district=self.kollam_district):
            # Kollam spans ~8.75 to 9.16 N, 76.45 to 77.26 E
            self.assertGreaterEqual(float(dest.latitude), 8.70, f"Latitude too low for {dest.name}")
            self.assertLessEqual(float(dest.latitude), 9.20, f"Latitude too high for {dest.name}")
            self.assertGreaterEqual(float(dest.longitude), 76.40, f"Longitude too low for {dest.name}")
            self.assertLessEqual(float(dest.longitude), 77.30, f"Longitude too high for {dest.name}")
            self.assertTrue(bool(dest.source_name), f"Missing source for {dest.name}")
            self.assertEqual(dest.verification_status, VerificationStatus.VERIFIED)

    def test_04_kollam_list_view_loads_with_50_markers(self):
        """4. Verify Kollam list page loads with HTTP 200 and strictly 50 Kollam map markers."""
        url = reverse('destinations:kollam_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Kollam Interactive Destination Map")
        self.assertContains(response, "Ashtamudi Lake")
        self.assertContains(response, "Jatayu Earth's Center")
        self.assertContains(response, "Palaruvi Waterfalls")
        self.assertContains(response, "Mayyanad Subramanya Swamy Temple")
        self.assertNotContains(response, "Kovalam Beach")
        self.assertNotContains(response, "Krishnapuram Palace")
        self.assertEqual(len(response.context['map_markers']), 50)

    def test_05_kollam_search_and_category_filters(self):
        """5. Test Kollam category and search query filters."""
        url = reverse('destinations:kollam_list')
        res_cat = self.client.get(url, {'category': 'waterfalls'})
        self.assertEqual(res_cat.status_code, 200)
        self.assertContains(res_cat, "Palaruvi Waterfalls")
        self.assertNotContains(res_cat, "Kollam Beach")

        res_search = self.client.get(url, {'q': 'Jatayu'})
        self.assertEqual(res_search.status_code, 200)
        self.assertEqual(res_search.context['total_count'], 1)
        self.assertContains(res_search, "Jatayu Earth's Center")
        self.assertNotContains(res_search, "Sambranikodi Island")

    def test_06_kollam_destination_detail_and_homepage_links(self):
        """6. Verify Kollam destination detail view and active district pill on homepage."""
        detail_url = reverse('destinations:destination_detail', kwargs={
            'district_slug': 'kollam',
            'slug': 'mayyanad-subramanya-swamy-temple'
        })
        res = self.client.get(detail_url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Mayyanad Subramanya Swamy Temple")
        self.assertContains(res, "Back to Kollam")

        home_res = self.client.get(reverse('core:home'))
        self.assertEqual(home_res.status_code, 200)
        self.assertContains(home_res, reverse('destinations:district_list', kwargs={'district_slug': 'kollam'}))
        self.assertContains(home_res, reverse('destinations:district_list', kwargs={'district_slug': 'thiruvananthapuram'}))

    def test_07_kollam_import_idempotency(self):
        """7. Running Kollam import twice keeps strictly 50 Kollam destinations and 100 total."""
        call_command('import_kollam_destinations')
        self.assertEqual(Destination.objects.filter(district=self.kollam_district).count(), 50)
        self.assertEqual(Destination.objects.count(), 100)

