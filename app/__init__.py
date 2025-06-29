from flask import Flask
from .routes import routes
from dotenv import load_dotenv

load_dotenv()  # This loads DATABASE_URL from your .env

def create_app():
    app = Flask(__name__)
    app.register_blueprint(routes)
    return app