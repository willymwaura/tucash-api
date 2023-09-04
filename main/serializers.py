
from rest_framework import serializers
from . models import Mpesa

class Mpesaserializer(serializers.ModelSerializer):
    class Meta:
        model=Mpesa
        fields='__all__'


