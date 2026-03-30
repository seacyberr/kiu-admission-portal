#!/usr/bin/env python3
"""Add program_choices column to admission_applications table."""

import os
import sys

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(__file__))

# Set environment variables before importing app
os.environ["DATABASE_URL"] = "mysql+pymysql://root@localhost:3306/kiu_admissions"
os.environ["SEED_DATABASE"] = "false"
os.environ["JWT_SECRET"] = "test-secret-key-for-development"
os.environ["FLASK_ENV"] = "development"

from app import create_app
from models import db
from sqlalchemy import text

def add_program_choices_column():
    """Add program_choices column to admission_applications table."""
    
    app = create_app()
    
    with app.app_context():
        try:
            # Check if the column already exists (MySQL syntax)
            result = db.session.execute(text("SHOW COLUMNS FROM admission_applications LIKE 'program_choices'"))
            columns = [row[0] for row in result.fetchall()]
            
            if 'program_choices' in columns:
                print("Column 'program_choices' already exists in admission_applications table.")
                return
            
            # Add the column (MySQL syntax)
            db.session.execute(text("ALTER TABLE admission_applications ADD COLUMN program_choices JSON"))
            db.session.commit()
            
            print("Successfully added 'program_choices' column to admission_applications table.")
            
        except Exception as e:
            print(f"Error adding column: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    add_program_choices_column()