#!/usr/bin/env python3
"""
Full comprehensive test suite - API + Manual workflow verification
"""

import sys
import os

# Activate venv
venv_path = "/home/sea/venv"
if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
    pass
else:
    activate_script = os.path.join(venv_path, "bin", "activate_this.py")
    if os.path.exists(activate_script):
        exec(open(activate_script).read(), {'__file__': activate_script})

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests
import json
import random
import time

BASE_URL = "http://127.0.0.1:5001"
TEST_RESULTS = []

def log_test(name, status, details=""):
    symbol = "SUCCESS:" if status else "ERROR:"
    TEST_RESULTS.append({"name": name, "status": status, "details": details})
    print(f"{symbol} {name}")
    if details:
        print(f"   {details}")

def test_api():
    print("\n" + "="*60)
    print("PART 1: API ENDPOINT TESTS")
    print("="*60)
    
    # 1. Health Check
    try:
        r = requests.get(f"{BASE_URL}/api/health", timeout=5)
        log_test("Health Endpoint", r.status_code == 200 and r.json().get('status') == 'healthy')
    except Exception as e:
        log_test("Health Endpoint", False, str(e))
    
    # 2. Programs List
    try:
        r = requests.get(f"{BASE_URL}/api/admission/programs", timeout=5)
        if r.status_code == 200:
            data = r.json()
            count = len(data) if isinstance(data, list) else len(data.get('programs', []))
            log_test("Programs List", True, f"{count} programs found")
        else:
            log_test("Programs List", False, f"Status {r.status_code}")
    except Exception as e:
        log_test("Programs List", False, str(e))
    
    # 3. Certificate Standards
    try:
        r = requests.get(f"{BASE_URL}/api/certificate-verification/verification-standards", timeout=5)
        log_test("Certificate Standards", r.status_code == 200, f"Status {r.status_code}")
    except Exception as e:
        log_test("Certificate Standards", False, str(e))
    
    # 4. Registration with unique email
    global TEST_EMAIL, TEST_TOKEN
    TEST_EMAIL = f"test{random.randint(100000,999999)}@kiu.ac.ug"
    try:
        r = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": TEST_EMAIL,
            "password": "TestPass123!",
            "first_name": "Test",
            "last_name": "User",
            "phone": f"+2567{random.randint(10000000,99999999)}",
            "role": "applicant"
        }, timeout=5)
        if r.status_code == 201:
            log_test("User Registration", True, f"Email: {TEST_EMAIL}")
        else:
            log_test("User Registration", False, f"Status {r.status_code}: {r.text[:100]}")
    except Exception as e:
        log_test("User Registration", False, str(e))
    
    # 5. Login
    try:
        r = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": "TestPass123!"
        }, timeout=5)
        if r.status_code == 200:
            data = r.json()
            TEST_TOKEN = data.get('access_token')
            log_test("User Login", True, f"Token: {TEST_TOKEN[:20]}..." if TEST_TOKEN else "No token")
        else:
            log_test("User Login", False, f"Status {r.status_code}")
            TEST_TOKEN = None
    except Exception as e:
        log_test("User Login", False, str(e))
        TEST_TOKEN = None
    
    # 6. NCHE Assessment
    try:
        r = requests.post(f"{BASE_URL}/api/v1/nche/assess", json={
            "qualification": "uace",
            "curriculum": "new",
            "subjects": [
                {"name": "Mathematics", "grade": "A"},
                {"name": "Physics", "grade": "B"},
                {"name": "Chemistry", "grade": "B"}
            ]
        }, timeout=5)
        if r.status_code == 200:
            data = r.json()
            has_transparency = 'transparency' in data
            log_test("NCHE Assessment", True, f"Eligible: {data.get('eligible')}, Transparency: {has_transparency}")
        else:
            log_test("NCHE Assessment", False, f"Status {r.status_code}")
    except Exception as e:
        log_test("NCHE Assessment", False, str(e))
    
    # 7. Create Application (authenticated)
    if TEST_TOKEN:
        try:
            r = requests.post(f"{BASE_URL}/api/admission/applications", 
                json={"program_id": 1, "intake": "september_2025", "sponsorship_type": "private"},
                headers={"Authorization": f"Bearer {TEST_TOKEN}"},
                timeout=5)
            log_test("Create Application", r.status_code in [200, 201], f"Status {r.status_code}")
        except Exception as e:
            log_test("Create Application", False, str(e))
    else:
        log_test("Create Application", False, "No auth token")

def test_manual_workflows():
    print("\n" + "="*60)
    print("PART 2: MANUAL WORKFLOW VERIFICATION")
    print("="*60)
    
    # Test program data structure
    try:
        r = requests.get(f"{BASE_URL}/api/admission/programs", timeout=5)
        if r.status_code == 200:
            data = r.json()
            programs = data if isinstance(data, list) else data.get('programs', [])
            if programs:
                p = programs[0]
                required_fields = ['id', 'name', 'code', 'faculty', 'level', 'duration']
                missing = [f for f in required_fields if f not in p]
                log_test("Program Data Structure", len(missing) == 0, 
                        f"Missing fields: {missing}" if missing else "All required fields present")
                
                # Check fee fields exist
                fee_fields = ['fees_local_per_semester', 'fees_international_per_semester']
                has_fees = all(f in p for f in fee_fields)
                log_test("Program Fee Fields", has_fees, f"Fee fields present: {has_fees}")
            else:
                log_test("Program Data Structure", False, "No programs returned")
    except Exception as e:
        log_test("Program Data Structure", False, str(e))
    
    # Test NCHE transparency
    try:
        r = requests.post(f"{BASE_URL}/api/v1/nche/assess", json={
            "qualification": "uace",
            "curriculum": "new",
            "subjects": [{"name": "Mathematics", "grade": "F"}]  # Failing grade to test transparency
        }, timeout=5)
        if r.status_code == 200:
            data = r.json()
            transp = data.get('transparency', {})
            checks = [
                ('checked_criteria' in transp, "checked_criteria"),
                ('failed_criteria' in transp, "failed_criteria"),
                ('actionable_steps' in transp, "actionable_steps"),
                ('alternative_pathways' in transp, "alternative_pathways")
            ]
            passed = sum(1 for c, _ in checks if c)
            log_test("NCHE Transparency Fields", passed == len(checks), 
                    f"{passed}/{len(checks)} fields present")
        else:
            log_test("NCHE Transparency Fields", False, f"Status {r.status_code}")
    except Exception as e:
        log_test("NCHE Transparency Fields", False, str(e))
    
    # Test error responses
    try:
        r = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": "invalid-email",
            "password": "123"  # Too short
        }, timeout=5)
        has_error = r.status_code == 400 and ('error' in r.text.lower() or 'message' in r.text.lower())
        log_test("Error Response Format", has_error, f"Status {r.status_code}, has error message: {has_error}")
    except Exception as e:
        log_test("Error Response Format", False, str(e))

def print_summary():
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    passed = sum(1 for r in TEST_RESULTS if r['status'])
    total = len(TEST_RESULTS)
    print(f"Passed: {passed}/{total} ({passed*100//total}%)")
    print()
    
    if passed < total:
        print("FAILED TESTS:")
        for r in TEST_RESULTS:
            if not r['status']:
                print(f"  ERROR: {r['name']}: {r['details']}")
    
    print("\n" + "="*60)
    if passed == total:
        print("SUCCESS: ALL TESTS PASSED - Ready for manual testing!")
    else:
        print(f"WARNING:  {total-passed} TEST(S) FAILED - Review issues above")
    print("="*60)

if __name__ == "__main__":
    test_api()
    test_manual_workflows()
    print_summary()
