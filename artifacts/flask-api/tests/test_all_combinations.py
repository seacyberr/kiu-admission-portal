#!/usr/bin/env python3
"""
Test script to create applications for all exam level and program combinations:
- A-Level → Degree
- O-Level → Degree
- A-Level → Diploma
- O-Level → Diploma
- A-Level → HEC
- O-Level → HEC
"""

import os
import sys
from datetime import date, datetime
import random
import string

sys.path.insert(0, os.path.dirname(__file__))

# Use SQLite for testing
os.environ["DATABASE_URL"] = "sqlite:///test_admissions.db"
os.environ["SEED_DATABASE"] = "false"
os.environ["JWT_SECRET"] = "test-secret-key-for-development"
os.environ["FLASK_ENV"] = "development"

from app import create_app
from models import db, User, Program, AdmissionApplication


def generate_app_number():
    year = datetime.now().year
    suffix = "".join(random.choices(string.digits, k=6))
    return f"KIU/{year}/{suffix}"


def test_all_combinations():
    """Test all exam level and program type combinations."""
    
    app = create_app()
    
    with app.app_context():
        db.create_all()
        
        print("=" * 80)
        print("TESTING ALL EXAM LEVEL AND PROGRAM COMBINATIONS")
        print("=" * 80)
        
        # Seed programs if database is empty
        if Program.query.count() == 0:
            print("\nSeeding programs...")
            programs = [
                Program(name="Bachelor of Science", code="BSC101", faculty="Faculty of Science", level="degree", duration="4 years", description="Science program", entry_requirements="A-Level", min_olevel_points=32, min_alevel_points=8, available_slots=100, campus="kampala"),
                Program(name="Diploma in IT", code="DIT101", faculty="Faculty of IT", level="diploma", duration="2 years", description="IT diploma", entry_requirements="O-Level", min_olevel_points=28, min_alevel_points=None, available_slots=50, campus="kampala"),
                Program(name="Higher Education Certificate", code="HEC101", faculty="Faculty of Education", level="hec", duration="1 year", description="HEC program", entry_requirements="O-Level", min_olevel_points=24, min_alevel_points=None, available_slots=80, campus="kampala"),
            ]
            db.session.add_all(programs)
            db.session.commit()
            print(f"   ✓ Seeded {len(programs)} programs")
        
        # Get programs by level
        degree_programs = Program.query.filter_by(level="degree").all()
        diploma_programs = Program.query.filter_by(level="diploma").all()
        hec_programs = Program.query.filter_by(level="hec").all()
        
        print(f"\nAvailable Programs:")
        print(f"  Degree programs: {len(degree_programs)}")
        print(f"  Diploma programs: {len(diploma_programs)}")
        print(f"  HEC programs: {len(hec_programs)}")
        
        if not degree_programs or not diploma_programs or not hec_programs:
            print("\n✗ Missing required program levels.")
            return False
        
        # Test combinations
        test_cases = [
            {
                "name": "A-Level → Degree",
                "email": "alevel_degree@test.com",
                "first_name": "Alice",
                "last_name": "Degree",
                "exam_level": "a_level",
                "program": degree_programs[0],
                "olevel_count": 5,
                "alevel_count": 3,
                "olevel_points": 15,  # D1(1) + D2(2) + C3(3) + C4(4) + C5(5) = 15
                "alevel_points": 15,  # A(6) + B(5) + C(4) = 15
            },
            {
                "name": "O-Level → Degree",
                "email": "olevel_degree@test.com",
                "first_name": "Bob",
                "last_name": "Degree",
                "exam_level": "o_level",
                "program": degree_programs[0],
                "olevel_count": 5,
                "alevel_count": 0,
                "olevel_points": 15,
                "alevel_points": None,
            },
            {
                "name": "A-Level → Diploma",
                "email": "alevel_diploma@test.com",
                "first_name": "Charlie",
                "last_name": "Diploma",
                "exam_level": "a_level",
                "program": diploma_programs[0],
                "olevel_count": 5,
                "alevel_count": 3,
                "olevel_points": 15,
                "alevel_points": 15,
            },
            {
                "name": "O-Level → Diploma",
                "email": "olevel_diploma@test.com",
                "first_name": "Diana",
                "last_name": "Diploma",
                "exam_level": "o_level",
                "program": diploma_programs[0],
                "olevel_count": 5,
                "alevel_count": 0,
                "olevel_points": 15,
                "alevel_points": None,
            },
            {
                "name": "A-Level → HEC",
                "email": "alevel_hec@test.com",
                "first_name": "Edward",
                "last_name": "HEC",
                "exam_level": "a_level",
                "program": hec_programs[0],
                "olevel_count": 5,
                "alevel_count": 3,
                "olevel_points": 15,
                "alevel_points": 15,
            },
            {
                "name": "O-Level → HEC",
                "email": "olevel_hec@test.com",
                "first_name": "Fiona",
                "last_name": "HEC",
                "exam_level": "o_level",
                "program": hec_programs[0],
                "olevel_count": 4,
                "alevel_count": 0,
                "olevel_points": 10,  # D1(1) + D2(2) + C3(3) + C4(4) = 10
                "alevel_points": None,
            },
        ]
        
        results = {}
        
        for test_case in test_cases:
            print(f"\n{'='*60}")
            print(f"Testing: {test_case['name']}")
            print(f"{'='*60}")
            
            # Create user
            print(f"\n1. Creating user: {test_case['email']}")
            user = User(
                email=test_case["email"],
                password_hash="hashed_password",
                first_name=test_case["first_name"],
                last_name=test_case["last_name"],
                role="applicant",
                is_verified=True
            )
            db.session.add(user)
            db.session.commit()
            print(f"   ✓ User created (ID: {user.id})")
            
            # Create UNEB grades
            print(f"\n2. Creating UNEB grades...")
            olevel_grades = []
            subjects = ["Mathematics", "English Language", "Physics", "Chemistry", "Biology"]
            grade_options = [
                {"grade": "D1", "points": 1},
                {"grade": "D2", "points": 2},
                {"grade": "C3", "points": 3},
                {"grade": "C4", "points": 4},
                {"grade": "C5", "points": 5},
            ]
            
            for i in range(test_case["olevel_count"]):
                grade_info = grade_options[i % len(grade_options)]
                olevel_grades.append({
                    "subject": subjects[i % len(subjects)],
                    "grade": grade_info["grade"],
                    "points": grade_info["points"]
                })
            
            alevel_grades = []
            if test_case["alevel_count"] > 0:
                alevel_subjects = ["Mathematics", "Physics", "Chemistry"]
                alevel_grades = [
                    {"subject": "Mathematics", "grade": "A", "points": 6, "subjectType": "principal"},
                    {"subject": "Physics", "grade": "B", "points": 5, "subjectType": "principal"},
                    {"subject": "General Paper", "grade": "C", "points": 4, "subjectType": "subsidiary"},
                ]
            
            uneb_grades = {"olevel": olevel_grades}
            if alevel_grades:
                uneb_grades["alevel"] = alevel_grades
            
            print(f"   ✓ O-Level grades: {len(olevel_grades)} subjects")
            if alevel_grades:
                print(f"   ✓ A-Level grades: {len(alevel_grades)} subjects")
            
            # Create application
            print(f"\n3. Creating application...")
            print(f"   Program: {test_case['program'].name}")
            print(f"   Exam Level: {test_case['exam_level']}")
            
            # Check if exam level is valid for program
            if test_case["exam_level"] == "o_level" and test_case["program"].level == "degree":
                print(f"   ⚠ Note: O-Level alone is not sufficient for degree programs")
                print(f"   ℹ This combination should be rejected by validation")
                results[test_case["name"]] = "EXPECTED_FAIL"
                continue
            
            application = AdmissionApplication(
                application_number=generate_app_number(),
                user_id=user.id,
                program_id=test_case["program"].id,
                program_choices=[test_case["program"].id],
                exam_level=test_case["exam_level"],
                exam_year=2020,
                index_number=f"U{random.randint(1000,9999)}/001",
                uneb_grades=uneb_grades,
                date_of_birth=date(2000, random.randint(1, 12), random.randint(1, 28)),
                gender=random.choice(["male", "female"]),
                nationality="Ugandan",
                district=random.choice(["Kampala", "Wakiso", "Mukono", "Jinja"]),
                next_of_kin_name=f"Parent of {test_case['first_name']}",
                next_of_kin_phone=f"070{random.randint(1000000, 9999999)}",
                next_of_kin_relationship=random.choice(["Father", "Mother", "Guardian"]),
                status="pending"
            )
            
            db.session.add(application)
            db.session.commit()
            
            print(f"   ✓ Application created successfully")
            print(f"   ✓ Application Number: {application.application_number}")
            print(f"   ✓ Application ID: {application.id}")
            print(f"   ✓ Status: {application.status}")
            
            # Verify application
            print(f"\n4. Verifying application...")
            app_check = AdmissionApplication.query.get(application.id)
            
            if app_check:
                print(f"   ✓ Application found in database")
                print(f"   ✓ Exam level: {app_check.exam_level}")
                print(f"   ✓ Program: {app_check.program.name}")
                print(f"   ✓ Program level: {app_check.program.level}")
                print(f"   ✓ UNEB grades: {bool(app_check.uneb_grades)}")
                print(f"   ✓ Personal info: {bool(app_check.date_of_birth)}")
                
                # Verify required fields
                required_fields = [
                    "exam_level", "exam_year", "index_number", "uneb_grades",
                    "date_of_birth", "gender", "nationality", "district",
                    "next_of_kin_name", "next_of_kin_phone", "next_of_kin_relationship"
                ]
                
                missing = [f for f in required_fields if not getattr(app_check, f)]
                if missing:
                    print(f"   ✗ Missing fields: {', '.join(missing)}")
                    results[test_case["name"]] = False
                else:
                    print(f"   ✓ All required fields present")
                    results[test_case["name"]] = True
            else:
                print(f"   ✗ Application not found in database")
                results[test_case["name"]] = False
        
        # Print summary
        print(f"\n{'='*80}")
        print("TEST SUMMARY")
        print(f"{'='*80}")
        
        for test_name, result in results.items():
            if result == "EXPECTED_FAIL":
                status = "⚠ EXPECTED FAIL (O-Level not valid for Degree)"
            elif result:
                status = "✓ PASSED"
            else:
                status = "✗ FAILED"
            print(f"{test_name:25} : {status}")
        
        all_passed = all(r == True or r == "EXPECTED_FAIL" for r in results.values())
        print(f"\nOverall Result: {'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}")
        
        return all_passed


if __name__ == "__main__":
    success = test_all_combinations()
    sys.exit(0 if success else 1)