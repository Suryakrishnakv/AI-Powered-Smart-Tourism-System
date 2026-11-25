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




