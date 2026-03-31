"""KIU Portal API - Main application factory."""
import logging
import os
import sys
import uuid
import secrets
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

from flask import Flask, g, jsonify, request, send_from_directory
try:
    from flask_cors import CORS
except ModuleNotFoundError:
    CORS = None
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from models import db, bcrypt
from config import get_config
from migrations import run_migrations
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

    # JWT secret configuration
    jwt_secret = config.JWT_SECRET
    if not jwt_secret or jwt_secret == "change-me-to-a-random-secret-key":
        if os.environ.get("FLASK_ENV", "").lower() == "production":
            raise RuntimeError("JWT_SECRET (or SECRET_KEY) must be set in production")
        jwt_secret = secrets.token_hex(32)
        log.warning("JWT_SECRET not set — using auto-generated key")
    app.config["SECRET_KEY"] = jwt_secret

    # Create upload directories
    os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(os.path.join(config.UPLOAD_FOLDER, "certificates"), exist_ok=True)

    # Configure CORS
    cors_origins = config.CORS_ORIGINS
    if cors_origins == "*":
        origins = "*"
    else:
        origins = [o.strip() for o in cors_origins.split(",") if o.strip()]
    if CORS:
        CORS(app, resources={r"/api/*": {"origins": origins}})

    # Initialize extensions
    db.init_app(app)
    if bcrypt:
        bcrypt.init_app(app)

    # Configure rate limiting
    raw_limits = config.RATE_LIMIT_DEFAULT
    if raw_limits:
        default_limits = [x.strip() for x in raw_limits.split(",") if x.strip()]
    else:
        default_limits = ["200 per day", "50 per hour"]
    Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=default_limits,
        storage_uri=config.RATE_LIMIT_STORAGE_URI,
    )

    # Request middleware
    @app.before_request
    def _assign_request_id():
        g.request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

    @app.after_request
    def _security_headers_and_request_id(resp):
        resp.headers["X-Request-ID"] = getattr(g, "request_id", "")
        if config.ENABLE_SECURITY_HEADERS:
            resp.headers["X-Content-Type-Options"] = "nosniff"
            resp.headers["X-Frame-Options"] = "DENY"
            resp.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            resp.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
            if request.headers.get("X-Forwarded-Proto") == "https" or config.ENABLE_HSTS:
                resp.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return resp

    # Register blueprints
    from routes.auth import auth_bp
    from routes.admission import admission_bp
    from routes.career import career_bp
    from routes.opportunities import opportunities_bp
    from routes.users import users_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(admission_bp, url_prefix="/api/admission")
    app.register_blueprint(career_bp, url_prefix="/api/career")
    app.register_blueprint(opportunities_bp, url_prefix="/api/opportunities")
    app.register_blueprint(users_bp, url_prefix="/api/users")

    # Health check endpoints
    @app.route("/api/healthz")
    def healthz():
        return jsonify({"status": "ok", "service": "kiu-portal-api"}), 200

    @app.route("/api/readyz")
    def readyz():
        from sqlalchemy import text
        try:
            db.session.execute(text("SELECT 1"))
        except Exception as exc:
            log.exception("Readiness check failed: %s", exc)
            return jsonify({"status": "unavailable", "database": "error", "message": "Database unreachable"}), 503
        return jsonify({"status": "ok", "database": db.engine.dialect.name}), 200

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

    # Initialize database and seed data
    with app.app_context():
        db.create_all()
        run_migrations()
        seed_database(
            replace_programs=config.REPLACE_PROGRAMS,
            seed_enabled=config.SEED_DATABASE,
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