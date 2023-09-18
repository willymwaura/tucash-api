
from rest_framework import serializers
from . models import Mpesa
from .models import Balance

class Mpesaserializer(serializers.ModelSerializer):
    class Meta:
        model=Mpesa
        fields=['Amount','PhoneNumber']




class BalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Balance
        fields = ['user_id', 'amount']


class TransactionSerializer(serializers.Serializer):
    sender_id = serializers.IntegerField()
    receiver_phone_number = serializers.CharField()
    amount = serializers.FloatField()


