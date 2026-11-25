from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import District, Category, Destination

DISTRICT_ORDER = {
    'thiruvananthapuram': '01',
    'kollam': '02',
    'pathanamthitta': '03',
    'alappuzha': '04',
    'kottayam': '05',
    'idukki': '06',
    'ernakulam': '07',
    'thrissur': '08',
    'palakkad': '09',
    'malappuram': '10',
    'kozhikode': '11',
    'wayanad': '12',
    'kannur': '13',
    'kasaragod': '14',
}


def district_destinations_view(request, district_slug='thiruvananthapuram'):
    """
    Unified District Explore page displaying verified destinations strictly
    belonging to the requested Kerala district alongside an interactive Leaflet map.
    """
    district = get_object_or_404(District, slug=district_slug)
    all_district_destinations = Destination.objects.filter(
        district=district
    ).select_related('category', 'district')
    district_total = all_district_destinations.count()
    destinations = all_district_destinations

    # Category filter
    selected_category_slug = request.GET.get('category', '').strip()
    if selected_category_slug:
        destinations = destinations.filter(category__slug=selected_category_slug)

    # Search query
    query = request.GET.get('q', '').strip()
    if query:
        destinations = destinations.filter(
            Q(name__icontains=query) |
            Q(short_description__icontains=query) |
            Q(village_locality__icontains=query) |
            Q(available_activities__icontains=query)
        )

    categories = Category.objects.all()

    # Prepare lightweight destination markers for Leaflet map
    map_markers = [
        {
            'name': d.name,
            'lat': float(d.latitude),
            'lng': float(d.longitude),
            'category': d.category.name,
            'locality': d.village_locality,
            'image_url': d.display_image_url,
            'url': d.get_absolute_url(),
        }
        for d in destinations
    ]

    return render(request, 'destinations/district_list.html', {
        'district': district,
        'district_number': DISTRICT_ORDER.get(district.slug, '--'),
        'destinations': destinations,
        'categories': categories,
        'selected_category': selected_category_slug,
        'query': query,
        'map_markers': map_markers,
        'total_count': destinations.count(),
        'district_total': district_total,
    })


def thiruvananthapuram_destinations_view(request):
    """Backwards-compatible alias for Thiruvananthapuram explore view."""
    return district_destinations_view(request, district_slug='thiruvananthapuram')


def destination_detail_view(request, district_slug, slug):
    """
    Displays full detailed, verified information and interactive map for a destination.
    """
    destination = get_object_or_404(
        Destination.objects.select_related('district', 'category'),
        district__slug=district_slug,
        slug=slug
    )
    gallery_images = destination.gallery_images.all()

    # Nearby destinations in the same district
    nearby_destinations = Destination.objects.filter(
        district=destination.district
    ).exclude(id=destination.id)[:3]

    return render(request, 'destinations/destination_detail.html', {
        'destination': destination,
        'gallery_images': gallery_images,
        'nearby_destinations': nearby_destinations,
    })
