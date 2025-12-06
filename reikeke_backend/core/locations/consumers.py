import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from locations.models import DriverLocation
from rides.models import RideRequest
from django.contrib.auth import get_user_model

User = get_user_model()


class DriverLocationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time driver location tracking.
    Allows drivers to broadcast their location to passengers watching their ride.
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope["user"]
        self.ride_id = self.scope['url_route']['kwargs'].get('ride_id')
        self.room_group_name = f'ride_{self.ride_id}'
        
        # Add user to the ride group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages from drivers"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'driver_location':
                await self.handle_driver_location(data)
            elif message_type == 'ping':
                await self.send(text_data=json.dumps({'type': 'pong'}))
        except json.JSONDecodeError:
            await self.send_error("Invalid JSON")
        except Exception as e:
            await self.send_error(str(e))
    
    async def handle_driver_location(self, data):
        """Handle driver location update"""
        # Verify user is the driver for this ride
        ride = await self.get_ride(self.ride_id)
        
        if not ride:
            await self.send_error("Ride not found")
            return
        
        if ride.assigned_driver_id != self.user.id:
            await self.send_error("Not authorized - you are not the driver")
            return
        
        # Update driver location
        lat = data.get('lat')
        lng = data.get('lng')
        accuracy = data.get('accuracy')
        
        if lat is None or lng is None:
            await self.send_error("Latitude and longitude required")
            return
        
        await self.update_driver_location(self.user.id, lat, lng, accuracy)
        
        # Broadcast location to all users in this ride group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'broadcast_location',
                'driver_id': self.user.id,
                'lat': lat,
                'lng': lng,
                'accuracy': accuracy,
                'timestamp': str(data.get('timestamp', ''))
            }
        )
    
    async def broadcast_location(self, event):
        """Broadcast location update to all connected clients"""
        await self.send(text_data=json.dumps({
            'type': 'driver_location',
            'driver_id': event['driver_id'],
            'lat': event['lat'],
            'lng': event['lng'],
            'accuracy': event['accuracy'],
            'timestamp': event['timestamp']
        }))
    
    async def send_error(self, message):
        """Send error message to client"""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message
        }))
    
    @database_sync_to_async
    def get_ride(self, ride_id):
        """Get ride from database"""
        try:
            return RideRequest.objects.get(pk=ride_id)
        except RideRequest.DoesNotExist:
            return None
    
    @database_sync_to_async
    def update_driver_location(self, driver_id, lat, lng, accuracy):
        """Update driver location in database"""
        driver_location, _ = DriverLocation.objects.get_or_create(driver_id=driver_id)
        driver_location.lat = lat
        driver_location.lng = lng
        if accuracy:
            driver_location.accuracy = accuracy
        driver_location.save()
