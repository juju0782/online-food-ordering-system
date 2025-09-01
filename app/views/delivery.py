from flask import Blueprint, request, jsonify
import math

delivery = Blueprint('delivery', __name__)

from flask import Blueprint, request, jsonify
import math

delivery = Blueprint('delivery', __name__)

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

@delivery.route('/calculate-delivery', methods=['GET', 'POST'])
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



