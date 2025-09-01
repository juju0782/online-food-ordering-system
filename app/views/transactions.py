from flask import Blueprint, render_template, abort, request, redirect, url_for, flash, current_app, jsonify, send_file
from flask_login import login_required, current_user
from flask_mail import Message
from flask import send_file
from app import mail
import os
from app.models.transactions import Transactions
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from app import db

transactions = Blueprint('transactions', __name__)

@transactions.route('/transactions', methods=['GET'])
def get_transactions():
    transactions = Transactions.query.all()
    print("Fetched Transactions:", transactions)  
    return jsonify([t.to_dict() for t in transactions])

def generate_pdf(user_id, transactions):
    if not transactions:
        return None  

    os.makedirs("static", exist_ok=True)  
    filename = f"transaction_history_client_{user_id}.pdf"
    file_path = os.path.join("static", filename)
    total_amount = sum(txn.amount or 0 for txn in transactions)  

    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter

    logo_path = "static/logo.png"
    if os.path.exists(logo_path):
        logo = ImageReader(logo_path)
        c.drawImage(logo, 50, height - 80, width=100, height=50)

    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.darkblue)
    c.drawString(200, height - 50, f"Transaction History - Client {user_id}")


    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 120, "Date")
    c.drawString(200, height - 120, "Food Item")
    c.drawString(400, height - 120, "Amount ($)")
    c.line(50, height - 125, 550, height - 125)


    c.setFont("Helvetica", 10)
    y_position = height - 150
    for txn in transactions:
        c.drawString(50, y_position, txn.date.strftime('%Y-%m-%d %H:%M:%S'))
        c.drawString(200, y_position, txn.food_item)
        c.drawString(400, y_position, f"${txn.amount:.2f}")
        y_position -= 20

    c.save()
    return file_path

@transactions.route('/transactions/update/<int:transaction_id>', methods=['GET', 'POST'])
@login_required  
def update_transactions(transaction_id):
    transaction = Transactions.query.get_or_404(transaction_id)

    if transaction.user_id != current_user.user_id:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('main.transaction_history', user_id=current_user.user_id))

    if request.method == 'POST':
        transaction.food_item = request.form['food_item']
        transaction.amount = request.form['amount']
        transaction.payment_method = request.form['payment_method']

        try:
            db.session.commit()
            flash("Transaction updated successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating transaction: {str(e)}", "danger")

        return redirect(url_for('main.transaction_history', client_id=current_user.client.id))

    return render_template('edit_transaction.html', transaction=transaction)  



@transactions.route('/transaction/edit/<int:transaction_id>', methods=['GET', 'POST'])
def edit_transaction(transaction_id):
    transaction = Transactions.query.get(transaction_id)

    if not transaction:
        flash('Transaction not found', 'danger')
        return redirect(url_for('main.transactions_page'))

    if request.method == 'POST':
        transaction.client_id = request.form['user_id']
        transaction.food_item = request.form['food_item']
        transaction.amount = request.form['amount']
        transaction.payment_method = request.form['payment_method']

        db.session.commit()
        flash('Transaction updated successfully', 'success')
        return redirect(url_for('main.transactions_page'))

    return render_template('edit_transaction.html', transaction=transaction)


@transactions.route('/transactions/delete/<int:transaction_id>', methods=['POST', 'GET'])
def delete_transaction(transaction_id):
    transaction = Transactions.query.get_or_404(transaction_id)
    db.session.delete(transaction)
    db.session.commit()
    return redirect(url_for('main.transactions_page'))

@transactions.route("/transaction-history/<int:user_id>")
@login_required
def transaction_history(user_id):
    if user_id != current_user.user_id:  
        return redirect(url_for("main.home"))  

    transactions = Transactions.query.filter_by(user_id=current_user.user_id).all()  
    return render_template("transaction_history.html", transactions=transactions)


@transactions.route('/transaction-history/email/<int:user_id>', methods=['GET'])
def send_transaction_pdf(user_email, pdf_file_path):
    msg = Message("Your Transaction History", recipients=[user_email])
    msg.body = "Attached is your transaction history."
    with open(pdf_file_path, 'rb') as f:
        msg.attach("Transaction_History.pdf", "application/pdf", f.read())
    mail.send(msg)

@transactions.route('/send_transaction_history_email/<int:user_id>')
@login_required
def send_transaction_history_email(user_id):
    return f"Email sent to user {user_id}"

@transactions.route("/download_transaction_history/<int:user_id>")
@login_required
def download_transaction_history(user_id):
    if user_id != current_user.user_id:
        flash("Unauthorized", "danger")
        return redirect(url_for("main.home"))

    transactions = Transactions.query.filter_by(user_id=user_id).all()
    pdf_path = generate_pdf(transactions)
    return send_file(pdf_path, as_attachment=True)