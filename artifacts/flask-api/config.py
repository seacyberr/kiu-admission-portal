"""Application configuration."""
import os


def _is_production():
    return os.environ.get("FLASK_ENV", "").lower() == "production"


def _resolve_db_url():
    url = os.environ.get("DATABASE_URL", "").strip()
    # Plain mysql:// → mysql+pymysql:// for PyMySQL driver
    if url.startswith("mysql://"):
        url = "mysql+pymysql" + url[5:]
    # Explicitly disallow PostgreSQL
    if url.startswith("postgres://") or url.startswith("postgresql://"):
        raise RuntimeError(
            "PostgreSQL DATABASE_URL is not supported. Use a MySQL URL (mysql+pymysql://...)."
        )
    return url


def _default_database_url():
    return "mysql+pymysql://root@localhost:3306/kiu_admissions"


class Config:
    """Base configuration."""

    # Database
    DATABASE_URL = _resolve_db_url() or _default_database_url()
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # MySQL connection pooling
    if DATABASE_URL.startswith("sqlite"):
        SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    else:
        SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_pre_ping": True,
            "pool_recycle": 300,
            "pool_size": 20,
            "max_overflow": 10,
        }

    # JWT
    JWT_SECRET = os.environ.get("JWT_SECRET", "") or os.environ.get("SECRET_KEY", "")
    SECRET_KEY = JWT_SECRET

    # File uploads
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
    ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB

    # CORS
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")

    # Rate limiting
    RATE_LIMIT_STORAGE_URI = os.environ.get("RATE_LIMIT_STORAGE_URI", "memory://")
    RATE_LIMIT_DEFAULT = os.environ.get("RATE_LIMIT_DEFAULT", "200 per day, 50 per hour")

    # Flask-Caching
    CACHE_TYPE = os.environ.get("CACHE_TYPE", "SimpleCache")
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get("CACHE_DEFAULT_TIMEOUT", 300))

    # Email (Brevo SMTP)
    BREVO_SMTP_HOST = "smtp-relay.brevo.com"
    BREVO_SMTP_PORT = 587
    BREVO_SMTP_USER = os.environ.get("BREVO_SMTP_USER", "")
    BREVO_SMTP_KEY = os.environ.get("BREVO_SMTP_KEY", "")

    # Sentry
    SENTRY_DSN = os.environ.get("SENTRY_DSN", "")

    # Features
    ENABLE_SECURITY_HEADERS = os.environ.get("ENABLE_SECURITY_HEADERS", "true").lower() == "true"
    ENABLE_HSTS = os.environ.get("ENABLE_HSTS", "").lower() == "true"
    SEED_DATABASE = os.environ.get("SEED_DATABASE", "true").lower() not in ("0", "false", "no")
    REPLACE_PROGRAMS = os.environ.get("REPLACE_PROGRAMS", "false").lower() in ("1", "true", "yes")


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


def get_config():
    """Get configuration based on environment."""
    env = os.environ.get("FLASK_ENV", "development").lower()
    if env == "production":
        return ProductionConfig
    elif env == "testing":
        return TestingConfig
    return DevelopmentConfig