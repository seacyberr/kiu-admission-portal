#!/usr/bin/env python3
"""Add diploma and HEC programs to the database."""

import os
import sys

# Add the parent directory to the path (where app.py is located)
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Set environment variables before importing app
os.environ["DATABASE_URL"] = "mysql+pymysql://admin:adekunle%2312@localhost/kiu_admissions"
os.environ["SEED_DATABASE"] = "false"
os.environ["JWT_SECRET"] = "test-secret-key-for-development"
os.environ["FLASK_ENV"] = "development"

from app import create_app
from models import db, Program

def add_diploma_hec_programs():
    """Add diploma and HEC programs to the database."""
    
    app = create_app()
    
    with app.app_context():
        try:
            # Check existing programs
            existing_programs = Program.query.all()
            existing_codes = {p.code for p in existing_programs}
            
            print(f"Existing programs: {len(existing_programs)}")
            print(f"Existing codes: {existing_codes}")
            
            # Define diploma programs
            diploma_programs = [
                {
                    "name": "Diploma in Business Administration",
                    "code": "DIP-BUS-001",
                    "faculty": "Faculty of Business and Management",
                    "department": "Department of Business Administration",
                    "level": "diploma",
                    "duration": "2 Years",
                    "description": "A comprehensive diploma program covering business fundamentals, management principles, and practical business skills.",
                    "entryRequirements": "O-Level with at least 5 passes including English and Mathematics",
                    "minOlevelPoints": 28,
                    "minAlevelPoints": None,
                    "availableSlots": 50,
                    "campus": "kampala"
                },
                {
                    "name": "Diploma in Information Technology",
                    "code": "DIP-IT-001",
                    "faculty": "Faculty of Science and Technology",
                    "department": "Department of Information Technology",
                    "level": "diploma",
                    "duration": "2 Years",
                    "description": "Practical IT diploma covering computer systems, networking, programming, and database management.",
                    "entryRequirements": "O-Level with at least 5 passes including Mathematics and Physics",
                    "minOlevelPoints": 28,
                    "minAlevelPoints": None,
                    "availableSlots": 60,
                    "campus": "kampala"
                },
                {
                    "name": "Diploma in Electrical Engineering",
                    "code": "DIP-EE-001",
                    "faculty": "Faculty of Engineering",
                    "department": "Department of Electrical Engineering",
                    "level": "diploma",
                    "duration": "3 Years",
                    "description": "Hands-on electrical engineering diploma covering circuits, power systems, and electronics.",
                    "entryRequirements": "O-Level with at least 5 passes including Mathematics, Physics, and English",
                    "minOlevelPoints": 30,
                    "minAlevelPoints": None,
                    "availableSlots": 40,
                    "campus": "kampala"
                },
                {
                    "name": "Diploma in Civil Engineering",
                    "code": "DIP-CE-001",
                    "faculty": "Faculty of Engineering",
                    "department": "Department of Civil Engineering",
                    "level": "diploma",
                    "duration": "3 Years",
                    "description": "Practical civil engineering diploma covering construction, surveying, and structural design.",
                    "entryRequirements": "O-Level with at least 5 passes including Mathematics, Physics, and English",
                    "minOlevelPoints": 30,
                    "minAlevelPoints": None,
                    "availableSlots": 40,
                    "campus": "kampala"
                },
                {
                    "name": "Diploma in Mechanical Engineering",
                    "code": "DIP-ME-001",
                    "faculty": "Faculty of Engineering",
                    "department": "Department of Mechanical Engineering",
                    "level": "diploma",
                    "duration": "3 Years",
                    "description": "Mechanical engineering diploma covering machines, manufacturing, and maintenance.",
                    "entryRequirements": "O-Level with at least 5 passes including Mathematics, Physics, and English",
                    "minOlevelPoints": 30,
                    "minAlevelPoints": None,
                    "availableSlots": 40,
                    "campus": "kampala"
                },
                {
                    "name": "Diploma in Nursing",
                    "code": "DIP-NUR-001",
                    "faculty": "Faculty of Health Sciences",
                    "department": "Department of Nursing",
                    "level": "diploma",
                    "duration": "3 Years",
                    "description": "Comprehensive nursing diploma preparing students for clinical practice and patient care.",
                    "entryRequirements": "O-Level with at least 5 passes including English, Biology, and Chemistry",
                    "minOlevelPoints": 32,
                    "minAlevelPoints": None,
                    "availableSlots": 80,
                    "campus": "western"
                },
                {
                    "name": "Diploma in Clinical Medicine",
                    "code": "DIP-CM-001",
                    "faculty": "Faculty of Health Sciences",
                    "department": "Department of Clinical Medicine",
                    "level": "diploma",
                    "duration": "3 Years",
                    "description": "Clinical medicine diploma for healthcare professionals in community health settings.",
                    "entryRequirements": "O-Level with at least 5 passes including English, Biology, Chemistry, and Mathematics",
                    "minOlevelPoints": 32,
                    "minAlevelPoints": None,
                    "availableSlots": 60,
                    "campus": "western"
                },
                {
                    "name": "Diploma in Pharmacy",
                    "code": "DIP-PHARM-001",
                    "faculty": "Faculty of Health Sciences",
                    "department": "Department of Pharmacy",
                    "level": "diploma",
                    "duration": "3 Years",
                    "description": "Pharmacy diploma covering drug dispensing, pharmaceutical care, and medication management.",
                    "entryRequirements": "O-Level with at least 5 passes including English, Biology, Chemistry, and Mathematics",
                    "minOlevelPoints": 32,
                    "minAlevelPoints": None,
                    "availableSlots": 50,
                    "campus": "western"
                },
                {
                    "name": "Diploma in Education (Primary)",
                    "code": "DIP-EDU-P-001",
                    "faculty": "Faculty of Education",
                    "department": "Department of Primary Education",
                    "level": "diploma",
                    "duration": "3 Years",
                    "description": "Teacher training diploma for primary school education.",
                    "entryRequirements": "O-Level with at least 5 passes including English",
                    "minOlevelPoints": 28,
                    "minAlevelPoints": None,
                    "availableSlots": 100,
                    "campus": "kampala"
                },
                {
                    "name": "Diploma in Education (Secondary)",
                    "code": "DIP-EDU-S-001",
                    "faculty": "Faculty of Education",
                    "department": "Department of Secondary Education",
                    "level": "diploma",
                    "duration": "3 Years",
                    "description": "Teacher training diploma for secondary school education.",
                    "entryRequirements": "O-Level with at least 5 passes including English",
                    "minOlevelPoints": 28,
                    "minAlevelPoints": None,
                    "availableSlots": 80,
                    "campus": "kampala"
                }
            ]
            
            # Define HEC programs
            hec_programs = [
                {
                    "name": "Higher Education Certificate in Business",
                    "code": "HEC-BUS-001",
                    "faculty": "Faculty of Business and Management",
                    "department": "Department of Business Administration",
                    "level": "hec",
                    "duration": "1 Year",
                    "description": "Foundation certificate in business studies preparing students for diploma or degree programs.",
                    "entryRequirements": "O-Level with at least 4 passes",
                    "minOlevelPoints": 24,
                    "minAlevelPoints": None,
                    "availableSlots": 100,
                    "campus": "kampala"
                },
                {
                    "name": "Higher Education Certificate in Information Technology",
                    "code": "HEC-IT-001",
                    "faculty": "Faculty of Science and Technology",
                    "department": "Department of Information Technology",
                    "level": "hec",
                    "duration": "1 Year",
                    "description": "Foundation certificate in IT covering basic computer skills and programming concepts.",
                    "entryRequirements": "O-Level with at least 4 passes including Mathematics",
                    "minOlevelPoints": 24,
                    "minAlevelPoints": None,
                    "availableSlots": 80,
                    "campus": "kampala"
                },
                {
                    "name": "Higher Education Certificate in Health Sciences",
                    "code": "HEC-HS-001",
                    "faculty": "Faculty of Health Sciences",
                    "department": "Department of Health Sciences",
                    "level": "hec",
                    "duration": "1 Year",
                    "description": "Foundation certificate in health sciences preparing students for health-related diploma programs.",
                    "entryRequirements": "O-Level with at least 4 passes including Biology and English",
                    "minOlevelPoints": 26,
                    "minAlevelPoints": None,
                    "availableSlots": 60,
                    "campus": "western"
                },
                {
                    "name": "Higher Education Certificate in Education",
                    "code": "HEC-EDU-001",
                    "faculty": "Faculty of Education",
                    "department": "Department of Education",
                    "level": "hec",
                    "duration": "1 Year",
                    "description": "Foundation certificate in education for aspiring teachers.",
                    "entryRequirements": "O-Level with at least 4 passes including English",
                    "minOlevelPoints": 24,
                    "minAlevelPoints": None,
                    "availableSlots": 80,
                    "campus": "kampala"
                },
                {
                    "name": "Higher Education Certificate in Engineering",
                    "code": "HEC-ENG-001",
                    "faculty": "Faculty of Engineering",
                    "department": "Department of Engineering",
                    "level": "hec",
                    "duration": "1 Year",
                    "description": "Foundation certificate in engineering covering basic mathematics and physics.",
                    "entryRequirements": "O-Level with at least 4 passes including Mathematics and Physics",
                    "minOlevelPoints": 26,
                    "minAlevelPoints": None,
                    "availableSlots": 60,
                    "campus": "kampala"
                }
            ]
            
            # Add programs
            programs_added = 0
            for program_data in diploma_programs + hec_programs:
                if program_data["code"] not in existing_codes:
                    program = Program(
                        name=program_data["name"],
                        code=program_data["code"],
                        faculty=program_data["faculty"],
                        department=program_data["department"],
                        level=program_data["level"],
                        duration=program_data["duration"],
                        description=program_data["description"],
                        entry_requirements=program_data["entryRequirements"],
                        min_olevel_points=program_data["minOlevelPoints"],
                        min_alevel_points=program_data["minAlevelPoints"],
                        available_slots=program_data["availableSlots"],
                        campus=program_data["campus"]
                    )
                    db.session.add(program)
                    programs_added += 1
                    print(f"Added: {program_data['name']} ({program_data['code']})")
                else:
                    print(f"Skipped (already exists): {program_data['name']} ({program_data['code']})")
            
            db.session.commit()
            
            print(f"\nSuccessfully added {programs_added} programs!")
            print(f"Total programs now: {Program.query.count()}")
            
            # Show summary
            degree_count = Program.query.filter_by(level='degree').count()
            diploma_count = Program.query.filter_by(level='diploma').count()
            hec_count = Program.query.filter_by(level='hec').count()
            
            print(f"\nProgram summary:")
            print(f"  Degree programs: {degree_count}")
            print(f"  Diploma programs: {diploma_count}")
            print(f"  HEC programs: {hec_count}")
            
        except Exception as e:
            print(f"Error adding programs: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    add_diploma_hec_programs()