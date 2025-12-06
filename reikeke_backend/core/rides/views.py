from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import RideRequest, Offer
from .serializers import RideRequestSerializer, OfferSerializer, RideDetailSerializer
from django.utils import timezone
from datetime import timedelta
from .utils import find_nearest_active_drivers, expire_offers_and_create_next
from rest_framework.permissions import IsAuthenticated

class CreateRideRequestView(generics.CreateAPIView):
    serializer_class = RideRequestSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        ride = serializer.save(passenger=self.request.user)
    
        drivers = find_nearest_active_drivers(ride.pickup_lat, ride.pickup_lng, max_results=3)
        from datetime import timedelta
        for d in drivers:
            Offer.objects.create(
                ride=ride,
                driver=d,
                expires_at=timezone.now() + timedelta(minutes=5)
            )

class OfferListView(generics.ListAPIView):
    serializer_class = OfferSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Offer.objects.filter(driver=user, status='pending', expires_at__gt=timezone.now()).order_by('created_at')

class OfferAcceptView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, offer_id):
        user = request.user
        try:
            offer = Offer.objects.get(pk=offer_id, driver=user)
        except Offer.DoesNotExist:
            return Response({'detail':'Offer not found'}, status=404)
        if offer.status != 'pending':
            return Response({'detail':'Offer not pending'}, status=400)

        offer.status = 'accepted'
        offer.save()
        ride = offer.ride
        ride.assigned_driver = user
        ride.status = 'driver_accepted'
        ride.save()
        return Response({'detail':'accepted'})

class OfferRejectView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, offer_id):
        user = request.user
        try:
            offer = Offer.objects.get(pk=offer_id, driver=user)
        except Offer.DoesNotExist:
            return Response({'detail':'Offer not found'}, status=404)
        if offer.status != 'pending':
            return Response({'detail':'Offer not pending'}, status=400)
        offer.status = 'rejected'
        offer.save()
     
        expire_offers_and_create_next(offer.ride)
        return Response({'detail':'rejected'})

class RideConfirmView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, ride_id):
        # passenger confirms driver
        try:
            ride = RideRequest.objects.get(pk=ride_id, passenger=request.user)
        except RideRequest.DoesNotExist:
            return Response({'detail':'Ride not found'}, status=404)
        if ride.status != 'driver_accepted':
            return Response({'detail':'Ride not in driver_accepted state'}, status=400)
        ride.status = 'passenger_confirmed'
        ride.save()
        return Response({'detail':'passenger_confirmed'})

class RideStartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, ride_id):
      
        try:
            ride = RideRequest.objects.get(pk=ride_id, assigned_driver=request.user)
        except RideRequest.DoesNotExist:
            return Response({'detail':'Ride not found or not assigned to you'}, status=404)
        if ride.status != 'passenger_confirmed':
            return Response({'detail':'Ride must be passenger_confirmed before starting'}, status=400)
        ride.started_at = timezone.now()
        ride.status = 'ongoing'
        ride.save()
        return Response({'detail':'ride_started'})

class RideCompleteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, ride_id):
        try:
            ride = RideRequest.objects.get(pk=ride_id, assigned_driver=request.user)
        except RideRequest.DoesNotExist:
            return Response({'detail':'Ride not found or not assigned to you'}, status=404)
        if ride.status != 'ongoing':
            return Response({'detail':'Ride not ongoing'}, status=400)
        ride.completed_at = timezone.now()
        ride.status = 'completed'
        ride.save()
        return Response({'detail':'completed'})
class RideDetailView(generics.RetrieveAPIView):
    serializer_class = RideDetailSerializer
    permission_classes = [IsAuthenticated]
    queryset = RideRequest.objects.all()
