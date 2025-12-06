from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Location, DriverLocation, FavoriteLocation
from .serializers import (
    LocationSerializer, 
    DriverLocationSerializer, 
    FavoriteLocationSerializer,
    LocationDetailSerializer
)


class LocationListCreateView(generics.ListCreateAPIView):
    """List all user's saved locations or create a new one"""
    serializer_class = LocationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Location.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class LocationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete a specific location"""
    serializer_class = LocationDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Location.objects.filter(user=self.request.user)

    def get_object(self):
        return get_object_or_404(Location, pk=self.kwargs['pk'], user=self.request.user)


class SetDefaultLocationView(APIView):
    """Set a location as default"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            location = Location.objects.get(pk=pk, user=request.user)
            # Remove default from other locations
            Location.objects.filter(user=request.user).update(is_default=False)
            # Set this as default
            location.is_default = True
            location.save()
            return Response({'status': 'Location set as default'}, status=status.HTTP_200_OK)
        except Location.DoesNotExist:
            return Response({'error': 'Location not found'}, status=status.HTTP_404_NOT_FOUND)


class DriverLocationUpdateView(generics.UpdateAPIView):
    """Update driver's real-time location"""
    serializer_class = DriverLocationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj, _ = DriverLocation.objects.get_or_create(driver=self.request.user)
        return obj


class DriverLocationDetailView(generics.RetrieveAPIView):
    """Get a driver's current location"""
    serializer_class = DriverLocationSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'driver_id'

    def get_queryset(self):
        return DriverLocation.objects.all()


class FavoriteLocationListView(generics.ListAPIView):
    """List user's favorite locations (most frequently used)"""
    serializer_class = FavoriteLocationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FavoriteLocation.objects.filter(user=self.request.user)


class AddFavoriteLocationView(APIView):
    """Add a location to favorites"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, location_id):
        try:
            location = Location.objects.get(pk=location_id, user=request.user)
            favorite, created = FavoriteLocation.objects.get_or_create(
                user=request.user,
                location=location
            )
            serializer = FavoriteLocationSerializer(favorite)
            status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
            return Response(serializer.data, status=status_code)
        except Location.DoesNotExist:
            return Response({'error': 'Location not found'}, status=status.HTTP_404_NOT_FOUND)


class RemoveFavoriteLocationView(APIView):
    """Remove a location from favorites"""
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, location_id):
        try:
            location = Location.objects.get(pk=location_id, user=request.user)
            FavoriteLocation.objects.filter(
                user=request.user,
                location=location
            ).delete()
            return Response({'status': 'Location removed from favorites'}, status=status.HTTP_204_NO_CONTENT)
        except Location.DoesNotExist:
            return Response({'error': 'Location not found'}, status=status.HTTP_404_NOT_FOUND)


class IncrementLocationUsageView(APIView):
    """Increment usage count for a favorite location"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, location_id):
        try:
            location = Location.objects.get(pk=location_id, user=request.user)
            favorite = FavoriteLocation.objects.get(user=request.user, location=location)
            favorite.times_used += 1
            favorite.save()
            serializer = FavoriteLocationSerializer(favorite)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (Location.DoesNotExist, FavoriteLocation.DoesNotExist):
            return Response({'error': 'Location not found in favorites'}, status=status.HTTP_404_NOT_FOUND)
