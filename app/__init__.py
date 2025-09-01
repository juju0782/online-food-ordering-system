from flask import Flask, request, render_template, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_session import Session
from flask_mail import Mail
from datetime import timedelta
from werkzeug.utils import secure_filename
import os
from twilio.rest import Client


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)
    app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=30)

    
    TWILIO_ACCOUNT_SID = app.config.get("TWILIO_ACCOUNT_SID", "your_twilio_account_sid")
    TWILIO_AUTH_TOKEN = app.config.get("TWILIO_AUTH_TOKEN", "your_twilio_auth_token")
    TWILIO_WHATSAPP_NUMBER = app.config.get("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
    

    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


    @app.context_processor
    def inject_company_details():
        return {
            'company_name': app.config.get('COMPANY_NAME', 'Your Company'),
            'company_email_1': app.config.get('COMPANY_EMAIL_1', ''),
            'company_email_2': app.config.get('COMPANY_EMAIL_2', ''),
            'company_phone_1': app.config.get('COMPANY_PHONE_1', ''),
            'company_phone_2': app.config.get('COMPANY_PHONE_2', ''),
            'company_url': app.config.get('COMPANY_URL', '')
        }


    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)


    login_manager.login_view = "auth.login"  

    @login_manager.user_loader
    def load_user(user_id):
        from app.models.users import User
        from app.models.client import Client

        return User.query.get(int(user_id))

    from app.views import main 
    from app.views.admin import admin
    from app.views.auth import auth
    from app.views.cart import cart
    from app.views.product import product
    from app.views.userprofile import userprofile
    from app.views.transactions import transactions
    from app.views.client import client
    from app.views.orders import orders
    from app.views.inventory import inventory
    from app.views.delivery import delivery
    from app.views.supplier import supplier
    from app.views.payment import payment

    app.register_blueprint(main, url_prefix="/")  
    app.register_blueprint(admin, url_prefix="/admin")  
    app.register_blueprint(auth, url_prefix="/auth")  
    app.register_blueprint(cart, url_prefix="/cart")  
    app.register_blueprint(product, url_prefix="/product") 
    app.register_blueprint(userprofile, url_prefix="/user") 
    app.register_blueprint(transactions, url_prefix="/transactions")
    app.register_blueprint(client, url_prefix="/client")
    app.register_blueprint(orders, url_prefix="/orders")
    app.register_blueprint(inventory, url_prefix="/inventory")
    app.register_blueprint(delivery, url_prefix="/delivery")
    app.register_blueprint(supplier, url_prefix="/supplier")
    app.register_blueprint(payment, url_prefix="/payment")
    return app  
