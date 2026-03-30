#!/usr/bin/env python3
"""Test script for all exam levels (O-Level, HEC, Diploma, A-Level)."""

import os
import json
import requests
from datetime import date

# Configuration
BASE_URL = "http://localhost:5001/api"

def test_exam_level(exam_level, program_level, program_id, test_name):
    """Test a specific exam level with a program."""
    print(f"\n{'='*60}")
    print(f"Testing: {test_name}")
    print(f"Exam Level: {exam_level}")
    print(f"Program Level: {program_level}")
    print(f"Program ID: {program_id}")
    print(f"{'='*60}")
    
    # Login
    login_response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "applicant@test.com",
        "password": "test123"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    token = login_response.json().get("token")
    
    # Prepare test data based on exam level
    if exam_level == "o_level":
        uneb_grades = {
            "olevel": [
                {"subject": "Mathematics", "grade": "D1", "points": 1},
                {"subject": "English Language", "grade": "D2", "points": 2},
                {"subject": "Physics", "grade": "C3", "points": 3},
                {"subject": "Chemistry", "grade": "C4", "points": 4},
                {"subject": "Biology", "grade": "C5", "points": 5}
            ]
        }
    elif exam_level == "a_level":
        uneb_grades = {
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
        }
    elif exam_level == "diploma":
        uneb_grades = {
            "olevel": [
                {"subject": "Mathematics", "grade": "D1", "points": 1},
                {"subject": "English Language", "grade": "D2", "points": 2},
                {"subject": "Physics", "grade": "C3", "points": 3},
                {"subject": "Chemistry", "grade": "C4", "points": 4},
                {"subject": "Biology", "grade": "C5", "points": 5}
            ]
        }
    elif exam_level == "hec":
        uneb_grades = {
            "olevel": [
                {"subject": "Mathematics", "grade": "D1", "points": 1},
                {"subject": "English Language", "grade": "D2", "points": 2},
                {"subject": "Physics", "grade": "C3", "points": 3},
                {"subject": "Chemistry", "grade": "C4", "points": 4},
                {"subject": "Biology", "grade": "C5", "points": 5}
            ]
        }
    
    # Submit application
    test_data = {
        "programIds": [program_id],
        "examLevel": exam_level,
        "examYear": 2020,
        "indexNumber": f"U{exam_level.upper()[:3]}001/001",
        "unebGrades": uneb_grades,
        "dateOfBirth": "2000-04-04",
        "gender": "male",
        "nationality": "Ugandan",
        "district": "Kampala",
        "nextOfKinName": "John Doe",
        "nextOfKinPhone": "0701240315",
        "nextOfKinRelationship": "Father"
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.post(
        f"{BASE_URL}/admission/applications",
        headers=headers,
        json=test_data
    )
    
    print(f"Response Status: {response.status_code}")
    
    if response.status_code == 201:
        print(f"✅ {test_name} - SUCCESS!")
        app_data = response.json()
        print(f"   Application ID: {app_data.get('id')}")
        print(f"   Application Number: {app_data.get('applicationNumber')}")
        print(f"   Status: {app_data.get('status')}")
        return True
    else:
        print(f"❌ {test_name} - FAILED!")
        print(f"   Response: {response.text}")
        return False

def main():
    """Test all exam levels."""
    print("="*60)
    print("TESTING ALL EXAM LEVELS")
    print("="*60)
    
    # Get available programs
    programs_response = requests.get(f"{BASE_URL}/admission/programs")
    if programs_response.status_code != 200:
        print("❌ Failed to fetch programs")
        return
    
    programs = programs_response.json().get("programs", [])
    
    # Find programs by level
    degree_programs = [p for p in programs if p.get("level") == "degree"]
    diploma_programs = [p for p in programs if p.get("level") == "diploma"]
    hec_programs = [p for p in programs if p.get("level") == "hec"]
    
    print(f"\nFound {len(degree_programs)} degree programs")
    print(f"Found {len(diploma_programs)} diploma programs")
    print(f"Found {len(hec_programs)} hec programs")
    
    if not degree_programs:
        print("❌ No degree programs found")
        return
    
    if not diploma_programs:
        print("❌ No diploma programs found")
        return
    
    if not hec_programs:
        print("❌ No hec programs found")
        return
    
    # Test different combinations
    test_results = []
    
    # Test 1: O-Level with Diploma program (should work)
    test_results.append(test_exam_level(
        "o_level",
        "diploma",
        diploma_programs[0].get("id"),
        "O-Level with Diploma Program"
    ))
    
    # Test 2: O-Level with HEC program (should work)
    test_results.append(test_exam_level(
        "o_level",
        "hec",
        hec_programs[0].get("id"),
        "O-Level with HEC Program"
    ))
    
    # Test 3: A-Level with Degree program (should work)
    test_results.append(test_exam_level(
        "a_level",
        "degree",
        degree_programs[0].get("id"),
        "A-Level with Degree Program"
    ))
    
    # Test 4: Diploma with Degree program (should work now)
    test_results.append(test_exam_level(
        "diploma",
        "degree",
        degree_programs[0].get("id"),
        "Diploma with Degree Program"
    ))
    
    # Test 5: HEC with Degree program (should work now)
    test_results.append(test_exam_level(
        "hec",
        "degree",
        degree_programs[0].get("id"),
        "HEC with Degree Program"
    ))
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    passed = sum(test_results)
    total = len(test_results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed")

if __name__ == "__main__":
    main()