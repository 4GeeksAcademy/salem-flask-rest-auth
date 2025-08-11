import os
import logging
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_restx import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_security.core import Security
from flask_security.datastore import SQLAlchemyUserDatastore
from werkzeug.exceptions import HTTPException

# Extensions: instantiate at module level, init in factory
from models import Role, User, db

# Load environment variables once at module level
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# Instantiate extensions (no app bound yet)
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
security = Security()


def validate_required_env_vars():
    """Validate that all required environment variables are set."""
    required_vars = [
        "SECRET_KEY",
        "JWT_SECRET_KEY", 
        "SECURITY_PASSWORD_SALT",
        "CORS_ORIGINS"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )


def create_app():
    """Create and configure the Flask application instance."""
    
    # Validate environment variables first
    validate_required_env_vars()
    
    app = Flask(__name__)
    app.url_map.strict_slashes = False
    
    # Configure logging
    if not app.debug:
        logging.basicConfig(level=logging.INFO)
    
    # Load config from environment
    app.config.update({
        "SECRET_KEY": os.getenv("SECRET_KEY"),
        "JWT_SECRET_KEY": os.getenv("JWT_SECRET_KEY"),
        "SECURITY_PASSWORD_SALT": os.getenv("SECURITY_PASSWORD_SALT"),
        "SECURITY_PASSWORD_HASH": "bcrypt",  # Avoid argon2 dependency
        "JWT_ACCESS_TOKEN_EXPIRES": int(os.getenv("JWT_EXPIRES_IN_SECONDS", 86400)),
        "SQLALCHEMY_TRACK_MODIFICATIONS": False
    })

    # Database configuration - more robust path handling
    db_dir = Path(__file__).parent / "instance"
    db_dir.mkdir(exist_ok=True)  # Ensure instance directory exists
    db_path = db_dir / "database.db"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path.absolute()}"

    # CORS configuration with validation
    cors_origins = os.getenv("CORS_ORIGINS", "").strip()
    if not cors_origins:
        app.logger.warning("CORS_ORIGINS not set - using default localhost origins")
        cors_origins = "http://localhost:3000,http://localhost:3001"
    
    origins_list = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/*": {"origins": origins_list}})

    # Initialize Flask-RESTX API and register namespaces
    try:
        from routes import people_ns, planets_ns, vehicles_ns, favorites_ns
        api = Api(
            app, 
            doc='/swagger/',
            title='Star Wars API',
            version='1.0',
            description='A Star Wars themed REST API'
        )
        api.add_namespace(people_ns)
        api.add_namespace(planets_ns)
        api.add_namespace(vehicles_ns)
        api.add_namespace(favorites_ns)
    except ImportError as e:
        app.logger.error(f"Failed to import routes: {e}")
        raise

    # Setup Flask-Security
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security.init_app(app, user_datastore)

    # Register admin interface
    try:
        from admin import init_admin
        init_admin(app)
    except ImportError as e:
        app.logger.warning(f"Admin interface not available: {e}")

    # Register routes and error handlers
    register_routes(app)
    register_error_handlers(app)

    # Database connection test (not in testing environment)
    if os.getenv("FLASK_ENV") != "testing":
        test_database_connection(app)

    return app


def register_routes(app):
    """Register application routes."""
    
    @app.route("/", endpoint="root_page")
    def root():
        return """
        <html>
        <head>
            <title>Star Wars Flask REST API</title>
            <style>
                body { font-family: sans-serif; max-width: 600px; margin: 40px auto; }
                .link-list { font-size: 1.2em; }
                .footer { color: #888; margin-top: 2em; }
            </style>
        </head>
        <body>
            <h1>🚀 Star Wars Flask REST API</h1>
            <ul class="link-list">
                <li><a href="/swagger/">API Documentation (Swagger UI)</a></li>
                <li><a href="/admin/">Admin Panel</a> (login required)</li>
                <li><a href="http://localhost:3001">Frontend App</a></li>
            </ul>
            <p class="footer">
                For setup and usage instructions, see the 
                <a href="https://github.com/4GeeksAcademy/salem-flask-rest-auth">README</a>.
            </p>
        </body>
        </html>
        """

    @app.route("/health")
    def health_check():
        """Simple health check endpoint."""
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat()
        })


def register_error_handlers(app):
    """Register application error handlers."""
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        """Handle HTTP exceptions with JSON responses for API routes."""
        if request.path.startswith("/api/") or request.path.startswith("/swagger/"):
            response = e.get_response()
            response.data = jsonify({
                "code": e.code,
                "name": e.name,
                "description": e.description,
                "path": request.path
            }).data
            response.content_type = "application/json"
            return response
        return e

    @app.errorhandler(Exception)
    def handle_unhandled_exception(e):
        """Log and handle all unhandled exceptions."""
        app.logger.error("Unhandled Exception", exc_info=e)
        
        # Return JSON for API routes, HTML for others
        if request.path.startswith("/api/") or request.path.startswith("/swagger/"):
            return jsonify({
                "error": "Internal server error",
                "message": str(e) if app.debug else "An unexpected error occurred"
            }), 500
        
        # For non-API routes, you might want to render an error template
        return f"<h1>500 Internal Server Error</h1><p>An unexpected error occurred.</p>", 500


def test_database_connection(app):
    """Test database connection on startup."""
    with app.app_context():
        try:
            from sqlalchemy import text
            db.session.execute(text("SELECT 1"))
            app.logger.info("Database connection successful")
        except Exception as e:
            app.logger.error("Database connection error: %s", str(e))
            raise


if __name__ == "__main__":
    from datetime import datetime
    
    application = create_app()
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    port = int(os.environ.get("PORT", 3000))
    
    application.logger.info(f"Starting Flask application on port {port}")
    application.run(
        host="0.0.0.0", 
        port=port, 
        debug=debug_mode, 
        use_reloader=False
    )