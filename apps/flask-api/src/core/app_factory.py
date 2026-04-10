"""
Application Factory - Clean Flask app creation with all extensions
"""
import logging
import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_limiting import Limiter
from flask_limiting.util import get_remote_address

from .config import ConfigFactory, AppConfig
from .extensions import db, bcrypt, cors, limiter

logger = logging.getLogger(__name__)


def create_app(config_name: str = None) -> Flask:
    """
    Application factory pattern - creates Flask app with all configurations
    
    Args:
        config_name: Environment name (development, production, testing)
        
    Returns:
        Configured Flask application instance
    """
    config = ConfigFactory.create(config_name)
    
    app = Flask(__name__)
    app.config.from_object(config)
    
    # Core configuration
    app.config["SECRET_KEY"] = config.secret_key
    app.config["SQLALCHEMY_DATABASE_URI"] = config.database.uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = config.database.track_modifications
    app.config["SQLALCHEMY_ECHO"] = config.database.echo
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_size": config.database.pool_size,
        "max_overflow": config.database.max_overflow
    }
    app.config["MAX_CONTENT_LENGTH"] = config.max_content_length
    app.config["UPLOAD_FOLDER"] = config.upload_folder
    
    # Initialize extensions
    _init_extensions(app, config)
    
    # Register blueprints
    _register_blueprints(app)
    
    # Register error handlers
    _register_error_handlers(app)
    
    # Register middleware
    _register_middleware(app, config)
    
    logger.info(f"Application created: {config.env} environment")
    return app


def _init_extensions(app: Flask, config: AppConfig):
    """Initialize Flask extensions"""
    # Database
    db.init_app(app)
    
    # Password hashing
    bcrypt.init_app(app)
    
    # CORS
    cors.init_app(app, origins=config.cors_origins)
    
    # Rate limiting
    limiter.init_app(app)
    
    # Sentry (production only)
    if config.sentry_dsn and config.env == "production":
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration
        
        sentry_sdk.init(
            dsn=config.sentry_dsn,
            integrations=[FlaskIntegration()],
            traces_sample_rate=0.1,
            environment=config.env
        )


def _register_blueprints(app: Flask):
    """Register all API blueprints with versioned prefixes"""
    # API v1 routes
    from src.api.v1.auth.routes import auth_bp
    from src.api.v1.admissions.routes import admissions_bp
    from src.api.v1.recommendations.routes import recommendations_bp
    from src.api.v1.payments.routes import payments_bp
    from src.api.v1.users.routes import users_bp
    from src.api.v1.programs.routes import programs_bp
    from src.api.v1.documents.routes import documents_bp
    from src.api.v1.notifications.routes import notifications_bp
    
    # Health check
    from src.api.health.routes import health_bp
    
    # Register with prefixes
    app.register_blueprint(health_bp, url_prefix="/api/health")
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(admissions_bp, url_prefix="/api/v1/admissions")
    app.register_blueprint(recommendations_bp, url_prefix="/api/v1/recommendations")
    app.register_blueprint(payments_bp, url_prefix="/api/v1/payments")
    app.register_blueprint(users_bp, url_prefix="/api/v1/users")
    app.register_blueprint(programs_bp, url_prefix="/api/v1/programs")
    app.register_blueprint(documents_bp, url_prefix="/api/v1/documents")
    app.register_blueprint(notifications_bp, url_prefix="/api/v1/notifications")


def _register_error_handlers(app: Flask):
    """Register global error handlers"""
    from src.core.errors import handle_validation_error, handle_not_found, handle_server_error
    
    app.register_error_handler(400, handle_validation_error)
    app.register_error_handler(404, handle_not_found)
    app.register_error_handler(405, handle_not_found)
    app.register_error_handler(500, handle_server_error)


def _register_middleware(app: Flask, config: AppConfig):
    """Register request/response middleware"""
    
    @app.before_request
    def before_request():
        """Pre-request processing"""
        pass
    
    @app.after_request
    def after_request(response):
        """Post-response processing - security headers"""
        if config.security.enable_security_headers:
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            
            if config.security.enable_hsts:
                response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # No-cache for API responses
        if request.path.startswith('/api/'):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
        
        return response
