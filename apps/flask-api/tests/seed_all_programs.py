#!/usr/bin/env python3
"""Seed all KIU programs into the database from the catalog"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

os.environ["DATABASE_URL"] = "mysql+pymysql://admin:adekunle%2312@localhost/kiu_admissions"
os.environ["SEED_DATABASE"] = "false"
os.environ["JWT_SECRET"] = "test-secret-key-for-development"
os.environ["FLASK_ENV"] = "development"

from app import create_app
from models import db, Program

# Import program data
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'data'))
from data import (
    PHD_PROGRAMS,
    MASTERS_PROGRAMS,
    PGD_PROGRAMS,
    BACHELORS_PROGRAMS,
    DIPLOMA_PROGRAMS,
    CERTIFICATE_PROGRAMS,
    HEC_PROGRAMS,
)

def generate_code(name, level, existing_code=None):
    """Generate a program code from name and level, or use existing code if provided"""
    # If program already has a code defined, use it
    if existing_code:
        return existing_code
    
    import re
    # Remove special characters and convert to uppercase
    clean = re.sub(r'[^\w\s]', '', name).upper()
    # Get first letter of each word
    words = clean.split()
    code = ''.join(w[0] for w in words[:4] if w)
    # Add level suffix
    level_suffix = {
        'phd': 'PHD',
        'masters': 'MSC',
        'pgd': 'PGD',
        'degree': 'BSC',
        'diploma': 'DIP',
        'certificate': 'CERT',
        'hec': 'HEC'
    }.get(level, 'PRG')
    return f"{level_suffix}-{code[:6]}-001"

def seed_programs():
    """Seed all programs from the KIU catalog"""
    app = create_app()
    
    with app.app_context():
        existing_codes = {p.code for p in Program.query.all()}
        
        programs_to_add = []
        
        # Combine all program lists
        all_programs_data = [
            (PHD_PROGRAMS, 'phd', 'Postgraduate'),
            (MASTERS_PROGRAMS, 'masters', 'Postgraduate'),
            (PGD_PROGRAMS, 'pgd', 'Postgraduate'),
            (BACHELORS_PROGRAMS, 'degree', 'Undergraduate'),
            (DIPLOMA_PROGRAMS, 'diploma', 'Undergraduate'),
            (CERTIFICATE_PROGRAMS, 'certificate', 'Undergraduate'),  # Certificate programs (1-2.5 years)
            (HEC_PROGRAMS, 'hec', 'Undergraduate'),
        ]
        
        for program_list, level, faculty_base in all_programs_data:
            for prog_data in program_list:
                name = prog_data['name']
                # Use predefined code if available, otherwise generate one
                existing_code = prog_data.get('code')
                code = generate_code(name, level, existing_code)
                
                # Skip if already exists
                if code in existing_codes or any(p.name == name for p in Program.query.all()):
                    print(f"Skipping existing: {name}")
                    continue
                
                # Determine faculty based on category
                category = prog_data.get('category', 'general')
                faculty_map = {
                    'business': 'Faculty of Business and Management',
                    'engineering': 'Faculty of Engineering',
                    'health_sciences': 'School of Health Sciences',
                    'medicine': 'School of Medicine',
                    'agriculture': 'Faculty of Agriculture',
                    'technology': 'Faculty of Science and Technology',
                    'education': 'Faculty of Education',
                    'law': 'Faculty of Law',
                    'social_sciences': 'Faculty of Social Sciences',
                    'economics': 'Faculty of Economics',
                    'tourism': 'Faculty of Tourism',
                    'communication': 'Faculty of Mass Communication',
                    'psychology': 'Faculty of Psychology',
                    'administration': 'Faculty of Public Administration',
                    'international': 'Faculty of International Relations',
                    'social_work': 'Faculty of Social Work',
                    'development': 'Faculty of Development Studies',
                    'language': 'Faculty of Languages and Communication Skills',
                }
                faculty = faculty_map.get(category, faculty_base)
                
                # Build entry requirements string
                reqs = prog_data.get('requirements', [])
                entry_req = "Entry: " + ", ".join(reqs)
                if 'min_principals' in prog_data:
                    entry_req += f" | Min {prog_data['min_principals']} principals"
                
                program = Program(
                    name=name,
                    code=code,
                    faculty=faculty,
                    department=f"Department of {category.title().replace('_', ' ')}",
                    level=level,
                    duration=prog_data.get('duration', 'N/A'),
                    description=f"{name} program at KIU. {prog_data.get('note', '')}",
                    entryRequirements=entry_req,
                    availableSlots=50,
                    campus=prog_data.get('campus', 'Main'),
                    active=True
                )
                
                programs_to_add.append(program)
                print(f"Prepared: {name} ({code})")
        
        # Add all programs
        if programs_to_add:
            db.session.add_all(programs_to_add)
            db.session.commit()
            print(f"\nSUCCESS: Successfully added {len(programs_to_add)} programs!")
        else:
            print("\nINFO No new programs to add (all already exist)")
        
        print(f"\nTotal programs in database: {Program.query.count()}")

if __name__ == "__main__":
    seed_programs()
