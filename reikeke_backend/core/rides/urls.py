
from django.urls import path
from .views import (
    CreateRideRequestView, OfferListView, OfferAcceptView, OfferRejectView,
    UpdateLocationView, RideConfirmView, RideStartView, RideCompleteView,RideDetailView
)

urlpatterns = [
    path('rides/', CreateRideRequestView.as_view(), name='create-ride'),
    path('offers/', OfferListView.as_view(), name='offers-list'),
    path('offers/<int:offer_id>/accept/', OfferAcceptView.as_view(), name='offer-accept'),
    path('offers/<int:offer_id>/reject/', OfferRejectView.as_view(), name='offer-reject'),
    path('drivers/location/', UpdateLocationView.as_view(), name='driver-location'),
    path('rides/<int:ride_id>/confirm/', RideConfirmView.as_view(), name='ride-confirm'),
    path('rides/<int:ride_id>/start/', RideStartView.as_view(), name='ride-start'),
    path('rides/<int:ride_id>/complete/', RideCompleteView.as_view(), name='ride-complete'),
    path('ride/<int:pk>/', RideDetailView.as_view(), name='ride-detail'),

]
