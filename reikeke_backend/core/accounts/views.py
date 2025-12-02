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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

  
        PassengerProfile.objects.get_or_create(user=user)

     
        token, _ = Token.objects.get_or_create(user=user)

        # Return response
        return Response({
            "user_id": user.id,
            "phone_number": user.phone_number,
            "token": token.key
        })




class DriverRegisterView(generics.CreateAPIView):
    serializer_class = DriverRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

  
        user = serializer.save()

        DriverProfile.objects.get_or_create(user=user)

        token, _ = Token.objects.get_or_create(user=user)

  
        return Response({
            "user_id": user.id,
            "phone_number": user.phone_number,
            "token": token.key
        })



class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        
        user = serializer.validated_data

        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "user_id": user.id,
            "phone_number": user.phone_number,
            "token": token.key
        })
