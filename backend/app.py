import os
import secrets

from dotenv import load_dotenv
from flasgger import Swagger
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_security.core import Security
from flask_security.datastore import SQLAlchemyUserDatastore
from models import Role, User, db
from routes import register_routes

# Load environment variables from .env file before anything else
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


def create_app():
    """Create and configure the Flask application instance."""
    flask_app = Flask(__name__)
    flask_app.url_map.strict_slashes = False

    @flask_app.route("/")
    def root():
        return """
        <html>
        <head><title>Star Wars Flask REST API</title></head>
        <body style="font-family: sans-serif; max-width: 600px; margin: 40px auto;">
            <h1>🚀 Star Wars Flask REST API</h1>
            <ul style="font-size: 1.2em;">
                <li><a href="/api/docs">API Docs (Swagger UI)</a></li>
                <li><a href="/admin">Admin Panel</a> (login required)</li>
                <li><a href="http://localhost:3001">Frontend App</a></li>
            </ul>
            <p style="color: #888;">For setup and usage, see the <a href="https://github.com/4GeeksAcademy/salem-flask-rest-auth">README</a>.</p>
        </body>
        </html>
        """

    # Swagger/OpenAPI config
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "Star Wars REST API",
            "description": "API for Star Wars data with JWT and admin.",
            "version": "1.0.0",
        },
        "basePath": "/",
        "schemes": ["http"],
    }
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec_1",
                "route": "/api/docs/apispec_1.json",
                "rule_filter": lambda rule: True,  # all endpoints
                "model_filter": lambda tag: True,  # all models
            }
        ],
        "swagger_ui": True,
        "specs_route": "/api/docs/",
    }
    Swagger(flask_app, template=swagger_template, config=swagger_config)

    from admin import setup_admin

    setup_admin(flask_app)

    # Setup Flask-Security
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    Security(flask_app, user_datastore)

    # Register all API routes (required for Swagger docs)
    register_routes(flask_app)

    # Require secrets from environment, no fallbacks
    secret_key = os.getenv("SECRET_KEY")
    jwt_secret = os.getenv("JWT_SECRET_KEY")
    if not secret_key or not jwt_secret:
        raise RuntimeError(
            "SECRET_KEY and JWT_SECRET_KEY must be set as environment variables in production."
        )
    flask_app.config["SECRET_KEY"] = secret_key
    flask_app.config["JWT_SECRET_KEY"] = jwt_secret
    jwt_expiry = os.getenv("JWT_EXPIRES_IN_SECONDS")
    flask_app.config["JWT_ACCESS_TOKEN_EXPIRES"] = (
        int(jwt_expiry) if jwt_expiry else 86400
    )
    JWTManager(flask_app)

    db_path = os.environ.get("DATABASE_URL") or os.path.join(
        flask_app.instance_path, "database.db"
    )
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = (
        db_path if db_path.startswith("postgres://") else f"sqlite:///{db_path}"
    )
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(flask_app)
    if os.getenv("FLASK_ENV") != "testing":
        with flask_app.app_context():
            try:
                from sqlalchemy import text

                db.session.execute(text("SELECT 1"))
            except Exception as e:
                flask_app.logger.error("Database connection error: %s", str(e))
    Migrate(flask_app, db)
    cors_origins = os.getenv("CORS_ORIGINS")
    if not cors_origins:
        raise RuntimeError(
            "CORS_ORIGINS must be set to a comma-separated list of trusted domains in production."
        )
    CORS(flask_app, resources={r"/*": {"origins": cors_origins.split(",")}})

    # Context7 best practice: Return JSON for all API errors
    from flask import jsonify, request
    from werkzeug.exceptions import HTTPException

    @flask_app.errorhandler(HTTPException)
    def handle_api_exception(e):
        if request.path.startswith("/api/"):
            response = e.get_response()
            response.data = jsonify(
                {
                    "code": e.code,
                    "name": e.name,
                    "description": e.description,
                }
            ).data
            response.content_type = "application/json"
            return response
        return e

    return flask_app


if __name__ == "__main__":
    application = create_app()
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    application.run(host="0.0.0.0", port=3000, debug=debug_mode)
