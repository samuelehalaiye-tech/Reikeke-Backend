from rest_framework import serializers
from .models import User, DriverProfile, PassengerProfile
from django.contrib.auth import authenticate



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['id','phone_number']


class PassengerRegisterSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True)

    class Meta:
        model=User
        fields= ['phone_number','password']
    

    def create(self, validated_data):
        user=User.objects.create_user(
            phone_number=validated_data['phone number'],
            password=validated_data['password']
        )


        PassengerProfile.objects.create(user=user)
        return user


class DriverRegisterSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True)

    class Meta:
        model=User
        fields= ['phone_number','password']
    

    def create(self, validated_data):
        user=User.objects.create_user(
            phone_number=validated_data['phone number'],
            password=validated_data['password']
        )


        DriverProfile.objects.create(user=user)
        return user

class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(
            phone_number=data['phone_number'],
            password=data['password']
        )
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Invalid credentials")
