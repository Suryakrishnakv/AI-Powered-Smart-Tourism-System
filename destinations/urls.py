from django.urls import path
from . import views

app_name = 'destinations'

urlpatterns = [
    path('thiruvananthapuram/', views.district_destinations_view, {'district_slug': 'thiruvananthapuram'}, name='thiruvananthapuram_list'),
    path('kollam/', views.district_destinations_view, {'district_slug': 'kollam'}, name='kollam_list'),
    path('<slug:district_slug>/', views.district_destinations_view, name='district_list'),
    path('<slug:district_slug>/<slug:slug>/', views.destination_detail_view, name='destination_detail'),
]
