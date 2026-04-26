#!/usr/bin/env python3
"""Create admin user for admission portal."""

import os
import sys

# Add the parent directory to the path (where app.py is located)
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Set environment variables before importing app
os.environ["DATABASE_URL"] = "mysql+pymysql://admin:adekunle%2312@localhost/kiu_admissions"
os.environ["SEED_DATABASE"] = "false"
os.environ["JWT_SECRET"] = "test-secret-key-for-development"
os.environ["FLASK_ENV"] = "development"

from app import create_app
from models import db, User

def create_admin_user():
    """Create an admin user for admission portal."""
    
    app = create_app()
    
    with app.app_context():
        # Check if test user already exists
        existing_user = User.query.filter_by(email="test@example.com").first()
        
        if existing_user:
            print("Test user already exists!")
            print(f"Email: {existing_user.email}")
            print(f"Role: {existing_user.role}")
            print(f"Verified: {existing_user.is_verified}")
            return
        
        # Create test user
        test_user = User(
            email="test@example.com",
            first_name="Test",
            last_name="Applicant",
            role="applicant",
            is_verified=True
        )
        test_user.set_password("testpass123")
        
        db.session.add(test_user)
        db.session.commit()
        
        print("✅ Test user created successfully!")
        print(f"Email: test@example.com")
        print(f"Password: testpass123")
        print(f"Role: applicant")
        print(f"Verified: True")

if __name__ == "__main__":
    create_admin_user()
