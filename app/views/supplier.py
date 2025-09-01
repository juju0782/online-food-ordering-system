from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models.supplier import Supplier
from app.models.commodity import Commodity
import mysql.connector

supplier = Blueprint('supplier', __name__)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="KADUDA56ras",
        database="tj_dinehive",
        port=3307
    )

@supplier.route('/supplier')
def list_supplier():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM supplier")
    supplier_list = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('supplier/list.html', supplier=supplier_list)

@supplier.route('/supplier/add', methods=['GET', 'POST'])
def add_supplier():
    if request.method == 'POST':
        name = request.form['name']
        contact_person = request.form['contact_person']
        phone = request.form['phone']
        email = request.form['email']
        commodities = request.form['commodities']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO supplier (name, contact_person, email, phone, commodities)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, contact_person, email, phone, commodities))
        conn.commit()
        cur.close()
        conn.close()
        flash('Supplier added successfully!', 'success')
        return redirect(url_for('supplier.list_supplier'))
    return render_template('supplier/add.html')

@supplier.route('/edit/<int:supplier_id>', methods=['GET', 'POST'])
def edit_supplier(supplier_id):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    if request.method == 'POST':
        name = request.form['name']
        contact = request.form['contact_person']
        email = request.form['email']
        phone = request.form['phone']
        commodities = request.form['commodities']

        cur.execute(
            "UPDATE supplier SET name=%s, contact_person=%s, email=%s, phone=%s, commodities=%s WHERE supplier_id=%s",
            (name, contact, email, phone, commodities, supplier_id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('supplier.list_supplier'))

    cur.execute("SELECT * FROM supplier WHERE supplier_id = %s", (supplier_id,))
    supplier_data = cur.fetchone()
    conn.close()
    return render_template('supplier/edit.html', supplier=supplier_data)

@supplier.route('/delete/<int:supplier_id>', methods=['POST'])
def delete_supplier(supplier_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM supplier WHERE supplier_id = %s", (supplier_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('supplier.list_supplier'))

@supplier.route("/supplier/<int:supplier_id>/commodities")
def supplier_commodities(supplier_id):
    supplier_obj = Supplier.query.get_or_404(supplier_id)
    return render_template("supplier/supplier_commodities.html", supplier=supplier_obj)

@supplier.route("/supplier/<int:supplier_id>/add-commodity", methods=["GET", "POST"])
def add_commodity(supplier_id):
    supplier_obj = Supplier.query.get_or_404(supplier_id)

    if request.method == "POST":
        name = request.form["name"]
        quantity = float(request.form["quantity"])
        unit = request.form["unit"]
        price = float(request.form["price"])

        new_commodity = Commodity(
            name=name,
            quantity=quantity,
            unit=unit,
            price=price,
            supplier=supplier_obj
        )
        db.session.add(new_commodity)
        db.session.commit()
        flash("Commodity added successfully!", "success")
        return redirect(url_for("supplier.supplier_commodities", supplier_id=supplier_id))

    return render_template("supplier/add_commodity.html", supplier=supplier_obj)

@supplier.route('/supplier/commodity/<int:commodity_id>/edit', methods=['GET', 'POST'])
def edit_commodity(commodity_id):
    commodity = Commodity.query.get_or_404(commodity_id)

    if request.method == 'POST':
        commodity.name = request.form['name']
        commodity.quantity = request.form['quantity']
        commodity.unit = request.form['unit']
        commodity.price = request.form['price']

        try:
            db.session.commit()
            flash('Commodity updated successfully!', 'success')
            return redirect(url_for('supplier.supplier_commodities', supplier_id=commodity.supplier_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating commodity: {e}', 'danger')

    return render_template('supplier/edit_commodity.html', commodity=commodity)

@supplier.route('/supplier/commodity/<int:commodity_id>/delete', methods=['POST'])
def delete_commodity(commodity_id):
    commodity = Commodity.query.get_or_404(commodity_id)
    supplier_id = commodity.supplier_id

    try:
        db.session.delete(commodity)
        db.session.commit()
        flash('Commodity deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting commodity: {e}', 'danger')

    return redirect(url_for('supplier.supplier_commodities', supplier_id=supplier_id))
