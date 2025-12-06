from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

User = settings.AUTH_USER_MODEL

class Location(models.Model):
    """Represents a saved location (home, work, etc.)"""
    LOCATION_TYPE_CHOICES = [
        ('home', 'Home'),
        ('work', 'Work'),
        ('favorites', 'Favorites'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_locations')
    name = models.CharField(max_length=100)  # "Home", "Work", etc.
    latitude = models.DecimalField(max_digits=9, decimal_places=6, validators=[MinValueValidator(-90), MaxValueValidator(90)])
    longitude = models.DecimalField(max_digits=9, decimal_places=6, validators=[MinValueValidator(-180), MaxValueValidator(180)])
    address = models.CharField(max_length=255, blank=True)
    location_type = models.CharField(max_length=20, choices=LOCATION_TYPE_CHOICES, default='other')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_default = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('user', 'latitude', 'longitude')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.user.phone_number}"


class DriverLocation(models.Model):
    """Real-time location tracking for drivers"""
    driver = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver_location')
    lat = models.DecimalField(max_digits=9, decimal_places=6, validators=[MinValueValidator(-90), MaxValueValidator(90)])
    lng = models.DecimalField(max_digits=9, decimal_places=6, validators=[MinValueValidator(-180), MaxValueValidator(180)])
    updated_at = models.DateTimeField(auto_now=True)
    accuracy = models.FloatField(null=True, blank=True)  # GPS accuracy in meters
    
    def __str__(self):
        return f"Driver {self.driver.phone_number} at ({self.lat}, {self.lng})"


class FavoriteLocation(models.Model):
    """Frequently used locations for quick access"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_locations')
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    times_used = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'location')
        ordering = ['-times_used', '-created_at']
    
    def __str__(self):
        return f"{self.user.phone_number} - {self.location.name}"
