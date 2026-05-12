#!/usr/bin/env python3
import sys
import os
import subprocess
import time

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_command(cmd, cwd=None):
    """Run a shell command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10, cwd=cwd)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout"

def main():
    print("="*70)
    print("FULL APPLICATION TEST SUITE")
    print("="*70)
    
    BASE_URL = "http://127.0.0.1:5001"
    
    # Check if server is running
    print("\n[1] Checking server status...")
    ret, out, err = run_command(f"curl -s {BASE_URL}/api/health")
    if ret == 0 and 'healthy' in out:
        print("    SUCCESS: Server is running")
    else:
        print("    ERROR: Server not running - attempting to start...")
        # Try to start server
        ret, out, err = run_command("gunicorn -w 1 -b 127.0.0.1:5001 wsgi:app --daemon", 
                                    cwd="/home/sea/Downloads/Kiu-Admission-Portal/apps/flask-api")
        time.sleep(5)
        ret, out, err = run_command(f"curl -s {BASE_URL}/api/health")
        if ret == 0 and 'healthy' in out:
            print("    SUCCESS: Server started successfully")
        else:
            print(f"    ERROR: Failed to start server: {err}")
            return
    
    # Test endpoints
    tests = [
        ("Health", f"curl -s {BASE_URL}/api/health", "healthy"),
        ("Programs", f"curl -s {BASE_URL}/api/admission/programs", "["),
        ("Certificate Standards", f"curl -s {BASE_URL}/api/certificate-verification/verification-standards", "o_level"),
    ]
    
    print("\n[2] API Endpoint Tests:")
    for name, cmd, expected in tests:
        ret, out, err = run_command(cmd)
        if ret == 0 and expected in out:
            print(f"    SUCCESS: {name}")
        else:
            print(f"    ERROR: {name} - Error: {err[:50] if err else out[:50]}")
    
    # Test NCHE Assessment
    print("\n[3] NCHE Assessment Test:")
    nche_data = '{"qualification":"uace","curriculum":"new","subjects":[{"name":"Mathematics","grade":"A"}]}'
    ret, out, err = run_command(f"curl -s -X POST {BASE_URL}/api/v1/nche/assess -H 'Content-Type: application/json' -d '{nche_data}'")
    if ret == 0 and '"eligible"' in out:
        print("    SUCCESS: NCHE Assessment working")
        if '"transparency"' in out:
            print("    SUCCESS: Transparency field present")
        else:
            print("    WARNING: Transparency field missing")
    else:
        print(f"    ERROR: NCHE Assessment failed: {out[:100]}")
    
    # Test Registration
    print("\n[4] User Registration Test:")
    import random
    email = f"test{random.randint(10000,99999)}@kiu.ac.ug"
    reg_data = f'"email":"{email}","password":"TestPass123!","first_name":"Test","last_name":"User","phone":"+256799999999","role":"applicant"'
    ret, out, err = run_command(f"curl -s -X POST {BASE_URL}/api/auth/register -H 'Content-Type: application/json' -d '{{{reg_data}}}'")
    if ret == 0 and ('user_id' in out or 'id' in out or '201' in str(ret)):
        print(f"    SUCCESS: User registration working ({email})")
    else:
        print(f"    WARNING: Registration: {out[:100]}")
    
    # Frontend checks
    print("\n[5] Frontend File Verification:")
    frontend_path = "/home/sea/Downloads/Kiu-Admission-Portal/apps/kiu-portal/src/pages/applicant"
    files_to_check = ["apply.tsx", "nche-recommend.tsx"]
    for f in files_to_check:
        if os.path.exists(f"{frontend_path}/{f}"):
            print(f"    SUCCESS: {f} exists")
        else:
            print(f"    ERROR: {f} missing")
    
    # Check subject lists
    apply_file = f"{frontend_path}/apply.tsx"
    if os.path.exists(apply_file):
        with open(apply_file, 'r') as f:
            content = f.read()
        print("\n[6] Subject Lists Verification:")
        lists = ["OLEVEL_COMPULSORY_SUBJECTS", "OLEVEL_OPTIONAL_SUBJECTS", 
                 "ALEVEL_PRINCIPAL_SUBJECTS", "ALEVEL_SUBSIDIARY_SUBJECTS"]
        for lst in lists:
            if lst in content:
                print(f"    SUCCESS: {lst} defined")
            else:
                print(f"    ERROR: {lst} missing")
    
    print("\n" + "="*70)
    print("TESTS COMPLETE")
    print("="*70)

if __name__ == "__main__":
    main()
