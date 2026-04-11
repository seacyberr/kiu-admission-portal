#!/usr/bin/env python3
"""
Reset database for fresh testing
Clears all accounts, applications, and user data
Keeps programs and system tables intact
"""

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
from models import db, User, AdmissionApplication, OtpCode, AuditLog, RefreshToken
from sqlalchemy import text

def reset_database():
    app = create_app()
    
    with app.app_context():
        print("🧹 Clearing all user data for fresh testing...\n")
        
        # Delete in order to avoid foreign key constraints
        tables_to_clear = [
            ("admission_applications", "Applications"),
            ("otp_codes", "OTP codes"),
            ("refresh_tokens", "Refresh tokens"),
            ("audit_logs", "Audit logs"),
            ("users", "User accounts"),
        ]
        
        for table, description in tables_to_clear:
            try:
                result = db.session.execute(text(f"DELETE FROM {table}"))
                count = result.rowcount if hasattr(result, 'rowcount') else 'unknown'
                print(f"✅ Cleared {description}: {count} rows deleted")
            except Exception as e:
                print(f"⚠️  {description}: {str(e)}")
        
        # Reset auto-increment counters for MySQL
        print("\n🔄 Resetting auto-increment counters...")
        tables_with_ai = ['users', 'admission_applications', 'otp_codes', 'audit_logs']
        for table in tables_with_ai:
            try:
                db.session.execute(text(f"ALTER TABLE {table} AUTO_INCREMENT = 1"))
                print(f"✅ Reset {table} auto-increment")
            except Exception as e:
                print(f"⚠️  {table} AI reset: {str(e)}")
        
        db.session.commit()
        
        # Verify
        print("\n📊 Verification:")
        for table, description in tables_to_clear:
            try:
                result = db.session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"   {description}: {count} rows remaining")
            except Exception as e:
                print(f"   {description}: Error - {str(e)}")
        
        print("\n✅ Database reset complete!")
        print("\n📝 Note: Programs and system tables preserved")

if __name__ == "__main__":
    confirm = input("⚠️  WARNING: This will DELETE ALL user data!\nType 'RESET' to confirm: ")
    if confirm == "RESET":
        reset_database()
    else:
        print("❌ Reset cancelled")
        sys.exit(1)
