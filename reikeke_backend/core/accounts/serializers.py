from rest_framework import serializers
from .models import User, DriverProfile, PassengerProfile
import re


def normalize_phone(phone: str) -> str:
    """Normalize phone numbers to local 0XXXXXXXXXX format.
    - Strip non-digit characters
    - If starts with country code '234' convert to leading 0 + last 10 digits
    - If 10 digits, prepend 0
    """
    if not phone:
        return phone
    digits = re.sub(r"\D", "", phone)
    if digits.startswith("234") and len(digits) >= 12:
        return "0" + digits[-10:]
    if len(digits) == 10:
        return "0" + digits
    return digits


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone_number']



class PassengerRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['phone_number', 'password']

    def validate_phone_number(self, value):
        norm = normalize_phone(value)
        if User.objects.filter(phone_number=norm).exists():
            raise serializers.ValidationError("Phone number already registered")
        return norm

    def create(self, validated_data):
        phone = validated_data.get('phone_number')
        phone = normalize_phone(phone)
        user = User.objects.create_user(
            phone_number=phone,
            password=validated_data['password']
        )
        PassengerProfile.objects.get_or_create(user=user)
        return user  



class DriverRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['phone_number', 'password']

    def validate_phone_number(self, value):
        norm = normalize_phone(value)
        if User.objects.filter(phone_number=norm).exists():
            raise serializers.ValidationError("Phone number already registered")
        return norm

    def create(self, validated_data):
        phone = validated_data.get('phone_number')
        phone = normalize_phone(phone)
        user = User.objects.create_user(
            phone_number=phone,
            password=validated_data['password']
        )
        DriverProfile.objects.get_or_create(user=user)
        return user  



from django.contrib.auth import authenticate
import logging

logger = logging.getLogger(__name__)

class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        phone = data.get('phone_number')
        phone = normalize_phone(phone)
        pwd = data.get('password')
        
        logger.info(f"LoginSerializer.validate() called with phone_number={phone}")
        
        # First, check if user exists
        from .models import User
        try:
            user_obj = User.objects.get(phone_number=phone)
            logger.info(f"User found: {user_obj.id}, phone_number={user_obj.phone_number}")
        except User.DoesNotExist:
            logger.error(f"User with phone {phone} does not exist")
            raise serializers.ValidationError("Invalid credentials")
        
        # Now authenticate
        user = authenticate(username=phone, password=pwd)
        logger.info(f"authenticate() returned: {user}")
        
        if user and user.is_active:
            logger.info(f"Authentication successful for user {user.id}")
            return user  
        
        logger.error(f"Authentication failed. User: {user}, is_active: {user.is_active if user else 'N/A'}")
        raise serializers.ValidationError("Invalid credentials")
