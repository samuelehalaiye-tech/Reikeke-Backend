
from django.db import models
from django.conf import settings
from django.utils import timezone
User = settings.AUTH_USER_MODEL

class RideRequest(models.Model):
    STATUS_CHOICES = [
        ('pending','Pending'),
        ('driver_accepted','Driver Accepted'),
        ('passenger_confirmed','Passenger Confirmed'),
        ('ongoing','Ongoing'),
        ('completed','Completed'),
        ('cancelled','Cancelled'),
    ]
    passenger = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rides_requested')
    pickup_lat = models.FloatField()
    pickup_lng = models.FloatField()
    dropoff_lat = models.FloatField()
    dropoff_lng = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    assigned_driver = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='rides_assigned')
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)





    
    def __str__(self):
        return f"Ride {self.id} - {self.passenger}"

class Offer(models.Model):
    OFFER_STATUS = [
        ('pending','Pending'),
        ('accepted','Accepted'),
        ('rejected','Rejected'),
        ('expired','Expired'),
        ('cancelled','Cancelled'),
    ]
    ride = models.ForeignKey(RideRequest, on_delete=models.CASCADE, related_name='offers')
    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offers')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=OFFER_STATUS, default='pending')
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"Offer {self.id} ride {self.ride_id} -> driver {self.driver_id}"

class DriverLocation(models.Model):
    driver = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver_location')
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Location {self.driver} ({self.lat},{self.lng})"
