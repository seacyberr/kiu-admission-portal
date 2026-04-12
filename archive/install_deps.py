#!/usr/bin/env python3
"""
Dependency Installation Script for KIU Admission Portal API
Checks and installs all required dependencies
"""

import subprocess
import sys

# List of all required packages with their PyPI names
REQUIRED_PACKAGES = [
    # Core Flask
    ("flask", "Flask>=3.1.0,<4.0.0"),
    ("flask_sqlalchemy", "Flask-SQLAlchemy>=3.1.0,<4.0.0"),
    ("flask_cors", "Flask-Cors>=6.0.0,<7.0.0"),
    ("flask_limiter", "Flask-Limiter>=3.12.0,<4.0.0"),
    ("flask_bcrypt", "Flask-Bcrypt>=1.0.1,<2.0.0"),
    ("flask_mail", "Flask-Mail>=0.10.0,<1.0.0"),
    ("flask_caching", "Flask-Caching>=2.3.0,<3.0.0"),
    ("werkzeug", "Werkzeug>=3.1.0,<4.0.0"),
    ("jinja2", "Jinja2>=3.1.2,<4.0.0"),
    ("itsdangerous", "itsdangerous>=2.2.0,<3.0.0"),
    
    # Database
    ("sqlalchemy", "SQLAlchemy>=2.0.0,<3.0.0"),
    ("pymysql", "PyMySQL>=1.1.0,<2.0.0"),
    ("alembic", "alembic>=1.13.0,<2.0.0"),
    ("cachelib", "cachelib>=0.13.0,<1.0.0"),
    
    # Security
    ("jwt", "PyJWT>=2.10.0,<3.0.0"),
    ("cryptography", "cryptography>=44.0.0,<46.0.0"),
    ("bcrypt", "bcrypt>=4.0.0,<5.0.0"),
    ("email_validator", "email-validator>=2.2.0,<3.0.0"),
    
    # Serialization
    ("marshmallow", "marshmallow>=3.26.0,<4.0.0"),
    ("marshmallow_sqlalchemy", "marshmallow-sqlalchemy>=1.4.0,<2.0.0"),
    ("pydantic", "pydantic>=2.12.0,<3.0.0"),
    
    # Documentation
    ("flasgger", "flasgger>=0.9.7,<1.0.0"),
    ("apispec", "apispec>=6.0.0,<7.0.0"),
    ("yaml", "PyYAML>=6.0.0,<7.0.0"),
    
    # Monitoring
    ("sentry_sdk", "sentry-sdk>=2.0.0,<3.0.0"),
    ("blinker", "blinker>=1.7.0,<2.0.0"),
    ("structlog", "structlog>=24.0.0,<25.0.0"),
    
    # Caching & Rate Limiting
    ("redis", "redis>=5.0.0,<6.0.0"),
    ("limits", "limits>=3.13.0,<4.0.0"),
    
    # HTTP
    ("requests", "requests>=2.31.0,<3.0.0"),
    ("urllib3", "urllib3>=1.26.11,<3.0.0"),
    ("certifi", "certifi>=2024.0.0"),
    
    # Utilities
    ("dotenv", "python-dotenv>=1.0.0,<2.0.0"),
    ("click", "click>=8.1.0,<9.0.0"),
    ("phonenumbers", "phonenumbers>=8.12.0,<9.0.0"),
    ("dateutil", "python-dateutil>=2.9.0,<3.0.0"),
    
    # Server
    ("gunicorn", "gunicorn>=23.0.0,<26.0.0"),
]

def check_package(import_name):
    """Check if a package is installed"""
    try:
        __import__(import_name)
        return True
    except ImportError:
        return False

def install_package(package_spec):
    """Install a package using pip"""
    print(f"Installing {package_spec}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_spec])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install {package_spec}: {e}")
        return False

def main():
    print("=" * 60)
    print("KIU Portal API - Dependency Check & Installation")
    print("=" * 60)
    print()
    
    missing = []
    installed = []
    
    # Check all packages
    for import_name, package_spec in REQUIRED_PACKAGES:
        if check_package(import_name):
            installed.append(import_name)
            print(f"✅ {import_name}")
        else:
            missing.append((import_name, package_spec))
            print(f"❌ {import_name} - MISSING")
    
    print()
    print("-" * 60)
    
    if not missing:
        print("✅ ALL DEPENDENCIES INSTALLED!")
        print()
        print("You can now run the app with:")
        print("  gunicorn -w 2 -b 127.0.0.1:5001 wsgi:app")
        return 0
    
    print(f"Found {len(missing)} missing packages")
    print()
    
    # Install missing packages
    print("Installing missing packages...")
    print()
    
    failed = []
    for import_name, package_spec in missing:
        if install_package(package_spec):
            installed.append(import_name)
        else:
            failed.append(package_spec)
    
    print()
    print("-" * 60)
    
    if failed:
        print(f"❌ Failed to install {len(failed)} packages:")
        for pkg in failed:
            print(f"  - {pkg}")
        return 1
    
    print("✅ All packages installed successfully!")
    print()
    print("You can now run the app with:")
    print("  gunicorn -w 2 -b 127.0.0.1:5001 wsgi:app")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
