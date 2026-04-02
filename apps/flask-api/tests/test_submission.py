#!/usr/bin/env python3
"""Diagnostic script to test admission submission with detailed error reporting."""

import os
import json
import requests
from datetime import date

# Configuration
BASE_URL = "http://localhost:5001/api"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpass123"

def test_submission():
    """Test the full admission submission flow."""
    
    print("=" * 60)
    print("KIU ADMISSION SUBMISSION DIAGNOSTIC")
    print("=" * 60)
    
    # Step 1: Login
    print("\n1. Testing login...")
    login_response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"   Response: {login_response.text}")
        return
    
    login_data = login_response.json()
    token = login_data.get("token")
    user = login_data.get("user")
    
    print(f"✅ Login successful")
    print(f"   User: {user.get('firstName')} {user.get('lastName')}")
    print(f"   Role: {user.get('role')}")
    print(f"   Verified: {user.get('isVerified')}")
    
    if user.get('role') != 'applicant':
        print("❌ User role is not 'applicant'")
        return
    
    # Step 2: Get programs
    print("\n2. Fetching programs...")
    programs_response = requests.get(f"{BASE_URL}/admission/programs")
    
    if programs_response.status_code != 200:
        print(f"❌ Failed to fetch programs: {programs_response.status_code}")
        return
    
    programs_data = programs_response.json()
    programs = programs_data.get("programs", [])
    
    # Find a degree program
    degree_programs = [p for p in programs if p.get("level") == "degree"]
    
    if not degree_programs:
        print("❌ No degree programs found")
        return
    
    program = degree_programs[0]
    print(f"✅ Found degree program: {program.get('name')} (ID: {program.get('id')})")
    
    # Step 3: Submit application with A-Level and old curriculum
    print("\n3. Submitting A-Level degree application with old curriculum...")
    
    test_data = {
        "programIds": [program.get('id')],
        "examLevel": "a_level",
        "examYear": 2020,
        "indexNumber": "U0001/001",
        "unebGrades": {
            "olevel": [
                {"subject": "Mathematics", "grade": "D1", "points": 1},
                {"subject": "English Language", "grade": "D2", "points": 2},
                {"subject": "Physics", "grade": "C3", "points": 3},
                {"subject": "Chemistry", "grade": "C4", "points": 4},
                {"subject": "Biology", "grade": "C5", "points": 5}
            ],
            "alevel": [
                {"subject": "Mathematics", "grade": "A", "points": 6, "subjectType": "principal"},
                {"subject": "Physics", "grade": "B", "points": 5, "subjectType": "principal"},
                {"subject": "General Paper", "grade": "C", "points": 4, "subjectType": "subsidiary"}
            ]
        },
        "dateOfBirth": "2000-04-04",  # Correct format: YYYY-MM-DD
        "gender": "male",
        "nationality": "Ugandan",
        "district": "Kampala",
        "nextOfKinName": "JOHN DOE",
        "nextOfKinPhone": "0701240315",
        "nextOfKinRelationship": "Father"
    }
    
    print(f"   Sending data: {json.dumps(test_data, indent=2)}")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    submit_response = requests.post(
        f"{BASE_URL}/admission/applications",
        headers=headers,
        json=test_data
    )
    
    print(f"\n   Response status: {submit_response.status_code}")
    print(f"   Response headers: {dict(submit_response.headers)}")
    
    if submit_response.status_code == 201:
        print("✅ Application submitted successfully!")
        app_data = submit_response.json()
        print(f"   Application ID: {app_data.get('id')}")
        print(f"   Application Number: {app_data.get('applicationNumber')}")
        print(f"   Status: {app_data.get('status')}")
    else:
        print(f"❌ Application submission failed: {submit_response.status_code}")
        print(f"   Response: {submit_response.text}")
        
        try:
            error_data = submit_response.json()
            print(f"   Error: {error_data.get('message', 'Unknown error')}")
        except:
            print(f"   Could not parse error response")

if __name__ == "__main__":
    test_submission()