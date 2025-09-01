from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app import db


class Supplier(db.Model):
    __tablename__ = 'supplier'
    supplier_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=db.func.now())

    inventory_items = db.relationship('Inventory', backref='supplier', lazy=True)
    commodities = db.relationship('Commodity', backref='supplier', lazy=True)

class Inventory(db.Model):
    __tablename__ = 'inventory'

    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_name = db.Column(db.String(100), nullable=False)
    stock_quantity = db.Column(db.Integer, default=0, nullable=True)
    reorder_level = db.Column(db.Integer, nullable=False, default=10)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.supplier_id'))

    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.supplier_id'), nullable=True)

    def __repr__(self):
        return f"<Inventory {self.product_name} - Qty: {self.quantity}>"