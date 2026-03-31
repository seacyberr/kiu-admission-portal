#!/usr/bin/env python3
"""Create an admin user for accessing the admin dashboard."""

import os
import sys

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(__file__))

# Create instance directory if it doesn't exist
instance_dir = os.path.join(os.path.dirname(__file__), "instance")
os.makedirs(instance_dir, exist_ok=True)

# Set environment variables before importing app
os.environ["DATABASE_URL"] = "sqlite+pysqlite:///instance/test_admissions.db"
os.environ["SEED_DATABASE"] = "false"
os.environ["JWT_SECRET"] = "test-secret-key-for-development"
os.environ["FLASK_ENV"] = "development"

from app import create_app
from models import db, User

def create_admin_user():
    """Create an admin user for accessing the admin dashboard."""
    
    app = create_app()
    
    with app.app_context():
        # Check if admin user already exists
        existing_admin = User.query.filter_by(email="admin@kiu.ac.ug").first()
        
        if existing_admin:
            print("Admin user already exists!")
            print(f"Email: {existing_admin.email}")
            print(f"Role: {existing_admin.role}")
            print(f"Verified: {existing_admin.is_verified}")
            return
        
        # Create admin user
        admin_user = User(
            email="admin@kiu.ac.ug",
            first_name="Admin",
            last_name="User",
            role="admin",
            is_verified=True
        )
        admin_user.set_password("admin123")
        
        db.session.add(admin_user)
        db.session.commit()
        
        print("✅ Admin user created successfully!")
        print(f"Email: admin@kiu.ac.ug")
        print(f"Password: admin123")
        print(f"Role: admin")
        print(f"Verified: True")
        print("\nYou can now login to the admin dashboard at /admin")

if __name__ == "__main__":
    create_admin_user()