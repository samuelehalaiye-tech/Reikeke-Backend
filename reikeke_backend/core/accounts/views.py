from django.shortcuts import render
from rest_framework import generics, permissions
from serializers import(PassengerRegisterSerializer, DriverRegisterSerializer,LoginSerializer,UserSerializer)
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
# Create your views here.


class PassengerRegisterView(generics.CreateAPIView):
    serializer_class= PassengerRegisterSerializer
    permission_classes=[permissions.AllowAny]




class LoginView(APIView):
    permission_classes=[permissions.AllowAny]
    def post(self, request):
        serializer= LoginSerializer(data=request.data)
        user= serializer.validated_data
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.id,
            'phone_number': user.phone_number
        })































































