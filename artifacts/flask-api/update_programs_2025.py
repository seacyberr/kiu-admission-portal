#!/usr/bin/env python3
"""
Script to update KIU programs for 2025/2026 academic year.
This script reads from seed-programs.json and updates the database.
"""

import json
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app
from models import db, Program

def update_programs():
    """Update programs in the database from seed-programs.json"""
    
    # Read the seed programs
    seed_file = Path(__file__).parent / "seed-programs.json"
    with open(seed_file, 'r') as f:
        data = json.load(f)
    
    programs = data.get('programs', [])
    
    print(f"Found {len(programs)} programs to update")
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        # Get existing programs
        existing_programs = {p.code: p for p in Program.query.all()}
        print(f"Found {len(existing_programs)} existing programs in database")
        
        updated_count = 0
        created_count = 0
        
        for program_data in programs:
            code = program_data['code']
            
            if code in existing_programs:
                # Update existing program
                program = existing_programs[code]
                program.name = program_data['name']
                program.faculty = program_data['faculty']
                program.level = program_data['level']
                program.duration = program_data['duration']
                program.campus = program_data['campus']
                program.description = program_data.get('description', '')
                program.entry_requirements = program_data.get('entryRequirements', '')
                program.min_olevel_points = program_data.get('minOlevelPoints')
                program.min_alevel_points = program_data.get('minAlevelPoints')
                program.available_slots = program_data.get('availableSlots', 100)
                updated_count += 1
                print(f"  Updated: {code} - {program_data['name']}")
            else:
                # Create new program
                program = Program(
                    name=program_data['name'],
                    code=code,
                    faculty=program_data['faculty'],
                    level=program_data['level'],
                    duration=program_data['duration'],
                    campus=program_data['campus'],
                    description=program_data.get('description', ''),
                    entry_requirements=program_data.get('entryRequirements', ''),
                    min_olevel_points=program_data.get('minOlevelPoints'),
                    min_alevel_points=program_data.get('minAlevelPoints'),
                    available_slots=program_data.get('availableSlots', 100)
                )
                db.session.add(program)
                created_count += 1
                print(f"  Created: {code} - {program_data['name']}")
        
        # Commit changes
        db.session.commit()
        
        print(f"\nSummary:")
        print(f"  Created: {created_count} new programs")
        print(f"  Updated: {updated_count} existing programs")
        print(f"  Total: {created_count + updated_count} programs processed")
        
        # Verify final count
        final_count = Program.query.count()
        print(f"  Final database count: {final_count} programs")

if __name__ == '__main__':
    update_programs()