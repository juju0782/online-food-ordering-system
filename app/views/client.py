from flask import Blueprint, jsonify, render_template, request
from app import db
from app.models.client import Client


client = Blueprint('clients', __name__)

@client.route('/client/<int:user_id>', methods=['GET'])
def get_client(user_id):
    client = Client.query.get(user_id)
    if client:
        return jsonify(client.to_dict())
    return jsonify({"error": "Client not found"}), 404

@client.route('/add_client', methods=['GET', 'POST'])
def add_client():
    if request.method == 'POST':
        pass
    return render_template('add_client.html')  
