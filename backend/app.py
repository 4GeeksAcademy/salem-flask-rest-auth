"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db
from routes import register_routes

def create_app():
    app = Flask(__name__)
    app.url_map.strict_slashes = False
    
    # Session configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # JWT Configuration
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-string-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Tokens never expire (for development)
    
    # Initialize JWT
    jwt = JWTManager(app)

    # Simple SQLite database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////Users/salemmohd/Documents/GitHub/salem-flask-rest-auth/instance/database.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    Migrate(app, db)
    CORS(app)
    setup_admin(app)
    register_routes(app)

    @app.errorhandler(APIException)
    def handle_invalid_usage(error):
        return jsonify(error.to_dict()), error.status_code

    @app.route('/')
    def sitemap():
        return generate_sitemap(app)

    return app

if __name__ == '__main__':
    app = create_app()
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
