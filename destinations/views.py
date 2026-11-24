from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import District, Category, Destination


def thiruvananthapuram_destinations_view(request):
    """
    Explore Thiruvananthapuram page displaying real, verified destinations
    strictly belonging to Thiruvananthapuram district with interactive Leaflet map.
    """
    district = get_object_or_404(District, slug='thiruvananthapuram')
    destinations = Destination.objects.filter(district=district).select_related('category', 'district')

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
    map_markers = []
    for d in destinations:
        map_markers.append({
            'name': d.name,
            'lat': float(d.latitude),
            'lng': float(d.longitude),
            'category': d.category.name,
            'locality': d.village_locality,
            'image_url': d.display_image_url,
            'url': d.get_absolute_url(),
        })

    return render(request, 'destinations/thiruvananthapuram_list.html', {
        'district': district,
        'destinations': destinations,
        'categories': categories,
        'selected_category': selected_category_slug,
        'query': query,
        'map_markers': map_markers,
        'total_count': destinations.count(),
    })


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
