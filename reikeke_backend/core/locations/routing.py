from django.urls import re_path
from locations.consumers import DriverLocationConsumer

websocket_urlpatterns = [
    re_path(r'ws/rides/(?P<ride_id>\d+)/location/$', DriverLocationConsumer.as_asgi()),
]
