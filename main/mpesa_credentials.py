
import requests
import json
from requests.auth import HTTPBasicAuth
from datetime import datetime
import base64
'''

class MpesaC2bCredential:
    consumer_key = 'tD4pH6DJPxegfGAIBx2dQhh7t6Aig7kj'
    consumer_secret = 'ap7qAoVZ5hIL4ocx'
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
class MpesaAccessToken:
    r = requests.get(MpesaC2bCredential.api_URL,auth=HTTPBasicAuth(MpesaC2bCredential.consumer_key, MpesaC2bCredential.consumer_secret))
    mpesa_access_token = json.loads(r.text)
    print(mpesa_access_token)
    validated_mpesa_access_token = mpesa_access_token['access_token']'''

from dotenv import load_dotenv


# Load the environment variables from the .env file
load_dotenv()
import os

class LipanaMpesaPpassword:
    lipa_time = datetime.now().strftime('%Y%m%d%H%M%S')
    Business_short_code = os.getenv('Business_short_code')
    passkey = os.getenv('passkey')
    data_to_encode = Business_short_code + passkey + lipa_time
    online_password = base64.b64encode(data_to_encode.encode())
    decode_password = online_password.decode('utf-8')