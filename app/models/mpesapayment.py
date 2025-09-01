from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app import db


class mpesapayment(db.Model):
    __tablename__ = 'mpesapayment'

    id = db.Column(db.Integer, primary_key=True)
    merchant_request_id = db.Column(db.String(100))
    checkout_request_id = db.Column(db.String(100))
    result_code = db.Column(db.Integer)
    result_desc = db.Column(db.String(255))
    amount = db.Column(db.Float)
    mpesa_receipt_number = db.Column(db.String(50))
    phone_number = db.Column(db.String(15))
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)