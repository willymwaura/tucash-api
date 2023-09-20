from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from .serializers import CustomUserSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserLoginSerializer
from django.contrib.auth import authenticate
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from main.models import Balance
from authapp.models import CustomUser

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    print("creating a user")
    print(request.data)
    serializer = CustomUserSerializer(data=request.data)
    if serializer.is_valid():
        user=serializer.save()
        Balance.objects.create(user_id=user.id, amount=0)
        response_data = {
            "message": "User created successfully",
            "user": serializer.data  # You can include user data in the response if needed
        }
        return Response(response_data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.permissions import AllowAny

class UserLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            print(email)
            password = serializer.validated_data['password']
            #hashed_password = make_password(password)
            #print(hashed_password)
            user = authenticate(request, email=email, password=password)
            print(user)
            
            if user is not None:
                refresh = RefreshToken.for_user(user)
                print("authenticated")
                print("authenticated")
                print(str(refresh.access_token))
                print(str(refresh))
                user_id = user.id
                tel_number=user.phone_number
                
                return Response({
                    'id':user_id,
                    "PhoneNumber":tel_number,
                    'access_token': str(refresh.access_token),
                   'refresh_token': str(refresh),
                   'message':"user logged in successful"
                })
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def reset_password(request):
    user_id = request.data.get('user_id')
    new_password = request.data.get('new_password')

    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    # Hash the new password
    hashed_password = make_password(new_password)
    user.password = hashed_password
    user.save()

    return Response({"message": "Password reset successfully"}, status=status.HTTP_200_OK)
