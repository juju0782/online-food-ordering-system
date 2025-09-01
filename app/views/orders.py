from flask import Blueprint, request, jsonify
from app import db

orders = Blueprint('orders', __name__)
'''
@orders.route('/create-order', methods=['POST'])
def create_order():
    data = request.json
    total_price = data.get("total_price")
    total_cost = data.get("total_cost")

    new_order = Order(
        customer_name=data.get("customer_name"),
        total_price=total_price,
        total_cost=total_cost
    )
    new_order.calculate_profit()

    db.session.add(new_order)
    db.session.commit()

    return jsonify({"message": "Order recorded", "profit": new_order.profit}), 201
'''