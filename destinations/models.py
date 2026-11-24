from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse
from core.models import VerifiableDataModel


class District(VerifiableDataModel):
    """
    District model representing one of the 14 official revenue districts of Kerala.
    Inherits verifiable provenance and tracking.
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="District Name")
    slug = models.SlugField(max_length=100, unique=True)
    headquarters = models.CharField(max_length=100, verbose_name="District Headquarters")
    description = models.TextField(verbose_name="District Overview")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Center Latitude")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Center Longitude")
    cover_image = models.ImageField(upload_to='districts/', blank=True, null=True)
    cover_image_url = models.URLField(max_length=500, blank=True, help_text="Verified official or Commons image URL")
    official_dtpc_website = models.URLField(max_length=500, blank=True, verbose_name="Official DTPC Website")
    dtpc_contact = models.CharField(max_length=200, blank=True, verbose_name="DTPC Helpline / Contact")

    class Meta:
        ordering = ['name']
        verbose_name = "Kerala District"
        verbose_name_plural = "Kerala Districts"

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if self.latitude is not None and (self.latitude < -90 or self.latitude > 90):
            raise ValidationError({'latitude': 'Latitude must be between -90 and 90 degrees.'})
        if self.longitude is not None and (self.longitude < -180 or self.longitude > 180):
            raise ValidationError({'longitude': 'Longitude must be between -180 and 180 degrees.'})


class Category(models.Model):
    """
    Categories of tourist destinations (Hill Stations, Beaches, Waterfalls, Temples, etc.).
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Category Name")
    slug = models.SlugField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, default='bi-geo-alt', help_text="Bootstrap Icons class (e.g. bi-water)")
    description = models.TextField(blank=True, verbose_name="Description")

    class Meta:
        ordering = ['name']
        verbose_name = "Destination Category"
        verbose_name_plural = "Destination Categories"

    def __str__(self):
        return self.name


class Destination(VerifiableDataModel):
    """
    Real tourist destination belonging strictly to a Kerala District.
    Inherits VerifiableDataModel for strict source provenance & verification status.
    """
    name = models.CharField(max_length=200, verbose_name="Destination Name")
    slug = models.SlugField(max_length=200, unique=True)
    district = models.ForeignKey(District, on_delete=models.PROTECT, related_name='destinations', verbose_name="District")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='destinations', verbose_name="Category")
    
    short_description = models.TextField(max_length=500, verbose_name="Brief Summary")
    detailed_description = models.TextField(verbose_name="Detailed Description")
    village_locality = models.CharField(max_length=150, blank=True, verbose_name="Village / Locality / Taluk")
    full_address = models.TextField(blank=True, verbose_name="Full Official Address")
    
    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="GPS Latitude")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="GPS Longitude")
    
    main_image = models.ImageField(upload_to='destinations/', blank=True, null=True, verbose_name="Uploaded Cover Image")
    main_image_url = models.URLField(max_length=500, blank=True, help_text="Verified high-res URL (Kerala Tourism / Wikimedia Commons)")
    image_caption = models.CharField(max_length=255, blank=True, verbose_name="Image Caption")
    image_attribution = models.CharField(max_length=255, blank=True, verbose_name="License & Photographer Credit")

    available_activities = models.TextField(blank=True, help_text="Comma-separated activities (e.g. Boating, Swimming, Trekking, Photography)")
    entry_fee = models.CharField(max_length=150, blank=True, help_text="Official entry ticket fee structure or 'Free / No Entry Fee'")
    opening_hours = models.CharField(max_length=150, blank=True, help_text="Official visiting hours (e.g. 9:00 AM - 5:00 PM)")
    best_time_to_visit = models.CharField(max_length=100, blank=True, default="October to March")
    contact_info = models.CharField(max_length=200, blank=True, verbose_name="Official Contact / Help Desk")
    official_website = models.URLField(max_length=500, blank=True, verbose_name="Official Webpage")
    is_featured = models.BooleanField(default=False, verbose_name="Featured Destination")

    class Meta:
        ordering = ['name']
        verbose_name = "Tourist Destination"
        verbose_name_plural = "Tourist Destinations"
        unique_together = ('name', 'district')

    def __str__(self):
        return f"{self.name} ({self.district.name})"

    def clean(self):
        super().clean()
        if self.latitude is not None and (self.latitude < -90 or self.latitude > 90):
            raise ValidationError({'latitude': 'Latitude must be between -90 and 90 degrees.'})
        if self.longitude is not None and (self.longitude < -180 or self.longitude > 180):
            raise ValidationError({'longitude': 'Longitude must be between -180 and 180 degrees.'})

    def get_absolute_url(self):
        return reverse('destinations:destination_detail', kwargs={'district_slug': self.district.slug, 'slug': self.slug})

    @property
    def display_image_url(self):
        """Returns uploaded image URL if available, else external verified URL, else placeholder."""
        if self.main_image:
            return self.main_image.url
        if self.main_image_url:
            return self.main_image_url
        return 'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?auto=format&fit=crop&w=800&q=80'

    @property
    def activities_list(self):
        """Returns list of activities parsed from comma-separated string."""
        if not self.available_activities:
            return []
        return [act.strip() for act in self.available_activities.split(',') if act.strip()]


class DestinationImage(models.Model):
    """
    Multiple gallery images for a destination with full license and credit tracking.
    """
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='destinations/gallery/', blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, help_text="Verified Wikimedia Commons image URL")
    caption = models.CharField(max_length=255, blank=True)
    source_name = models.CharField(max_length=200, blank=True, default="Wikimedia Commons")
    source_url = models.URLField(max_length=500, blank=True)
    license_info = models.CharField(max_length=150, blank=True, default="Creative Commons Attribution-Share Alike")
    photographer_attribution = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']
        verbose_name = "Destination Gallery Image"
        verbose_name_plural = "Destination Gallery Images"

    def __str__(self):
        return f"Gallery image for {self.destination.name}"

    @property
    def display_image_url(self):
        if self.image:
            return self.image.url
        return self.image_url
