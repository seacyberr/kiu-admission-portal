#!/usr/bin/env python3
"""
Diagnostic script to identify actual workflow failures
Run this to find what's broken in the application
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

import requests
import json

BASE_URL = "http://127.0.0.1:5001"

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def log_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def log_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def log_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def log_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

def test_endpoint(method, path, data=None, expected_status=200):
    """Test an API endpoint"""
    url = f"{BASE_URL}{path}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5)
        else:
            response = requests.request(method, url, json=data, timeout=5)
        
        if response.status_code == expected_status:
            log_success(f"{method} {path} - {response.status_code}")
            return True, response.json() if response.text else None
        else:
            log_error(f"{method} {path} - Expected {expected_status}, got {response.status_code}")
            return False, None
    except requests.exceptions.ConnectionError:
        log_error(f"{method} {path} - Connection refused. Is the server running?")
        return False, None
    except Exception as e:
        log_error(f"{method} {path} - {str(e)}")
        return False, None

def main():
    print("=" * 60)
    print("KIU Portal - Diagnostic Report")
    print("=" * 60)
    print()
    
    # Check if server is running
    log_info("Checking if backend is running...")
    success, _ = test_endpoint("GET", "/api/health")
    if not success:
        print()
        log_error("Backend is not responding!")
        print()
        print("To start the server:")
        print("  cd /home/sea/Downloads/Kiu-Admission-Portal/apps/flask-api")
        print("  gunicorn -w 2 -b 127.0.0.1:5001 wsgi:app")
        return 1
    
    print()
    log_info("Testing Core Workflows...")
    print()
    
    failures = []
    
    # 1. Test Registration
    log_info("1. Testing Registration...")
    reg_data = {
        "email": "diagnostic_test@example.com",
        "password": "Test123!@#",
        "first_name": "Diagnostic",
        "last_name": "Test",
        "phone": "+256700000001",
        "role": "applicant"
    }
    success, result = test_endpoint("POST", "/api/auth/register", reg_data, expected_status=201)
    if not success:
        failures.append("Registration")
    
    # 2. Test Login
    log_info("2. Testing Login...")
    login_data = {
        "email": "diagnostic_test@example.com",
        "password": "Test123!@#"
    }
    success, result = test_endpoint("POST", "/api/auth/login", login_data)
    token = None
    if success and result:
        token = result.get("access_token")
        log_success("Got access token")
    else:
        failures.append("Login")
    
    # 3. Test Programs Endpoint
    log_info("3. Testing Programs List...")
    success, _ = test_endpoint("GET", "/api/admission/programs")
    if not success:
        failures.append("Programs list")
    
    # 4. Test NCHE Assess
    log_info("4. Testing NCHE Assessment...")
    assess_data = {
        "qualification": "uace",
        "curriculum": "new",
        "subjects": [
            {"name": "Mathematics", "grade": "A"},
            {"name": "Physics", "grade": "B"},
            {"name": "Chemistry", "grade": "B"}
        ]
    }
    success, _ = test_endpoint("POST", "/api/v1/nche/assess", assess_data)
    if not success:
        failures.append("NCHE Assessment")
    
    # 5. Test Certificate Verification Standards
    log_info("5. Testing Certificate Verification Standards...")
    success, _ = test_endpoint("GET", "/api/certificate-verification/verification-standards")
    if not success:
        failures.append("Certificate verification standards")
    
    # 6. Test Application Creation (if authenticated)
    if token:
        log_info("6. Testing Application Creation...")
        app_data = {
            "programIds": [1],
            "examLevel": "uace",
            "examYear": 2023,
            "indexNumber": "U0001/001",
            "unebGrades": [{"subject": "Mathematics", "grade": "A"}],
            "dateOfBirth": "2000-01-01",
            "gender": "male"
        }
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.post(
                f"{BASE_URL}/api/admission/applications",
                json=app_data,
                headers=headers,
                timeout=5
            )
            if response.status_code == 201:
                log_success("Application creation - 201 Created")
            else:
                log_error(f"Application creation - {response.status_code}")
                failures.append("Application creation")
        except Exception as e:
            log_error(f"Application creation - {str(e)}")
            failures.append("Application creation")
    else:
        log_warning("Skipping application test (no token)")
    
    # Summary
    print()
    print("=" * 60)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 60)
    print()
    
    if not failures:
        log_success("All core workflows passed!")
        return 0
    else:
        log_error(f"{len(failures)} workflow(s) failed:")
        for f in failures:
            print(f"  - {f}")
        print()
        log_info("Common fixes:")
        print("  1. Check database connection")
        print("  2. Verify models are properly defined")
        print("  3. Check required fields in requests")
        print("  4. Review server logs for detailed errors")
        return 1

if __name__ == "__main__":
    sys.exit(main())
