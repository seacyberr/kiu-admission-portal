"""Database migrations - safe to run on every startup."""
import logging
from sqlalchemy import inspect, text
from models import db

log = logging.getLogger(__name__)


def run_migrations():
    """Run database migrations for schema changes."""
    if db.engine.dialect.name == "sqlite":
        return

    insp = inspect(db.engine)

    # ── users table ────────────────────────────────────────────────────────
    user_cols = {c["name"] for c in insp.get_columns("users")}
    col_added = False
    with db.engine.begin() as conn:
        if "is_verified" not in user_cols:
            conn.execute(text(
                "ALTER TABLE users ADD COLUMN is_verified BOOLEAN NOT NULL DEFAULT FALSE"
            ))
            col_added = True
            log.info("Added is_verified column to users table")

    # Existing users (pre-OTP era) are auto-verified so they are not locked out
    if col_added:
        with db.engine.begin() as conn:
            conn.execute(text("UPDATE users SET is_verified = TRUE"))
            log.info("Auto-verified existing users")

    # ── admission_applications table ───────────────────────────────────────
    app_cols = {c["name"] for c in insp.get_columns("admission_applications")}
    with db.engine.begin() as conn:
        if "olevel_certificate_path" not in app_cols:
            conn.execute(text(
                "ALTER TABLE admission_applications ADD COLUMN olevel_certificate_path TEXT"
            ))
        if "alevel_certificate_path" not in app_cols:
            conn.execute(text(
                "ALTER TABLE admission_applications ADD COLUMN alevel_certificate_path TEXT"
            ))
        if "diploma_certificate_path" not in app_cols:
            conn.execute(text(
                "ALTER TABLE admission_applications ADD COLUMN diploma_certificate_path TEXT"
            ))
        if "hec_certificate_path" not in app_cols:
            conn.execute(text(
                "ALTER TABLE admission_applications ADD COLUMN hec_certificate_path TEXT"
            ))

    # Ensure admin is always verified
    with db.engine.begin() as conn:
        conn.execute(text(
            "UPDATE users SET is_verified = TRUE WHERE role = 'admin'"
        ))

    log.info("Database migrations completed")