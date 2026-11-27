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


class KeralaInteractiveMapTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('import_thiruvananthapuram_destinations')
        call_command('import_kollam_destinations')

    def setUp(self):
        self.client = Client()
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.user = User.objects.create_user(
            username='tourist_test',
            email='tourist_test@example.com',
            password='TestPassword123!'
        )

    def test_01_kerala_map_page_loads_with_all_destinations(self):
        """Verify the full-screen Kerala Interactive Map page loads with all 100 destinations."""
        url = reverse('destinations:kerala_map')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Kerala Tourism Map")
        self.assertContains(response, "kerala-interactive-map")
        self.assertContains(response, "initial-destinations-data")
        self.assertEqual(response.context['total_destinations_count'], 100)
        self.assertIn("Kovalam Beach", response.context['destinations_json'])
        self.assertIn("Jatayu Earth's Center", response.context['destinations_json'])

    def test_02_api_destinations_list_and_filters(self):
        """Verify API destination list returns JSON and respects filters."""
        url = reverse('destinations:api_destinations_list')

        # All destinations
        res_all = self.client.get(url)
        self.assertEqual(res_all.status_code, 200)
        data_all = res_all.json()
        self.assertEqual(data_all['status'], 'success')
        self.assertEqual(data_all['count'], 100)

        # District filter: Kollam only
        res_kollam = self.client.get(url, {'district': 'kollam'})
        data_kollam = res_kollam.json()
        self.assertEqual(data_kollam['count'], 50)
        for dest in data_kollam['destinations']:
            self.assertEqual(dest['district_slug'], 'kollam')

        # Query search
        res_search = self.client.get(url, {'q': 'Ponmudi'})
        data_search = res_search.json()
        self.assertGreaterEqual(data_search['count'], 1)
        search_names = [d['name'] for d in data_search['destinations']]
        self.assertIn('Ponmudi Hill Station', search_names)

    def test_03_api_nearby_destinations_haversine(self):
        """Verify nearby API calculates distances from GPS coordinates accurately and sorts closest first."""
        url = reverse('destinations:api_nearby_destinations')
        # Thiruvananthapuram center GPS: 8.5241 N, 76.9366 E
        res = self.client.get(url, {'lat': '8.5241', 'lng': '76.9366', 'radius': '15'})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['status'], 'success')
        self.assertGreater(data['count'], 0)
        
        # Verify sorted ascending by distance
        distances = [d['distance_km'] for d in data['destinations']]
        self.assertEqual(distances, sorted(distances))
        self.assertEqual(data['destinations'][0]['distance_type'], 'straight_line_haversine')

    def test_04_api_route_proxy_returns_geometry_and_metrics(self):
        """Verify route proxy API calculates multi-stop route metrics and valid GeoJSON geometry."""
        url = reverse('destinations:api_route_proxy')
        # Route from Kovalam Beach (76.97, 8.40) to Napier Museum (76.95, 8.51)
        res = self.client.get(url, {'coordinates': '76.9786,8.4021;76.9553,8.5147', 'profile': 'driving'})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('distance_km', data)
        self.assertGreater(data['distance_km'], 10.0) # roughly 13-18 km road distance
        self.assertGreater(data['duration_min'], 10)
        self.assertEqual(data['geometry']['type'], 'LineString')
        self.assertGreaterEqual(len(data['geometry']['coordinates']), 2)

    def test_05_api_save_trip_and_list_lifecycle(self):
        """Verify trip itinerary saving lifecycle: anonymous rejection, authenticated save, and retrieval."""
        save_url = reverse('destinations:api_save_trip')
        list_url = reverse('destinations:api_list_trips')

        d1 = Destination.objects.first()
        d2 = Destination.objects.last()

        payload = {
            'title': 'Southern Kerala Explorer',
            'notes': 'Scenic coastal and heritage tour',
            'destination_ids': [d1.id, d2.id],
            'total_distance_km': 65.5,
            'estimated_duration_min': 95
        }

        # Anonymous save attempt must return 401
        res_anon = self.client.post(save_url, data=payload, content_type='application/json')
        self.assertEqual(res_anon.status_code, 401)

        # Authenticate user and save
        self.client.force_login(self.user)
        res_auth = self.client.post(save_url, data=payload, content_type='application/json')
        self.assertEqual(res_auth.status_code, 200)
        res_data = res_auth.json()
        self.assertEqual(res_data['status'], 'success')
        self.assertIn('trip_id', res_data)

        # List trips for user
        res_list = self.client.get(list_url)
        self.assertEqual(res_list.status_code, 200)
        list_data = res_list.json()
        self.assertEqual(list_data['status'], 'success')
        self.assertEqual(len(list_data['trips']), 1)
        self.assertEqual(list_data['trips'][0]['title'], 'Southern Kerala Explorer')
        self.assertEqual(list_data['trips'][0]['stops_count'], 2)

    def test_06_api_districts_geojson_returns_14_official_boundaries(self):
        """Verify the district GeoJSON API returns all 14 official district boundaries of Kerala."""
        url = reverse('destinations:api_districts_geojson')
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res['Content-Type'], 'application/json')
        data = res.json()
        self.assertEqual(data['type'], 'FeatureCollection')
        self.assertEqual(len(data['features']), 14)

        district_names = [f['properties']['name'] for f in data['features']]
        self.assertIn('Thiruvananthapuram', district_names)
        self.assertIn('Kollam', district_names)
        self.assertIn('Wayanad', district_names)
        self.assertIn('Ernakulam', district_names)
        self.assertIn('Kasaragod', district_names)

    def test_07_api_autocomplete_suggestions(self):
        """Verify real-time autocomplete matches destinations across name and activities."""
        url = reverse('destinations:api_autocomplete')

        # Short query (< 2 chars) must return empty results
        res_short = self.client.get(url, {'q': 'k'})
        self.assertEqual(res_short.status_code, 200)
        self.assertEqual(len(res_short.json()['results']), 0)

        # Matched query
        res = self.client.get(url, {'q': 'Kovalam'})
        self.assertEqual(res.status_code, 200)
        results = res.json()['results']
        self.assertGreaterEqual(len(results), 1)
        names = [r['name'] for r in results]
        self.assertIn('Kovalam Beach', names)
        self.assertIn('lat', results[0])
        self.assertIn('lng', results[0])

    def test_08_api_add_review_lifecycle(self):
        """Verify review submission lifecycle: unauthenticated rejection and tourist review creation."""
        url = reverse('destinations:api_add_review')
        dest = Destination.objects.first()

        # Anonymous rejection
        res_anon = self.client.post(
            url,
            data={'destination_id': dest.id, 'rating': 5, 'comment': 'Breathtaking scenery!'},
            content_type='application/json'
        )
        self.assertEqual(res_anon.status_code, 401)

        # Authenticated tourist submission
        self.client.force_login(self.user)
        res_auth = self.client.post(
            url,
            data={
                'destination_id': dest.id,
                'rating': 5,
                'title': 'Must visit in Kerala',
                'comment': 'Stunning sunrise views, clean pathways, and very polite local guides.'
            },
            content_type='application/json'
        )
        self.assertEqual(res_auth.status_code, 200)
        data = res_auth.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['average_rating'], 5.0)
        self.assertEqual(data['reviews_count'], 1)

    def test_09_destination_detail_page_has_complete_information_and_reviews(self):
        """Verify destination detail page displays complete visitor advice, safety rules, and reviews."""
        dest = Destination.objects.get(slug='kovalam-beach')
        url = dest.get_absolute_url()
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Visitor Guidelines & Tourist Advice")
        self.assertContains(res, "Tourist Reviews & Ratings")
        self.assertContains(res, "Official Data Verification Record")
        self.assertContains(res, "Nearby Verified Attractions")


class PathanamthittaDestinationsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('import_thiruvananthapuram_destinations')
        call_command('import_kollam_destinations')
        call_command('import_pathanamthitta_destinations')

    def setUp(self):
        self.client = Client()
        self.tvm_district = District.objects.get(slug='thiruvananthapuram')
        self.kollam_district = District.objects.get(slug='kollam')
        self.pta_district = District.objects.get(slug='pathanamthitta')

    def test_01_pathanamthitta_has_50_destinations_and_others_preserved(self):
        """1. Verify Pathanamthitta has exactly 50 destinations, TVM has 50, Kollam has 50 (Total: 150)."""
        pta_count = Destination.objects.filter(district=self.pta_district).count()
        tvm_count = Destination.objects.filter(district=self.tvm_district).count()
        kollam_count = Destination.objects.filter(district=self.kollam_district).count()
        total_count = Destination.objects.count()

        self.assertEqual(pta_count, 50)
        self.assertEqual(tvm_count, 50)
        self.assertEqual(kollam_count, 50)
        self.assertEqual(total_count, 150)

    def test_02_pathanamthitta_coordinates_within_district_bounds(self):
        """2. Verify all Pathanamthitta destinations have valid coordinates strictly within district boundaries."""
        for dest in Destination.objects.filter(district=self.pta_district):
            lat = float(dest.latitude)
            lng = float(dest.longitude)
            # Pathanamthitta spans ~9.05 to 9.55 N, 76.45 to 77.30 E
            self.assertGreaterEqual(lat, 9.00, f"Latitude too low for {dest.name}: {lat}")
            self.assertLessEqual(lat, 9.60, f"Latitude too high for {dest.name}: {lat}")
            self.assertGreaterEqual(lng, 76.45, f"Longitude too low for {dest.name}: {lng}")
            self.assertLessEqual(lng, 77.35, f"Longitude too high for {dest.name}: {lng}")
            self.assertTrue(bool(dest.source_name), f"Missing source for {dest.name}")
            self.assertEqual(dest.verification_status, VerificationStatus.VERIFIED)
            self.assertTrue(bool(dest.main_image_url), f"Missing image URL for {dest.name}")

    def test_03_duplicate_prevention_and_slug_uniqueness(self):
        """3. Verify zero duplicate slugs exist within Pathanamthitta and across the whole database."""
        pta_slugs = Destination.objects.filter(district=self.pta_district).values_list('slug', flat=True)
        self.assertEqual(len(pta_slugs), len(set(pta_slugs)))
        self.assertEqual(len(pta_slugs), 50)

        all_slugs = Destination.objects.values_list('slug', flat=True)
        self.assertEqual(len(all_slugs), len(set(all_slugs)))
        self.assertEqual(len(all_slugs), 150)

    def test_04_pathanamthitta_list_view_loads_with_50_destinations(self):
        """4. Verify Pathanamthitta district list page loads with HTTP 200 and lists key destinations."""
        url = reverse('destinations:pathanamthitta_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sabarimala Sree Dharma Sastha Temple")
        self.assertContains(response, "Gavi Eco-Tourism")
        self.assertContains(response, "Aranmula Sree Parthasarathy Temple")
        self.assertContains(response, "Konni Elephant Training Centre")
        self.assertContains(response, "50 Verified Tourist Destinations")

    def test_05_pathanamthitta_detail_view_complete_information(self):
        """5. Verify Pathanamthitta destination detail view renders complete visitor and trust metadata."""
        dest = Destination.objects.get(slug='gavi-eco-tourism-and-wildlife-reserve')
        url = dest.get_absolute_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Gavi Eco-Tourism and Wildlife Reserve")
        self.assertContains(response, "Visitor Guidelines & Tourist Advice")
        self.assertContains(response, "Safety Instructions")
        self.assertContains(response, "Official Data Verification Record")
        self.assertContains(response, "Kerala Forest Development Corporation (KFDC)")

    def test_06_idempotency_of_pathanamthitta_import_command(self):
        """6. Verify calling import_pathanamthitta_destinations multiple times preserves exactly 50 destinations."""
        call_command('import_pathanamthitta_destinations')
        self.assertEqual(Destination.objects.filter(district=self.pta_district).count(), 50)
        self.assertEqual(Destination.objects.count(), 150)

    def test_07_kerala_map_api_filters_pathanamthitta_destinations(self):
        """7. Verify Kerala interactive map API endpoint filters Pathanamthitta destinations properly."""
        url = reverse('destinations:api_destinations_list')
        response = self.client.get(url, {'district': 'pathanamthitta'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['count'], 50)
        self.assertEqual(len(data['destinations']), 50)
        names = [d['name'] for d in data['destinations']]
        self.assertIn("Sabarimala Sree Dharma Sastha Temple", names)
        self.assertIn("Perunthenaruvi Waterfalls and Eco-Tourism", names)
        self.assertIn("Adavi Eco-Tourism and Coracle Rafting Centre", names)


class AlappuzhaDestinationsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('import_thiruvananthapuram_destinations')
        call_command('import_kollam_destinations')
        call_command('import_pathanamthitta_destinations')
        call_command('import_alappuzha_destinations')

    def setUp(self):
        self.client = Client()
        self.tvm_district = District.objects.get(slug='thiruvananthapuram')
        self.kollam_district = District.objects.get(slug='kollam')
        self.pta_district = District.objects.get(slug='pathanamthitta')
        self.alpy_district = District.objects.get(slug='alappuzha')

        from django.contrib.auth.models import User
        self.admin_user = User.objects.create_superuser(
            username='alpy_admin', email='admin@smarttourism.local', password='AdminPass123!'
        )

    def test_01_alappuzha_has_50_destinations_and_all_previous_districts_unchanged(self):
        """1. Verify Alappuzha has 50 verified destinations and TVM/Kollam/Pathanamthitta remain 50 each (Total: 200)."""
        self.assertEqual(Destination.objects.filter(district=self.tvm_district).count(), 50)
        self.assertEqual(Destination.objects.filter(district=self.kollam_district).count(), 50)
        self.assertEqual(Destination.objects.filter(district=self.pta_district).count(), 50)
        self.assertEqual(Destination.objects.filter(district=self.alpy_district).count(), 50)
        self.assertEqual(Destination.objects.count(), 200)

    def test_02_out_of_district_attractions_excluded_from_alappuzha(self):
        """2. Verify Kumarakom Bird Sanctuary (Kottayam) and Sree Vallabha Temple (Pathanamthitta) are excluded from Alappuzha."""
        alpy_names = set(
            Destination.objects.filter(district=self.alpy_district).values_list('name', flat=True)
        )
        self.assertNotIn("Kumarakom Bird Sanctuary", alpy_names)
        self.assertNotIn("Sree Vallabha Temple", alpy_names)
        self.assertNotIn("Sree Vallabha Temple, Thiruvalla", alpy_names)

        # Verify Krishnapuram Palace is strictly inside Alappuzha now
        self.assertIn("Krishnapuram Palace", alpy_names)
        self.assertIn("Alappuzha Beach", alpy_names)
        self.assertIn("Pathiramanal Island & Bird Sanctuary", alpy_names)
        self.assertIn("Thanneermukkom Bund (Saltwater Barrier)", alpy_names)

    def test_03_alappuzha_coordinates_and_verification_integrity(self):
        """3. Verify GPS bounds within Alappuzha, verified images, attribution, and status provenance."""
        for dest in Destination.objects.filter(district=self.alpy_district):
            lat = float(dest.latitude)
            lng = float(dest.longitude)
            # Alappuzha spans ~9.08 to 9.88 N, 76.27 to 76.68 E
            self.assertGreaterEqual(lat, 9.05, f"Latitude too low for {dest.name}: {lat}")
            self.assertLessEqual(lat, 9.90, f"Latitude too high for {dest.name}: {lat}")
            self.assertGreaterEqual(lng, 76.25, f"Longitude too low for {dest.name}: {lng}")
            self.assertLessEqual(lng, 76.70, f"Longitude too high for {dest.name}: {lng}")
            self.assertTrue(bool(dest.source_name), f"Missing source_name for {dest.name}")
            self.assertTrue(bool(dest.main_image_url), f"Missing main_image_url for {dest.name}")
            self.assertTrue(bool(dest.image_attribution), f"Missing image_attribution for {dest.name}")
            self.assertEqual(dest.verification_status, VerificationStatus.VERIFIED)
            self.assertIsNotNone(dest.last_verified_date)

    def test_04_duplicate_prevention_constraint_and_idempotency(self):
        """4. Verify unique constraint (name, district) prevents duplicates and import command is idempotent."""
        from django.db import IntegrityError
        call_command('import_alappuzha_destinations')
        self.assertEqual(Destination.objects.filter(district=self.alpy_district).count(), 50)

        all_slugs = Destination.objects.values_list('slug', flat=True)
        self.assertEqual(len(all_slugs), len(set(all_slugs)))

        cat = Category.objects.first()
        with self.assertRaises(IntegrityError):
            Destination.objects.create(
                name="Alappuzha Beach",
                slug="alappuzha-beach-dup-test",
                district=self.alpy_district,
                category=cat,
                short_description="Duplicate test",
                detailed_description="Duplicate test",
                latitude=9.4926,
                longitude=76.3177,
                source_name="Test",
            )

    def test_05_alappuzha_district_filter_search_and_detail_views(self):
        """5. Verify Alappuzha district explore view, category filter, keyword search, and detail panel."""
        list_url = reverse('destinations:alappuzha_list')
        res = self.client.get(list_url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Alappuzha Interactive Destination Map")
        self.assertContains(res, "50 Verified Tourist Destinations")
        self.assertContains(res, "Alappuzha Beach")
        self.assertContains(res, "Krishnapuram Palace")

        # Filter by category
        res_cat = self.client.get(list_url, {'category': 'beaches-and-coastal'})
        self.assertEqual(res_cat.status_code, 200)
        self.assertContains(res_cat, "Marari Beach")

        # Search query
        res_search = self.client.get(list_url, {'q': 'Krishnapuram'})
        self.assertEqual(res_search.status_code, 200)
        self.assertContains(res_search, "Krishnapuram Palace")

        # Detail view
        palace = Destination.objects.get(slug='krishnapuram-palace')
        res_detail = self.client.get(palace.get_absolute_url())
        self.assertEqual(res_detail.status_code, 200)
        self.assertContains(res_detail, "Gajendra Moksham")
        self.assertContains(res_detail, "Official Data Verification Record")
        self.assertContains(res_detail, "Visitor Guidelines & Tourist Advice")

    def test_06_kerala_map_integration_mobile_layout_and_autocomplete(self):
        """6. Verify interactive Kerala map includes Alappuzha filter, clusters, autocomplete, directions, and mobile CSS."""
        map_url = reverse('destinations:kerala_map')
        res = self.client.get(map_url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "200 Places")
        self.assertContains(res, "alappuzha")
        self.assertContains(res, "@media (max-width: 991px)")
        self.assertContains(res, "Location Permission Required")

        # API district filter
        api_res = self.client.get(reverse('destinations:api_destinations_list'), {'district': 'alappuzha'})
        self.assertEqual(api_res.status_code, 200)
        data = api_res.json()
        self.assertEqual(data['count'], 50)

        # Autocomplete search
        auto_res = self.client.get(reverse('destinations:api_autocomplete'), {'q': 'Punnamada'})
        self.assertEqual(auto_res.status_code, 200)
        names = [r['name'] for r in auto_res.json()['results']]
        self.assertIn("Punnamada Lake", names)

    def test_07_pending_and_expired_data_never_marked_confirmed(self):
        """7. Verify PENDING and EXPIRED records carry is_confirmed=False and do not render confirmed timestamps."""
        cat = Category.objects.first()
        pending_dest = Destination.objects.create(
            name="Test Pending Spot Alappuzha",
            slug="test-pending-spot-alappuzha",
            district=self.alpy_district,
            category=cat,
            short_description="Pending verification spot",
            detailed_description="Pending verification details",
            latitude=9.5100,
            longitude=76.3400,
            source_name="Admin Submission",
            verification_status=VerificationStatus.PENDING,
        )
        res = self.client.get(reverse('destinations:api_destinations_list'), {'q': 'Test Pending Spot'})
        self.assertEqual(res.status_code, 200)
        item = res.json()['destinations'][0]
        self.assertEqual(item['verification_status'], 'PENDING')
        self.assertFalse(item['is_confirmed'])
        self.assertEqual(item['last_verified_date'], 'Not yet verified')
        self.assertIn('Pending Verification', item['entry_fee'])

        detail_res = self.client.get(pending_dest.get_absolute_url())
        self.assertEqual(detail_res.status_code, 200)
        self.assertContains(detail_res, "PENDING")
        self.assertContains(detail_res, "Pending Verification")

    def test_08_admin_crud_filters_and_verification_actions(self):
        """8. Verify Django Admin supports CRUD, map picker assets, missing GPS/duplicate filters, and verification actions."""
        self.client.force_login(self.admin_user)
        changelist_url = reverse('admin:destinations_destination_changelist')

        # Changelist + Alappuzha filter
        res = self.client.get(changelist_url, {'district__id__exact': self.alpy_district.id})
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Alappuzha Beach")

        # Missing GPS & Duplicate Detection filters work cleanly
        self.assertEqual(self.client.get(changelist_url, {'has_gps': 'missing'}).status_code, 200)
        self.assertEqual(self.client.get(changelist_url, {'duplicates': 'possible'}).status_code, 200)

        # Map picker JS included on add/change pages
        add_res = self.client.get(reverse('admin:destinations_destination_add'))
        self.assertEqual(add_res.status_code, 200)
        self.assertContains(add_res, "map_picker.js")

        # Admin create, edit, bulk verify action, and delete
        cat = Category.objects.first()
        create_data = {
            'name': 'Admin Test Spot Alappuzha',
            'slug': 'admin-test-spot-alappuzha',
            'district': self.alpy_district.id,
            'category': cat.id,
            'short_description': 'Created via admin',
            'detailed_description': 'Detailed description',
            'village_locality': 'Alappuzha',
            'latitude': '9.495000',
            'longitude': '76.335000',
            'source_name': 'DTPC Alappuzha',
            'source_url': 'https://dtpcalappuzha.com/',
            'verification_status': VerificationStatus.PENDING,
            'gallery_images-TOTAL_FORMS': '0',
            'gallery_images-INITIAL_FORMS': '0',
            'gallery_images-MIN_NUM_FORMS': '0',
            'gallery_images-MAX_NUM_FORMS': '1000',
            'reviews-TOTAL_FORMS': '0',
            'reviews-INITIAL_FORMS': '0',
            'reviews-MIN_NUM_FORMS': '0',
            'reviews-MAX_NUM_FORMS': '1000',
        }
        post_res = self.client.post(reverse('admin:destinations_destination_add'), data=create_data)
        self.assertEqual(post_res.status_code, 302)
        created_obj = Destination.objects.get(slug='admin-test-spot-alappuzha')
        self.assertEqual(created_obj.verification_status, VerificationStatus.PENDING)

        # Bulk action: mark_as_verified updates status and last_verified_date
        action_res = self.client.post(changelist_url, {
            'action': 'mark_as_verified',
            '_selected_action': [str(created_obj.id)],
        })
        self.assertEqual(action_res.status_code, 302)
        created_obj.refresh_from_db()
        self.assertEqual(created_obj.verification_status, VerificationStatus.VERIFIED)
        self.assertIsNotNone(created_obj.last_verified_date)

        # Admin delete
        del_res = self.client.post(
            reverse('admin:destinations_destination_delete', args=[created_obj.id]),
            {'post': 'yes'}
        )
        self.assertEqual(del_res.status_code, 302)
        self.assertFalse(Destination.objects.filter(slug='admin-test-spot-alappuzha').exists())


class KottayamDestinationsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('import_thiruvananthapuram_destinations')
        call_command('import_kollam_destinations')
        call_command('import_pathanamthitta_destinations')
        call_command('import_alappuzha_destinations')
        call_command('import_kottayam_destinations')

    def setUp(self):
        self.client = Client()
        self.tvm_district = District.objects.get(slug='thiruvananthapuram')
        self.kollam_district = District.objects.get(slug='kollam')
        self.pta_district = District.objects.get(slug='pathanamthitta')
        self.alpy_district = District.objects.get(slug='alappuzha')
        self.ktm_district = District.objects.get(slug='kottayam')

        from django.contrib.auth.models import User
        self.admin_user = User.objects.create_superuser(
            username='ktm_admin', email='ktm_admin@smarttourism.local', password='AdminPass123!'
        )

    def test_01_kottayam_counts_and_earlier_districts_preserved(self):
        """1. Verify Kottayam has 43 audited records (42 VERIFIED, 1 PENDING) and earlier 200 records stay intact."""
        self.assertEqual(Destination.objects.filter(district=self.tvm_district).count(), 50)
        self.assertEqual(Destination.objects.filter(district=self.kollam_district).count(), 50)
        self.assertEqual(Destination.objects.filter(district=self.pta_district).count(), 50)
        self.assertEqual(Destination.objects.filter(district=self.alpy_district).count(), 50)

        ktm_qs = Destination.objects.filter(district=self.ktm_district)
        self.assertEqual(ktm_qs.count(), 43)
        self.assertEqual(ktm_qs.filter(verification_status=VerificationStatus.VERIFIED).count(), 42)
        self.assertEqual(ktm_qs.filter(verification_status=VerificationStatus.PENDING).count(), 1)
        self.assertEqual(ktm_qs.filter(verification_status=VerificationStatus.EXPIRED).count(), 0)
        self.assertEqual(Destination.objects.count(), 243)

    def test_02_out_of_district_and_cross_district_duplicates_excluded(self):
        """2. Verify Idukki attractions (Nadukani, Vagamon Pine Forest) & Alappuzha duplicates are excluded from Kottayam."""
        ktm_names = set(
            Destination.objects.filter(district=self.ktm_district).values_list('name', flat=True)
        )
        self.assertNotIn("Nadukani Pavilion", ktm_names)
        self.assertNotIn("Vagamon Pine Forest", ktm_names)
        self.assertNotIn("Pathiramanal Island", ktm_names)
        self.assertNotIn("Pathiramanal Island & Bird Sanctuary", ktm_names)
        self.assertNotIn("Thanneermukkom Bund", ktm_names)
        self.assertNotIn("Kottayam District Tourism Centre", ktm_names)

        # Verify Kottayam highlights exist
        self.assertIn("Illikkal Kallu", ktm_names)
        self.assertIn("Ilaveezhapoonchira", ktm_names)
        self.assertIn("Kumarakom Bird Sanctuary", ktm_names)
        self.assertIn("Ettumanoor Mahadeva Temple", ktm_names)
        self.assertIn("Vaikom Mahadeva Temple", ktm_names)
        self.assertIn("Bharananganam St. Mary's Forane Church & St. Alphonsa Shrine", ktm_names)

    def test_03_kottayam_coordinates_images_and_pending_status_integrity(self):
        """3. Verify coordinates inside Kottayam polygon bounds, real images, attribution, and Mozart Gallery PENDING status."""
        for dest in Destination.objects.filter(district=self.ktm_district):
            lat = float(dest.latitude)
            lng = float(dest.longitude)
            # Kottayam GeoJSON bounds: 9.4003..9.8573 N, 76.3657..76.9845 E
            self.assertGreaterEqual(lat, 9.40, f"Latitude too low for {dest.name}: {lat}")
            self.assertLessEqual(lat, 9.86, f"Latitude too high for {dest.name}: {lat}")
            self.assertGreaterEqual(lng, 76.36, f"Longitude too low for {dest.name}: {lng}")
            self.assertLessEqual(lng, 76.99, f"Longitude too high for {dest.name}: {lng}")
            self.assertTrue(bool(dest.source_name), f"Missing source_name for {dest.name}")
            self.assertTrue(bool(dest.main_image_url), f"Missing main_image_url for {dest.name}")
            self.assertTrue(bool(dest.image_attribution), f"Missing image_attribution for {dest.name}")

        mozart = Destination.objects.get(slug='mozart-art-gallery-ayemenem')
        self.assertEqual(mozart.verification_status, VerificationStatus.PENDING)
        self.assertIsNone(mozart.last_verified_date)

        api_res = self.client.get(reverse('destinations:api_destinations_list'), {'q': 'Mozart'})
        self.assertEqual(api_res.status_code, 200)
        item = api_res.json()['destinations'][0]
        self.assertEqual(item['verification_status'], 'PENDING')
        self.assertFalse(item['is_confirmed'])
        self.assertEqual(item['last_verified_date'], 'Not yet verified')

    def test_04_kottayam_list_filter_search_and_detail_page_features(self):
        """4. Verify Kottayam explore filter, category filter, search, detail page Best Season & Add to Trip option."""
        list_url = reverse('destinations:kottayam_list')
        res = self.client.get(list_url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Kottayam Interactive Destination Map")
        self.assertContains(res, "Illikkal Kallu")
        self.assertContains(res, "Kumarakom Bird Sanctuary")

        # Category filter
        res_cat = self.client.get(list_url, {'category': 'waterfalls'})
        self.assertEqual(res_cat.status_code, 200)
        self.assertContains(res_cat, "Marmala Waterfalls")
        self.assertContains(res_cat, "Kattikkayam Waterfalls")

        # Search query
        res_search = self.client.get(list_url, {'q': 'Ettumanoor'})
        self.assertEqual(res_search.status_code, 200)
        self.assertContains(res_search, "Ettumanoor Mahadeva Temple")

        # Detail page completeness (Section 6)
        illikkal = Destination.objects.get(slug='illikkal-kallu')
        detail_res = self.client.get(illikkal.get_absolute_url())
        self.assertEqual(detail_res.status_code, 200)
        self.assertContains(detail_res, "Best Season to Visit")
        self.assertContains(detail_res, "Add to Trip")
        self.assertContains(detail_res, "add_to_trip=1")
        self.assertContains(detail_res, "Visitor Guidelines & Tourist Advice")
        self.assertContains(detail_res, "Official Data Verification Record")
        self.assertContains(detail_res, "Nearby Verified Attractions")

    def test_05_map_integration_nearby_directions_and_mobile_responsiveness(self):
        """5. Verify interactive Kerala map shows Kottayam markers, autocomplete, nearby API, directions, and mobile CSS."""
        map_res = self.client.get(reverse('destinations:kerala_map'))
        self.assertEqual(map_res.status_code, 200)
        self.assertContains(map_res, "243 Places")
        self.assertContains(map_res, "kottayam")
        self.assertContains(map_res, "@media (max-width: 991px)")
        self.assertContains(map_res, "add_to_trip")

        # API district filter
        api_ktm = self.client.get(reverse('destinations:api_destinations_list'), {'district': 'kottayam'})
        self.assertEqual(api_ktm.status_code, 200)
        self.assertEqual(api_ktm.json()['count'], 43)

        # Autocomplete
        auto = self.client.get(reverse('destinations:api_autocomplete'), {'q': 'Illikkal'})
        self.assertEqual(auto.status_code, 200)
        self.assertIn("Illikkal Kallu", [r['name'] for r in auto.json()['results']])

        # Nearby attractions around Kottayam center (9.5915, 76.5221)
        nearby = self.client.get(reverse('destinations:api_nearby_destinations'), {
            'lat': '9.5915', 'lng': '76.5221', 'radius': '15', 'district': 'kottayam'
        })
        self.assertEqual(nearby.status_code, 200)
        nearby_names = [d['name'] for d in nearby.json()['destinations']]
        self.assertIn("Thirunakkara Mahadeva Temple", nearby_names)

        # Directions proxy between Thirunakkara Temple & Kumarakom Bird Sanctuary
        route = self.client.get(reverse('destinations:api_route_proxy'), {
            'coordinates': '76.5189,9.5906;76.4226,9.6312', 'profile': 'driving'
        })
        self.assertEqual(route.status_code, 200)
        self.assertEqual(route.json()['status'], 'success')
        self.assertGreater(route.json()['distance_km'], 8.0)

    def test_06_duplicate_prevention_idempotency_and_admin_crud(self):
        """6. Verify duplicate prevention, command idempotency, and Admin CRUD + verification date update."""
        from django.db import IntegrityError, transaction
        call_command('import_kottayam_destinations')
        self.assertEqual(Destination.objects.filter(district=self.ktm_district).count(), 43)
        self.assertEqual(Destination.objects.count(), 243)

        # Duplicate constraint check inside an atomic savepoint
        cat = Category.objects.first()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Destination.objects.create(
                    name="Illikkal Kallu",
                    slug="illikkal-kallu-dup",
                    district=self.ktm_district,
                    category=cat,
                    short_description="Duplicate",
                    detailed_description="Duplicate",
                    latitude=9.7452,
                    longitude=76.8118,
                    source_name="Test",
                )

        # Admin CRUD & verification update action
        self.client.force_login(self.admin_user)
        changelist_url = reverse('admin:destinations_destination_changelist')
        res = self.client.get(changelist_url, {'district__id__exact': self.ktm_district.id})
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Illikkal Kallu")

        mozart = Destination.objects.get(slug='mozart-art-gallery-ayemenem')
        action_res = self.client.post(changelist_url, {
            'action': 'update_verification_date_today',
            '_selected_action': [str(mozart.id)],
        })
        self.assertEqual(action_res.status_code, 302)
        mozart.refresh_from_db()
        self.assertIsNotNone(mozart.last_verified_date)


class IdukkiDestinationsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('import_thiruvananthapuram_destinations')
        call_command('import_kollam_destinations')
        call_command('import_pathanamthitta_destinations')
        call_command('import_alappuzha_destinations')
        call_command('import_kottayam_destinations')
        call_command('import_idukki_destinations')

    def setUp(self):
        self.client = Client()
        self.tvm_district = District.objects.get(slug='thiruvananthapuram')
        self.kollam_district = District.objects.get(slug='kollam')
        self.pta_district = District.objects.get(slug='pathanamthitta')
        self.alpy_district = District.objects.get(slug='alappuzha')
        self.ktm_district = District.objects.get(slug='kottayam')
        self.idk_district = District.objects.get(slug='idukki')

        from django.contrib.auth.models import User
        self.admin_user = User.objects.create_superuser(
            username='idk_admin', email='idk_admin@smarttourism.local', password='AdminPass123!'
        )

    def test_01_idukki_counts_and_earlier_districts_preserved(self):
        """1. Verify Idukki has 43 records (42 VERIFIED, 1 PENDING) and all 243 prior records remain untouched."""
        self.assertEqual(Destination.objects.filter(district=self.tvm_district).count(), 50)
        self.assertEqual(Destination.objects.filter(district=self.kollam_district).count(), 50)
        self.assertEqual(Destination.objects.filter(district=self.pta_district).count(), 50)
        self.assertEqual(Destination.objects.filter(district=self.alpy_district).count(), 50)
        self.assertEqual(Destination.objects.filter(district=self.ktm_district).count(), 43)

        idk_qs = Destination.objects.filter(district=self.idk_district)
        self.assertEqual(idk_qs.count(), 43)
        self.assertEqual(idk_qs.filter(verification_status=VerificationStatus.VERIFIED).count(), 42)
        self.assertEqual(idk_qs.filter(verification_status=VerificationStatus.PENDING).count(), 1)
        self.assertEqual(idk_qs.filter(verification_status=VerificationStatus.EXPIRED).count(), 0)
        self.assertEqual(Destination.objects.count(), 286)

    def test_02_out_of_district_and_restricted_exclusions_verified(self):
        """2. Verify Wayanad, Ernakulam, Pathanamthitta, TN border & closed Anamudi summit excluded from Idukki."""
        idk_names = set(
            Destination.objects.filter(district=self.idk_district).values_list('name', flat=True)
        )
        self.assertNotIn("Banasura Sagar Dam", idk_names)
        self.assertNotIn("Thattekkad Bird Sanctuary", idk_names)
        self.assertNotIn("Gavi", idk_names)
        self.assertNotIn("Anamudi Peak", idk_names)
        self.assertNotIn("Kolukkumalai", idk_names)
        self.assertEqual(
            Destination.objects.filter(district=self.idk_district, name__icontains='Chinnar').count(),
            1
        )
        self.assertIn("Munnar Hill Station", idk_names)
        self.assertIn("Eravikulam National Park (Rajamalai)", idk_names)
        self.assertIn("Idukki Arch Dam, Cheruthoni Dam & Reservoir", idk_names)
        self.assertIn("Mangala Devi Kannagi Temple", idk_names)

    def test_03_idukki_coordinates_and_pending_guard(self):
        """3. Verify Idukki GPS coordinates, image provenance, and PENDING Erattayar Dam status."""
        for dest in Destination.objects.filter(district=self.idk_district):
            lat = float(dest.latitude)
            lng = float(dest.longitude)
            # Idukki spans ~9.40..10.36 N, 76.62..77.41 E
            self.assertGreaterEqual(lat, 9.40, f"Latitude too low for {dest.name}: {lat}")
            self.assertLessEqual(lat, 10.36, f"Latitude too high for {dest.name}: {lat}")
            self.assertGreaterEqual(lng, 76.62, f"Longitude too low for {dest.name}: {lng}")
            self.assertLessEqual(lng, 77.41, f"Longitude too high for {dest.name}: {lng}")
            self.assertTrue(bool(dest.source_name), f"Missing source for {dest.name}")
            self.assertTrue(bool(dest.main_image_url), f"Missing image URL for {dest.name}")
            self.assertTrue(bool(dest.image_attribution), f"Missing attribution for {dest.name}")

        erattayar = Destination.objects.get(slug='erattayar-dam-idukki')
        self.assertEqual(erattayar.verification_status, VerificationStatus.PENDING)
        self.assertIsNone(erattayar.last_verified_date)

        # Creating a new destination with valid GPS does NOT auto-verify it
        cat = Category.objects.first()
        default_status_dest = Destination.objects.create(
            name="Unverified GPS Check Spot",
            slug="unverified-gps-check-spot",
            district=self.idk_district,
            category=cat,
            short_description="Check default status",
            detailed_description="Check default status",
            latitude=9.85,
            longitude=76.97,
            source_name="Test",
        )
        self.assertEqual(default_status_dest.verification_status, VerificationStatus.PENDING)

    def test_04_protected_area_permits_and_detail_page_display(self):
        """4. Verify protected areas & dams expose permit_requirements in API and Detail pages."""
        eravikulam = Destination.objects.get(slug='eravikulam-national-park-munnar')
        self.assertIn("Anamudi Peak", eravikulam.permit_requirements)
        detail_res = self.client.get(eravikulam.get_absolute_url())
        self.assertEqual(detail_res.status_code, 200)
        self.assertContains(detail_res, "Permit, Booking & Access Restrictions")
        self.assertContains(detail_res, "eravikulamnationalpark.in")
        self.assertContains(detail_res, "Best Season to Visit")
        self.assertContains(detail_res, "Add to Trip")
        self.assertContains(detail_res, "Official Data Verification Record")

        # Mangala Devi single-day opening clearly documented
        mangala = Destination.objects.get(slug='mangala-devi-kannagi-temple-idukki')
        self.assertIn("Chitra Pournami", mangala.permit_requirements)
        mangala_api = self.client.get(reverse('destinations:api_destinations_list'), {'q': 'Mangala Devi'})
        self.assertEqual(mangala_api.status_code, 200)
        self.assertIn("Chitra Pournami", mangala_api.json()['destinations'][0]['permit_requirements'])

    def test_05_idukki_map_integration_filters_nearby_directions_and_mobile(self):
        """5. Verify interactive Kerala map filters Idukki, search, nearby API, directions, and mobile responsiveness."""
        list_res = self.client.get(reverse('destinations:idukki_list'))
        self.assertEqual(list_res.status_code, 200)
        self.assertContains(list_res, "Idukki Interactive Destination Map")
        self.assertContains(list_res, "Munnar Hill Station")

        # Category filter on Idukki list
        cat_res = self.client.get(reverse('destinations:idukki_list'), {'category': 'wildlife-and-ecotourism'})
        self.assertEqual(cat_res.status_code, 200)
        self.assertContains(cat_res, "Periyar Tiger Reserve")

        map_res = self.client.get(reverse('destinations:kerala_map'))
        self.assertEqual(map_res.status_code, 200)
        self.assertContains(map_res, "286 Places")
        self.assertContains(map_res, "drawerPermitBox")
        self.assertContains(map_res, "@media (max-width: 991px)")

        # Map API & Autocomplete
        self.assertEqual(
            self.client.get(reverse('destinations:api_destinations_list'), {'district': 'idukki'}).json()['count'],
            43
        )
        auto = self.client.get(reverse('destinations:api_autocomplete'), {'q': 'Mattupetty'})
        self.assertIn("Mattupetty Dam & Reservoir", [r['name'] for r in auto.json()['results']])

        # Nearby Munnar & Route Directions
        nearby = self.client.get(reverse('destinations:api_nearby_destinations'), {
            'lat': '10.0889', 'lng': '77.0595', 'radius': '15', 'district': 'idukki'
        })
        self.assertIn("Attukad Waterfalls", [d['name'] for d in nearby.json()['destinations']])

        route = self.client.get(reverse('destinations:api_route_proxy'), {
            'coordinates': '77.0595,10.0889;77.1239,10.1063', 'profile': 'driving'
        })
        self.assertEqual(route.status_code, 200)
        self.assertEqual(route.json()['status'], 'success')
        self.assertGreater(route.json()['distance_km'], 5.0)

    def test_06_duplicate_prevention_idempotency_and_admin_permit_management(self):
        """6. Verify duplicate prevention, command idempotency, and Admin permit/verification management."""
        from django.db import IntegrityError, transaction
        call_command('import_idukki_destinations')
        self.assertEqual(Destination.objects.filter(district=self.idk_district).count(), 43)

        cat = Category.objects.first()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Destination.objects.create(
                    name="Munnar Hill Station",
                    slug="munnar-dup",
                    district=self.idk_district,
                    category=cat,
                    short_description="Duplicate",
                    detailed_description="Duplicate",
                    latitude=10.0889,
                    longitude=77.0595,
                    source_name="Test",
                )

        self.client.force_login(self.admin_user)
        eravikulam = Destination.objects.get(slug='eravikulam-national-park-munnar')
        change_url = reverse('admin:destinations_destination_change', args=[eravikulam.id])
        change_res = self.client.get(change_url)
        self.assertEqual(change_res.status_code, 200)
        self.assertContains(change_res, "permit_requirements")
        self.assertContains(change_res, "map_picker.js")


class ErnakulamDestinationsTests(TestCase):
    """Comprehensive verification for audited Ernakulam District destinations & existing districts."""

    @classmethod
    def setUpTestData(cls):
        from django.contrib.auth.models import User
        call_command('import_thiruvananthapuram_destinations')
        call_command('import_kollam_destinations')
        call_command('import_pathanamthitta_destinations')
        call_command('import_alappuzha_destinations')
        call_command('import_kottayam_destinations')
        call_command('import_idukki_destinations')
        call_command('import_ernakulam_destinations')
        cls.ekm_district = District.objects.get(slug='ernakulam')
        cls.admin_user = User.objects.create_superuser(
            username='ekm_admin', email='ekmadmin@smarttourism.local', password='StrongPass!123'
        )

    def setUp(self):
        self.client = Client()

    def test_01_prior_districts_preserved_and_ernakulam_counts_verified(self):
        """1. Confirm all 286 previous district records stay untouched and Ernakulam loads 50 audited places."""
        self.assertEqual(Destination.objects.filter(district__slug='thiruvananthapuram').count(), 50)
        self.assertEqual(Destination.objects.filter(district__slug='kollam').count(), 50)
        self.assertEqual(Destination.objects.filter(district__slug='pathanamthitta').count(), 50)
        self.assertEqual(Destination.objects.filter(district__slug='alappuzha').count(), 50)
        self.assertEqual(Destination.objects.filter(district__slug='kottayam').count(), 43)
        self.assertEqual(Destination.objects.filter(district__slug='idukki').count(), 43)

        ekm_qs = Destination.objects.filter(district=self.ekm_district)
        self.assertEqual(ekm_qs.count(), 50)
        self.assertEqual(ekm_qs.filter(verification_status=VerificationStatus.VERIFIED).count(), 48)
        self.assertEqual(ekm_qs.filter(verification_status=VerificationStatus.PENDING).count(), 1)
        self.assertEqual(ekm_qs.filter(verification_status=VerificationStatus.EXPIRED).count(), 1)
        self.assertEqual(Destination.objects.count(), 336)

    def test_02_exclusions_consolidations_and_geojson_land_bounds(self):
        """2. Verify out-of-district exclusions, consolidations, GeoJSON containment, and PENDING default."""
        import json
        ekm_qs = Destination.objects.filter(district=self.ekm_district)
        self.assertFalse(ekm_qs.filter(name__icontains='Athirappilly').exists())
        self.assertFalse(ekm_qs.filter(name__icontains='Kumbhavurutty').exists())
        self.assertFalse(ekm_qs.filter(name__icontains='Ilaveezhapoonchira').exists())
        self.assertFalse(ekm_qs.filter(name__iexact='Vypin Island').exists())

        # Consolidated & verified entries
        self.assertTrue(ekm_qs.filter(slug='thattekad-bird-sanctuary').exists())
        self.assertTrue(ekm_qs.filter(slug='bhoothathankettu-dam-forest').exists())
        self.assertEqual(ekm_qs.filter(name__icontains='Malayattoor').count(), 1)
        self.assertEqual(ekm_qs.filter(name__icontains='Mattancherry Palace').count(), 1)
        self.assertEqual(ekm_qs.filter(name__icontains='Paradesi Synagogue').count(), 1)

        gj = json.load(open('static/data/kerala_districts.geojson', 'r', encoding='utf-8'))
        ekm_feat = [f for f in gj['features'] if f['properties'].get('slug') == 'ernakulam'][0]
        geom = ekm_feat['geometry']
        polys = [geom['coordinates']] if geom['type'] == 'Polygon' else geom['coordinates']

        def point_in_ring(lon, lat, ring):
            inside = False
            j = len(ring) - 1
            for i in range(len(ring)):
                xi, yi = ring[i][0], ring[i][1]
                xj, yj = ring[j][0], ring[j][1]
                if ((yi > lat) != (yj > lat)) and (lon < (xj - xi) * (lat - yi) / ((yj - yi) or 1e-12) + xi):
                    inside = not inside
                j = i
            return inside

        for dest in ekm_qs:
            lat, lon = float(dest.latitude), float(dest.longitude)
            self.assertGreaterEqual(lat, 9.75)
            self.assertLessEqual(lat, 10.35)
            self.assertGreaterEqual(lon, 76.14)
            self.assertLessEqual(lon, 76.85)
            self.assertTrue(
                any(point_in_ring(lon, lat, p[0]) for p in polys),
                f"{dest.slug} ({lat}, {lon}) fell outside Ernakulam GeoJSON polygon",
            )

        # Default verification status remains PENDING even when GPS coordinates exist
        cat = Category.objects.first()
        draft = Destination.objects.create(
            name="Test Ernakulam Unverified Landmark",
            slug="test-ekm-pending-landmark",
            district=self.ekm_district,
            category=cat,
            short_description="Draft",
            detailed_description="Draft details",
            latitude=10.000000,
            longitude=76.300000,
            source_name="Manual Draft",
        )
        self.assertEqual(draft.verification_status, VerificationStatus.PENDING)

    def test_03_ernakulam_filters_search_and_detail_page(self):
        """3. Verify district page, API filters, search, autocomplete, and full detail views including permits/EXPIRED."""
        list_res = self.client.get(reverse('destinations:ernakulam_list'))
        self.assertEqual(list_res.status_code, 200)
        self.assertContains(list_res, "Ernakulam")
        self.assertContains(list_res, "Fort Kochi Beach")

        # API district & category filtering
        api_ekm = self.client.get(reverse('destinations:api_destinations_list'), {'district': 'ernakulam'})
        self.assertEqual(api_ekm.status_code, 200)
        self.assertEqual(api_ekm.json()['count'], 50)

        api_beach = self.client.get(
            reverse('destinations:api_destinations_list'),
            {'district': 'ernakulam', 'category': 'beaches-and-coastal'},
        )
        self.assertEqual(api_beach.json()['count'], 5)

        api_search = self.client.get(reverse('destinations:api_destinations_list'), {'q': 'Thattekad'})
        self.assertEqual(api_search.status_code, 200)
        thattekad_matches = [d for d in api_search.json()['destinations'] if 'Thattekad Bird Sanctuary' in d['name']]
        self.assertEqual(len(thattekad_matches), 1)
        self.assertIn('FOREST SANCTUARY PERMIT', thattekad_matches[0]['permit_requirements'])

        auto_res = self.client.get(reverse('destinations:api_autocomplete'), {'q': 'Paradesi'})
        self.assertEqual(auto_res.status_code, 200)
        self.assertTrue(any('Paradesi' in s['name'] for s in auto_res.json()['results']))

        # Detail page checks: VERIFIED heritage + permit, PENDING, EXPIRED
        synagogue = Destination.objects.get(slug='paradesi-synagogue-jew-town')
        det_res = self.client.get(synagogue.get_absolute_url())
        self.assertEqual(det_res.status_code, 200)
        self.assertContains(det_res, "Shabbat")
        self.assertContains(det_res, "add_to_trip=1")
        self.assertContains(det_res, "Oct")

        kodanad = Destination.objects.get(slug='kodanad-elephant-kraal-historic')
        kod_res = self.client.get(kodanad.get_absolute_url())
        self.assertEqual(kod_res.status_code, 200)
        self.assertContains(kod_res, "EXPIRED")
        self.assertContains(kod_res, "Abhayaranyam")

        kadambrayar = Destination.objects.get(slug='kadambrayar-ecotourism-village')
        kad_res = self.client.get(kadambrayar.get_absolute_url())
        self.assertEqual(kad_res.status_code, 200)
        self.assertContains(kad_res, "PENDING")

    def test_04_map_clusters_nearby_gps_routing_and_mobile_css(self):
        """4. Verify Kerala map 336-place clusters, GPS nearby recommendations, routing proxy, and mobile responsiveness."""
        map_res = self.client.get(reverse('destinations:kerala_map'))
        self.assertEqual(map_res.status_code, 200)
        self.assertContains(map_res, "336 Places")
        self.assertContains(map_res, "drawerPermitBox")
        self.assertContains(map_res, "@media (max-width: 991px)")

        # Nearby GPS check from central Kochi (Marine Drive)
        nearby = self.client.get(reverse('destinations:api_nearby_destinations'), {
            'lat': '9.9785', 'lng': '76.2758', 'radius': '15', 'limit': '8'
        })
        self.assertEqual(nearby.status_code, 200)
        names = [d['name'] for d in nearby.json()['destinations']]
        self.assertIn("Marine Drive, Kochi", names)
        self.assertIn("Mangalavanam Bird Sanctuary", names)

        # Driving route check between Marine Drive and Fort Kochi
        route = self.client.get(reverse('destinations:api_route_proxy'), {
            'coordinates': '76.2758,9.9785;76.2399,9.9672', 'profile': 'driving'
        })
        self.assertEqual(route.status_code, 200)
        self.assertEqual(route.json()['status'], 'success')
        self.assertGreater(route.json()['distance_km'], 3.0)

    def test_05_duplicate_prevention_idempotency_and_admin_management(self):
        """5. Verify import idempotency, DB unique_together duplicate prevention, and Admin CRUD + map picker."""
        from django.db import IntegrityError, transaction
        call_command('import_ernakulam_destinations')
        self.assertEqual(Destination.objects.filter(district=self.ekm_district).count(), 50)

        cat = Category.objects.first()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Destination.objects.create(
                    name="Cherai Beach",
                    slug="cherai-dup",
                    district=self.ekm_district,
                    category=cat,
                    short_description="Duplicate",
                    detailed_description="Duplicate",
                    latitude=10.142270,
                    longitude=76.178255,
                    source_name="Test",
                )

        self.client.force_login(self.admin_user)
        thattekad = Destination.objects.get(slug='thattekad-bird-sanctuary')
        change_url = reverse('admin:destinations_destination_change', args=[thattekad.id])
        change_res = self.client.get(change_url)
        self.assertEqual(change_res.status_code, 200)
        self.assertContains(change_res, "permit_requirements")
        self.assertContains(change_res, "map_picker.js")

        list_admin_res = self.client.get(reverse('admin:destinations_destination_changelist'), {'district__id__exact': self.ekm_district.id})
        self.assertEqual(list_admin_res.status_code, 200)
        self.assertContains(list_admin_res, "Thattekad")


class ThrissurDestinationsTests(TestCase):
    """Comprehensive verification for audited Thrissur District destinations & existing districts."""

    @classmethod
    def setUpTestData(cls):
        from django.contrib.auth.models import User
        call_command('import_thiruvananthapuram_destinations')
        call_command('import_kollam_destinations')
        call_command('import_pathanamthitta_destinations')
        call_command('import_alappuzha_destinations')
        call_command('import_kottayam_destinations')
        call_command('import_idukki_destinations')
        call_command('import_ernakulam_destinations')
        call_command('import_thrissur_destinations')
        cls.tsr_district = District.objects.get(slug='thrissur')
        cls.admin_user = User.objects.create_superuser(
            username='tsr_admin', email='tsradmin@smarttourism.local', password='StrongPass!123'
        )

    def setUp(self):
        self.client = Client()

    def test_01_prior_districts_preserved_and_thrissur_counts_verified(self):
        """1. Confirm all 336 previous district records stay untouched and Thrissur loads 45 audited places."""
        self.assertEqual(Destination.objects.filter(district__slug='thiruvananthapuram').count(), 50)
        self.assertEqual(Destination.objects.filter(district__slug='kollam').count(), 50)
        self.assertEqual(Destination.objects.filter(district__slug='pathanamthitta').count(), 50)
        self.assertEqual(Destination.objects.filter(district__slug='alappuzha').count(), 50)
        self.assertEqual(Destination.objects.filter(district__slug='kottayam').count(), 43)
        self.assertEqual(Destination.objects.filter(district__slug='idukki').count(), 43)
        self.assertEqual(Destination.objects.filter(district__slug='ernakulam').count(), 50)

        tsr_qs = Destination.objects.filter(district=self.tsr_district)
        self.assertEqual(tsr_qs.count(), 45)
        self.assertEqual(tsr_qs.filter(verification_status=VerificationStatus.VERIFIED).count(), 44)
        self.assertEqual(tsr_qs.filter(verification_status=VerificationStatus.PENDING).count(), 1)
        self.assertEqual(tsr_qs.filter(verification_status=VerificationStatus.EXPIRED).count(), 0)
        self.assertEqual(Destination.objects.count(), 381)

    def test_02_exclusions_consolidations_and_geojson_land_bounds(self):
        """2. Verify out-of-district exclusions, consolidations, GeoJSON bounds, and PENDING default."""
        import json
        tsr_qs = Destination.objects.filter(district=self.tsr_district)
        self.assertFalse(tsr_qs.filter(name__icontains='Keralamkundu').exists())
        self.assertEqual(tsr_qs.filter(name__icontains='Thumboormuzhi').count(), 1)
        self.assertEqual(tsr_qs.filter(name__icontains='Chimmony').count(), 1)
        self.assertEqual(tsr_qs.filter(name__icontains='Vilangan Hills').count(), 1)
        self.assertEqual(tsr_qs.filter(name__icontains='Palayur').count(), 1)
        self.assertEqual(tsr_qs.filter(name__icontains='Shakthan Thampuran').count(), 1)
        self.assertEqual(tsr_qs.filter(name__icontains='Bible Tower').count(), 1)
        self.assertEqual(tsr_qs.filter(name__icontains='Punnathur Kotta').count(), 1)

        # Verify relocated Puthur Zoo + Kole visitor trail + Kandanassery monument
        self.assertTrue(tsr_qs.filter(slug='puthur-zoological-park-thrissur').exists())
        self.assertTrue(tsr_qs.filter(slug='thrissur-state-museum-chembukkavu').exists())
        self.assertTrue(tsr_qs.filter(slug='pullazhi-manakkody-kole-wetlands').exists())
        self.assertTrue(tsr_qs.filter(slug='kandanassery-munimada-burial-cave').exists())

        gj = json.load(open('static/data/kerala_districts.geojson', 'r', encoding='utf-8'))
        tsr_feat = [f for f in gj['features'] if f['properties'].get('slug') == 'thrissur'][0]
        geom = tsr_feat['geometry']
        polys = [geom['coordinates']] if geom['type'] == 'Polygon' else geom['coordinates']

        def point_in_ring(lon, lat, ring):
            inside = False
            j = len(ring) - 1
            for i in range(len(ring)):
                xi, yi = ring[i][0], ring[i][1]
                xj, yj = ring[j][0], ring[j][1]
                if ((yi > lat) != (yj > lat)) and (lon < (xj - xi) * (lat - yi) / ((yj - yi) or 1e-12) + xi):
                    inside = not inside
                j = i
            return inside

        for dest in tsr_qs:
            lat, lon = float(dest.latitude), float(dest.longitude)
            self.assertGreaterEqual(lat, 10.17)
            self.assertLessEqual(lat, 10.76)
            self.assertGreaterEqual(lon, 75.94)
            self.assertLessEqual(lon, 76.68)
            self.assertTrue(
                any(point_in_ring(lon, lat, p[0]) for p in polys),
                f"{dest.slug} ({lat}, {lon}) fell outside Thrissur GeoJSON polygon",
            )

        cat = Category.objects.first()
        draft = Destination.objects.create(
            name="Test Thrissur Draft Landmark",
            slug="test-tsr-pending-landmark",
            district=self.tsr_district,
            category=cat,
            short_description="Draft",
            detailed_description="Draft details",
            latitude=10.520000,
            longitude=76.210000,
            source_name="Manual Draft",
        )
        self.assertEqual(draft.verification_status, VerificationStatus.PENDING)

    def test_03_thrissur_filters_search_and_detail_page(self):
        """3. Verify district page, API filters, search, autocomplete, and full detail views including permits/PENDING."""
        list_res = self.client.get(reverse('destinations:thrissur_list'))
        self.assertEqual(list_res.status_code, 200)
        self.assertContains(list_res, "Thrissur")
        self.assertContains(list_res, "Athirappilly Waterfalls")

        api_tsr = self.client.get(reverse('destinations:api_destinations_list'), {'district': 'thrissur'})
        self.assertEqual(api_tsr.status_code, 200)
        self.assertEqual(api_tsr.json()['count'], 45)

        api_falls = self.client.get(
            reverse('destinations:api_destinations_list'),
            {'district': 'thrissur', 'category': 'waterfalls'},
        )
        self.assertEqual(api_falls.json()['count'], 3)

        api_beaches = self.client.get(
            reverse('destinations:api_destinations_list'),
            {'district': 'thrissur', 'category': 'beaches-and-coastal'},
        )
        self.assertEqual(api_beaches.json()['count'], 5)

        api_search = self.client.get(reverse('destinations:api_destinations_list'), {'q': 'Puthur'})
        self.assertEqual(api_search.status_code, 200)
        puthur_matches = [d for d in api_search.json()['destinations'] if 'Thrissur Zoological Park' in d['name']]
        self.assertEqual(len(puthur_matches), 1)
        self.assertIn('tzp-cds.com', puthur_matches[0]['permit_requirements'])

        auto_res = self.client.get(reverse('destinations:api_autocomplete'), {'q': 'Guruvayur'})
        self.assertEqual(auto_res.status_code, 200)
        self.assertTrue(any('Guruvayur' in s['name'] for s in auto_res.json()['results']))

        guruvayur = Destination.objects.get(slug='guruvayur-sri-krishna-temple')
        det_res = self.client.get(guruvayur.get_absolute_url())
        self.assertEqual(det_res.status_code, 200)
        self.assertContains(det_res, "mundu")
        self.assertContains(det_res, "add_to_trip=1")
        self.assertContains(det_res, "VERIFIED")

        peringal = Destination.objects.get(slug='peringalkuthu-dam')
        per_res = self.client.get(peringal.get_absolute_url())
        self.assertEqual(per_res.status_code, 200)
        self.assertContains(per_res, "PENDING")
        self.assertContains(per_res, "KSEB")

    def test_04_map_clusters_nearby_gps_routing_and_mobile_css(self):
        """4. Verify Kerala map 381-place clusters, GPS nearby suggestions, routing proxy, and mobile responsiveness."""
        map_res = self.client.get(reverse('destinations:kerala_map'))
        self.assertEqual(map_res.status_code, 200)
        self.assertContains(map_res, "381 Places")
        self.assertContains(map_res, "drawerPermitBox")
        self.assertContains(map_res, "@media (max-width: 991px)")

        nearby = self.client.get(reverse('destinations:api_nearby_destinations'), {
            'lat': '10.5244', 'lng': '76.2145', 'radius': '15', 'limit': '8'
        })
        self.assertEqual(nearby.status_code, 200)
        names = [d['name'] for d in nearby.json()['destinations']]
        self.assertIn("Vadakkunnathan Temple, Thrissur", names)
        self.assertIn("Shakthan Thampuran Palace & Archaeological Museum", names)

        route = self.client.get(reverse('destinations:api_route_proxy'), {
            'coordinates': '76.2145,10.5244;76.0390,10.5945', 'profile': 'driving'
        })
        self.assertEqual(route.status_code, 200)
        self.assertEqual(route.json()['status'], 'success')
        self.assertGreater(route.json()['distance_km'], 15.0)

    def test_05_duplicate_prevention_idempotency_and_admin_management(self):
        """5. Verify import idempotency, DB unique_together duplicate prevention, and Admin CRUD + map picker."""
        from django.db import IntegrityError, transaction
        call_command('import_thrissur_destinations')
        self.assertEqual(Destination.objects.filter(district=self.tsr_district).count(), 45)

        cat = Category.objects.first()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Destination.objects.create(
                    name="Athirappilly Waterfalls",
                    slug="athirappilly-dup",
                    district=self.tsr_district,
                    category=cat,
                    short_description="Duplicate",
                    detailed_description="Duplicate",
                    latitude=10.286500,
                    longitude=76.568611,
                    source_name="Test",
                )

        self.client.force_login(self.admin_user)
        athira = Destination.objects.get(slug='athirappilly-waterfalls')
        change_url = reverse('admin:destinations_destination_change', args=[athira.id])
        change_res = self.client.get(change_url)
        self.assertEqual(change_res.status_code, 200)
        self.assertContains(change_res, "permit_requirements")
        self.assertContains(change_res, "map_picker.js")

        list_admin_res = self.client.get(reverse('admin:destinations_destination_changelist'), {'district__id__exact': self.tsr_district.id})
        self.assertEqual(list_admin_res.status_code, 200)
        self.assertContains(list_admin_res, "Athirappilly")









