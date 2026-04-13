"""KIU Portal API - Main application factory."""
import logging
import os
import sys
import uuid
from werkzeug.middleware.proxy_fix import ProxyFix

# Sentry for error monitoring
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

# Structured logging
import structlog

sys.path.insert(0, os.path.dirname(__file__))

log = logging.getLogger("kiu.portal")

# Load .env file if present
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
except ImportError:
    pass

from flask import Flask, g, jsonify, request, send_from_directory, make_response
try:
    from flask_cors import CORS
except ModuleNotFoundError:
    CORS = None
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flask_jwt_extended import JWTManager
from models import db, bcrypt
from config import get_config
from seed import seed_database


def _configure_logging():
    """Configure application logging."""
    level_name = os.environ.get("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    root = logging.getLogger()
    if not root.handlers:
        logging.basicConfig(
            level=level,
            format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    root.setLevel(level)
    log.setLevel(level)

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.BoundLogger,
        cache_logger_on_first_use=True,
    )


def create_app():
    """Create and configure the Flask application."""
    _configure_logging()

    # Initialize Sentry for error monitoring
    sentry_dsn = os.environ.get("SENTRY_DSN", "")
    if sentry_dsn:
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[FlaskIntegration()],
            traces_sample_rate=0.1,
            environment=os.environ.get("FLASK_ENV", "development"),
        )

    config = get_config()

    app = Flask(__name__)
    app.config.from_object(config)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)

    # JWT secret configuration - ALWAYS require explicit configuration
    jwt_secret = config.JWT_SECRET
    if not jwt_secret or jwt_secret == "change-me-to-a-random-secret-key":
        # Always require explicit JWT secret - no auto-generation
        raise RuntimeError(
            "JWT_SECRET (or SECRET_KEY) environment variable must be set. "
            "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
        )
    app.config["SECRET_KEY"] = jwt_secret
    
    # Flask-JWT-Extended configuration
    app.config["JWT_SECRET_KEY"] = jwt_secret
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 8 * 3600  # 8 hours
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = 7 * 24 * 3600  # 7 days
    app.config["JWT_TOKEN_LOCATION"] = ["cookies", "headers"]
    app.config["JWT_COOKIE_SECURE"] = os.environ.get("FLASK_ENV", "").lower() == "production"
    app.config["JWT_COOKIE_SAMESITE"] = "Lax"
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False  # Disable for simplicity, enable in production
    app.config["JWT_ERROR_MESSAGE_KEY"] = "error"
    
    jwt = JWTManager(app)
    
    # JWT token blocklist loader (for logout)
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        from utils.caching import cache_manager
        jti = jwt_payload.get("jti")
        if jti:
            return cache_manager.get(f"jwt_blacklist:{jti}", False)
        return False

    # Create upload directories
    os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(os.path.join(config.UPLOAD_FOLDER, "certificates"), exist_ok=True)

    # Configure CORS using manual after_request handler
    cors_origins = config.CORS_ORIGINS
    if cors_origins == "*":
        origins = ["*"]
    else:
        origins = [o.strip() for o in cors_origins.split(",") if o.strip()]
    
    @app.after_request
    def after_request_cors(resp):
        # If resp is None, create a new response
        if resp is None:
            resp = make_response('')
            
        # Ensure resp is a valid response object with headers
        if not hasattr(resp, 'headers'):
            return resp
            
        if request.path.startswith('/api/'):
            # Get the origin from the request or use the first allowed origin
            req_origin = request.headers.get('Origin')
            if req_origin and req_origin in origins:
                resp.headers['Access-Control-Allow-Origin'] = req_origin
            elif '*' in origins:
                resp.headers['Access-Control-Allow-Origin'] = '*'
            elif origins:
                resp.headers['Access-Control-Allow-Origin'] = origins[0]
            else:
                resp.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
                
            resp.headers['Access-Control-Allow-Credentials'] = 'true'
            resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
            resp.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Request-ID, Accept'
            
        return resp
    
    # Handle OPTIONS requests for CORS preflight
    @app.route('/api/<path:path>', methods=['OPTIONS'])
    def handle_options(path):
        return '', 204

    # Initialize extensions
    db.init_app(app)
    if bcrypt:
        bcrypt.init_app(app)
    
    # Initialize Flask-Caching
    cache = Cache(app)

    # Configure advanced rate limiting
    from utils.rate_limiting import apply_rate_limits
    apply_rate_limits(app)
    
    # Configure caching
    from utils.caching import CacheManager, CacheMiddleware, warm_cache
    cache_manager = CacheManager()
    cache_middleware = CacheMiddleware(app)
    cache_middleware.init_app(app)
    
    # Warm up cache on startup
    try:
        warm_cache()
        log.info("Cache warm-up completed successfully")
    except Exception as e:
        log.warning(f"Cache warm-up failed: {e}")

    # Request middleware
    @app.before_request
    def _assign_request_id():
        g.request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

    @app.after_request
    def _security_headers_and_request_id(resp):
        if resp is not None:
            resp.headers["X-Request-ID"] = getattr(g, "request_id", "")
            if config.ENABLE_SECURITY_HEADERS:
                resp.headers["X-Content-Type-Options"] = "nosniff"
                resp.headers["X-Frame-Options"] = "DENY"
                resp.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
                resp.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
                if request.headers.get("X-Forwarded-Proto") == "https" or config.ENABLE_HSTS:
                    resp.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return resp

    # Global API cache-control - prevent browser caching of all API responses
    @app.after_request
    def _api_cache_control(resp):
        if resp is not None and request.path.startswith('/api/'):
            # Don't override if already set by specific endpoint
            if 'Cache-Control' not in resp.headers:
                resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
                resp.headers['Pragma'] = 'no-cache'
                resp.headers['Expires'] = '0'
        return resp

    # Register blueprints
    from routes.auth import auth_bp
    from routes.admission import admission_bp
    from routes.career import career_bp
    from routes.opportunities import opportunities_bp
    from routes.users import users_bp
    from routes.docs import docs_bp
    from routes.notifications import notifications_bp
    from routes.nche_recommendations import recommendations_bp
    from routes.certificate_verification import certificate_verification_bp
    from routes.reports import reports_bp
    from routes.audit import audit_bp
    from routes.recommendations_v2 import recommendations_v2_bp
    from routes.admin import admin_bp
    from routes.finalist import finalist_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(finalist_bp, url_prefix="/api/finalist")
    app.register_blueprint(admission_bp, url_prefix="/api/admission")
    app.register_blueprint(career_bp, url_prefix="/api/career")
    app.register_blueprint(opportunities_bp, url_prefix="/api/opportunities")
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(notifications_bp, url_prefix="/api/notifications")
    app.register_blueprint(docs_bp, url_prefix="/api/docs")
    app.register_blueprint(certificate_verification_bp, url_prefix="/api/certificate-verification")
    app.register_blueprint(reports_bp, url_prefix="/api/reports")
    app.register_blueprint(audit_bp, url_prefix="/api/audit")

    # Unified Recommendations API v2 (handles both old and new curriculum)
    app.register_blueprint(recommendations_v2_bp, url_prefix="/api/v2/recommendations")

    # Legacy NCHE-based recommendations (deprecated, kept for backward compatibility)
    app.register_blueprint(recommendations_bp, url_prefix="/api")

    # Initialize Prometheus metrics
    from metrics import init_metrics
    init_metrics(app)

    # Health check endpoints
    @app.route("/api/healthz")
    @app.route("/api/health")
    def healthz():
        return jsonify({"status": "ok", "service": "kiu-portal-api"}), 200

    @app.route("/api/readyz")
    def readyz():
        from sqlalchemy import text
        from utils.caching import cache_manager
        
        health_data = {"status": "ok"}
        
        # Check database
        try:
            db.session.execute(text("SELECT 1"))
            health_data["database"] = db.engine.dialect.name
        except Exception as exc:
            log.exception("Database check failed: %s", exc)
            return jsonify({
                "status": "unavailable",
                "database": "error",
                "message": "Database unreachable"
            }), 503
        
        # Check cache
        cache_health = cache_manager.health_check()
        health_data["cache"] = cache_health
        
        return jsonify(health_data), 200

    @app.route("/api/cache/stats")
    def cache_stats():
        """Get cache statistics (admin only)"""
        from utils.caching import cache_manager
        from flask_jwt_extended import jwt_required, get_jwt_identity
        
        # Simple auth check - verify JWT and role
        try:
            jwt_required()(lambda: None)()  # Apply jwt_required
            user_id = get_jwt_identity()
            from models import User
            user = User.query.get(user_id)
            if not user or user.role != "admin":
                return jsonify({"error": "Forbidden", "message": "Admin access required"}), 403
        except:
            return jsonify({"error": "Unauthorized", "message": "Valid admin token required"}), 401
        
        stats = cache_manager.get_stats()
        return jsonify({
            "status": "success",
            "data": stats
        }), 200

    # Certificate file serving
    @app.route("/api/uploads/certificates/<path:filename>")
    def serve_certificate(filename):
        from routes.auth import get_current_user
        from models import AdmissionApplication
        from sqlalchemy import or_

        user, error = get_current_user()
        if error:
            return jsonify({"error": "Unauthorized", "message": error}), 401

        path_fragment = f"/api/uploads/certificates/{filename}"
        application = (
            AdmissionApplication.query
            .filter(or_(
                AdmissionApplication.olevel_certificate_path == path_fragment,
                AdmissionApplication.alevel_certificate_path == path_fragment,
                AdmissionApplication.diploma_certificate_path == path_fragment,
                AdmissionApplication.hec_certificate_path == path_fragment,
            ))
            .first()
        )
        if not application:
            return jsonify({"error": "Not found", "message": "Certificate not found"}), 404
        if user.role != "admin" and application.user_id != user.id:
            return jsonify({"error": "Forbidden", "message": "Access denied"}), 403

        return send_from_directory(os.path.join(config.UPLOAD_FOLDER, "certificates"), filename)

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found", "message": str(e)}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method not allowed", "message": str(e)}), 405

    @app.errorhandler(413)
    def file_too_large(e):
        return jsonify({"error": "File too large", "message": "Max file size is 5MB"}), 413

    @app.errorhandler(500)
    def internal_error(e):
        log.exception("Unhandled server error: %s", e)
        if os.environ.get("FLASK_ENV", "").lower() == "production":
            return jsonify({"error": "Internal server error", "message": "An unexpected error occurred"}), 500
        return jsonify({"error": "Internal server error", "message": str(e)}), 500

    # Database initialization is handled via CLI commands (alembic upgrade head)
    # Do NOT auto-create tables or run migrations on startup
    # This prevents accidental schema changes in production
    with app.app_context():
        # Only seed data if explicitly enabled (for initial setup only)
        if config.SEED_DATABASE:
            seed_database(
                replace_programs=config.REPLACE_PROGRAMS,
                seed_enabled=True,
            )

    return app


if __name__ == "__main__":
    application = create_app()
    port = int(os.environ.get("PORT", 5001))
    print(f"\n{'='*60}")
    print(f"  KIU Portal API Server")
    print(f"  Port     : {port}")
    print(f"{'='*60}\n", flush=True)
    application.run(host="0.0.0.0", port=port, debug=False)