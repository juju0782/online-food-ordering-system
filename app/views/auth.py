'''
from flask import Blueprint,render_template,request,redirect,url_for,flash,session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user,login_required, logout_user, current_user
from flask_mail import Mail, Message
from datetime import datetime, timedelta
from app import db
from app.forms.auth import RegistrationForm, LoginForm, RequestOtp, VerifyOtp,ResetPassword, UserProfileForm
from app.models.users import User
from app.utils.otp import generate_otp

auth = Blueprint("auth",__name__,url_prefix="/auth/")

mail = Mail()


# @auth.route("register", methods=["POST","GET"])
# def register():
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         email = form.email.data
#         phone = form.phone.data
#         password = form.password.data
#         # chech if the user already exists using email and phone
#         existing_user = User.query.filter((User.email == email) | (User.phone == phone )).first()
#         if existing_user:
#             flash("Email or password already exists","danger")
#             return redirect(url_for("auth.register"))
#         # els create a new user
#         new_user = User(
#             email = email,
#             phone = phone,
#             password_hash = generate_password_hash(password)
#         )
#         try:
#             db.session.add(new_user)
#             db.session.commit()
#             flash("Registration successful! You can now log in.", "success")
#             return redirect(url_for("auth.login"))
#         except Exception as e:
#             flash(f"An error:  {e} occured", "danger")
#             return redirect(url_for("auth.register"))
#     return render_template("auth/register.html",form=form)

import mysql.connector
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()

@auth.route("/register", methods=["POST", "GET"])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        email = form.email.data
        phone = form.phone.data
        password = form.password.data  # Raw password

        # Hash the password using bcrypt
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        try:
            # Connect to MySQL database
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="tj_dinehive",
                port=3307
            )
            cur = conn.cursor()

            # Check if user already exists
            cur.execute("SELECT * FROM users WHERE email = %s OR phone = %s", (email, phone))
            existing_user = cur.fetchone()


            if existing_user:
                flash("Email or phone number already exists!", "danger")
                return redirect(url_for("auth.register"))

            # Insert new user with hashed password
            cur.execute("INSERT INTO users (email, phone, password_hash) VALUES (%s, %s, %s)",
                        (email, phone, hashed_password))
            conn.commit()

            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for("auth.login"))

        except mysql.connector.Error as e:
            flash(f"Database error: {e}", "danger")
        finally:
            if 'cur' in locals() and cur:
                cur.close()
            if 'conn' in locals() and conn:
                conn.close()

    return render_template("auth/register.html", form=form)








@auth.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        try:
            # Connect to MySQL database
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",  # Adjust if your password is not empty
                database="tj_dinehive",
                port=3307
            )
            cur = conn.cursor(dictionary=True)

            # Query user by email, explicitly selecting user_id instead of id
            cur.execute("SELECT user_id, email, password_hash FROM users WHERE email = %s", (email,))
            user = cur.fetchone()  # Fetch one row

            # Debugging: Print the fetched data
            print("User Data from DB:", user)

            if not user:
                flash("User not found.", "danger")
                return redirect(url_for("auth.login"))

            stored_hash = user.get("password_hash")  # Retrieve password hash safely

            # Verify password using bcrypt check
            if bcrypt.check_password_hash(stored_hash, password):
                # Ensure user_id is available before accessing it
                user_id = user.get("user_id")
                if not user_id:
                    flash("User ID not found in database.", "danger")
                    return redirect(url_for("auth.login"))

                # Create a User object (assuming you have a User model)
                logged_in_user = User(user_id=user_id, email=user["email"])

                login_user(logged_in_user)  # Flask-Login function
                flash("Login successful!", "success")
                return redirect(url_for("main.home"))
            else:
                flash("Invalid email or password.", "danger")

        except mysql.connector.Error as e:
            flash(f"Database error: {e}", "danger")
        finally:
            if 'cur' in locals() and cur:
                cur.close()
            if 'conn' in locals() and conn:
                conn.close()

    return render_template("auth/login.html", form=form)










@auth.route("forgot-password", methods=["POST", "GET"])
def forgot_password():
    form = RequestOtp()
    if form.validate_on_submit():
        email = form.email.data

        user = User.query.filter_by(email=email).first()
        if user:
            otp = generate_otp()  # Call the external generate_otp function
            user.otp = otp  # Set the OTP on the user object
            user.otp_created_at = datetime.now()  # Set the creation time
            db.session.commit()  # Save changes to the database

            msg = Message(
                "Your OTP Code",
                sender="WENDY-OTP",
                recipients=[email]
            )
            msg.body = f"Your OTP code is: {otp}"  # Include the OTP in the email body
            mail.send(msg)  # Send the email
            flash(f"An OTP has been sent to email address: {email}", "success")
            return redirect(url_for("auth.verify_otp", email=email))
        else:
            flash("Email address not found.", "danger")
    return render_template("auth/forgot_password.html", form=form)








@auth.route("verify-otp", methods=["POST", "GET"])
def verify_otp():
    form = VerifyOtp()
    email = request.args.get("email")  # Retrieve email from query parameter

    if request.method == "POST" and form.validate_on_submit():
        otp_input = form.otp.data  # Get the OTP entered by the user
        user = User.query.filter_by(email=email).first()  # Retrieve the user by email

        if not user:
            flash("Invalid email address. Please request a new OTP.", "danger")
            return redirect(url_for("auth.forgot_password"))

        if user.otp != otp_input:
            flash("Invalid OTP. Please try again.", "danger")
            return redirect(url_for("auth.verify_otp", email=email))

        # Ensure the OTP is still valid (e.g., expires in 30 minutes)
        if user.otp_created_at and datetime.now() - user.otp_created_at > timedelta(minutes=30):
            flash("The OTP has expired. Please request a new one.", "danger")
            return redirect(url_for("auth.forgot_password"))

        # OTP is valid - clear it from the database for security
        user.otp = None
        user.otp_created_at = None
        db.session.commit()

        flash("OTP verified successfully. You can now reset your password.", "success")
        return redirect(url_for("auth.reset_password", email=email))

    return render_template("auth/verify_otp.html", form=form, email=email)  # Pass email to the template


@auth.route("reset-password", methods=["POST", "GET"])
def reset_password():
    form = ResetPassword() # Ensure you are using the correct form class
    email = request.args.get("email")  # Retrieve email from query parameter

    if request.method == "POST" and form.validate_on_submit():
        password = form.password.data
        user = User.query.filter_by(email=email).first()

        if not user:
            flash("Invalid email address. Please request a new OTP.", "danger")
            return redirect(url_for("auth.forgot_password"))

        # Update the user's password
        user.password_hash = generate_password_hash(password)  # Hash the new password
        db.session.commit()  # Commit the changes to the database

        flash("Your password has been reset successfully. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", form=form, email=email)  # Pass email to the template



@auth.route("user-profile", methods=["GET", "POST"])
@login_required
def profile():
    form = UserProfileForm()

    # Fetch User Data from MySQL
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="tj_dinehive",
            port=3307
        )
        cur = conn.cursor(dictionary=True)

        cur.execute("SELECT email, phone FROM users WHERE user_id = %s", (current_user.user_id,))
        user_data = cur.fetchone()

        if user_data:
            form.email.data = user_data["email"]
            form.phone.data = user_data["phone"]

    except mysql.connector.Error as e:
        flash(f"Database error: {e}", "danger")
        return redirect(url_for("auth.user_profile"))
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

    # Handle Profile Update
    if form.validate_on_submit():
        email = form.email.data
        phone = form.phone.data
        password = form.password.data  # Optional password change

        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="tj_dinehive",
                port=3307
            )
            cur = conn.cursor()

            # If the user wants to change their password
            if password:
                hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
                cur.execute(
                    "UPDATE users SET email = %s, phone = %s, password_hash = %s WHERE user_id = %s",
                    (email, phone, hashed_password, current_user.user_id)
                )
            else:
                cur.execute(
                    "UPDATE users SET email = %s, phone = %s WHERE user_id = %s",
                    (email, phone, current_user.user_id)
                )

            conn.commit()
            flash("Profile updated successfully!", "success")
            return redirect(url_for("auth.user_profile"))

        except mysql.connector.Error as e:
            flash(f"Database error: {e}", "danger")
        finally:
            if 'cur' in locals():
                cur.close()
            if 'conn' in locals():
                conn.close()

    return render_template("auth/user_profile.html", form=form)



@auth.route("/logout")
def logout():
    logout_user()  # Log the user out
    flash("You have been logged out.", "success")  # Optional: Flash a message
    return redirect(url_for("main.home"))  # Redirect to the home page or another page
'''

from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from datetime import datetime, timedelta
from app import db
from app.forms.auth import RegistrationForm, LoginForm, RequestOtp, VerifyOtp, ResetPassword, UserProfileForm
from app.models.users import User
from app.utils.otp import generate_otp
import mysql.connector
from flask_bcrypt import Bcrypt

auth = Blueprint("auth", __name__, url_prefix="/auth/")
mail = Mail()
bcrypt = Bcrypt()

@auth.route("/register", methods=["POST", "GET"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data
        phone = form.phone.data
        password = form.password.data
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="KADUDA56ras",
                database="tj_dinehive",
                port=3307
            )
            cur = conn.cursor()

            cur.execute("SELECT * FROM users WHERE email = %s OR phone = %s", (email, phone))
            existing_user = cur.fetchone()

            if existing_user:
                flash("Email or phone number already exists!", "danger")
                return redirect(url_for("auth.register"))

            cur.execute("INSERT INTO users (email, phone, password_hash) VALUES (%s, %s, %s)",
                        (email, phone, hashed_password))
            conn.commit()
            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for("auth.login"))

        except mysql.connector.Error as e:
            flash(f"Database error: {e}", "danger")
        finally:
            cur.close()
            conn.close()

    return render_template("auth/register.html", form=form)


@auth.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="KADUDA56ras",
                database="tj_dinehive",
                port=3307
            )
            cur = conn.cursor(dictionary=True)

            cur.execute("SELECT user_id, email, password_hash FROM users WHERE email = %s", (email,))
            user = cur.fetchone()

            if not user:
                flash("User not found.", "danger")
                return redirect(url_for("auth.login"))

            stored_hash = user.get("password_hash")

            if bcrypt.check_password_hash(stored_hash, password):
                user_id = user.get("user_id")
                if not user_id:
                    flash("User ID not found in database.", "danger")
                    return redirect(url_for("auth.login"))

                logged_in_user = User(user_id=user_id, email=user["email"])
                login_user(logged_in_user)  

                flash("Login successful!", "success")
                return redirect(url_for("main.home"))
            else:
                flash("Invalid email or password.", "danger")

        except mysql.connector.Error as e:
            flash(f"Database error: {e}", "danger")
        finally:
            cur.close()
            conn.close()

    return render_template("auth/login.html", form=form)


@auth.route("/forgot-password", methods=["POST", "GET"])
def forgot_password():
    form = RequestOtp()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()

        if user:
            otp = generate_otp()
            user.otp = otp
            user.otp_created_at = datetime.now()
            db.session.commit()

            msg = Message("Your OTP Code", sender="WENDY-OTP", recipients=[email])
            msg.body = f"Your OTP code is: {otp}"
            mail.send(msg)

            flash(f"An OTP has been sent to: {email}", "success")
            return redirect(url_for("auth.verify_otp", email=email))
        else:
            flash("Email address not found.", "danger")

    return render_template("auth/forgot_password.html", form=form)

@auth.route("/verify-otp", methods=["POST", "GET"])
def verify_otp():
    form = VerifyOtp()
    email = request.args.get("email")

    if form.validate_on_submit():
        otp_input = form.otp.data
        user = User.query.filter_by(email=email).first()

        if not user or user.otp != otp_input:
            flash("Invalid OTP. Try again.", "danger")
            return redirect(url_for("auth.verify_otp", email=email))

        if datetime.now() - user.otp_created_at > timedelta(minutes=30):
            flash("OTP expired. Request a new one.", "danger")
            return redirect(url_for("auth.forgot_password"))

        user.otp = None
        user.otp_created_at = None
        db.session.commit()

        flash("OTP verified! Reset your password.", "success")
        return redirect(url_for("auth.reset_password", email=email))

    return render_template("auth/verify_otp.html", form=form, email=email)


@auth.route("/reset-password", methods=["POST", "GET"])
def reset_password():
    form = ResetPassword()
    email = request.args.get("email")

    if form.validate_on_submit():
        password = form.password.data
        user = User.query.filter_by(email=email).first()

        if not user:
            flash("Invalid email. Request a new OTP.", "danger")
            return redirect(url_for("auth.forgot_password"))

        user.password_hash = generate_password_hash(password)
        db.session.commit()

        flash("Password reset successful! Log in now.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", form=form, email=email)


@auth.route("/user-profile", methods=["GET", "POST"])
@login_required
def profile():
    form = UserProfileForm()
    
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="KADUDA56ras",
            database="tj_dinehive",
            port=3307
        )
        cur = conn.cursor(dictionary=True)

        cur.execute("SELECT email, phone FROM users WHERE user_id = %s", (current_user.get_id(),))
        user_data = cur.fetchone()

        if user_data:
            form.email.data = user_data["email"]
            form.phone.data = user_data["phone"]

    except mysql.connector.Error as e:
        flash(f"Database error: {e}", "danger")
    finally:
        cur.close()
        conn.close()

    if form.validate_on_submit():
        email = form.email.data
        phone = form.phone.data
        password = form.password.data

        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="KADUDA56ras",
                database="tj_dinehive",
                port=3307
            )
            cur = conn.cursor()

            if password:
                hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
                cur.execute("UPDATE users SET email = %s, phone = %s, password_hash = %s WHERE user_id = %s",
                            (email, phone, hashed_password, current_user.get_id()))
            else:
                cur.execute("UPDATE users SET email = %s, phone = %s WHERE user_id = %s",
                            (email, phone, current_user.get_id()))

            conn.commit()
            flash("Profile updated successfully!", "success")

        except mysql.connector.Error as e:
            flash(f"Database error: {e}", "danger")
        finally:
            cur.close()
            conn.close()

    return render_template("auth/user_profile.html", form=form, user=current_user)

@auth.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form.get('password')  

        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="KADUDA56ras",
                database="tj_dinehive",
                port=3307
            )
            cur = conn.cursor()

            if email != current_user.email:
                cur.execute("SELECT * FROM users WHERE email = %s", (email,))
                existing_user = cur.fetchone()
                if existing_user:
                    flash('Email is already in use. Please choose a different one.', 'danger')
                    cur.close()
                    conn.close()
                    return redirect(url_for('auth.edit_profile'))

            if password:
                hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
                cur.execute("UPDATE users SET name = %s, email = %s, password = %s WHERE id = %s",
                            (name, email, hashed_password, current_user.id))
            else:
                cur.execute("UPDATE users SET name = %s, email = %s WHERE id = %s",
                            (name, email, current_user.id))

            conn.commit()
            cur.close()
            conn.close()

            flash('Profile updated successfully.', 'success')
            return redirect(url_for('auth.edit_profile'))

        except Exception as e:
            flash(f"An error occurred: {str(e)}", 'danger')
            return redirect(url_for('auth.edit_profile'))


    return render_template('auth/edit_profile.html', user=current_user)

@auth.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("main.home"))

