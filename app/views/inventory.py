from flask import Blueprint, render_template, request, flash, redirect, url_for
from datetime import datetime, timedelta
import mysql.connector

inventory = Blueprint('inventory', __name__)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="KADUDA56ras",
        database="tj_dinehive",
        port=3307
    )

@inventory.route("/inventory", methods=["GET", "POST"])
def inventory_dashboard():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    
    cur.execute("""
        SELECT i.*, s.name AS supplier_name
        FROM inventory i
        LEFT JOIN suppliers s ON i.supplier_id = s.supplier_id
    """)
    items = cur.fetchall()


    low_stock = [item for item in items if item['stock_quantity'] <= item['reorder_level']]

    cur.close()
    conn.close()
    return render_template("inventory_dashboard.html", items=items, low_stock=low_stock)

@inventory.route("/inventory/add", methods=["GET", "POST"])
def add_inventory():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":
        product_name = request.form["product_name"]
        stock_quantity = request.form["stock_quantity"]
        reorder_level = request.form["reorder_level"]
        supplier_id = request.form.get("supplier_id") or None

        cur.execute("""
            INSERT INTO inventory (product_name, stock_quantity, reorder_level, supplier_id)
            VALUES (%s, %s, %s, %s)
        """, (product_name, stock_quantity, reorder_level, supplier_id))
        conn.commit()
        flash("Inventory item added", "success")
        return redirect(url_for("inventory.inventory_dashboard"))

    cur.execute("SELECT supplier_id, name FROM suppliers")
    supplier = cur.fetchall()

    cur.close()
    conn.close()
    return render_template("inventory_add.html", supplier=supplier)



@inventory.route("/predict-stock")
def predict_stock():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT product_id, SUM(quantity) AS total_sold
        FROM order_items
        WHERE order_date >= NOW() - INTERVAL 30 DAY
        GROUP BY order_item_id
    """)
    data = cur.fetchall()

    predictions = []
    for item in data:
        predicted = int(item["total_sold"] / 30 * 7)  
        cur.execute("SELECT product_name, stock_quantity FROM inventory WHERE product_id = %s", (item["product_id"],))
        inventory_info = cur.fetchone()

        if inventory_info:
         predictions.append({
            "product_name": inventory_info["product_name"],
            "current_stock": inventory_info["stock_quantity"],
            "predicted_weekly_demand": predicted,
            "status": "Restock Needed" if predicted > inventory_info["stock_quantity"] else "Stock OK"
        })
         
    else:
        predictions.append({
            "product_name": f"Product ID {item['product_id']} (Not found)",
            "current_stock": 0,
            "predicted_weekly_demand": predicted,
            "status": "No Data"
        })

    cur.close()
    conn.close()
    return render_template("stock_prediction.html", predictions=predictions)
