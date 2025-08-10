"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
import logging
import secrets
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
    
    # Session configuration - Generate secure random key if not provided
    if os.getenv('SECRET_KEY'):
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    else:
        # In development, use a consistent but random key
        import secrets
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(16))
        if os.getenv('FLASK_ENV') == 'production':
            app.logger.warning('Using auto-generated SECRET_KEY in production is not recommended')
    
    # JWT Configuration - Allow different key than session key for better security
    if os.getenv('JWT_SECRET_KEY'):
        app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    else:
        # Default to the app's secret key if no specific JWT key is provided
        app.config['JWT_SECRET_KEY'] = app.config['SECRET_KEY']
    
    # JWT Token expiration - default 1 day for development, configurable via environment
    jwt_expiry = os.getenv('JWT_EXPIRES_IN_SECONDS')
    if jwt_expiry:
        app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(jwt_expiry)
    else:
        # Development mode: tokens expire in 1 day (86400 seconds)
        app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400 if os.getenv('FLASK_ENV') == 'production' else False
    
    # Initialize JWT
    jwt = JWTManager(app)

    # Simple SQLite database configuration
    db_path = os.environ.get('DATABASE_URL', None)
    if db_path is None:
        # Use a relative path based on the app's instance folder
        db_path = os.path.join(app.instance_path, 'database.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
    else:
        # Use the provided DATABASE_URL environment variable
        app.config['SQLALCHEMY_DATABASE_URI'] = db_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize database
    db.init_app(app)
    
    # Check database connection on startup if not in testing mode
    if os.getenv('FLASK_ENV') != 'testing':
        with app.app_context():
            try:
                # Verify database connection works
                from sqlalchemy import text
                db.session.execute(text('SELECT 1'))
                app.logger.info(f"Successfully connected to database at {app.config['SQLALCHEMY_DATABASE_URI']}")
            except Exception as e:
                app.logger.error(f"Database connection error: {e}")
                # Log but don't fail - will likely fail on first request anyway
    
    Migrate(app, db)
    
    # Configure CORS based on environment
    cors_origins = os.getenv('CORS_ORIGINS', '*')
    CORS(app, resources={r"/*": {"origins": cors_origins.split(',')}})
    
    setup_admin(app)
    register_routes(app)

    @app.errorhandler(APIException)
    def handle_invalid_usage(error):
        return jsonify(error.to_dict()), error.status_code

    @app.route('/')
    def root():
        # Redirect the root endpoint to admin page
        from flask import redirect
        return redirect('/admin')
    
    # Keep the sitemap functionality but move it to a different endpoint
    @app.route('/api/sitemap')
    def sitemap():
        return generate_sitemap(app)

    return app

if __name__ == '__main__':
    app = create_app()
    PORT = int(os.environ.get('PORT', 3000))
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG)
