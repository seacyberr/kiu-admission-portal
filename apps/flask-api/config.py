"""Application configuration."""

import os


def _is_production() -> bool:
    return os.environ.get("FLASK_ENV", "").lower() == "production"


def _resolve_db_url() -> str:
    url = os.environ.get("DATABASE_URL", "").strip()

    # Normalise mysql:// → mysql+pymysql:// for PyMySQL driver
    if url.startswith("mysql://"):
        url = "mysql+pymysql" + url[5:]

    # Explicitly disallow PostgreSQL
    if url.startswith("postgres://") or url.startswith("postgresql://"):
        raise RuntimeError(
            "PostgreSQL DATABASE_URL is not supported. "
            "Use a MySQL URL (mysql+pymysql://...)."
        )

    return url


def _default_database_url() -> str:
    return "mysql+pymysql://root@localhost:3306/kiu_admissions"


class Config:
    """Base configuration."""

    # ------------------------------------------------------------------ #
    # Database
    # ------------------------------------------------------------------ #
    DATABASE_URL: str = _resolve_db_url() or _default_database_url()
    SQLALCHEMY_DATABASE_URI: str = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @classmethod
    def get_engine_options(cls, db_url: str) -> dict:
        """Resolve engine options dynamically based on actual database URL."""
        if db_url.startswith("sqlite"):
            return {"pool_pre_ping": True}
        return {
            "pool_pre_ping": True,
            "pool_recycle": 300,
            "pool_size": 20,
            "max_overflow": 10,
        }

    SQLALCHEMY_ENGINE_OPTIONS: dict = get_engine_options.__func__(object, DATABASE_URL)

    # ------------------------------------------------------------------ #
    # Secrets
    # FIX: previously fell through to "" if both env vars were unset, which
    # meant JWTs were signed with an empty secret — completely insecure.
    # Now raises a hard RuntimeError at startup if no secret is configured.
    # ------------------------------------------------------------------ #
    JWT_SECRET: str = (
        os.environ.get("JWT_SECRET", "")
        or os.environ.get("SECRET_KEY", "")
    )
    SECRET_KEY: str = JWT_SECRET

    # ------------------------------------------------------------------ #
    # File uploads
    # ------------------------------------------------------------------ #
    UPLOAD_FOLDER: str = os.path.join(os.path.dirname(__file__), "uploads")
    ALLOWED_EXTENSIONS: set = {"pdf", "jpg", "jpeg", "png"}
    MAX_CONTENT_LENGTH: int = 5 * 1024 * 1024  # 5 MB

    # ------------------------------------------------------------------ #
    # CORS
    # FIX: wildcard "*" is incompatible with credentials: 'include'.
    # Browsers silently block cookies when origin is "*". Default to
    # localhost:5173 (Vite dev server) so auth works out of the box locally.
    # In production, set CORS_ORIGINS to your actual domain.
    # ------------------------------------------------------------------ #
    CORS_ORIGINS: str = os.environ.get(
        "CORS_ORIGINS", "http://localhost:5173"
    )

    # ------------------------------------------------------------------ #
    # Rate limiting
    # ------------------------------------------------------------------ #
    RATE_LIMIT_STORAGE_URI: str = os.environ.get(
        "RATE_LIMIT_STORAGE_URI", "memory://"
    )
    RATE_LIMIT_DEFAULT: str = os.environ.get(
        "RATE_LIMIT_DEFAULT", "200 per day, 50 per hour"
    )

    # ------------------------------------------------------------------ #
    # Caching (SimpleCache in dev, RedisCache in prod)
    # ------------------------------------------------------------------ #
    CACHE_TYPE: str = os.environ.get("CACHE_TYPE", "SimpleCache")
    CACHE_DEFAULT_TIMEOUT: int = int(
        os.environ.get("CACHE_DEFAULT_TIMEOUT", 300)
    )
    CACHE_REDIS_URL: str = os.environ.get("CACHE_REDIS_URL", "")

    # ------------------------------------------------------------------ #
    # Email (Brevo SMTP)
    # ------------------------------------------------------------------ #
    BREVO_SMTP_HOST = "smtp-relay.brevo.com"
    BREVO_SMTP_PORT = 587
    BREVO_SMTP_USER: str = os.environ.get("BREVO_SMTP_USER", "")
    BREVO_SMTP_KEY: str = os.environ.get("BREVO_SMTP_KEY", "")

    # ------------------------------------------------------------------ #
    # Monitoring
    # ------------------------------------------------------------------ #
    SENTRY_DSN: str = os.environ.get("SENTRY_DSN", "")

    # ------------------------------------------------------------------ #
    # Feature flags
    # ------------------------------------------------------------------ #
    ENABLE_SECURITY_HEADERS: bool = (
        os.environ.get("ENABLE_SECURITY_HEADERS", "true").lower() == "true"
    )
    ENABLE_HSTS: bool = (
        os.environ.get("ENABLE_HSTS", "").lower() == "true"
    )

    # FIX: changed default from "true" to "false".
    # Previously, seed data ran on every startup unless explicitly disabled.
    # This is a footgun in production — it can overwrite or duplicate real data.
    # Now opt-in: set SEED_DATABASE=true to seed.
    SEED_DATABASE: bool = (
        os.environ.get("SEED_DATABASE", "false").lower()
        in ("1", "true", "yes")
    )

    REPLACE_PROGRAMS: bool = (
        os.environ.get("REPLACE_PROGRAMS", "false").lower()
        in ("1", "true", "yes")
    )


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True

    # In dev, seed by default so fresh installs have demo data.
    # This overrides the base class safe default intentionally.
    SEED_DATABASE: bool = (
        os.environ.get("SEED_DATABASE", "true").lower()
        in ("1", "true", "yes")
    )


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    # Never seed in tests — use fixtures instead
    SEED_DATABASE = False
    # Allow empty JWT secret in unit tests
    JWT_SECRET = os.environ.get("JWT_SECRET", "test-secret-key-not-for-production")
    SECRET_KEY = JWT_SECRET


def get_config():
    """Return the configuration class for the current environment."""
    env = os.environ.get("FLASK_ENV", "development").lower()
    configs = {
        "production": ProductionConfig,
        "testing": TestingConfig,
        "development": DevelopmentConfig,
    }
    return configs.get(env, DevelopmentConfig)


def validate_config(app) -> None:
    """
    Hard startup validation — called from the Flask app factory.
    Raises RuntimeError for any configuration that would cause silent failures
    at runtime (e.g. empty JWT secret, wildcard CORS with credentials).
    """
    if app.config.get("TESTING"):
        return  # Relax checks in unit tests

    # JWT secret must be set
    if not app.config.get("JWT_SECRET") or not app.config.get("SECRET_KEY"):
        raise RuntimeError(
            "JWT_SECRET (or SECRET_KEY) environment variable must be set. "
            "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
        )

    # Wildcard CORS is incompatible with credentials
    if app.config.get("CORS_ORIGINS") == "*" and not app.debug:
        raise RuntimeError(
            "CORS_ORIGINS='*' is incompatible with httpOnly cookie auth. "
            "Set CORS_ORIGINS to your actual frontend origin, e.g. https://yourdomain.com"
        )