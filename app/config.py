import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = "9fdde50cf248cc178bac18fa6cb3e6de1510bcd207c5a4e3a1ec3d832eb44af0"
    SQLALCHEMY_DATABASE_URI= "mysql+pymysql://root:KADUDA56ras@localhost:3307/tj_dinehive"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf"}  

    UPLOAD_FOLDER = "app/static/upload"
    PRODUCT_UPLOAD_FOLDER = "app/static/images/products"
    CATEGORY_UPLOAD_FOLDER = "app/static/images/category"

    COMPANY_NAME = "TJ DINEHIVE"
    COMPANY_PHONE_1 = "+254 769 805233"
    COMPANY_PHONE_2 = "+254 790555378"
    COMPANY_EMAIL_1 = "wendybolo84@gmail.com"
    COMPANY_EMAIL_2 = "vallarybollo84@gmail.com"
    COMPANY_URL = "https://wendy.pythonanywhere.com/"

    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "wendybolo84@gmail.com"
    MAIL_PASSWORD = "bekx dhiy umud rnst"
    MAIL_DEFAULT_SENDER = ("Wendy Pending-Order :Details", MAIL_USERNAME) 

    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    SESSION_TYPE = "filesystem"
    SESSION_FILE_DIR = os.path.join(BASE_DIR, "flask_sessions")
    SESSION_USE_SIGNER = True



