#!/usr/bin/env python3
"""Reset admin password without deleting the database."""

import os
import sys
import secrets
import string

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(__file__))

# Set environment variables before importing app
os.environ["DATABASE_URL"] = "mysql+pymysql://admin:adekunle%2312@localhost/kiu_admissions"
os.environ["SEED_DATABASE"] = "false"
os.environ["JWT_SECRET"] = "f131fc8547c2e22a729336ced59c89b98b57ae209d79a6e0ae744a2f1cd6c657"
os.environ["FLASK_ENV"] = "development"

from app import create_app
from models import db, User

def reset_admin_password():
    """Reset the admin password without deleting the database."""
    
    app = create_app()
    
    with app.app_context():
        # Find the admin user
        admin = User.query.filter_by(role="admin").first()
        
        if not admin:
            print("❌ No admin user found in the database!")
            print("Run the server with SEED_DATABASE=true to create an admin user.")
            return
        
        # Generate a new password
        new_password = ''.join(secrets.choice(string.ascii_letters + string.digits + "!@#$%") for _ in range(12))
        
        # Update the password
        admin.set_password(new_password)
        db.session.commit()
        
        print("=" * 60)
        print("  KIU PORTAL — ADMIN PASSWORD RESET")
        print("=" * 60)
        print(f"  Admin Login")
        print(f"  Email    : {admin.email}")
        print(f"  Password : {new_password}")
        print("=" * 60)
        print("\n✅ Admin password has been reset successfully!")
        print("You can now login to the admin dashboard at /admin")

if __name__ == "__main__":
    reset_admin_password()