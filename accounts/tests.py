from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import TouristProfile

class TouristAuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('accounts:register')
        self.login_url = reverse('accounts:login')
        self.logout_url = reverse('accounts:logout')
        self.dashboard_url = reverse('accounts:dashboard')
        self.profile_edit_url = reverse('accounts:profile_edit')

        # Sample valid registration payload
        self.valid_payload = {
            'full_name': 'Anandhu Kumar',
            'username': 'anandhu',
            'email': 'anandhu@example.com',
            'phone_number': '+91 9847123456',
            'password': 'Kerala@Travel2026',
            'confirm_password': 'Kerala@Travel2026',
        }

    def test_01_tourist_registration(self):
        """1. Test successful tourist registration."""
        response = self.client.post(self.register_url, self.valid_payload, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.login_url)

        # Verify User was created
        user = User.objects.filter(username='anandhu').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.first_name, 'Anandhu')
        self.assertEqual(user.last_name, 'Kumar')
        self.assertEqual(user.email, 'anandhu@example.com')
        # Verify NEVER admin or staff
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

        # Verify TouristProfile was created
        profile = TouristProfile.objects.filter(user=user).first()
        self.assertIsNotNone(profile)
        self.assertEqual(profile.phone_number, '+91 9847123456')

    def test_02_duplicate_username(self):
        """2. Test registration rejection on duplicate username."""
        # Register first
        self.client.post(self.register_url, self.valid_payload)

        # Attempt to register with same username but different email
        duplicate_payload = self.valid_payload.copy()
        duplicate_payload['email'] = 'different@example.com'
        response = self.client.post(self.register_url, duplicate_payload)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This username is already taken")

    def test_03_duplicate_email(self):
        """3. Test registration rejection on duplicate email."""
        # Register first
        self.client.post(self.register_url, self.valid_payload)

        # Attempt to register with same email but different username
        duplicate_payload = self.valid_payload.copy()
        duplicate_payload['username'] = 'anotheruser'
        response = self.client.post(self.register_url, duplicate_payload)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "An account with this email address already exists")

    def test_04_password_mismatch(self):
        """4. Test registration rejection on password mismatch."""
        mismatch_payload = self.valid_payload.copy()
        mismatch_payload['confirm_password'] = 'DifferentPassword123'
        response = self.client.post(self.register_url, mismatch_payload)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Passwords do not match")

    def test_05_successful_login(self):
        """5. Test successful login using username AND using email."""
        # Create user & profile
        self.client.post(self.register_url, self.valid_payload)

        # A. Login by Username
        login_by_username = {
            'username_or_email': 'anandhu',
            'password': 'Kerala@Travel2026',
        }
        res_user = self.client.post(self.login_url, login_by_username, follow=True)
        self.assertEqual(res_user.status_code, 200)
        self.assertRedirects(res_user, self.dashboard_url)
        self.assertTrue(res_user.context['user'].is_authenticated)

        # Logout
        self.client.logout()

        # B. Login by Email
        login_by_email = {
            'username_or_email': 'anandhu@example.com',
            'password': 'Kerala@Travel2026',
        }
        res_email = self.client.post(self.login_url, login_by_email, follow=True)
        self.assertEqual(res_email.status_code, 200)
        self.assertRedirects(res_email, self.dashboard_url)
        self.assertTrue(res_email.context['user'].is_authenticated)

    def test_06_invalid_login(self):
        """6. Test login failure with invalid credentials."""
        # Non-existent user
        bad_login = {
            'username_or_email': 'nonexistent',
            'password': 'WrongPassword123',
        }
        response = self.client.post(self.login_url, bad_login)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username/email or password")

    def test_07_dashboard_access_authenticated(self):
        """7. Test dashboard access for authenticated tourist."""
        self.client.post(self.register_url, self.valid_payload)
        self.client.login(username='anandhu', password='Kerala@Travel2026')
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome, Anandhu Kumar!")
        self.assertContains(response, "Tourist Profile")
        self.assertContains(response, "My Trips")

    def test_08_logout(self):
        """8. Test logout clears session and redirects to login."""
        self.client.post(self.register_url, self.valid_payload)
        self.client.login(username='anandhu', password='Kerala@Travel2026')
        response = self.client.get(self.logout_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.login_url)
        self.assertFalse(response.context['user'].is_authenticated)

    def test_09_dashboard_access_unauthenticated(self):
        """9. Test unauthenticated dashboard access redirects to login."""
        # Directly trying to visit dashboard without logging in
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 302)
        expected_redirect = f"{self.login_url}?next={self.dashboard_url}"
        self.assertRedirects(response, expected_redirect)

    def test_10_profile_edit_page_loads_for_authenticated_tourist(self):
        """10. Test profile edit & map page loads with Leaflet for authenticated tourist."""
        self.client.post(self.register_url, self.valid_payload)
        self.client.login(username='anandhu', password='Kerala@Travel2026')
        response = self.client.get(self.profile_edit_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "keralaMap")
        self.assertContains(response, "Use My Current Location")
        self.assertContains(response, "Interactive Kerala Location Picker")

    def test_11_save_valid_gps_coordinates(self):
        """11. Test saving valid GPS coordinates and landmark to TouristProfile."""
        self.client.post(self.register_url, self.valid_payload)
        self.client.login(username='anandhu', password='Kerala@Travel2026')

        payload = {
            'first_name': 'Anandhu',
            'last_name': 'Kumar',
            'phone_number': '+91 9847123456',
            'district': 'Ernakulam',
            'address': 'Marine Drive, Kochi',
            'location_address': 'Fort Kochi Beach',
            'latitude': '9.965800',
            'longitude': '76.242100',
        }
        response = self.client.post(self.profile_edit_url, payload, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.dashboard_url)

        # Verify profile updated in database
        profile = TouristProfile.objects.get(user__username='anandhu')
        self.assertEqual(float(profile.latitude), 9.965800)
        self.assertEqual(float(profile.longitude), 76.242100)
        self.assertEqual(profile.location_address, 'Fort Kochi Beach')
        self.assertEqual(profile.district, 'Ernakulam')

    def test_12_update_gps_coordinates(self):
        """12. Test updating existing coordinates to a new Kerala destination (Munnar)."""
        self.client.post(self.register_url, self.valid_payload)
        self.client.login(username='anandhu', password='Kerala@Travel2026')

        # First save (Kochi)
        self.client.post(self.profile_edit_url, {
            'first_name': 'Anandhu',
            'last_name': 'Kumar',
            'phone_number': '+91 9847123456',
            'district': 'Ernakulam',
            'location_address': 'Fort Kochi',
            'latitude': '9.965800',
            'longitude': '76.242100',
        })

        # Update to Munnar, Idukki
        update_payload = {
            'first_name': 'Anandhu',
            'last_name': 'Kumar',
            'phone_number': '+91 9847123456',
            'district': 'Idukki',
            'location_address': 'Munnar Tea Estates, Idukki',
            'latitude': '10.088933',
            'longitude': '77.059525',
        }
        response = self.client.post(self.profile_edit_url, update_payload, follow=True)
        self.assertEqual(response.status_code, 200)

        profile = TouristProfile.objects.get(user__username='anandhu')
        self.assertEqual(float(profile.latitude), 10.088933)
        self.assertEqual(float(profile.longitude), 77.059525)
        self.assertEqual(profile.district, 'Idukki')
        self.assertEqual(profile.location_address, 'Munnar Tea Estates, Idukki')

    def test_13_reject_invalid_gps_coordinates(self):
        """13. Test server-side validation rejects invalid latitude/longitude ranges."""
        self.client.post(self.register_url, self.valid_payload)
        self.client.login(username='anandhu', password='Kerala@Travel2026')

        # Latitude > 90
        invalid_lat_payload = {
            'first_name': 'Anandhu',
            'latitude': '95.000000',
            'longitude': '76.242100',
        }
        res_lat = self.client.post(self.profile_edit_url, invalid_lat_payload)
        self.assertEqual(res_lat.status_code, 200)
        self.assertContains(res_lat, "Latitude must be between -90.0 and 90.0")

        # Longitude > 180
        invalid_lng_payload = {
            'first_name': 'Anandhu',
            'latitude': '10.000000',
            'longitude': '195.000000',
        }
        res_lng = self.client.post(self.profile_edit_url, invalid_lng_payload)
        self.assertEqual(res_lng.status_code, 200)
        self.assertContains(res_lng, "Longitude must be between -180.0 and 180.0")

    def test_14_reject_unbalanced_coordinates(self):
        """14. Test rejection when one coordinate is provided without the other."""
        self.client.post(self.register_url, self.valid_payload)
        self.client.login(username='anandhu', password='Kerala@Travel2026')

        unbalanced_payload = {
            'first_name': 'Anandhu',
            'latitude': '10.850500',
            'longitude': '',  # missing
        }
        res = self.client.post(self.profile_edit_url, unbalanced_payload)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Both latitude and longitude must be provided together")

    def test_15_profile_data_remains_intact_when_updating_gps(self):
        """15. Test that existing user info (username, email) remains intact when updating GPS."""
        self.client.post(self.register_url, self.valid_payload)
        self.client.login(username='anandhu', password='Kerala@Travel2026')

        payload = {
            'first_name': 'Anandhu Renamed',
            'last_name': 'Kumar Updated',
            'phone_number': '+91 9999999999',
            'district': 'Wayanad',
            'location_address': 'Vythiri, Wayanad',
            'latitude': '11.551800',
            'longitude': '76.041600',
        }
        self.client.post(self.profile_edit_url, payload)

        user = User.objects.get(username='anandhu')
        self.assertEqual(user.email, 'anandhu@example.com')  # Email preserved
        self.assertEqual(user.first_name, 'Anandhu Renamed')
        self.assertFalse(user.is_staff)  # Privileges safe
        self.assertFalse(user.is_superuser)

    def test_16_profile_edit_unauthenticated_redirect(self):
        """16. Test unauthenticated access to profile edit is redirected to login."""
        response = self.client.get(self.profile_edit_url)
        self.assertEqual(response.status_code, 302)
        expected = f"{self.login_url}?next={self.profile_edit_url}"
        self.assertRedirects(response, expected)

    def test_17_profile_avatar_upload(self):
        """17. Test uploading a profile avatar photograph."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.client.post(self.register_url, self.valid_payload)
        self.client.login(username='anandhu', password='Kerala@Travel2026')

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x05\x04\x04'
            b'\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44'
            b'\x01\x00\x3b'
        )
        avatar = SimpleUploadedFile('avatar.gif', small_gif, content_type='image/gif')

        payload = {
            'first_name': 'Anandhu',
            'last_name': 'Kumar',
            'phone_number': '+91 9847123456',
            'district': 'Alappuzha',
            'profile_image': avatar,
        }
        response = self.client.post(self.profile_edit_url, payload, follow=True)
        self.assertEqual(response.status_code, 200)

        profile = TouristProfile.objects.get(user__username='anandhu')
        self.assertTrue(bool(profile.profile_image))
        self.assertIn('avatar', profile.profile_image.name)
