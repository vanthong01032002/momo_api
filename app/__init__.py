from flask import Flask
from app.views import setup_routes

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_secret_key'
    setup_routes(app)
    return app