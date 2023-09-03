from django.urls import  path ,include

from .views import UserLoginAPIView 
from . import views
from rest_framework_simplejwt.views import TokenRefreshView



urlpatterns = [
    path('register/', views.register_user, name='register_user'),
    path('login/', UserLoginAPIView.as_view(), name='user-login'),
   
   
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_verify'),
    # Add other API endpoints here if needed
]