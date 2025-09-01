from app import create_app, Flask
from app.views import main


app = create_app()

def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config") 
    app.register_blueprint(main)  
    return app

if __name__ == "__main__":
    app.run(debug=True)

