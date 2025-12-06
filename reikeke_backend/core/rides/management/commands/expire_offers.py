from django.core.management.base import BaseCommand
from django.utils import timezone
from rides.models import Offer
from rides.utils import expire_offers_and_create_next

class Command(BaseCommand):
    help = "Expire old ride offers and create new ones automatically."

    def handle(self, *args, **kwargs):
        now = timezone.now()
        expired_offers = Offer.objects.filter(status='pending', expires_at__lt=now)

        for offer in expired_offers:
            self.stdout.write(f"Expiring offer {offer.id}")
            offer.status = 'expired'
            offer.save()
            expire_offers_and_create_next(offer.ride)

        self.stdout.write(self.style.SUCCESS("Offer expiry job completed."))
