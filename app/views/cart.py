from flask import Blueprint,Flask,render_template,jsonify, session, redirect, url_for, request, flash
from flask_mail import Message
from app import db, mail
from flask_login import login_required, current_user
from datetime import datetime
# models
from app.models.products import Product
from app.models.users import User
from app.models.order import Order, OrderItem



cart = Blueprint("cart",__name__)


@cart.route("/shopping-cart", methods=["GET", "POST"])
def shopping_cart():
    if "cart" not in session:
        session["cart"] = []

    if request.method == "GET":
        cart_items = session.get("cart", [])
        total_price = sum(item["price"] * item["quantity"] for item in cart_items)
        return render_template("cart/shopping_cart.html", cart_items=cart_items, total_price=total_price)

    if request.method == "POST" and request.is_json:
        data = request.get_json()
        product_id = data.get("product_id")
        action = data.get("action", "increment")

        if not product_id:
            return jsonify({"success": False, "message": "Product ID is required."}), 400
        
        try:
            product_id = int(product_id)
        except ValueError:
            return jsonify({"success": False, "message": "Invalid Product ID."}), 400

        if "cart" not in session:
            session["cart"] = []

        cart = session["cart"]
        product = next((item for item in cart if item["product_id"] == product_id), None)

        if product:
            if action == "increment":
                product["quantity"] += 1
            elif action == "decrement" :
              if  product["quantity"] > 1:
                    product["quantity"] -= 1
            else:
                cart.remove(product)
        else:

            db_product = Product.query.filter_by(product_id=product_id).first()
            if not db_product:
                return jsonify({"success": False, "message": "Product not found."}), 404

            cart.append({
                "product_id": db_product.product_id,
                "name": db_product.product_name,
                "price": db_product.price,
                "quantity": 1,
                "product_image_path": db_product.product_image_path,
            })

        session.modified = True


        total_price = sum(item["price"] * item["quantity"] for item in cart)
        cart_empty = len(cart) == 0

        return jsonify({
            "success": True,
            "updated_quantity": product["quantity"] if product else 1,
            "updated_item_total": product["price"] * product["quantity"] if product else 0,
            "new_total_price": total_price,
            "cart_empty": cart_empty,
        }), 200



@cart.route("/add-to-cart", methods=["POST"])
def add_to_cart():
    try:
        data = request.get_json()
        product_id = data.get("product_id")
        quantity = data.get("quantity", 1)

        if not product_id or quantity <= 0:
            return jsonify({"success": False, "message": "Invalid product ID or quantity."}), 400

        product = Product.query.filter_by(id=product_id).first()
        if not product:
            return jsonify({"success": False, "message": "Product not found."}), 404



        return jsonify({"success": True, "message": "Item added to cart."}), 200

    except Exception as e:
        print(f"Error adding to cart: {e}")
        return jsonify({"success": False, "message": "An error occurred while adding the item to the cart."}), 500



@cart.route("/cart-count", methods=["GET"])
def cart_count():

    total_items = sum(item["quantity"] for item in session.get("cart", []))
    

    print(f"total_items: {total_items}")
    
    
    return jsonify({"count": total_items}), 200



@cart.route("/remove_from_cart/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):
    cart_items = session.get('cart', [])
    
    cart_items = [item for item in cart_items if item['product_id'] != product_id]
    session['cart'] = cart_items  
    session.modified = True

    return redirect(url_for('cart.shopping_cart'))


@cart.route("/clear_cart", methods=["POST"])
def clear_cart():
    session.pop('cart', None)  
    session.modified = True
    return redirect(url_for('cart.shopping_cart'))



@cart.route("/place-order", methods=["GET", "POST"])
def place_order():
    cart_items = session.get("cart", [])
    if not cart_items:
        return redirect(url_for("cart.shopping_cart"))

    total_price = sum(item["price"] * item["quantity"] for item in cart_items)

    if request.method == "POST":
        return redirect(url_for("cart.finalize_order"))

    return render_template(
        "cart/place_order.html", cart_items=cart_items, total_price=total_price
    )



@cart.route("/finalize-order", methods=["POST"])
@login_required
def finalize_order():
    """
    Finalizes an order by inserting order details into the database.
    """

    if not current_user.is_authenticated or current_user.get_id() is None:
        flash("Please log in before placing an order.", "warning")
        return redirect(url_for("auth.login"))  


    shipping_address = request.form.get("shipping_address")
    contact_number = request.form.get("contact_number")
    cart_items = session.get("cart", [])
    total_price = sum(item["price"] * item["quantity"] for item in cart_items)

    
    if not shipping_address or not contact_number:
        flash("Missing required fields! Shipping address and contact number are mandatory.", "danger")
        return redirect(url_for("cart.place_order"))

    try:
        
        print(f"User Authenticated: {current_user.is_authenticated}, User ID: {current_user.user_id}")

        order = Order(
            user_id=current_user.user_id,  
            customer_name=current_user.name,
            contact_number=contact_number,
            shipping_address=shipping_address,
            total_price=total_price,
            order_date=datetime.utcnow(),
            status="Pending",
            updated_at=datetime.utcnow(),
        )
        db.session.add(order)
        db.session.flush()  

        
        for item in cart_items:
            order_item = OrderItem(
                order_id=order.order_id,
                product_id=item["product_id"],
                product_name=item["name"],
                quantity=item["quantity"],
                price=item["price"],
            )
            db.session.add(order_item)

        db.session.commit()  

        send_order_email(order, cart_items)


        
        session.pop("cart", None)
        flash("Order placed successfully!", "success")
        return redirect(url_for("cart.order_success", order_id=order.order_id))


    except Exception as e:
        db.session.rollback()
        print(f"Error finalizing order: {e}")
        flash("An error occurred while finalizing the order. Please try again.", "danger")
        return redirect(url_for("cart.place_order"))


@cart.route("/order-success/<int:order_id>")
def order_success(order_id):
    order = Order.query.get(order_id)  

    if not order:
        flash("Order not found!", "danger")
        return redirect(url_for("cart.shopping_cart"))


    order_details = {
        "order_id": order.order_id,
        "customer_name": order.customer_name,
        "total_price": order.total_price,
        "shipping_address": order.shipping_address,
        "contact_number": order.contact_number,
        "cart_items": [
            {
               "name": item.product.product_name if item.product else "Unknown Product",

                "quantity": item.quantity,
                "price": item.product.price
            }
            for item in order.items  
        ]
    }

    return render_template(
        "cart/order_success.html",
        order_id=order_id,
        order_details=order_details,
        company_name="TJ DINEHIVE",
        company_phone_1="+254769805233",
        company_phone_2="+254790555378",
    )

def send_order_email(order, cart_items):
    try:
        admin_email = "admin@example.com"

        order_details = f"""
        Order ID: {order.order_id}
        Customer: {order.customer_name}
        Contact: {order.contact_number}
        Shipping Address: {order.shipping_address}
        Total Price: Ksh {order.total_price:.2f}
        Order Date: {order.order_date.strftime('%Y-%m-%d %H:%M:%S')}

        Items Ordered:
        """

        for item in cart_items:
            order_details += f"\n- {item['name']} (Qty: {item['quantity']}) - Ksh {item['price'] * item['quantity']:.2f}"

        msg = Message(
            subject=f"New Order Placed - {order.order_id}",
            sender="noreply@example.com",
            recipients=[admin_email],
            body=order_details,
        )

        mail.send(msg)
    except Exception as e:
        print(f"Error sending order email: {e}")