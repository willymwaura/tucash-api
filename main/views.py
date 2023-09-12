
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

from main.models import Mpesa,Balance,Transactions
from authapp.models import CustomUser
from main.serializers import Mpesaserializer,BalanceSerializer,TransactionSerializer

from requests.auth import HTTPBasicAuth
import json
from django.shortcuts import get_object_or_404



class Homepage(APIView):
    def get(self, request):
        return HttpResponse("This is the homepage")
    
    
    



class gettoken(APIView):
    def post(self,request):
        consumer_key = 'bdABIHJcBQA5ki4tRYQumvcLA8QaaDP3'
        consumer_secret = 'QooVaV2gUsBcKziE'
        api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
        r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
        mpesa_access_token = json.loads(r.text)
        validated_mpesa_access_token = mpesa_access_token['access_token']
        return HttpResponse(validated_mpesa_access_token)
from  main.mpesa_credentials import LipanaMpesaPpassword , MpesaAccessToken 
class lipanampesa(APIView):
    
    def post(self,request):
        #from  main.mpesa_credentials import LipanaMpesaPpassword , MpesaAccessToken 
        
        print("starting")
        print(request.data)
        serializer=Mpesaserializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            print("saved")
        else:
            print("Validation Errors:", serializer.errors)
        
        
        phone=request.data["PhoneNumber"]
        Amount=request.data["Amount"]
        
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
            "CallBackURL": "https://tucash-api-production.up.railway.app/callback/",
            "AccountReference": "Tucash ",
            "TransactionDesc": "Testing stk push"
        }
        response = requests.post(api_url, json=request, headers=headers)
        return HttpResponse(response)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.exceptions import ObjectDoesNotExist  # Import ObjectDoesNotExist

class MpesaCallback(APIView):
    def post(self,request):
        data = json.loads(request.body.decode('utf-8'))
        print("call back running")
        print(data)

        # Extract transaction data from JSON payload
        #transaction_id = data['TransactionID']
        callback_data = data.get('Body', {}).get('stkCallback', {})
        amount = int(callback_data.get('CallbackMetadata', {}).get('Item', [])[0].get('Value'))
        phone_number = callback_data.get('CallbackMetadata', {}).get('Item', [])[4].get('Value')# Treat as a string, not an integer
        status = int(callback_data.get('ResultCode'))
        #account_reference = data['BillRefNumber']
        print(f"ResultCode: {status}")
        print(f"Amount: {amount}")
        print(f"PhoneNumber: {phone_number}")

        # Check if transaction status is successful
        if status == 0:
            try:
                # Find the user in the CustomUser model with the same phone number
                user = CustomUser.objects.get(phone_number=str(phone_number))

                # Update the balance model instance with the user's ID
                try:
                    balance_entry = Balance.objects.get(user_id=user.id)
                    balance_entry.amount += amount
                    balance_entry.save()
                except ObjectDoesNotExist:
                    # You may want to create a new balance entry for the user if it doesn't exist
                    pass

                # Transaction saved
                return JsonResponse({'message': 'Transaction saved'}, status=200)

            except CustomUser.DoesNotExist:
                # User not found, you may want to handle this case accordingly
                return JsonResponse({'error': 'User not found'}, status=404)

        return JsonResponse({'message': 'Transaction received'}, status=200)  # Respond with 200 even if status is not 0

    def get(self, request):
        return JsonResponse({'error': 'Method not allowed'}, status=405)  # Handle GET requests with a 405 response

class GetBalanceAPIView(APIView):
    def get(self, request, user_id):
        print(" the id passed is ",user_id)
        try:
            balance_entry = Balance.objects.get(user_id=user_id)
            serializer = BalanceSerializer(balance_entry)
            return Response(serializer.data)
        except Balance.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
class UpdateBalanceAPIView(APIView):
    def post(self, request):
        serializer = TransactionSerializer(data=request.data)

        if serializer.is_valid():
            sender_id = serializer.validated_data['sender_id']
            receiver_phone_number = serializer.validated_data['receiver_phone_number']
            amount = serializer.validated_data['amount']

            try:
                # Get the sender's balance
                
                sender_balance = Balance.objects.get(user_id=sender_id)

                # Check if the sender has sufficient balance
                if sender_balance.amount >= amount:
                    # Deduct the amount from the sender's balance
                    sender_balance.amount -= amount
                    sender_balance.save()

                    # Find the receiver by phone number
                    receiver = CustomUser.objects.get(phone_number=receiver_phone_number)
                    receiver = Balance.objects.get(user_id=receiver.id)

                    # Update the receiver's balance by adding the amount
                    receiver.amount += amount
                    receiver.save()

                    # Create a transaction record
                    Transactions.objects.create(sender=sender_id, receiver=receiver_phone_number, amount=amount)

                    return Response({'message': 'Transaction successful'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)
            except (Balance.DoesNotExist, Transactions.DoesNotExist):
                return Response({'error': 'Sender or receiver not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






