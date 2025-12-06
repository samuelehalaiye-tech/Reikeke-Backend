import math
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import  get_user_model

User= get_user_model()

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


def find_nearest_active_drivers(pickup_lat, pickup_lng, max_results=3, max_distance_km=10):
    drivers=[]
    qs= User.objects.filter(driverprofile__active_status=True, driver_location__isnull=False)

    for d in qs:
        lat= d.driver_location.lat
        lng=d.driver_location.lng
        if lat is None or lng is None:
            continue
        dist= haversine(pickup_lat, pickup_lng, lng, lat)
        if dist <= max_distance_km:
            drivers.append((d, dist))
    drivers.sort(key=lambda x:x[1])
    return [ d for d, _ in drivers[:max_results]]

def expire_offers_and_create_next(ride, exclude_driver_ids=None,max_results=1):
    from .models import Offer
    if exclude_driver_ids is None:
        exclude_driver_ids=set()
    now= timezone.now()
    expired = Offer.objects.filter(ride=ride, status='pending', expires_at__lt=now)
    expired.update(status='expired')
    existing= set(ride.offers.values_list('driver_id',flat=True))
    exclude=existing.union(set(exclude_driver_ids))
    nearest = find_nearest_active_drivers(ride.pickup_lat, ride.pickup_lng, max_results=max_results+len(exclude))

    created = []
    for d in nearest:
        if d.id in exclude:
            continue
        from django.utils import timezone
        from datetime import timedelta
        Offer.objects.create(
            ride=ride,
            driver=d,
            expires_at=timezone.now() + timedelta(minutes=5)
        )
        created.append(d)
        if len(created) >= max_results:
            break
    return created
