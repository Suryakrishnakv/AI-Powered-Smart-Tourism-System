from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class VerificationStatus(models.TextChoices):
    LIVE = 'LIVE', 'Live (Active Authorized Provider)'
    VERIFIED = 'VERIFIED', 'Verified (Checked Against Official Source)'
    ESTIMATED = 'ESTIMATED', 'Estimated (Approximate Calculation)'
    PENDING = 'PENDING', 'Pending (Awaiting Verification)'
    EXPIRED = 'EXPIRED', 'Expired (Requires Re-verification)'


class VerifiableDataModel(models.Model):
    """
    Reusable abstract base model implementing the Global Real & Verified Data Policy.
    All important real-world records (Destinations, Attractions, Transport, Hotels, Rates)
    inherit from this model across all development phases.
    """
    source_name = models.CharField(
        max_length=200,
        verbose_name="Official Data Source Name",
        help_text="e.g. Department of Tourism, Govt of Kerala, KSRTC, DTPC, Forest Dept, KTDC"
    )
    source_url = models.URLField(
        blank=True,
        max_length=500,
        verbose_name="Data Source URL",
        help_text="Direct link to official portal or verification document"
    )
    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING,
        verbose_name="Verification Status"
    )
    last_verified_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Last Verified Date"
    )
    valid_until = models.DateField(
        null=True,
        blank=True,
        verbose_name="Validity Expiry Date",
        help_text="Date after which this record requires mandatory re-verification"
    )
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_%(class)s_records",
        verbose_name="Verified by Administrator"
    )
    is_demo = models.BooleanField(
        default=False,
        verbose_name="Is Demo Data",
        help_text="Must be explicitly flagged True if used for sample/testing to prevent fake data presentation"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    @property
    def is_currently_valid(self):
        """Returns True only if verified/live and not past its valid_until date."""
        if self.verification_status in [VerificationStatus.LIVE, VerificationStatus.VERIFIED]:
            if self.valid_until and self.valid_until < timezone.now().date():
                return False
            return True
        return False

    @property
    def status_badge_class(self):
        """Returns Bootstrap badge class for consistent UI rendering."""
        mapping = {
            VerificationStatus.LIVE: 'bg-success',
            VerificationStatus.VERIFIED: 'bg-primary',
            VerificationStatus.ESTIMATED: 'bg-warning text-dark',
            VerificationStatus.PENDING: 'bg-secondary',
            VerificationStatus.EXPIRED: 'bg-danger',
        }
        return mapping.get(self.verification_status, 'bg-secondary')
