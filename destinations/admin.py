from django.contrib import admin
from django import forms
from django.utils import timezone
from django.db.models import Count
from .models import District, Category, Destination, DestinationImage, SavedTrip, SavedTripStop, DestinationReview
from core.models import VerificationStatus


class DestinationImageInline(admin.TabularInline):
    model = DestinationImage
    extra = 1
    fields = ('image', 'image_url', 'caption', 'source_name', 'license_info', 'photographer_attribution')


class DestinationReviewInline(admin.TabularInline):
    model = DestinationReview
    extra = 0
    readonly_fields = ('user', 'rating', 'created_at')
    fields = ('user', 'rating', 'title', 'comment', 'is_approved', 'created_at')


class MissingCoordinatesFilter(admin.SimpleListFilter):
    title = 'GPS Coordinates Status'
    parameter_name = 'has_gps'

    def lookups(self, request, model_admin):
        return (
            ('missing', 'Missing GPS Coordinates'),
            ('valid', 'Valid GPS Coordinates'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'missing':
            return queryset.filter(latitude__isnull=True) | queryset.filter(longitude__isnull=True)
        if self.value() == 'valid':
            return queryset.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
        return queryset


class DuplicateRecordsFilter(admin.SimpleListFilter):
    title = 'Duplicate Detection'
    parameter_name = 'duplicates'

    def lookups(self, request, model_admin):
        return (
            ('possible', 'Possible Duplicate Names / Coordinates'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'possible':
            dup_names = (
                Destination.objects.values('name')
                .annotate(name_count=Count('id'))
                .filter(name_count__gt=1)
                .values_list('name', flat=True)
            )
            dup_coords = (
                Destination.objects.values('latitude', 'longitude')
                .annotate(coord_count=Count('id'))
                .filter(coord_count__gt=1)
            )
            dup_coord_q = queryset.none()
            for item in dup_coords:
                dup_coord_q = dup_coord_q | queryset.filter(
                    latitude=item['latitude'], longitude=item['longitude']
                )
            return queryset.filter(name__in=dup_names) | dup_coord_q
        return queryset


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
    list_filter = ('district', 'category', 'verification_status', MissingCoordinatesFilter, DuplicateRecordsFilter, 'is_featured')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [DestinationImageInline, DestinationReviewInline]
    actions = ['mark_as_verified', 'mark_as_pending', 'mark_as_expired', 'update_verification_date_today']

    fieldsets = (
        ("Basic Destination Information", {
            'fields': ('name', 'slug', 'district', 'category', 'short_description', 'detailed_description', 'is_featured')
        }),
        ("Location & Verified GPS Coordinates", {
            'fields': ('village_locality', 'full_address', 'latitude', 'longitude'),
            'description': "Coordinates must be strictly verified within official Kerala district boundaries."
        }),
        ("Photography & Media", {
            'fields': ('main_image', 'main_image_url', 'image_caption', 'image_attribution')
        }),
        ("Visitor Information & Timings", {
            'fields': (
                'available_activities', 'entry_fee', 'opening_hours',
                'weekly_closing_day', 'expected_visit_duration', 'best_time_to_visit',
                'visitor_guidelines', 'safety_instructions', 'accessibility_info'
            )
        }),
        ("Official Contact Channels", {
            'fields': ('contact_info', 'official_website', 'official_email')
        }),
        ("Data Verification Provenance", {
            'fields': ('source_name', 'source_url', 'verification_status', 'last_verified_date', 'valid_until', 'verified_by')
        }),
    )

    class Media:
        css = {
            'all': ('https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',)
        }
        js = (
            'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',
            'admin/js/map_picker.js',
        )

    @admin.action(description="Mark selected destinations as VERIFIED (set date to today)")
    def mark_as_verified(self, request, queryset):
        queryset.update(
            verification_status=VerificationStatus.VERIFIED,
            last_verified_date=timezone.now().date(),
            verified_by=request.user,
        )

    @admin.action(description="Mark selected destinations as PENDING verification")
    def mark_as_pending(self, request, queryset):
        queryset.update(verification_status=VerificationStatus.PENDING)

    @admin.action(description="Mark selected destinations as EXPIRED (Requires Re-verification)")
    def mark_as_expired(self, request, queryset):
        queryset.update(verification_status=VerificationStatus.EXPIRED)

    @admin.action(description="Update Last Verified Date to Today")
    def update_verification_date_today(self, request, queryset):
        queryset.update(last_verified_date=timezone.now().date(), verified_by=request.user)


@admin.register(DestinationReview)
class DestinationReviewAdmin(admin.ModelAdmin):
    list_display = ('destination', 'user', 'rating', 'title', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved', 'created_at')
    search_fields = ('destination__name', 'user__username', 'comment', 'title')
    actions = ['approve_reviews', 'reject_reviews']

    @admin.action(description="Approve selected reviews for public display")
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)

    @admin.action(description="Hide / Reject selected reviews")
    def reject_reviews(self, request, queryset):
        queryset.update(is_approved=False)


class SavedTripStopInline(admin.TabularInline):
    model = SavedTripStop
    extra = 0
    ordering = ('stop_order',)


@admin.register(SavedTrip)
class SavedTripAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'total_distance_km', 'estimated_duration_min', 'is_public', 'created_at')
    search_fields = ('title', 'user__username', 'notes')
    list_filter = ('is_public', 'created_at')
    inlines = [SavedTripStopInline]


@admin.register(DestinationImage)
class DestinationImageAdmin(admin.ModelAdmin):
    list_display = ('destination', 'caption', 'source_name', 'license_info', 'created_at')
    search_fields = ('destination__name', 'caption', 'photographer_attribution')
