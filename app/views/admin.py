from flask import Blueprint, render_template, request, jsonify
from sqlalchemy import func
from flask_login import login_required
from app.models import transactions, users, order
from app.models.products import Product
from app.models.mpesapayment import mpesapayment
from app.models.supplier import Supplier
from datetime import datetime, timedelta
from app import db
import math


admin = Blueprint("admin", __name__, url_prefix="/admin/")


def _calculate_profit_logic(start_date, end_date):
    daily_profits = {}
    current_date = start_date

    while current_date <= end_date:
        next_day = current_date + timedelta(days=1)

        revenue = db.session.query(func.sum(order.total_price)) \
            .filter(order.created_at >= current_date, order.created_at < next_day) \
            .scalar() or 0.0

        daily_profits[current_date.strftime("%Y-%m-%d")] = round(revenue, 2)

        current_date = next_day

    return daily_profits



@admin.route("admin-dashboard", methods=["GET"])
@login_required
def admin_dash():
    supplier = Supplier.query.first()
    return render_template("admin/admin_dashboard.html", supplier=supplier)

@admin.route('/transactions')
@login_required
def admin_transaction_history():
    user_id = request.args.get('user_id')

    if user_id:
        transaction_list = transactions.query.filter_by(user_id=user_id).all()
    else:
        transaction_list = transactions.query.all()

    clients = users.query.all()
    return render_template('admin_transactions.html', transactions=transaction_list, clients=clients)

@admin.route('/calculate-profit', methods=['GET', 'POST'])
def calculate_profit():
    if request.content_type != 'application/json':
        return jsonify({"error": "Content-Type must be application/json"}), 415

    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid or missing JSON"}), 400

    start_date = data.get('start_date')
    end_date = data.get('end_date')

    print(f"Received: start={start_date}, end={end_date}")


    total_profit = 5000
    profits = [
        {"date": start_date, "profit": 1000},
        {"date": end_date, "profit": 4000}
    ]

    return jsonify({"total_profit": total_profit, "profits": profits})



@admin.route("/update-product", methods=["POST"])
def update_product():
    if not request.is_json:
        return jsonify({"success": False, "message": "Content-Type must be application/json"}), 415

    data = request.get_json()

    try:
        product_id = data.get("product_id")
        new_price = data.get("price")
        new_quantity = data.get("quantity")

        if not all([product_id, new_price, new_quantity]):
            return jsonify({"success": False, "message": "Missing fields"}), 400

        product_obj = Product.query.get(product_id)
        if not product_obj:
            return jsonify({"success": False, "message": "Product not found"}), 404

        product_obj.update_stock(new_price=new_price, new_quantity=new_quantity)
        db.session.commit()

        return jsonify({"success": True, "message": "Product updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    

AVERAGE_SPEED_KMH = 40  
BASE_DELIVERY_FEE = 50 
PER_KM_FEE = 5       
FREE_DISTANCE = 10      

def calculate_delivery_time(distance_km):
    """Estimate delivery time in minutes based on distance and speed."""
    time_hours = distance_km / AVERAGE_SPEED_KMH
    time_minutes = time_hours * 60
    return round(time_minutes)

def calculate_delivery_fee(distance_km):
    """Calculate delivery fee based on distance."""
    if distance_km <= FREE_DISTANCE:
        return BASE_DELIVERY_FEE
    else:
        extra_distance = distance_km - FREE_DISTANCE
        extra_fee = extra_distance * PER_KM_FEE
        total_fee = BASE_DELIVERY_FEE + extra_fee
        return math.ceil(total_fee)

@admin.route('/calculate-delivery', methods=['GET', 'POST'])
def calculate_delivery():
    if request.method == 'GET':
        return jsonify({"message": "Please use POST with JSON data to calculate delivery."})

    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 415

    data = request.get_json()

    if not data or 'distance' not in data:
        return jsonify({"error": "Missing distance field"}), 400

    try:
        distance = float(data['distance'])
        if distance <= 0:
            return jsonify({"error": "Distance must be greater than 0"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid distance format"}), 400

    estimated_time = calculate_delivery_time(distance)
    delivery_fee = calculate_delivery_fee(distance)

    return jsonify({
        'distance_km': distance,
        'estimated_time_minutes': estimated_time,
        'estimated_delivery_fee': delivery_fee
    })

@admin.route("/admin/mpesa-payments")
@login_required  
def mpesa_payments_list():
    payments = mpesapayment.query.order_by(mpesapayment.transaction_date.desc()).all()
    return render_template("admin/mpesa_payments.html", payments=payments)