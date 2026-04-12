#!/usr/bin/env python3
"""Migration script to add missing fee columns to programs table"""

import sys
import os

# Activate venv if not already active
venv_path = "/home/sea/venv"
if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
    pass  # Already in venv
else:
    activate_script = os.path.join(venv_path, "bin", "activate_this.py")
    if os.path.exists(activate_script):
        exec(open(activate_script).read(), {'__file__': activate_script})

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db
from sqlalchemy import text

def migrate():
    app = create_app()
    with app.app_context():
        # Check if columns exist
        try:
            db.session.execute(text("SELECT fees_local_per_semester FROM programs LIMIT 1"))
            print("✓ fees_local_per_semester column already exists")
        except Exception:
            db.session.execute(text("""
                ALTER TABLE programs 
                ADD COLUMN fees_local_per_semester DECIMAL(10, 2) DEFAULT 0
            """))
            print("✓ Added fees_local_per_semester column")

        try:
            db.session.execute(text("SELECT fees_international_per_semester FROM programs LIMIT 1"))
            print("✓ fees_international_per_semester column already exists")
        except Exception:
            db.session.execute(text("""
                ALTER TABLE programs 
                ADD COLUMN fees_international_per_semester DECIMAL(10, 2) DEFAULT 0
            """))
            print("✓ Added fees_international_per_semester column")

        try:
            db.session.execute(text("SELECT functional_fees_local FROM programs LIMIT 1"))
            print("✓ functional_fees_local column already exists")
        except Exception:
            db.session.execute(text("""
                ALTER TABLE programs 
                ADD COLUMN functional_fees_local DECIMAL(10, 2) DEFAULT 0
            """))
            print("✓ Added functional_fees_local column")

        try:
            db.session.execute(text("SELECT functional_fees_international FROM programs LIMIT 1"))
            print("✓ functional_fees_international column already exists")
        except Exception:
            db.session.execute(text("""
                ALTER TABLE programs 
                ADD COLUMN functional_fees_international DECIMAL(10, 2) DEFAULT 0
            """))
            print("✓ Added functional_fees_international column")

        db.session.commit()
        print("\n✅ Migration completed successfully!")

if __name__ == "__main__":
    migrate()
