from django.contrib import admin
from .models import District, Category, Destination, DestinationImage
from core.models import VerificationStatus


class DestinationImageInline(admin.TabularInline):
    model = DestinationImage
    extra = 1
    fields = ('image', 'image_url', 'caption', 'source_name', 'license_info', 'photographer_attribution')


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'headquarters', 'latitude', 'longitude', 'verification_status', 'last_verified_date')
    search_fields = ('name', 'headquarters', 'source_name')
    list_filter = ('verification_status',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'district', 'category', 'village_locality',
        'latitude', 'longitude', 'verification_status', 'last_verified_date', 'is_featured'
    )
    search_fields = ('name', 'village_locality', 'full_address', 'source_name')
    list_filter = ('district', 'category', 'verification_status', 'is_featured')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [DestinationImageInline]
    actions = ['mark_as_verified', 'mark_as_pending', 'mark_as_expired']

    @admin.action(description="Mark selected destinations as VERIFIED")
    def mark_as_verified(self, request, queryset):
        queryset.update(verification_status=VerificationStatus.VERIFIED)

    @admin.action(description="Mark selected destinations as PENDING verification")
    def mark_as_pending(self, request, queryset):
        queryset.update(verification_status=VerificationStatus.PENDING)

    @admin.action(description="Mark selected destinations as EXPIRED")
    def mark_as_expired(self, request, queryset):
        queryset.update(verification_status=VerificationStatus.EXPIRED)


@admin.register(DestinationImage)
class DestinationImageAdmin(admin.ModelAdmin):
    list_display = ('destination', 'caption', 'source_name', 'license_info', 'created_at')
    search_fields = ('destination__name', 'caption', 'photographer_attribution')
