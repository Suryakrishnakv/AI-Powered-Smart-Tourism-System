from django.contrib import admin
from .models import TouristProfile

@admin.register(TouristProfile)
class TouristProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_full_name', 'get_email', 'phone_number', 'district', 'latitude', 'longitude', 'created_date')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'phone_number', 'location_address')
    list_filter = ('district', 'created_date')

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Full Name'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'
