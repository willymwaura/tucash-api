
from rest_framework import serializers
from . models import MpesaDeposits
from .models import Balance,PaybillTranscations,TillTranscations

class Mpesaserializer(serializers.ModelSerializer):
    class Meta:
        model=MpesaDeposits
        fields=['Amount','PhoneNumber']




class BalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Balance
        fields = ['user_id', 'amount']


class TransactionSerializer(serializers.Serializer):
    sender_id = serializers.IntegerField()
    receiver_phone_number = serializers.CharField()
    amount = serializers.FloatField()

class PaybillSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaybillTranscations
        fields = ['paybill', 'account_number','amount','user_id']
class TillSerializer(serializers.ModelSerializer):
    class Meta:
        model = TillTranscations
        fields = ['till_number', 'amount','user_id']


