
from rest_framework import serializers
from .models import RideRequest, Offer
from django.contrib.auth import get_user_model

User = get_user_model()

class RideRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RideRequest
        fields = ['id','pickup_lat','pickup_lng','dropoff_lat','dropoff_lng','status','created_at']

class OfferSerializer(serializers.ModelSerializer):
    driver_phone = serializers.CharField(source='driver.phone_number', read_only=True)
    class Meta:
        model = Offer
        fields = ['id','ride','driver','driver_phone','status','created_at','expires_at']

class RideDetailSerializer(serializers.ModelSerializer):
    driver_phone = serializers.CharField(source='assigned_driver.phone_number', read_only=True)
    driver_location = serializers.SerializerMethodField()

    class Meta:
        model = RideRequest
        fields = [
            'id', 'status', 'pickup_lat', 'pickup_lng',
            'dropoff_lat', 'dropoff_lng',
            'assigned_driver', 'driver_phone',
            'driver_location', 'created_at', 'started_at', 'completed_at'
        ]

    def get_driver_location(self, obj):
        if obj.assigned_driver and hasattr(obj.assigned_driver, 'driver_location'):
            loc = obj.assigned_driver.driver_location
            return {
                'lat': loc.lat,
                'lng': loc.lng,
                'updated_at': loc.updated_at
            }
        return None


class PassengerRideHistorySerializer(serializers.ModelSerializer):
    driver_info = serializers.SerializerMethodField()
    
    class Meta:
        model = RideRequest
        fields = ['id', 'status', 'pickup_lat', 'pickup_lng', 'dropoff_lat', 'dropoff_lng', 
                  'created_at', 'started_at', 'completed_at', 'driver_info']
    
    def get_driver_info(self, obj):
        if obj.assigned_driver:
            return {
                'phone': obj.assigned_driver.phone_number,
                'id': obj.assigned_driver.id
            }
        return None
