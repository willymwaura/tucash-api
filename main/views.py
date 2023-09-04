
from django.shortcuts import redirect, render
from django.http import HttpResponse, response
from rest_framework import serializers,status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt

from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view, permission_classes
import requests

from main.models import Mpesa
from main.serializers import Mpesaserializer
from  main.mpesa_credentials import LipanaMpesaPpassword , MpesaAccessToken 
from requests.auth import HTTPBasicAuth
import json

@api_view(['GET'])
#@permission_classes([IsAuthenticated])


def homepage(request):
    return HttpResponse(" this is the homepage")

class gettoken(APIView):
    def post(self,request):
        consumer_key = 'bdABIHJcBQA5ki4tRYQumvcLA8QaaDP3'
        consumer_secret = 'QooVaV2gUsBcKziE'
        api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
        r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
        mpesa_access_token = json.loads(r.text)
        validated_mpesa_access_token = mpesa_access_token['access_token']
        return HttpResponse(validated_mpesa_access_token)
    
class lipanampesa(APIView):
    def post(self,request):
        

        serializer=Mpesaserializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        
        
        phone=Mpesa.objects.last().PhoneNumber
        Amount=Mpesa.objects.last().Amount
        Amount=Amount
        print(phone)
        access_token = MpesaAccessToken.validated_mpesa_access_token
        

        api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {"Authorization": "Bearer %s" % access_token}
        request = {
            "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
            "Password": LipanaMpesaPpassword.decode_password,
            "Timestamp": LipanaMpesaPpassword.lipa_time,
            "TransactionType": "CustomerPayBillOnline",
            "Amount":Amount,
            "PartyA":phone,
            "PartyB": LipanaMpesaPpassword.Business_short_code,
            "PhoneNumber":phone,
            "CallBackURL": "https://sandbox.safaricom.co.ke/mpesa/",
            "AccountReference": "Art gallery software company",
            "TransactionDesc": "Testing stk push"
        }
        response = requests.post(api_url, json=request, headers=headers)
        return HttpResponse(response)

@csrf_exempt
def mpesa_callback(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))

        # Extract transaction data from JSON payload
        print("transaction processing")
        transaction_id = data['TransactionID']
        print(transaction_id)
        amount = int(data['TransAmount'])
        print(amount)
        phone_number = int(data['MSISDN'])
        print(phone_number)
        status = int(data['ResultCode'])
        print(status)
        account_reference = data['BillRefNumber']
        print(account_reference)

        # Check if transaction status is successful
        if status == 0:
            print("checking if status is 0")
            # Store transaction data in database
            '''
            payment = Payments.objects.create(
                transaction_id=transaction_id,
                amount=amount,
                phone_number=phone_number,
                status=status,
                account_number=account_reference
            )
            payment.save()'''
            print("saved")

        return HttpResponse(status=200)
    else:
        return HttpResponse(status=400)

