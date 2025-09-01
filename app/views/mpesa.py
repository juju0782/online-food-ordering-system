import requests
import datetime
import base64
from requests.auth import HTTPBasicAuth

def stk_push(phone, amount):
    # GENERATING THE ACCESS TOKEN
    # create an account on safaricom daraja, here you are provided with below Credentials (Consumer Key and Secret Key)
    # For testing Purposes we use MODCOM Credentials
    consumer_key = "GTWADFxIpUfDoNikNGqq1C3023evM6UH"
    consumer_secret = "amFbAoUByPV2rM5A"

    # Pass Consumer and Secret Key to Mpesa URL
    api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials" # AUTH URL
    data = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret)).json()

    # We get access token from data above - To be used Later
    access_token = data['access_token']

    # GETTING THE PASSWORD
    timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
    passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
    business_short_code = "174379"
    # Combine the above 3 variables into single variable called "dats"
    data = business_short_code + passkey + timestamp
    # We encode data into base64(ASCII)
    encoded = base64.b64encode(data.encode())
    # Decode with utf-8
    password = encoded.decode('utf-8')
    print(password)

    payload = {
    "BusinessShortCode": "174379",
    "Password": "{}".format(password),
    "Timestamp": "{}".format(timestamp),
    "TransactionType": "CustomerPayBillOnline",
    "Amount": amount, 
    "PartyA": phone, 
    "PartyB": "174379",
    "PhoneNumber": phone,
    "CallBackURL": "https://your-ngrok-url.ngrok.io/mpesa/callback",
    "AccountReference": "account",
    "TransactionDesc": "account"
    }

    
    headers = {
    "Authorization": "Bearer " + access_token,
    "Content-Type": "application/json"
    }
    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest" 

    response = requests.post(url, json=payload, headers=headers)
    print(response.text)