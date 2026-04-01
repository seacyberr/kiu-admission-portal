#!/usr/bin/env python3
"""Test script for A-Level degree application with old curriculum."""

import os
os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["SEED_DATABASE"] = "false"
os.environ["JWT_SECRET"] = "test-secret-key"

from app import create_app
from models import db, User, Program
from datetime import date

app = create_app()

with app.app_context():
    # Create tables
    db.create_all()
    
    # Create a test user
    user = User(
        email="test@example.com",
        password_hash="hashed_password",
        first_name="Test",
        last_name="User",
        role="applicant",
        is_verified=True
    )
    db.session.add(user)
    db.session.commit()
    
    # Create a test program (A-Level degree)
    program = Program(
        name="Bachelor of Science",
        code="BSC101",
        faculty="Faculty of Science",
        level="degree",
        duration="4 years",
        description="A sample degree program",
        entry_requirements="A-Level with 2 principal passes",
        min_olevel_points=32,
        min_alevel_points=8,
        available_slots=100,
        campus="kampala"
    )
    db.session.add(program)
    db.session.commit()
    
    # Test data for A-Level degree application with old curriculum
    test_data = {
        "programIds": [program.id],
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
        "dateOfBirth": "2000-04-04",
        "gender": "male",
        "nationality": "Ugandan",
        "district": "Kampala",
        "nextOfKinName": "John Doe",
        "nextOfKinPhone": "0701240315",
        "nextOfKinRelationship": "Father"
    }
    
    print("Test data for A-Level degree application with old curriculum:")
    print(f"Program: {program.name}")
    print(f"Exam Level: {test_data['examLevel']}")
    print(f"O-Level subjects: {len(test_data['unebGrades']['olevel'])}")
    print(f"A-Level subjects: {len(test_data['unebGrades']['alevel'])}")
    print(f"Date of Birth: {test_data['dateOfBirth']}")
    print("\nTest data looks correct!")