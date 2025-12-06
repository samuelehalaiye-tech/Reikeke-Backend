from django.contrib import admin
from .models import Location, DriverLocation, FavoriteLocation

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'location_type', 'latitude', 'longitude', 'created_at')
    list_filter = ('location_type', 'created_at', 'is_default')
    search_fields = ('user__phone_number', 'name', 'address')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Info', {'fields': ('user', 'name', 'location_type', 'is_default')}),
        ('Coordinates', {'fields': ('latitude', 'longitude', 'accuracy')}),
        ('Details', {'fields': ('address',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

@admin.register(DriverLocation)
class DriverLocationAdmin(admin.ModelAdmin):
    list_display = ('driver', 'lat', 'lng', 'updated_at', 'accuracy')
    list_filter = ('updated_at',)
    search_fields = ('driver__phone_number',)
    readonly_fields = ('updated_at',)

@admin.register(FavoriteLocation)
class FavoriteLocationAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'times_used', 'created_at')
    list_filter = ('created_at', 'times_used')
    search_fields = ('user__phone_number', 'location__name')
    readonly_fields = ('created_at',)
