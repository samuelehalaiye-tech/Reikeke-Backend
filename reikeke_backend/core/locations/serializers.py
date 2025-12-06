from rest_framework import serializers
from .models import Location, DriverLocation, FavoriteLocation


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name', 'latitude', 'longitude', 'address', 'location_type', 'is_default', 'created_at']
        read_only_fields = ['id', 'created_at']


class LocationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name', 'latitude', 'longitude', 'address', 'location_type', 'is_default', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class DriverLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverLocation
        fields = ['lat', 'lng', 'accuracy', 'updated_at']
        read_only_fields = ['updated_at']


class FavoriteLocationSerializer(serializers.ModelSerializer):
    location_details = LocationSerializer(source='location', read_only=True)
    
    class Meta:
        model = FavoriteLocation
        fields = ['id', 'location', 'location_details', 'times_used', 'created_at']
        read_only_fields = ['id', 'created_at', 'times_used']
