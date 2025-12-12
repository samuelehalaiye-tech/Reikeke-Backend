from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from .serializers import (
    PassengerRegisterSerializer,
    DriverRegisterSerializer,
    LoginSerializer
)
from .models import PassengerProfile, DriverProfile



class PassengerRegisterView(generics.CreateAPIView):
    serializer_class = PassengerRegisterSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print(f"Validation errors: {serializer.errors}")
            return Response(serializer.errors, status=400)
        
        user = serializer.save()
        PassengerProfile.objects.get_or_create(user=user)
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "user_id": user.id,
            "phone_number": user.phone_number,
            "role": "passenger",
            "token": token.key
        }, status=201)




class DriverRegisterView(generics.CreateAPIView):
    serializer_class = DriverRegisterSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print(f"Validation errors: {serializer.errors}")
            return Response(serializer.errors, status=400)

        user = serializer.save()
        DriverProfile.objects.get_or_create(user=user)
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "user_id": user.id,
            "phone_number": user.phone_number,
            "role": "driver",
            "token": token.key
        }, status=201)



class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        user = serializer.validated_data
        token, _ = Token.objects.get_or_create(user=user)
        
        # Determine user role
        role = "passenger"  # Default
        if hasattr(user, 'driverprofile'):
            role = "driver"
        
        return Response({
            "user_id": user.id,
            "phone_number": user.phone_number,
            "role": role,
            "token": token.key
        }, status=200)
