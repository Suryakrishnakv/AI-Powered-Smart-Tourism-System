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
