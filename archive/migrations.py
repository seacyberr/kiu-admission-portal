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
        if "program_choices" not in app_cols:
            conn.execute(text(
                "ALTER TABLE admission_applications ADD COLUMN program_choices JSON NOT NULL DEFAULT '[]'"
            ))
            log.info("Added program_choices column to admission_applications table")
        if "personal_statement" not in app_cols:
            conn.execute(text(
                "ALTER TABLE admission_applications ADD COLUMN personal_statement TEXT"
            ))
            log.info("Added personal_statement column to admission_applications table")
        if "district" not in app_cols:
            conn.execute(text(
                "ALTER TABLE admission_applications ADD COLUMN district VARCHAR(100)"
            ))
            log.info("Added district column to admission_applications table")
        if "session_of_study" not in app_cols:
            conn.execute(text(
                "ALTER TABLE admission_applications ADD COLUMN session_of_study VARCHAR(20)"
            ))
            log.info("Added session_of_study column to admission_applications table")
        if "is_final_year" not in app_cols:
            conn.execute(text(
                "ALTER TABLE admission_applications ADD COLUMN is_final_year BOOLEAN DEFAULT FALSE"
            ))
            log.info("Added is_final_year column to admission_applications table")
        if "expected_graduation_year" not in app_cols:
            conn.execute(text(
                "ALTER TABLE admission_applications ADD COLUMN expected_graduation_year INTEGER"
            ))
            log.info("Added expected_graduation_year column to admission_applications table")
        if "current_year_of_study" not in app_cols:
            conn.execute(text(
                "ALTER TABLE admission_applications ADD COLUMN current_year_of_study INTEGER"
            ))
            log.info("Added current_year_of_study column to admission_applications table")
        if "student_number" not in app_cols:
            conn.execute(text(
                "ALTER TABLE admission_applications ADD COLUMN student_number VARCHAR(50)"
            ))
            log.info("Added student_number column to admission_applications table")
        if "next_of_kin_name" not in app_cols:
            conn.execute(text(
                "ALTER TABLE admission_applications ADD COLUMN next_of_kin_name VARCHAR(200)"
            ))
            log.info("Added next_of_kin_name column to admission_applications table")
        if "next_of_kin_phone" not in app_cols:
            conn.execute(text(
                "ALTER TABLE admission_applications ADD COLUMN next_of_kin_phone VARCHAR(20)"
            ))
            log.info("Added next_of_kin_phone column to admission_applications table")
        if "next_of_kin_relationship" not in app_cols:
            conn.execute(text(
                "ALTER TABLE admission_applications ADD COLUMN next_of_kin_relationship VARCHAR(50)"
            ))
            log.info("Added next_of_kin_relationship column to admission_applications table")
        if "admin_notes" not in app_cols:
            conn.execute(text(
                "ALTER TABLE admission_applications ADD COLUMN admin_notes TEXT"
            ))
            log.info("Added admin_notes column to admission_applications table")

    # ── programs table ──────────────────────────────────────────────────────
    prog_cols = {c["name"] for c in insp.get_columns("programs")}
    with db.engine.begin() as conn:
        if "fees_local" not in prog_cols:
            conn.execute(text(
                "ALTER TABLE programs ADD COLUMN fees_local INTEGER"
            ))
            log.info("Added fees_local column to programs table")
        if "fees_international" not in prog_cols:
            conn.execute(text(
                "ALTER TABLE programs ADD COLUMN fees_international INTEGER"
            ))
            log.info("Added fees_international column to programs table")
        if "functional_fees_local" not in prog_cols:
            conn.execute(text(
                "ALTER TABLE programs ADD COLUMN functional_fees_local INTEGER"
            ))
            log.info("Added functional_fees_local column to programs table")
        if "functional_fees_international" not in prog_cols:
            conn.execute(text(
                "ALTER TABLE programs ADD COLUMN functional_fees_international INTEGER"
            ))
            log.info("Added functional_fees_international column to programs table")

    # Ensure admin is always verified
    with db.engine.begin() as conn:
        conn.execute(text(
            "UPDATE users SET is_verified = TRUE WHERE role = 'admin'"
        ))

    # ── Create indexes for performance ──────────────────────────────────────
    # Note: SQLite doesn't support CREATE INDEX IF NOT EXISTS in older versions
    # MySQL/PostgreSQL do support it
    if db.engine.dialect.name in ("mysql", "postgresql"):
        indexes_to_create = [
            # Users table indexes
            ("users", "idx_users_email", "CREATE INDEX idx_users_email ON users(email)"),
            ("users", "idx_users_role", "CREATE INDEX idx_users_role ON users(role)"),
            ("users", "idx_users_is_verified", "CREATE INDEX idx_users_is_verified ON users(is_verified)"),
            ("users", "idx_users_created_at", "CREATE INDEX idx_users_created_at ON users(created_at)"),
            # Programs table indexes
            ("programs", "idx_programs_faculty", "CREATE INDEX idx_programs_faculty ON programs(faculty)"),
            ("programs", "idx_programs_level", "CREATE INDEX idx_programs_level ON programs(level)"),
            ("programs", "idx_programs_campus", "CREATE INDEX idx_programs_campus ON programs(campus)"),
            # Admission applications indexes
            ("admission_applications", "idx_app_user_id", "CREATE INDEX idx_app_user_id ON admission_applications(user_id)"),
            ("admission_applications", "idx_app_program_id", "CREATE INDEX idx_app_program_id ON admission_applications(program_id)"),
            ("admission_applications", "idx_app_status", "CREATE INDEX idx_app_status ON admission_applications(status)"),
            ("admission_applications", "idx_app_exam_level", "CREATE INDEX idx_app_exam_level ON admission_applications(exam_level)"),
            ("admission_applications", "idx_app_exam_year", "CREATE INDEX idx_app_exam_year ON admission_applications(exam_year)"),
            # Refresh tokens indexes
            ("refresh_tokens", "idx_rt_token", "CREATE INDEX idx_rt_token ON refresh_tokens(token)"),
            ("refresh_tokens", "idx_rt_user_id", "CREATE INDEX idx_rt_user_id ON refresh_tokens(user_id)"),
            # OTP codes indexes
            ("otp_codes", "idx_otp_user_id", "CREATE INDEX idx_otp_user_id ON otp_codes(user_id)"),
            ("otp_codes", "idx_otp_code", "CREATE INDEX idx_otp_code ON otp_codes(code)"),
        ]
        
        existing_indexes = {}
        for table, idx_name, create_sql in indexes_to_create:
            try:
                # Check if index already exists
                if table not in existing_indexes:
                    existing_indexes[table] = {idx['name'] for idx in insp.get_indexes(table)}
                
                if idx_name not in existing_indexes[table]:
                    conn.execute(text(create_sql))
                    log.info(f"Created index: {idx_name}")
            except Exception as e:
                log.warning(f"Could not create index {idx_name}: {e}")

    log.info("Database migrations completed")
