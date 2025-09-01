from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app import db


class Commodity(db.Model):
    __tablename__ = 'commodities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.String(50))  
    unit = db.Column(db.String(50))      
    price = db.Column(db.Float, nullable=True)

    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.supplier_id'), nullable=False)

    created_at = db.Column(db.DateTime, default=db.func.now())
