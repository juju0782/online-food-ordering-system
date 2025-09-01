from flask import Blueprint, render_template, abort, request, redirect, url_for, flash, current_app, jsonify, send_file, make_response
from flask_login import login_required, current_user
from xhtml2pdf import pisa
import mysql.connector
from flask_mail import Message
from flask import send_file
from app import mail
from app.models.products import Product
from app.models.users import User
from app.models.mpesapayment import mpesapayment
from app.models.supplier import Supplier
from app.models.transactions import Transactions
from app.models.commodity import Commodity
from app.utils.pdf_generator import generate_pdf
from app.models.client import Client  
from app.models.order import Order
from app.models.cart import Cart
from werkzeug.utils import secure_filename
import os
import io
from flask_mail import Mail, Message
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from datetime import datetime
from twilio.rest import Client as TwilioClient  
from app import db  


main = Blueprint("main", __name__)

@main.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get(product_id)
    if product is None:
        abort(404)
    return render_template('product_detail.html', product=product)
'''
@main.route('/product/delete-product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get(product_id)

    if not product:
        flash("Product not found!", "danger")
        return redirect(url_for("product.all_products"))

    print(f"Deleting product: {product.product_name}, ID: {product.product_id}")

    # Delete associated image
    if product.product_image_path:
        image_path = os.path.join("static", product.product_image_path)
        if os.path.exists(image_path):
            os.remove(image_path)
            print(f"Deleted image: {image_path}")
        else:
            print(f"Image file not found: {image_path}")

    # Try deleting the product
    try:
        db.session.delete(product)
        db.session.commit()
        print("Product successfully deleted from database.")
        flash("Product deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting product: {str(e)}")
        flash(f"Error deleting product: {str(e)}", "danger")

    return redirect(url_for('main.delete_products'))
'''


'''
@main.route("/")
def index():
    try:
        products = Product.query.all()
    except Exception as e:
        products = []
        print(f"Error retrieving products: {e}")
    return render_template('index.html', products=products)
''''''
@main.route("/home")
def home():

    print(f"Current User: {current_user}")  # Debugging
    print(f"User ID: {getattr(current_user, 'id', 'No ID')}")  # Check if ID exists
    try:
        products = Product.query.all()
    except Exception as e:
        products = []
        print(f"Error retrieving products: {e}")
    return render_template("home.html", products=products)
'''

@main.route("/")
def home():
    try:
        products = Product.query.all()
    except Exception as e:
        products = []
        print(f"Error retrieving products: {e}")  
    return render_template("home.html", products=products)



@main.route('/search')
def search():
    query = request.args.get('query', '')
    print(f"Search Query: {query}")  
    results = Product.query.filter(Product.product_name.ilike(f"%{query}%")).all()
    print(f"Search Results: {results}")  
    return render_template('search_results.html', results=results, query=query)


@main.context_processor
def inject_user():
    return dict(user=current_user)

@main.route("/upload", methods=["GET", "POST"])
def upload():
    def allowed_file(filename):
        return "." in filename and filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]

    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)

        file = request.files["file"]

        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)

            flash("File uploaded successfully!")
            return redirect(url_for("main.viewer", filename=filename))

    return render_template("upload.html")

@main.route("/viewer/<filename>")
def viewer(filename):
    return render_template("viewer.html", filename=filename)

@main.route('/debug_clients')
def debug_clients():
    clients = Client.query.all()
    return jsonify([{"id": c.id, "name": c.name, "email": c.email} for c in clients])

@main.route('/add-supplier', methods=['GET', 'POST'])
def add_supplier():
    if request.method == 'POST':
        pass
    return render_template('supplier/add.html')

@main.route('/supplier', methods=['GET', 'POST'])
def list_supplier():
    if request.method == 'POST':
        pass
    return render_template('supplier/list.html')

@main.route("/callback", methods=["POST"])
def mpesa_callback():
    data = request.json
    print("M-Pesa Callback Data:", data)
    return jsonify({"message": "Received"}), 200

@main.route('/clients')
def clients_page():
    return render_template('clients.html')

@main.route('/my_transactions')
@login_required
def my_transactions():
    transactions = Transactions.query.filter_by(user_id=current_user.user_id).order_by(Transactions.date.desc()).all()
    return render_template('my_transactions.html', transactions=transactions)




@main.route('/transactions')
def transactions_page():
    transactions = Transactions.query.all()
    return render_template('transactions.html', transactions=transactions)

@main.route('/add_transaction', methods=['POST'])
def add_transaction():
    try:
        
        print("Form Data Received:", request.form)  

        user_id = request.form['user_id']
        food_item = request.form['food_item']
        amount = request.form['amount']
        payment_method = request.form.get('payment_method', 'N/A')

        new_transaction = Transactions(
            user_id=int(user_id),
            food_item=food_item,
            amount=float(amount),
            payment_method=payment_method
        )

        db.session.add(new_transaction)
        db.session.commit()
        flash("Transaction added successfully!", "success")
    
    except Exception as e:
        db.session.rollback()  
        flash(f"Error adding transaction: {str(e)}", "danger")
    
    return redirect(url_for("main.transaction_history", user_id=user_id))


@main.route('/add_client', methods=['GET', 'POST'])
def add_client():
    if request.method == 'POST':
        
        pass
    return render_template('add_client.html')  


@main.route('/receipt/<int:transaction_id>')
def generate_receipt(transaction_id):
    transaction = Transactions.query.get(transaction_id)
    
    if not transaction:
        return "Transaction not found", 404

    client = transaction.client  
    receipt_path = f"static/receipt_{transaction_id}.pdf"
    
    c = canvas.Canvas(receipt_path, pagesize=letter)
    width, height = letter

    
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, height - 50, "Payment Receipt")


    c.setFont("Helvetica", 12)
    c.drawString(50, height - 100, f"Transaction ID: {transaction.id}")
    c.drawString(50, height - 120, f"Client Name: {client.name}")
    c.drawString(50, height - 140, f"Food Item: {transaction.food_item}")
    c.drawString(50, height - 160, f"Amount: ${transaction.amount:.2f}")
    c.drawString(50, height - 180, f"Payment Method: {transaction.payment_method}")
    c.drawString(50, height - 200, f"Date: {transaction.date.strftime('%Y-%m-%d %H:%M:%S')}")


    c.drawString(50, height - 250, "Thank you for your purchase!")

    c.save()
    
    return send_file(receipt_path, as_attachment=True)

@main.route('/view-receipt/<int:transaction_id>')
def view_receipt(transaction_id):
    transaction = Transactions.query.get(transaction_id)
    if not transaction:
        return "Transaction not found", 404
    return render_template("receipt.html", transaction=transaction)

'''
@main.route('/transaction-history', methods=['GET'])
def transaction_history():
    try:
        transactions = Transactions.query.all()
        print("Transactions retrieved:", transactions)  # Debugging line
        return render_template("transaction_history.html", transactions=transactions)
    except Exception as e:
        print(f"Error retrieving transactions: {e}")  # Print actual error
        return "An error occurred", 500
'''


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

@main.route('/download-my-transactions')
@login_required
def download_my_transactions():
    transactions = Transactions.query.filter_by(user_id=current_user.user_id).order_by(Transactions.date.desc()).all()
    
    
    html = render_template('pdf/client_transactions_pdf.html', transactions=transactions, user=current_user)
    
    
    result = io.BytesIO()
    pisa_status = pisa.CreatePDF(io.StringIO(html), dest=result)
    
    if pisa_status.err:
        return "PDF generation failed", 500

    
    response = make_response(result.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=my_transaction_history.pdf'
    return response

@main.route('/transactions/update/<int:transaction_id>', methods=['GET', 'POST'])
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



@main.route('/transaction/edit/<int:transaction_id>', methods=['GET', 'POST'])
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


@main.route('/transactions/delete/<int:transaction_id>', methods=['POST', 'GET'])
def delete_transaction(transaction_id):
    transaction = Transactions.query.get_or_404(transaction_id)
    db.session.delete(transaction)
    db.session.commit()
    return redirect(url_for('main.transactions_page'))

@main.route("/transaction-history/<int:user_id>")
@login_required
def transaction_history(user_id):
    if user_id != current_user.user_id:  
        return redirect(url_for("main.home"))  

    transactions = Transactions.query.filter_by(user_id=current_user.user_id).all()  
    return render_template("transaction_history.html", transactions=transactions)

@main.route('/client_transactions', methods=['GET'])
@login_required
def client_transaction_history():
    transactions = Transactions.query.filter_by(user_id=current_user.user_id).order_by(Transactions.date.desc()).all()
    return render_template('client_transaction_history.html', transactions=transactions)



@main.route('/transaction-history/email/<int:user_id>', methods=['GET'])
def send_transaction_pdf(user_email, pdf_file_path):
    msg = Message("Your Transaction History", recipients=[user_email])
    msg.body = "Attached is your transaction history."
    with open(pdf_file_path, 'rb') as f:
        msg.attach("Transaction_History.pdf", "application/pdf", f.read())
    mail.send(msg)

@main.route('/send_transaction_history_email/<int:user_id>')
@login_required
def send_transaction_history_email(user_id):

    return f"Email sent to user {user_id}"


@main.route('/download_transaction_history/<int:user_id>')
@login_required
def download_transaction_history(user_id):
    if current_user.user_id != user_id:
        abort(403)  

    transactions = Transactions.query.filter_by(user_id=user_id).all()
    pdf_path = generate_pdf(transactions)
    return send_file(pdf_path, as_attachment=True)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'KADUDA56ras',
    'database': 'tj_dinehive',
    'port': 3307
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@main.route('/calculate_profit', methods=["POST"])
def calculate_profit():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT 
            oi.quantity,
            p.price AS selling_price,
            p.cost_price AS cost_price
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        JOIN orders o ON oi.order_id = o.id
        WHERE (%s IS NULL OR o.date >= %s)
          AND (%s IS NULL OR o.date <= %s)
    """

    cursor.execute(query, (start_date, start_date, end_date, end_date))
    rows = cursor.fetchall()

    total_revenue = 0
    total_cost = 0

    for row in rows:
        revenue = row['selling_price'] * row['quantity']
        cost = row['cost_price'] * row['quantity']
        total_revenue += revenue
        total_cost += cost

    profit = total_revenue - total_cost

    cursor.close()
    connection.close()

    return jsonify({
        'total_revenue': total_revenue,
        'total_cost': total_cost,
        'profit': profit,
        'start_date': start_date,
        'end_date': end_date
    })

@main.route("/update-product", methods=["POST"])
def update_product():
    product_id = request.form.get("product_id")
    new_price = request.form.get("price")
    new_quantity = request.form.get("quantity")

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"success": False, "message": "Product not found"}), 404

    product.update_stock(new_price=new_price, new_quantity=new_quantity)
    return jsonify({"success": True, "message": "Product updated successfully"}), 200

@main.route('/calculate-delivery', methods=['GET', 'POST'])
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

    estimated_time = round(distance * 5, 2)
    delivery_fee = round(50 + (distance * 10), 2)

    return jsonify({
        'distance_km': distance,
        'estimated_time_minutes': estimated_time,
        'estimated_delivery_fee': delivery_fee
    })





'''
# ---------- EMAIL TRANSACTION HISTORY ----------

@main.route('/transaction-history/email/<int:client_id>', methods=['GET'])
def send_transaction_history_email(client_id):
    transactions = Transactions.query.filter_by(client_id=client_id).all()  
    if not transactions:
        return jsonify({"message": "No transactions found"}), 404

    client = Client.query.get(client_id)
    if not client:
        return jsonify({"message": "Client not found"}), 404

    pdf_path = generate_pdf(client_id, transactions)
    if not pdf_path:
        return jsonify({"message": "No transactions available for PDF generation"}), 404

    msg = Message("Your Food Order Transaction History", recipients=[client.email])
    msg.body = "Dear customer, attached is your transaction history.\n\nBest Regards,\nYour Food Service Team."
    with current_app.open_resource(pdf_path) as pdf:
        msg.attach("Transaction_History.pdf", "application/pdf", pdf.read())
    Mail(current_app).send(msg)

    return jsonify({"message": "Email sent successfully!"})

# ---------- WHATSAPP TRANSACTION HISTORY ----------
@main.route('/transaction-history/whatsapp/<int:client_id>', methods=['GET'])
def send_transaction_history_whatsapp(client_id):
    transactions = Transactions.query.filter_by(client_id=client_id).all()  
    if not transactions:
        return jsonify({"message": "No transactions found"}), 404

    client = Client.query.get(client_id)
    if not client:
        return jsonify({"message": "Client not found"}), 404

    pdf_path = generate_pdf(client_id, transactions)
    if not pdf_path:
        return jsonify({"message": "No transactions available for PDF generation"}), 404

    twilio_client = TwilioClient(
        current_app.config["TWILIO_ACCOUNT_SID"],
        current_app.config["TWILIO_AUTH_TOKEN"]
    )  

    pdf_filename = os.path.basename(pdf_path)
    message = twilio_client.messages.create(
        from_=f"whatsapp:{current_app.config['TWILIO_WHATSAPP_NUMBER']}",  
        body=f"Hello! Your transaction history is ready. Download it here: {request.host_url}static/{pdf_filename}",
        to=f"whatsapp:{client.phone}"
    )

    return jsonify({"message": f"Transaction history sent via WhatsApp to {client.phone}!"})
'''