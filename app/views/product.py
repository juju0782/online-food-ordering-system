from flask import Blueprint, render_template, redirect, url_for, request, flash,current_app
from werkzeug.utils import secure_filename
from app import db
import os
from app.models.products import Product
from app.models.users import User

product = Blueprint("product", __name__)

@product.route("/all_products", methods=["GET"])
def all_products():
    products = Product.query.all()
    return render_template("products/all_products.html", products=products)




@product.route("/product/<int:product_id>", methods=["GET"])
def single_product_detail(product_id):
    product = Product.query.get_or_404(product_id)  
    return render_template("products/single_product.html", product=product)


@product.route("/add-product", methods=["POST", "GET"])
def add_new_product():
    if request.method == "POST":
        try:
            product_name = request.form.get("product_name")
            product_category = request.form.get("product_category")
            price = request.form.get("price")
            description = request.form.get("description")
            product_image_path = request.files.get("product_image_path")

            
            if not all([product_name, product_category, price, description, product_image_path]):
                flash("All fields are required, including an image!", "danger")
                return render_template("products/new_product.html", 
                                       product_name=product_name,
                                       product_category=product_category,
                                       price=price,
                                       description=description)

            
            try:
                product_cost = float(price) 
            except ValueError:
                flash("Product cost must be a valid number.", "danger")
                return render_template("products/new_product.html", 
                                       product_name=product_name,
                                       product_category=product_category,
                                       price=price,
                                       description=description)

            image_filename = secure_filename(product_image_path.filename)
            upload_folder = current_app.config["PRODUCT_UPLOAD_FOLDER"]
            os.makedirs(upload_folder, exist_ok=True)
            image_path = os.path.join(upload_folder, image_filename)
            product_image_path.save(image_path)

            new_product = Product(
                product_category=product_category,
                product_name=product_name,
                description=description,
                price=price,  
                product_image_path=f"/static/images/products/{image_filename}"  
            )
            db.session.add(new_product)
            db.session.commit()

            flash(f"Product '{product_name}' added successfully!", "success")
            return redirect(url_for("product.all_products"))
        except Exception as e:
            db.session.rollback()  
            flash(f"An error occurred: {str(e)}", "danger")
            return render_template("products/new_product.html", 
                                   product_name=product_name,
                                   product_category=product_category,
                                   price=price,
                                   description=description,
                                   error="Something went wrong")
    return render_template("products/new_product.html")



@product.route("/single_item/<int:product_id>")
def single_item(product_id):
    single_result = Product.query.get(product_id)  
    if single_result is None:
        flash("Product not found.", "danger")
        return redirect(url_for("product.all_products"))
    return render_template("singleitem.html", single_item=single_result)



@product.route("/edit-product/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)  
    print(f"\nEDIT IMAGE:  {product.product_image_path}")

    
    if request.method == "POST":
        product_name = request.form["product_name"]
        product_category = request.form["product_category"]
        description = request.form["description"]
        price = request.form["price"]  
        product_image = request.files.get("product_image")  

        product.product_name = product_name
        product.product_category = product_category  
        product.description = description
        product.price = price

        if product_image and product_image.filename:
            image_filename = secure_filename(product_image.filename)
            upload_folder = current_app.config["PRODUCT_UPLOAD_FOLDER"]
            os.makedirs(upload_folder, exist_ok=True)
            image_path = os.path.join(upload_folder, image_filename)
            product_image.save(image_path)

            
            product.product_image_path = f"/static/images/products/{image_filename}"

        
        try:
            db.session.commit()
            flash("Product updated successfully!", "success")
            return redirect(url_for("product.all_products"))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while updating the product: {str(e)}", "danger")

    
    return render_template("products/edit_product.html", product=product)


@product.route("/delete-product/<int:product_id>", methods=["POST"])
def delete_product(product_id):
    product = Product.query.get(product_id)  

    if product is None:
        flash("Product not found.", "danger")
        return redirect(url_for("product.all_products"))

    try:
        db.session.delete(product)  
        db.session.commit()  
        flash("Product deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()  
        flash(f"An error occurred while deleting the product: {str(e)}", "danger")

    return redirect(url_for("product.all_products"))