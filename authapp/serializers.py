
from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth.hashers import make_password

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'
# serializers.py
    def create(self, validated_data):
        # Hash the plain-text password before saving it
        password = validated_data['password']
        hashed_password = make_password(password)
        validated_data['password'] = hashed_password

        # Create and return the user
        user = CustomUser.objects.create(**validated_data)
        return user 



class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
