from django.urls import path
from . import views

app_name = 'destinations'

urlpatterns = [
    path('map/', views.kerala_interactive_map_view, name='kerala_map'),
    path('api/districts-geojson/', views.api_districts_geojson, name='api_districts_geojson'),
    path('api/autocomplete/', views.api_autocomplete, name='api_autocomplete'),
    path('api/review/add/', views.api_add_review, name='api_add_review'),
    path('api/destinations/', views.api_destinations_list, name='api_destinations_list'),
    path('api/nearby/', views.api_nearby_destinations, name='api_nearby_destinations'),
    path('api/route/', views.api_route_proxy, name='api_route_proxy'),
    path('api/trip/save/', views.api_save_trip, name='api_save_trip'),
    path('api/trip/list/', views.api_list_trips, name='api_list_trips'),
    path('thiruvananthapuram/', views.district_destinations_view, {'district_slug': 'thiruvananthapuram'}, name='thiruvananthapuram_list'),
    path('kollam/', views.district_destinations_view, {'district_slug': 'kollam'}, name='kollam_list'),
    path('pathanamthitta/', views.district_destinations_view, {'district_slug': 'pathanamthitta'}, name='pathanamthitta_list'),
    path('alappuzha/', views.district_destinations_view, {'district_slug': 'alappuzha'}, name='alappuzha_list'),
    path('kottayam/', views.district_destinations_view, {'district_slug': 'kottayam'}, name='kottayam_list'),
    path('idukki/', views.district_destinations_view, {'district_slug': 'idukki'}, name='idukki_list'),
    path('ernakulam/', views.district_destinations_view, {'district_slug': 'ernakulam'}, name='ernakulam_list'),
    path('thrissur/', views.district_destinations_view, {'district_slug': 'thrissur'}, name='thrissur_list'),
    path('palakkad/', views.district_destinations_view, {'district_slug': 'palakkad'}, name='palakkad_list'),
    path('<slug:district_slug>/', views.district_destinations_view, name='district_list'),
    path('<slug:district_slug>/<slug:slug>/', views.destination_detail_view, name='destination_detail'),
]
