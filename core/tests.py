import datetime
from django.db import models
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import VerifiableDataModel, VerificationStatus

# Create a concrete model for testing the abstract base
class SampleTourismRecord(VerifiableDataModel):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'core'

class DataVerificationPolicyTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='verifier_admin',
            password='Password@123',
            email='admin@keralatourism.org'
        )

    def test_01_verification_status_choices(self):
        """1. Verify that all 5 required verification statuses are available."""
        expected_statuses = {'LIVE', 'VERIFIED', 'ESTIMATED', 'PENDING', 'EXPIRED'}
        available_statuses = set(VerificationStatus.values)
        self.assertEqual(expected_statuses, available_statuses)

    def test_02_default_status_is_pending(self):
        """2. Any newly entered record must default to PENDING verification."""
        record = SampleTourismRecord(
            name="Athirappilly Waterfalls",
            source_name="Kerala Tourism Official Portal",
            source_url="https://www.keralatourism.org/destination/athirappilly-water-falls/11"
        )
        self.assertEqual(record.verification_status, VerificationStatus.PENDING)
        self.assertFalse(record.is_currently_valid)

    def test_03_verified_within_validity_period(self):
        """3. A VERIFIED record before its validity expiry is currently valid."""
        today = timezone.now().date()
        record = SampleTourismRecord(
            name="Munnar Tea Museum",
            source_name="DTPC Idukki",
            source_url="https://idukki.nic.in/tourism/",
            verification_status=VerificationStatus.VERIFIED,
            last_verified_date=today,
            valid_until=today + datetime.timedelta(days=90),
            verified_by=self.admin_user
        )
        self.assertTrue(record.is_currently_valid)
        self.assertEqual(record.status_badge_class, 'bg-primary')

    def test_04_expired_record_detection(self):
        """4. A record whose validity date has passed must NOT be considered currently valid."""
        yesterday = timezone.now().date() - datetime.timedelta(days=1)
        record = SampleTourismRecord(
            name="Historical Fare Quote",
            source_name="KSRTC",
            source_url="https://online.keralartc.com",
            verification_status=VerificationStatus.VERIFIED,
            valid_until=yesterday
        )
        self.assertFalse(record.is_currently_valid)

    def test_05_demo_data_flag(self):
        """5. Demo records must be explicitly identifiable to prevent fake data presentation."""
        record = SampleTourismRecord(
            name="Test Hotel",
            source_name="Mock Generator",
            is_demo=True
        )
        self.assertTrue(record.is_demo)
