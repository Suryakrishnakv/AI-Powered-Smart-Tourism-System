from django.db import models
from django.contrib.auth.models import User

class TouristProfile(models.Model):
    """
    Profile model for tourists visiting Kerala, linked 1-to-1 with Django's User model.
    """
    DISTRICT_CHOICES = [
        ('Thiruvananthapuram', 'Thiruvananthapuram'),
        ('Kollam', 'Kollam'),
        ('Pathanamthitta', 'Pathanamthitta'),
        ('Alappuzha', 'Alappuzha'),
        ('Kottayam', 'Kottayam'),
        ('Idukki', 'Idukki'),
        ('Ernakulam', 'Ernakulam'),
        ('Thrissur', 'Thrissur'),
        ('Palakkad', 'Palakkad'),
        ('Malappuram', 'Malappuram'),
        ('Kozhikode', 'Kozhikode'),
        ('Wayanad', 'Wayanad'),
        ('Kannur', 'Kannur'),
        ('Kasaragod', 'Kasaragod'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='tourist_profile'
    )
    phone_number = models.CharField(max_length=20, blank=True, verbose_name="Phone Number")
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True, verbose_name="Profile Image")
    address = models.TextField(blank=True, verbose_name="Address")
    district = models.CharField(max_length=50, blank=True, choices=DISTRICT_CHOICES, verbose_name="Preferred/Home District")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Created Date")

    class Meta:
        verbose_name = "Tourist Profile"
        verbose_name_plural = "Tourist Profiles"
        ordering = ['-created_date']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.phone_number or 'No phone'})"
