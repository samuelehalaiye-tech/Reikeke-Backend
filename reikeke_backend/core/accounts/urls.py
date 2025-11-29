from django.urls import path
from .views import PassengerRegisterView, DriverRegisterView, LoginView

urlpatterns = [
    path('register/passenger/', PassengerRegisterView.as_view(), name='passenger-register'),
    path('register/driver/', DriverRegisterView.as_view(), name='driver-register'),
    path('login/', LoginView.as_view(), name='login'),
]
