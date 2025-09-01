from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app import db


class Product(db.Model):
    __tablename__ = 'products'

    product_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    product_category = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=True)
    product_image_path = db.Column(db.String(255), nullable=True)

    sku = db.Column(db.String(50), unique=True, nullable=True)  
    stock_quantity = db.Column(db.Integer, default=0, nullable=True)  
    is_active = db.Column(db.Boolean, default=True)  

    created_at = db.Column(db.DateTime, default=datetime.utcnow)  
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)  
    
    brand = db.Column(db.String(100), nullable=True)  
    tags = db.Column(db.Text, nullable=True)  
    discount_price = db.Column(db.Float, nullable=True)  
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.supplier_id'), nullable=True)


    def __repr__(self):
        return f'<Product {self.product_name}>'