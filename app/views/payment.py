'''
from flask import Blueprint, request, redirect, flash, url_for, jsonify
from app.views.mpesa import stk_push
from models import db, MpesaPayment
import json


payment = Blueprint('payment', __name__)

@payment.route('/pay', methods=['POST'])
def pay():
    phone = request.form['phone']
    amount = request.form['amount']

    response = stk_push(phone, amount)
    
    if response.get("ResponseCode") == "0":
        flash("Payment request sent to your phone.", "success")
    else:
        flash("Failed to initiate payment. Try again.", "danger")
    
    return redirect(url_for('cart.view_cart'))

@payment.route('/mpesa/callback', methods=['POST'])
def mpesa_callback():
    data = request.get_json()

    try:
        body = data['Body']['stkCallback']
        merchant_id = body['MerchantRequestID']
        checkout_id = body['CheckoutRequestID']
        result_code = body['ResultCode']
        result_desc = body['ResultDesc']

        amount = None
        receipt = None
        phone = None

        if result_code == 0:
            metadata = body['CallbackMetadata']['Item']
            for item in metadata:
                if item['Name'] == 'Amount':
                    amount = item['Value']
                elif item['Name'] == 'MpesaReceiptNumber':
                    receipt = item['Value']
                elif item['Name'] == 'PhoneNumber':
                    phone = item['Value']

        # Save to DB
        payment = MpesaPayment(
            merchant_request_id=merchant_id,
            checkout_request_id=checkout_id,
            result_code=result_code,
            result_desc=result_desc,
            amount=amount,
            mpesa_receipt_number=receipt,
            phone_number=phone
        )
        db.session.add(payment)
        db.session.commit()

        return jsonify({"ResultCode": 0, "ResultDesc": "Accepted"})

    except Exception as e:
        print("Callback parse error:", str(e))
        return jsonify({"ResultCode": 1, "ResultDesc": "Callback processing failed"})
'''

from flask import Blueprint, request, redirect, url_for, flash, render_template
from flask_login import login_required
from app.models.mpesapayment import mpesapayment
from app import db
import datetime

payment = Blueprint('payment', __name__)


@payment.route('/simulate-payment', methods=['GET', 'POST'])
def simulate_payment():
    if request.method == 'POST':
        phone = request.form.get('phone')
        amount = request.form.get('amount')

        payment = mpesapayment(
            phone_number=phone,
            amount=amount,
            mpesa_receipt_number="0769805233",
            result_code=0,
            result_desc="Success",
            merchant_request_id="SIM123",
            checkout_request_id="SIM456",
            transaction_date=datetime.datetime.now()
        )
        db.session.add(payment)
        db.session.commit()

        return redirect(url_for("cart.shopping_cart"))

    return render_template("payment/simulate_payment.html")
