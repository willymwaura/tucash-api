from django.urls import  path ,include

from .views import UserLoginAPIView 
from . import views



urlpatterns = [
    path('register/', views.register_user, name='register_user'),
    path('login/', UserLoginAPIView.as_view(), name='user-login'),
    # Add other API endpoints here if needed
]