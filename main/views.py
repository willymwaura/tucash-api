
from django.shortcuts import redirect, render
from django.http import HttpResponse, response
from rest_framework import serializers,status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist 
from django.urls import reverse
from datetime import datetime, timedelta
import time 

import threading

from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view, permission_classes
import requests
from django.core.cache import cache

from main.models import TillTranscations,Balance,MpesaDeposits,PaybillTranscations,TucashTransactions
from authapp.models import CustomUser
from main.serializers import Mpesaserializer,BalanceSerializer,TransactionSerializer,TillSerializer,PaybillSerializer

from requests.auth import HTTPBasicAuth
import json
from django.shortcuts import get_object_or_404



class Homepage(APIView):
    def get(self, request):
        return HttpResponse("This is the homepage")
    
    
    

class TokenManager:
    def __init__(self):
        self.access_token = None
        self.token_expiration_time = datetime.now() - timedelta(days=1)  # Set an initial value in the past
        self.consumer_key = 'tD4pH6DJPxegfGAIBx2dQhh7t6Aig7kj'
        self.consumer_secret = 'ap7qAoVZ5hIL4ocx'
        self.api_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
        self.lock = threading.Lock()
        
        # Start a thread to automatically renew the token before it expires
        renewal_thread = threading.Thread(target=self.auto_renew_token)
        renewal_thread.daemon = True
        renewal_thread.start()

    def get_access_token(self):
        with self.lock:
            if self.access_token is None or datetime.now() >= self.token_expiration_time:
                self.fetch_new_token()
            return self.access_token

    def fetch_new_token(self):
        r = requests.get(self.api_url, auth=HTTPBasicAuth(self.consumer_key, self.consumer_secret))
        mpesa_access_token = json.loads(r.text)
        self.access_token = mpesa_access_token.get('access_token')
        expires_in = mpesa_access_token.get('expires_in')

        if self.access_token and expires_in:
            # Convert expires_in to an integer before adding it to the current time
            expires_in = int(expires_in)
            # Ensure the expiration time is never in the past
            new_expiration_time = datetime.now() + timedelta(seconds=expires_in)
            if new_expiration_time > self.token_expiration_time:
                self.token_expiration_time = new_expiration_time
                # Store the renewed token in the cache
                cache.set('access_token', self.access_token, timeout=expires_in)

    def auto_renew_token(self):
        while True:
            # Sleep for a period slightly shorter than the token expiration time
            sleep_duration = (self.token_expiration_time - datetime.now() - timedelta(seconds=10)).total_seconds()
            if sleep_duration > 0:
                time.sleep(sleep_duration)
            
            # Renew the token and update the cache
            self.fetch_new_token()

class GetToken(APIView):
    token_manager = TokenManager()

    def get(self, request):
        access_token = self.token_manager.get_access_token()
        return HttpResponse(access_token)
from  main.mpesa_credentials import LipanaMpesaPpassword 
class lipanampesa(APIView):
    
    def post(self,request):
        #from  main.mpesa_credentials import LipanaMpesaPpassword , MpesaAccessToken 
        
        print("starting the stkpush")
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
        access_token = cache.get('access_token')
        print("the token is ",access_token)
        #access_token = MpesaAccessToken.validated_mpesa_access_token
        

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



class MpesaCallback(APIView):
    def post(self,request):
        data = json.loads(request.body.decode('utf-8'))
        print("call back running")
        print(data)

        # Extract transaction data from JSON payload
        #transaction_id = data['TransactionID']
        callback_data = data.get('Body', {}).get('stkCallback', {})
        status = int(callback_data.get('ResultCode'))
        #account_reference = data['BillRefNumber']
        print(f"ResultCode: {status}")
        

        # Check if transaction status is successful
        if status == 0:
            amount = float(callback_data.get('CallbackMetadata', {}).get('Item', [])[0].get('Value'))
            phone_number = callback_data.get('CallbackMetadata', {}).get('Item', [])[4].get('Value')
            print(amount)
            print(phone_number)
            try:
                # Find the user in the CustomUser model with the same phone number
                user = CustomUser.objects.get(phone_number=str(phone_number))
                

                # Update the balance model instance with the user's ID
                try:
                    balance_entry = Balance.objects.get(user_id=user.id)
                    balance_entry.amount += amount
                    balance_entry.save()
                    transaction=MpesaDeposits(Amount=amount,PhoneNumber=phone_number,status=True)
                    transaction.save()
                except ObjectDoesNotExist:
                    # You may want to create a new balance entry for the user if it doesn't exist
                    pass

                # Transaction saved
                return JsonResponse({'message': 'Transaction saved'}, status=200)

            except CustomUser.DoesNotExist:
                # User not found, you may want to handle this case accordingly
                return JsonResponse({'error': 'User not found'}, status=404)

        
        #return JsonResponse({'message': 'Transaction received'}, status=200)
        if status == 1030:
            amount = float(callback_data.get('CallbackMetadata', {}).get('Item', [])[0].get('Value'))
            phone_number = callback_data.get('CallbackMetadata', {}).get('Item', [])[3].get('Value')
            print("status 1013")
            print(amount)
            print(phone_number)
            transaction=MpesaDeposits(Amount=amount,PhoneNumber=phone_number)
            transaction.save()
            #logic to save the transaction
            return JsonResponse({'message':'stk response but not successful deposit'})
        else:
            return JsonResponse({'message':'stk response but not successful deposit'})

            

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
                    TucashTransactions.objects.create(sender=sender_id, receiver=receiver_phone_number, amount=amount)

                    return Response({'message': 'Transaction successful'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)
            except (Balance.DoesNotExist, TucashTransactions.DoesNotExist):
                return Response({'error': 'Sender or receiver not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

from  main.mpesa_credentials import LipanaMpesaPpassword
class paybill_transactions(APIView):
    
    def post(self, request):
        #from  main.mpesa_credentials import LipanaMpesaPpassword , MpesaAccessToken
        
        print("lipa to paybill starting")
        print(request.data)
        serializer = PaybillSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            print("saved")
        else:
            print("Validation Errors:", serializer.errors)

        paybill = request.data["paybill"]
        Amount = int(request.data["amount"])
        print("amount is ", Amount)
        account_number = request.data["account_number"]
        access_token = cache.get('access_token')
        #access_token = "8CMMHLGyFfqrj2KD0VtpyI7dBF73"
        print("the token is ", access_token)
        user_id = request.data["user_id"]

        #access_token = MpesaAccessToken.validated_mpesa_access_token
        sender_balance_obj = Balance.objects.get(user_id=user_id)
        sender_balance = int(sender_balance_obj.amount)  # Assuming 'balance' is the field with the float value
        print("sender balance is", sender_balance)

        try:
            print("try starting")
            if sender_balance >=Amount:
                print("fetching balance")
                sender_balance -= Amount
                sender_balance = float(sender_balance)
                sender_balance_obj.amount=sender_balance
                sender_balance_obj.save()

                api_url = "https://sandbox.safaricom.co.ke/mpesa/b2b/v1/paymentrequest"
                headers = {"Authorization": "Bearer %s" % access_token}
                request_data = { 
                    "Initiator": "API_Username",
                    "SecurityCredential": LipanaMpesaPpassword.decode_password,
                    "CommandID": "BusinessPayBill",
                    "SenderIdentifierType": "4",
                    "RecieverIdentifierType": "4",
                    "Amount": Amount,
                    "PartyA": LipanaMpesaPpassword.Business_short_code,
                    "PartyB": paybill,  # the paybill where money is being sent 
                    "AccountReference": account_number,
                    "Requester": "254700000000",  # the mobile number used to register the paybill
                    "Remarks": "OK",
                    "QueueTimeOutURL": "https://tucash-api-production.up.railway.app/callback/",
                    "ResultURL": "https://tucash-api-production.up.railway.app/paybill_callback/",
                }
                print("sending request")

                response = requests.post(api_url, json=request_data, headers=headers)
                print(response.text)
                if response.status_code == 200:
                    response_json = response.json()
                    originator_conversation_id = response_json.get('OriginatorConversationID')
                    print("the originator is is ",originator_conversation_id)

                            # Check if OriginatorConversationID is present in the response
                    if originator_conversation_id and originator_conversation_id !=111:
                        paybill_transaction = PaybillTranscations(
                                paybill=paybill,
                                amount=Amount,
                                OriginatorConversationID=originator_conversation_id,
                                account_number=account_number,
                                user_id=user_id
                                )
                        paybill_transaction.save()
                        return Response(response.json())
                    else:
                            # Handle JSON parsing error if the response is not valid JSON
                                print("Error: Response is not valid JSON.")
                                return Response({'message': ' Response is not valid JSON'}, status=status.HTTP_400_BAD_REQUEST)

                   
            else:
                return Response({'message': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)

        except:
            return Response({'message': 'error occurred'}, status=status.HTTP_400_BAD_REQUEST)

class till_transactions(APIView):
    
    def post(self,request):
        #from  main.mpesa_credentials import LipanaMpesaPpassword , MpesaAccessToken 
        
        print("starting paybill to till transaction")
        
        print(request.data)
        serializer=TillSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            print("saved")
        else:
            print("Validation Errors:", serializer.errors)
        
        
        till=request.data["till_number"]
        amount=request.data["amount"]
        user_id=request.data["user_id"]
        
        
        #access_token = MpesaAccessToken.validated_mpesa_access_token
        access_token = cache.get('access_token')
        print("the token is ",access_token)
        sender_balance = Balance.objects.get(user_id=user_id)
        try:
            if sender_balance.amount >= amount:
                    # Deduct the amount from the sender's balance
                    sender_balance.amount -= amount
                    sender_balance.save()
        

            api_url = "https://sandbox.safaricom.co.ke/mpesa/b2b/v1/paymentrequest"
            headers = {"Authorization": "Bearer %s" % access_token}
            request = {
                "InitiatorName": "API_Username",
                "SecurityCredential": LipanaMpesaPpassword.decode_password,
                "CommandID": "BusinessPayment",
                "Amount": amount,  # Change this to the desired amount for the transaction
                "PartyA": LipanaMpesaPpassword.Business_short_code,
                "PartyB": till,  # Change this to the Till number where money is being sent
                "Remarks": "Payment to Till",
                "QueueTimeOutURL": "https://tucash-api-production.up.railway.app/callback/",
                "ResultURL": "https://tucash-api-production.up.railway.app/paybill_callback/",
                "Occasion": "Payment"
            }
            
            response = requests.post(api_url, json=request, headers=headers)
            if response.headers.get('content-type') == 'application/json':
                try:
                    response_json = response.json()
                    originator_conversation_id = response_json.get('OriginatorConversationID')
                    
                    # Check if OriginatorConversationID is present in the response
                    if originator_conversation_id:
                        till_transaction=PaybillTranscations(till=till,amount=amount,OriginatorConversationID=originator_conversation_id,user_id=user_id)
                        till_transaction.save()
                except ValueError:
                    # Handle JSON parsing error if the response is not valid JSON
                    print("Error: Response is not valid JSON.")
            return HttpResponse(response)
        except:
            return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)
        
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

#@csrf_exempt  # Disable CSRF protection for this view if necessary
@method_decorator(csrf_exempt, name='dispatch')
class PaybillCallbackView(APIView):

    def post(self, request):
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body.decode('utf-8'))
            print(data)

            # Extract relevant information from the JSON data
            result_code = data["Result"]["ResultCode"]
            transaction_amount = data["TransactionAmount"]
            OriginatorConversationID = data["OriginatorConversationID"]

            # Save the extracted information to your database or perform other actions
            if result_code== 0:
                paybill_transaction=PaybillTranscations.objects.filter(OriginatorConversationID=OriginatorConversationID)
                paybill_transaction=paybill_transaction(status=True)
                paybill_transaction.save()
            # For example, you can use Django models to save data to your database.

            # Respond to the callback with a success message
                response_data = {"message": "Callback received and data saved successfully"}
                return JsonResponse(response_data, status=200)
            else:
                response_data = {"message": "Callback received and but the transaction was not  successfu"}
                return JsonResponse(response_data, status=200)

        except Exception as e:
            # Handle any exceptions that may occur during processing
            error_response = {"error": str(e)}
            return JsonResponse(error_response, status=500)
        
class TillCallbackView(APIView):

    def post(self, request):
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body.decode('utf-8'))

            # Extract relevant information from the JSON data
            result_code = data["Result"]["ResultCode"]
            transaction_amount = data["TransactionAmount"]
            OriginatorConversationID = data["OriginatorConversationID"]

            # Save the extracted information to your database or perform other actions
            # For example, you can use Django models to save data to your database.

            # Respond to the callback with a success message
            if result_code== 0:
                till_transaction=TillTranscations.objects.filter(OriginatorConversationID=OriginatorConversationID)
                till_transaction=till_transaction(status=True)
                till_transaction.save()
            # For example, you can use Django models to save data to your database.

            # Respond to the callback with a success message
                response_data = {"message": "Callback for till received and data saved successfully"}
                return JsonResponse(response_data, status=200)
            else:
                response_data = {"message": "Callback for till received and but the transaction was not  successfu"}
                return JsonResponse(response_data, status=200)
        except Exception as e:
            # Handle any exceptions that may occur during processing
            error_response = {"error": str(e)}
            return JsonResponse(error_response, status=500)




