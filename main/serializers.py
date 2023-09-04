
from rest_framework import serializers
from . models import Mpesa

class Mpesaserializer(serializers.ModelSerializer):
    class Meta:
        model=Mpesa
        fields='__all__'


from .models import Balance

class BalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Balance
        fields = ['user_id', 'amount']


class TransactionSerializer(serializers.Serializer):
    sender_id = serializers.IntegerField()
    receiver_phone_number = serializers.CharField()
    amount = serializers.FloatField()


