from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
import os

from app import db
from app.models.users import User
from app.models.order import Order, OrderItem
from app.forms.auth import UserProfileForm

userprofile = Blueprint("userprofile", __name__)

@userprofile.route("/user-profile", methods=["GET", "POST"])
@login_required
def profile():
    form = UserProfileForm()
    user = User.query.get(current_user.user_id)

    if request.method == "GET":
        if user:
            form.email.data = user.email
            form.phone.data = user.phone
            form.first_name.data = user.first_name
            form.last_name.data = user.last_name
            form.address.data = user.address
            form.city.data = user.city
            form.state.data = user.state
            form.zip_code.data = user.zip_code
            form.country.data = user.country

    if form.validate_on_submit():
        user.email = form.email.data
        user.phone = form.phone.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.address = form.address.data
        user.city = form.city.data
        user.state = form.state.data
        user.zip_code = form.zip_code.data
        user.country = form.country.data

        if form.password.data:
            user.password_hash = generate_password_hash(form.password.data)
        

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("userprofile.profile"))
    

    return render_template("auth/user_profile.html", form=form)


@userprofile.route("/user-order")
def user_track_orders():
    user_orders= Order.query.all()
    return render_template("cart/user_order.html",user_orders=user_orders)
