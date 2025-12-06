from django.urls import path
from .views import (
    LocationListCreateView,
    LocationDetailView,
    SetDefaultLocationView,
    DriverLocationUpdateView,
    DriverLocationDetailView,
    FavoriteLocationListView,
    AddFavoriteLocationView,
    RemoveFavoriteLocationView,
    IncrementLocationUsageView,
)

urlpatterns = [
    # Locations CRUD
    path('locations/', LocationListCreateView.as_view(), name='location-list-create'),
    path('locations/<int:pk>/', LocationDetailView.as_view(), name='location-detail'),
    path('locations/<int:pk>/set-default/', SetDefaultLocationView.as_view(), name='set-default-location'),
    
    # Driver Location
    path('driver-location/update/', DriverLocationUpdateView.as_view(), name='driver-location-update'),
    path('driver-location/<int:driver_id>/', DriverLocationDetailView.as_view(), name='driver-location-detail'),
    
    # Favorite Locations
    path('favorites/', FavoriteLocationListView.as_view(), name='favorite-list'),
    path('favorites/<int:location_id>/add/', AddFavoriteLocationView.as_view(), name='add-favorite'),
    path('favorites/<int:location_id>/remove/', RemoveFavoriteLocationView.as_view(), name='remove-favorite'),
    path('favorites/<int:location_id>/increment/', IncrementLocationUsageView.as_view(), name='increment-usage'),
]
