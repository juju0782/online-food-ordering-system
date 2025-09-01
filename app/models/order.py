from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app import db
from app.models.products import Product
from sqlalchemy.orm import foreign


class Order(db.Model):
    __tablename__ = 'orders'
    __table_args__ = {'extend_existing': True}  

    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    customer_name = db.Column(db.String(100), nullable=True)
    contact_number = db.Column(db.String(15), nullable=False)
    shipping_address = db.Column(db.String(255), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    total_cost_price = db.Column(db.Float, nullable=False, default=0.0)  
    profit = db.Column(db.Float, nullable=False, default=0.0) 
    order_date = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.String(20), default="Pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)



    items = db.relationship("OrderItem", backref="order", lazy=True)

    def calculate_profit(self):
        self.total_cost_price = sum(item.cost_price * item.quantity for item in self.items)
        self.profit = self.total_price - self.total_cost_price



    def __repr__(self):
        return f"<Order {self.order_id} - {self.contact_number}>"


class OrderItem(db.Model):
    __tablename__ = "order_items"

    order_item_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.order_id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.product_id"), nullable=False)
    product_name = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship("Product", backref="order_items")

    def __repr__(self):
        return f"<OrderItem {self.product_name} (x{self.quantity})>"
