from django.urls import path
from . import views

app_name = 'destinations'

urlpatterns = [
    path('thiruvananthapuram/', views.thiruvananthapuram_destinations_view, name='thiruvananthapuram_list'),
    path('<slug:district_slug>/<slug:slug>/', views.destination_detail_view, name='destination_detail'),
]
