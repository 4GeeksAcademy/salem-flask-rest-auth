import os
import secrets
from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models import db
from routes import register_routes


def create_app():

    """Create and configure the Flask application instance."""
    flask_app = Flask(__name__)
    flask_app.url_map.strict_slashes = False

    from admin import setup_admin
    setup_admin(flask_app)

    # Require secrets from environment, no fallbacks
    secret_key = os.getenv('SECRET_KEY')
    jwt_secret = os.getenv('JWT_SECRET_KEY')
    if not secret_key or not jwt_secret:
        raise RuntimeError('SECRET_KEY and JWT_SECRET_KEY must be set as environment variables in production.')
    flask_app.config['SECRET_KEY'] = secret_key
    flask_app.config['JWT_SECRET_KEY'] = jwt_secret
    jwt_expiry = os.getenv('JWT_EXPIRES_IN_SECONDS')
    flask_app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(jwt_expiry) if jwt_expiry else 86400
    JWTManager(flask_app)

    db_path = os.environ.get('DATABASE_URL') or os.path.join(flask_app.instance_path, 'database.db')
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = db_path if db_path.startswith('postgres://') else f"sqlite:///{db_path}"
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(flask_app)
    if os.getenv('FLASK_ENV') != 'testing':
        with flask_app.app_context():
            try:
                from sqlalchemy import text
                db.session.execute(text('SELECT 1'))
            except Exception as e:
                flask_app.logger.error("Database connection error: %s", str(e))
    Migrate(flask_app, db)
    cors_origins = os.getenv('CORS_ORIGINS')
    if not cors_origins:
        raise RuntimeError('CORS_ORIGINS must be set to a comma-separated list of trusted domains in production.')
    CORS(flask_app, resources={r"/*": {"origins": cors_origins.split(',')}})
    register_routes(flask_app)

    return flask_app

if __name__ == '__main__':
    application = create_app()
    PORT = int(os.environ.get('PORT', 3000))
    # Set debug mode based on environment variable (default: False)
    debug_mode = os.environ.get('FLASK_DEBUG', '0') == '1'
    application.run(host='0.0.0.0', port=PORT, debug=debug_mode)
