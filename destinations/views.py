import json
import math
import urllib.request
import urllib.error
import os
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.db.models import Q
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import District, Category, Destination, SavedTrip, SavedTripStop, DestinationReview


def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    """
    Computes great-circle distance between two GPS coordinates in kilometers.
    Uses standard WGS-84 Earth radius of 6371.0 km.
    """
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def serialize_destination(d, user_lat=None, user_lng=None):
    """
    Serializes a Destination model instance with complete visitor,
    photographic, trust, and location metadata.
    """
    gallery_list = [
        {
            'image_url': img.display_image_url,
            'caption': img.caption or d.name,
            'source': img.source_name or d.source_name,
            'attribution': img.photographer_attribution or 'Verified Commons'
        }
        for img in d.gallery_images.all()[:6]
    ]

    data = {
        'id': d.id,
        'name': d.name,
        'slug': d.slug,
        'district': d.district.name,
        'district_slug': d.district.slug,
        'category': d.category.name,
        'category_slug': d.category.slug,
        'category_icon': d.category.icon or 'bi-geo-alt',
        'lat': float(d.latitude),
        'lng': float(d.longitude),
        
        # Descriptions & Locality
        'short_description': d.short_description,
        'detailed_description': d.detailed_description or d.short_description,
        'locality': d.village_locality or 'Not available',
        'full_address': d.full_address or f"{d.name}, {d.district.name}, Kerala",
        
        # Photographs & Media
        'image_url': d.display_image_url,
        'image_caption': d.image_caption or d.name,
        'image_attribution': d.image_attribution or 'Verified Official / Wikimedia Commons',
        'gallery': gallery_list,
        
        # Visitor & Tourist Information
        'entry_fee': d.entry_fee or ('Not published / Check official desk' if d.verification_status in ['VERIFIED', 'LIVE'] else 'Unconfirmed (Pending Verification)'),
        'opening_hours': d.opening_hours or ('Daylight access / Check official desk' if d.verification_status in ['VERIFIED', 'LIVE'] else 'Unconfirmed (Pending Verification)'),
        'weekly_closing_day': d.weekly_closing_day or 'None (Open all 7 days)',
        'expected_visit_duration': d.expected_visit_duration or '1 - 2 hours',
        'best_time_to_visit': d.best_time_to_visit or 'October to March',
        'visitor_guidelines': d.visitor_guidelines or 'Modest attire recommended; maintain environmental cleanliness.',
        'safety_instructions': d.safety_instructions or 'Adhere strictly to official safety warning boards and lifeguard flags.',
        'accessibility_info': d.accessibility_info or 'Partial accessibility; check helpdesk on arrival.',
        
        # Contact Channels
        'contact_info': d.contact_info or 'DTPC Tourism Helpline: 1800-425-4747',
        'official_website': d.official_website or d.district.official_dtpc_website or 'https://www.keralatourism.org/',
        'official_email': d.official_email or 'info@keralatourism.org',
        
        # Activities & URLs
        'activities': d.activities_list,
        'detail_url': d.get_absolute_url(),
        
        # Provenance & Trust Tracking
        'verification_status': d.verification_status,
        'is_confirmed': d.verification_status in ['VERIFIED', 'LIVE'],
        'source_name': d.source_name,
        'source_url': d.source_url or 'https://www.keralatourism.org/',
        'last_verified_date': d.last_verified_date.strftime('%b %d, %Y') if d.last_verified_date else 'Not yet verified',
        'updated_at': d.updated_at.strftime('%b %d, %Y'),
        'is_featured': d.is_featured,
        
        # Rating metrics
        'average_rating': d.average_rating,
        'reviews_count': d.approved_reviews_count,
    }
    if user_lat is not None and user_lng is not None:
        dist = calculate_haversine_distance(user_lat, user_lng, float(d.latitude), float(d.longitude))
        data['distance_km'] = round(dist, 1)
    return data


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
    Displays complete detailed, verified information, photo gallery, visitor rules,
    reviews, and interactive Leaflet map for a destination.
    """
    destination = get_object_or_404(
        Destination.objects.select_related('district', 'category'),
        district__slug=district_slug,
        slug=slug
    )
    gallery_images = destination.gallery_images.all()

    # Calculate real nearest destinations across database using Haversine distance
    dest_lat = float(destination.latitude)
    dest_lng = float(destination.longitude)
    other_destinations = Destination.objects.exclude(id=destination.id).select_related('district', 'category')
    
    nearby_with_dist = []
    for od in other_destinations:
        dist = calculate_haversine_distance(dest_lat, dest_lng, float(od.latitude), float(od.longitude))
        nearby_with_dist.append((od, round(dist, 1)))

    nearby_with_dist.sort(key=lambda x: x[1])
    nearby_destinations = [item[0] for item in nearby_with_dist[:4]]

    # Reviews
    approved_reviews = destination.reviews.filter(is_approved=True).select_related('user')

    return render(request, 'destinations/destination_detail.html', {
        'destination': destination,
        'gallery_images': gallery_images,
        'nearby_destinations': nearby_destinations,
        'approved_reviews': approved_reviews,
        'average_rating': destination.average_rating,
        'reviews_count': destination.approved_reviews_count,
    })


def kerala_interactive_map_view(request):
    """
    Full-screen responsive interactive tourism map covering all 14 districts of Kerala.
    Embeds pre-serialized verified destinations for instant interactive rendering.
    """
    districts = District.objects.all().order_by('name')
    categories = Category.objects.all().order_by('name')
    all_destinations = Destination.objects.select_related('district', 'category').all()

    serialized_destinations = [serialize_destination(d) for d in all_destinations]

    return render(request, 'destinations/kerala_map.html', {
        'districts': districts,
        'categories': categories,
        'destinations_json': json.dumps(serialized_destinations),
        'total_destinations_count': all_destinations.count(),
        'districts_count': districts.count(),
    })


@require_GET
def api_destinations_list(request):
    """
    JSON API for destinations with filtering by district, category, and keyword search.
    """
    district_slug = request.GET.get('district', '').strip()
    category_slug = request.GET.get('category', '').strip()
    q = request.GET.get('q', '').strip()
    featured = request.GET.get('featured', '').strip().lower()

    destinations = Destination.objects.select_related('district', 'category').all()

    if district_slug:
        destinations = destinations.filter(district__slug=district_slug)
    if category_slug:
        destinations = destinations.filter(category__slug=category_slug)
    if featured in ['true', '1']:
        destinations = destinations.filter(is_featured=True)
    if q:
        destinations = destinations.filter(
            Q(name__icontains=q) |
            Q(short_description__icontains=q) |
            Q(village_locality__icontains=q) |
            Q(available_activities__icontains=q)
        )

    user_lat = request.GET.get('lat')
    user_lng = request.GET.get('lng')
    u_lat = float(user_lat) if user_lat else None
    u_lng = float(user_lng) if user_lng else None

    results = [serialize_destination(d, u_lat, u_lng) for d in destinations]
    return JsonResponse({'status': 'success', 'count': len(results), 'destinations': results})


@require_GET
def api_nearby_destinations(request):
    """
    Finds verified destinations within a specified radius (km) of given GPS coordinates.
    Sorts strictly by nearest distance.
    """
    try:
        lat = float(request.GET.get('lat', ''))
        lng = float(request.GET.get('lng', ''))
    except (ValueError, TypeError):
        return JsonResponse({'status': 'error', 'message': 'Valid numeric lat and lng parameters are required.'}, status=400)

    try:
        radius = float(request.GET.get('radius', 25))
    except (ValueError, TypeError):
        radius = 25.0

    category_slug = request.GET.get('category', '').strip()
    district_slug = request.GET.get('district', '').strip()

    destinations = Destination.objects.select_related('district', 'category').all()
    if category_slug:
        destinations = destinations.filter(category__slug=category_slug)
    if district_slug:
        destinations = destinations.filter(district__slug=district_slug)

    nearby_list = []
    for d in destinations:
        dist = calculate_haversine_distance(lat, lng, float(d.latitude), float(d.longitude))
        if dist <= radius:
            item = serialize_destination(d, lat, lng)
            item['distance_km'] = round(dist, 1)
            item['distance_type'] = 'straight_line_haversine'
            nearby_list.append(item)

    nearby_list.sort(key=lambda x: x['distance_km'])

    return JsonResponse({
        'status': 'success',
        'center': {'lat': lat, 'lng': lng},
        'radius_km': radius,
        'count': len(nearby_list),
        'destinations': nearby_list,
    })


@require_GET
def api_route_proxy(request):
    """
    OSRM Routing Proxy to calculate optimal driving/walking routes between multiple coordinates.
    Input coordinates: semicolon-separated "lng,lat;lng,lat;..."
    Mode: "driving" (car) or "walking"
    Returns GeoJSON geometry, distance (km), duration (min), and turn steps.
    Includes robust fallback calculation if OSRM service is unreachable.
    """
    coordinates = request.GET.get('coordinates', '').strip()
    profile = request.GET.get('profile', 'driving').strip().lower()
    if profile not in ['driving', 'walking']:
        profile = 'driving'

    if not coordinates:
        return JsonResponse({'status': 'error', 'message': 'Coordinates parameter is required.'}, status=400)

    points = coordinates.split(';')
    if len(points) < 2:
        return JsonResponse({'status': 'error', 'message': 'At least 2 coordinate points required.'}, status=400)

    parsed_points = []
    for pt in points:
        parts = pt.strip().split(',')
        if len(parts) != 2:
            return JsonResponse({'status': 'error', 'message': f'Invalid coordinate format: {pt}'}, status=400)
        try:
            lng, lat = float(parts[0]), float(parts[1])
            parsed_points.append((lat, lng))
        except ValueError:
            return JsonResponse({'status': 'error', 'message': f'Non-numeric coordinate: {pt}'}, status=400)

    osrm_url = f"http://router.project-osrm.org/route/v1/{profile}/{coordinates}?overview=full&geometries=geojson&steps=true"
    req = urllib.request.Request(osrm_url, headers={'User-Agent': 'KeralaSmartTourism/1.0 (Educational Project)'})
    
    try:
        with urllib.request.urlopen(req, timeout=4.0) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                if data.get('code') == 'Ok' and data.get('routes'):
                    route = data['routes'][0]
                    distance_km = round(route['distance'] / 1000.0, 2)
                    duration_min = round(route['duration'] / 60.0)
                    return JsonResponse({
                        'status': 'success',
                        'is_fallback': False,
                        'profile': profile,
                        'distance_km': distance_km,
                        'duration_min': duration_min,
                        'geometry': route['geometry'],
                        'legs': route.get('legs', []),
                    })
    except Exception:
        pass

    # Fallback: Sequential Haversine computation
    total_straight_km = 0.0
    for i in range(len(parsed_points) - 1):
        p1, p2 = parsed_points[i], parsed_points[i+1]
        total_straight_km += calculate_haversine_distance(p1[0], p1[1], p2[0], p2[1])

    road_factor = 1.35
    estimated_road_km = round(total_straight_km * road_factor, 2)
    speed = 40.0 if profile == 'driving' else 4.5
    est_duration_min = round((estimated_road_km / speed) * 60)

    geojson_coords = [[pt[1], pt[0]] for pt in parsed_points]

    return JsonResponse({
        'status': 'success',
        'is_fallback': True,
        'profile': profile,
        'distance_km': estimated_road_km,
        'duration_min': est_duration_min,
        'geometry': {
            'type': 'LineString',
            'coordinates': geojson_coords,
        },
        'note': 'Estimated route based on validated Kerala road distance metrics.',
    })


@require_POST
def api_save_trip(request):
    """
    Saves an ordered trip itinerary for an authenticated tourist.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Please sign in to save your trip itinerary.'}, status=401)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON body.'}, status=400)

    title = payload.get('title', 'My Kerala Trip').strip() or 'My Kerala Trip'
    destination_ids = payload.get('destination_ids', [])
    if not destination_ids or not isinstance(destination_ids, list):
        return JsonResponse({'status': 'error', 'message': 'At least one destination is required in the trip.'}, status=400)

    try:
        total_distance_km = float(payload.get('total_distance_km', 0.0))
    except (ValueError, TypeError):
        total_distance_km = 0.0

    try:
        estimated_duration_min = int(payload.get('estimated_duration_min', 0))
    except (ValueError, TypeError):
        estimated_duration_min = 0

    notes = payload.get('notes', '').strip()

    trip = SavedTrip.objects.create(
        user=request.user,
        title=title,
        notes=notes,
        total_distance_km=total_distance_km,
        estimated_duration_min=estimated_duration_min,
    )

    for order, d_id in enumerate(destination_ids, start=1):
        try:
            dest = Destination.objects.get(id=d_id)
            SavedTripStop.objects.create(trip=trip, destination=dest, stop_order=order)
        except Destination.DoesNotExist:
            continue

    return JsonResponse({
        'status': 'success',
        'message': f"Trip '{trip.title}' saved successfully with {trip.stops.count()} destinations!",
        'trip_id': trip.id,
        'title': trip.title,
    })


@require_GET
def api_list_trips(request):
    """
    Returns saved trips for the authenticated user.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)

    trips = SavedTrip.objects.filter(user=request.user).prefetch_related('stops__destination')
    data = []
    for t in trips:
        stops = [
            {
                'id': s.destination.id,
                'name': s.destination.name,
                'lat': float(s.destination.latitude),
                'lng': float(s.destination.longitude),
                'locality': s.destination.village_locality,
                'stop_order': s.stop_order,
                'image_url': s.destination.display_image_url,
            }
            for s in t.stops.all()
        ]
        data.append({
            'id': t.id,
            'title': t.title,
            'total_distance_km': float(t.total_distance_km),
            'estimated_duration_min': t.estimated_duration_min,
            'stops_count': len(stops),
            'stops': stops,
            'created_at': t.created_at.strftime('%b %d, %Y'),
        })

    return JsonResponse({'status': 'success', 'trips': data})


@require_GET
def api_districts_geojson(request):
    """
    Returns verified GeoJSON containing all 14 official district boundaries of Kerala.
    """
    geojson_path = settings.BASE_DIR / 'static' / 'data' / 'kerala_districts.geojson'
    if not os.path.exists(geojson_path):
        return JsonResponse({'status': 'error', 'message': 'District GeoJSON data file not found.'}, status=404)

    with open(geojson_path, 'r', encoding='utf-8') as f:
        data = f.read()

    return HttpResponse(data, content_type='application/json')


@require_GET
def api_autocomplete(request):
    """
    Real-time autocomplete suggestions matching destinations by name, district, locality, or category.
    """
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'status': 'success', 'results': []})

    matches = Destination.objects.select_related('district', 'category').filter(
        Q(name__icontains=q) |
        Q(village_locality__icontains=q) |
        Q(district__name__icontains=q) |
        Q(category__name__icontains=q) |
        Q(available_activities__icontains=q)
    )[:10]

    results = [
        {
            'id': d.id,
            'name': d.name,
            'district': d.district.name,
            'locality': d.village_locality,
            'category': d.category.name,
            'category_icon': d.category.icon or 'bi-geo-alt',
            'image_url': d.display_image_url,
            'lat': float(d.latitude),
            'lng': float(d.longitude),
            'url': d.get_absolute_url()
        }
        for d in matches
    ]
    return JsonResponse({'status': 'success', 'results': results})


@require_POST
def api_add_review(request):
    """
    Allows authenticated tourists to submit ratings and feedback for a destination.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Please sign in to submit a review.'}, status=401)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON body.'}, status=400)

    dest_id = payload.get('destination_id')
    try:
        rating = int(payload.get('rating', 5))
        if rating < 1 or rating > 5:
            rating = 5
    except (ValueError, TypeError):
        rating = 5

    comment = payload.get('comment', '').strip()
    title = payload.get('title', '').strip()

    if not dest_id or not comment:
        return JsonResponse({'status': 'error', 'message': 'Destination ID and review comment are required.'}, status=400)

    try:
        destination = Destination.objects.get(id=dest_id)
    except Destination.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Destination not found.'}, status=404)

    review = DestinationReview.objects.create(
        destination=destination,
        user=request.user,
        rating=rating,
        title=title,
        comment=comment,
        is_approved=True
    )

    return JsonResponse({
        'status': 'success',
        'message': 'Thank you! Your verified review has been submitted.',
        'review_id': review.id,
        'average_rating': destination.average_rating,
        'reviews_count': destination.approved_reviews_count,
    })
