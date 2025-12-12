from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db.models.signals import post_save
from django.dispatch import receiver
import re

class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Phone number is required")
        # Normalize phone numbers to local format (0XXXXXXXXXX)
        digits = re.sub(r"\D", "", str(phone_number))
        if digits.startswith("234") and len(digits) >= 12:
            phone_number = "0" + digits[-10:]
        elif len(digits) == 10:
            phone_number = "0" + digits
        else:
            phone_number = digits

        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=15, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    def __str__(self):
        return str(self.phone_number)


class DriverProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    vehicle_type = models.CharField(max_length=50, blank=True)
    active_status = models.BooleanField(default=False)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    last_seen = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return f"{self.user.phone_number} - Driver"


class PassengerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.phone_number} - Passenger"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    # Profile creation is handled explicitly in registration serializers/views.
    # Removing automatic PassengerProfile creation to avoid creating both
    # passenger and driver profiles for the same user when registering drivers.
    return
