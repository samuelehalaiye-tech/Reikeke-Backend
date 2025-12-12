from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import RideRequest, Offer
from .serializers import RideRequestSerializer, OfferSerializer, RideDetailSerializer, PassengerRideHistorySerializer
from django.utils import timezone
from datetime import timedelta
from .utils import find_nearest_active_drivers, expire_offers_and_create_next
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Avg, Q, Sum
from decimal import Decimal

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


class DriverStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        driver = request.user
        completed_rides = RideRequest.objects.filter(assigned_driver=driver, status='completed')
        
        total_rides = completed_rides.count()
        total_earnings = Decimal('0')
        avg_rating = 0
        acceptance_rate = 0
        
        if total_rides > 0:
            # Calculate stats
            total_earnings = Decimal('50.00') * total_rides  # Default $50 per ride
            avg_rating = 4.5  # Placeholder - would come from Rating model
        
        total_offers = Offer.objects.filter(driver=driver).count()
        accepted_offers = Offer.objects.filter(driver=driver, status='accepted').count()
        if total_offers > 0:
            acceptance_rate = (accepted_offers / total_offers) * 100
        
        return Response({
            'total_rides': total_rides,
            'total_earnings': float(total_earnings),
            'avg_rating': avg_rating,
            'acceptance_rate': round(acceptance_rate, 2),
            'active_rides': RideRequest.objects.filter(assigned_driver=driver, status__in=['driver_accepted', 'passenger_confirmed', 'ongoing']).count(),
        })


class DriverHistoryView(generics.ListAPIView):
    serializer_class = RideDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RideRequest.objects.filter(assigned_driver=self.request.user, status='completed').order_by('-completed_at')


class DriverActiveRideView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        driver = request.user
        active_ride = RideRequest.objects.filter(
            assigned_driver=driver,
            status__in=['driver_accepted', 'passenger_confirmed', 'ongoing']
        ).first()
        
        if not active_ride:
            return Response({'detail': 'No active ride'}, status=404)
        
        serializer = RideDetailSerializer(active_ride)
        return Response(serializer.data)


class PassengerActiveRideView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        passenger = request.user
        active_ride = RideRequest.objects.filter(
            passenger=passenger,
            status__in=['pending', 'driver_accepted', 'passenger_confirmed', 'ongoing']
        ).first()
        
        if not active_ride:
            return Response({'detail': 'No active ride'}, status=404)
        
        serializer = RideDetailSerializer(active_ride)
        return Response(serializer.data)


class PassengerRidesHistoryView(generics.ListAPIView):
    serializer_class = PassengerRideHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RideRequest.objects.filter(
            passenger=self.request.user,
            status__in=['completed', 'cancelled']
        ).order_by('-completed_at')


class RideCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, ride_id):
        try:
            ride = RideRequest.objects.get(pk=ride_id, passenger=request.user)
        except RideRequest.DoesNotExist:
            return Response({'detail': 'Ride not found'}, status=404)
        
        if ride.status not in ['pending', 'driver_accepted']:
            return Response(
                {'detail': 'Can only cancel pending or accepted rides'}, 
                status=400
            )
        
        ride.status = 'cancelled'
        ride.save()
        return Response({'detail': 'Ride cancelled'}, status=200)


class PassengerStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        passenger = request.user
        completed_rides = RideRequest.objects.filter(passenger=passenger, status='completed')
        
        total_rides = completed_rides.count()
        total_spent = Decimal('0')
        
        if total_rides > 0:
            total_spent = Decimal('50.00') * total_rides  # Default $50 per ride
        
        active_ride = RideRequest.objects.filter(
            passenger=passenger,
            status__in=['pending', 'driver_accepted', 'passenger_confirmed', 'ongoing']
        ).exists()
        
        return Response({
            'total_rides': total_rides,
            'total_spent': float(total_spent),
            'has_active_ride': active_ride,
        })
