#!/usr/bin/env python3
"""
Update programs database with correct data from KIU website.
Updates existing programs and adds new ones without deleting (to preserve foreign keys).
"""

from app import create_app
from models import db, Program

# Programs fetched from https://www.kiu.ac.ug/programmes-catalogue.php
DIPLOMA_PROGRAMS = [
    {"name": "Diploma in Law (Day)", "code": "DIP-LAW-DAY", "faculty": "Faculty of Law", "level": "diploma", "duration": "2 years", "campus": "kampala"},
    {"name": "Diploma in Development Studies", "code": "DIP-DS", "faculty": "Faculty of Social Sciences", "level": "diploma", "duration": "2 years", "campus": "kampala"},
    {"name": "Diploma in Guidance and Counselling", "code": "DIP-GC", "faculty": "Faculty of Social Sciences", "level": "diploma", "duration": "2 years", "campus": "kampala"},
    {"name": "Diploma in International Relations and Diplomatic Studies", "code": "DIP-IR", "faculty": "Faculty of Social Sciences", "level": "diploma", "duration": "2 years", "campus": "kampala"},
    {"name": "Diploma in Mass Communication", "code": "DIP-MC", "faculty": "Faculty of Social Sciences", "level": "diploma", "duration": "2 years", "campus": "kampala"},
    {"name": "Diploma in Public Administration", "code": "DIP-PA", "faculty": "Faculty of Social Sciences", "level": "diploma", "duration": "2 years", "campus": "kampala"},
    {"name": "Diploma in Social and Community Development", "code": "DIP-SCD", "faculty": "Faculty of Social Sciences", "level": "diploma", "duration": "2 years", "campus": "kampala"},
    {"name": "Diploma in Social Work and Social Administration", "code": "DIP-SWSA", "faculty": "Faculty of Social Sciences", "level": "diploma", "duration": "2 years", "campus": "kampala"},
    {"name": "Diploma in Business Administration", "code": "DIP-BA", "faculty": "Faculty of Business and Management", "level": "diploma", "duration": "2 years", "campus": "kampala"},
    {"name": "Diploma in Human Resource Management", "code": "DIP-HRM", "faculty": "Faculty of Business and Management", "level": "diploma", "duration": "2 years", "campus": "kampala"},
    {"name": "Diploma in Secretarial Studies", "code": "DIP-SS", "faculty": "Faculty of Business and Management", "level": "diploma", "duration": "2 years", "campus": "kampala"},
    {"name": "Diploma in Supplies and Procurement Management", "code": "DIP-SPM", "faculty": "Faculty of Business and Management", "level": "diploma", "duration": "2 years", "campus": "kampala"},
    {"name": "Diploma in Tourism and Hotel Management", "code": "DIP-THM", "faculty": "Faculty of Business and Management", "level": "diploma", "duration": "2 years", "campus": "kampala"},
    {"name": "Diploma in Automotive Engineering", "code": "DIP-AE", "faculty": "Faculty of Science and Technology", "level": "diploma", "duration": "2 years", "campus": "kampala"},
    {"name": "Diploma in Civil Engineering", "code": "DIP-CE", "faculty": "Faculty of Science and Technology", "level": "diploma", "duration": "2 years", "campus": "kampala"},
    {"name": "Diploma in Electrical Engineering", "code": "DIP-EE", "faculty": "Faculty of Science and Technology", "level": "diploma", "duration": "2 years", "campus": "kampala"},
    {"name": "Diploma in Mechanical Engineering", "code": "DIP-ME", "faculty": "Faculty of Science and Technology", "level": "diploma", "duration": "2 years", "campus": "kampala"},
    {"name": "Diploma in Telecommunication Engineering", "code": "DIP-TE", "faculty": "Faculty of Science and Technology", "level": "diploma", "duration": "2 years", "campus": "kampala"},
    {"name": "Diploma in Clinical Medicine and Community Health", "code": "DIP-CMCH", "faculty": "Faculty of Medicine", "level": "diploma", "duration": "2 years", "campus": "western"},
    {"name": "Diploma in Medical Laboratory Science", "code": "DIP-MLS", "faculty": "Faculty of Medicine", "level": "diploma", "duration": "2 years", "campus": "western"},
    {"name": "Diploma in Medical Radiography", "code": "DIP-MR", "faculty": "Faculty of Medicine", "level": "diploma", "duration": "2 years", "campus": "western"},
    {"name": "Diploma in Nursing Sciences (Direct)", "code": "DIP-NUR-D", "faculty": "Faculty of Medicine", "level": "diploma", "duration": "3 years", "campus": "western"},
    {"name": "Diploma in Nursing Sciences (Extension)", "code": "DIP-NUR-E", "faculty": "Faculty of Medicine", "level": "diploma", "duration": "2 years", "campus": "western"},
    {"name": "Diploma in Pharmacy", "code": "DIP-PHARM", "faculty": "Faculty of Medicine", "level": "diploma", "duration": "2 years", "campus": "western"},
    {"name": "Diploma in Computer Science", "code": "DIP-CS", "faculty": "Faculty of Science and Technology", "level": "diploma", "duration": "2 years", "campus": "kampala"},
    {"name": "Diploma in Secondary Education - Arts", "code": "DIP-EDU-SA", "faculty": "Faculty of Education", "level": "diploma", "duration": "2 years", "campus": "kampala"},
]

HEC_PROGRAMS = [
    {"name": "Higher Education Certificate in Biology and Chemistry", "code": "HEC-BC", "faculty": "Faculty of Science and Technology", "level": "hec", "duration": "1 year", "campus": "kampala"},
    {"name": "Higher Education Certificate in Biology and Physics", "code": "HEC-BP", "faculty": "Faculty of Science and Technology", "level": "hec", "duration": "1 year", "campus": "kampala"},
    {"name": "Higher Education Certificate in Chemistry and Mathematics", "code": "HEC-CM", "faculty": "Faculty of Science and Technology", "level": "hec", "duration": "1 year", "campus": "kampala"},
    {"name": "Higher Education Certificate in Economics and Mathematics", "code": "HEC-EM", "faculty": "Faculty of Business and Management", "level": "hec", "duration": "1 year", "campus": "kampala"},
    {"name": "Higher Education Certificate in Geography and Economics", "code": "HEC-GE", "faculty": "Faculty of Social Sciences", "level": "hec", "duration": "1 year", "campus": "kampala"},
    {"name": "Higher Education Certificate in Geography and Entrepreneurship", "code": "HEC-GEnt", "faculty": "Faculty of Social Sciences", "level": "hec", "duration": "1 year", "campus": "kampala"},
    {"name": "Higher Education Certificate in Geography and History", "code": "HEC-GH", "faculty": "Faculty of Social Sciences", "level": "hec", "duration": "1 year", "campus": "kampala"},
    {"name": "Higher Education Certificate in Geography and Mathematics", "code": "HEC-GM", "faculty": "Faculty of Social Sciences", "level": "hec", "duration": "1 year", "campus": "kampala"},
    {"name": "Higher Education Certificate in History and Economics", "code": "HEC-HE", "faculty": "Faculty of Social Sciences", "level": "hec", "duration": "1 year", "campus": "kampala"},
    {"name": "Higher Education Certificate in History and Entrepreneurship", "code": "HEC-HEnt", "faculty": "Faculty of Social Sciences", "level": "hec", "duration": "1 year", "campus": "kampala"},
    {"name": "Higher Education Certificate in History and Religious Education", "code": "HEC-HRE", "faculty": "Faculty of Social Sciences", "level": "hec", "duration": "1 year", "campus": "kampala"},
    {"name": "Higher Education Certificate in Literature and Geography", "code": "HEC-LG", "faculty": "Faculty of Social Sciences", "level": "hec", "duration": "1 year", "campus": "kampala"},
    {"name": "Higher Education Certificate in Literature and History", "code": "HEC-LH", "faculty": "Faculty of Social Sciences", "level": "hec", "duration": "1 year", "campus": "kampala"},
    {"name": "Higher Education Certificate in Literature and Religious Education", "code": "HEC-LRE", "faculty": "Faculty of Social Sciences", "level": "hec", "duration": "1 year", "campus": "kampala"},
    {"name": "Higher Education Certificate in Mathematics and Entrepreneurship", "code": "HEC-MEnt", "faculty": "Faculty of Science and Technology", "level": "hec", "duration": "1 year", "campus": "kampala"},
    {"name": "Higher Education Certificate in Physics and Mathematics", "code": "HEC-PM", "faculty": "Faculty of Science and Technology", "level": "hec", "duration": "1 year", "campus": "kampala"},
    {"name": "Higher Education Certificate in Religious Education and Economics", "code": "HEC-REE", "faculty": "Faculty of Social Sciences", "level": "hec", "duration": "1 year", "campus": "kampala"},
    {"name": "Higher Education Certificate in Religious Education and Entrepreneurship", "code": "HEC-REEnt", "faculty": "Faculty of Social Sciences", "level": "hec", "duration": "1 year", "campus": "kampala"},
]

DEGREE_PROGRAMS = [
    # Law
    {"name": "Bachelor of Laws (Day)", "code": "LLB-DAY", "faculty": "Faculty of Law", "level": "degree", "duration": "4 years", "campus": "kampala"},
    {"name": "Bachelor of Laws (Weekend)", "code": "LLB-WE", "faculty": "Faculty of Law", "level": "degree", "duration": "4 years", "campus": "kampala"},
    
    # Social Sciences
    {"name": "Bachelor of Arts in International Relations and Diplomatic Studies", "code": "BA-IRDS", "faculty": "Faculty of Social Sciences", "level": "degree", "duration": "3 years", "campus": "kampala"},
    {"name": "Bachelor of Arts in Mass Communication", "code": "BA-MC", "faculty": "Faculty of Social Sciences", "level": "degree", "duration": "3 years", "campus": "kampala"},
    {"name": "Bachelor of Arts in Public Administration", "code": "BA-PA", "faculty": "Faculty of Social Sciences", "level": "degree", "duration": "3 years", "campus": "kampala"},
    {"name": "Bachelor of Arts in Social Work And Social Administration", "code": "BA-SWSA", "faculty": "Faculty of Social Sciences", "level": "degree", "duration": "3 years", "campus": "kampala"},
    {"name": "Bachelor of Development Studies", "code": "BDS", "faculty": "Faculty of Social Sciences", "level": "degree", "duration": "3 years", "campus": "kampala"},
    {"name": "Bachelor of Guidance and Counseling", "code": "BGC", "faculty": "Faculty of Social Sciences", "level": "degree", "duration": "3 years", "campus": "kampala"},
    {"name": "Bachelor of Social and Community Development", "code": "BSCD", "faculty": "Faculty of Social Sciences", "level": "degree", "duration": "3 years", "campus": "kampala"},
    {"name": "Bachelor of Arts in Economics", "code": "BA-ECON", "faculty": "Faculty of Social Sciences", "level": "degree", "duration": "3 years", "campus": "kampala"},
    
    # Business and Management
    {"name": "Bachelor of Business Administration (Finance and Accounting)", "code": "BBA-FA", "faculty": "Faculty of Business and Management", "level": "degree", "duration": "3 years", "campus": "kampala"},
    {"name": "Bachelor of Business Administration (Finance and Banking)", "code": "BBA-FB", "faculty": "Faculty of Business and Management", "level": "degree", "duration": "3 years", "campus": "kampala"},
    {"name": "Bachelor of Business Administration (International Business)", "code": "BBA-IB", "faculty": "Faculty of Business and Management", "level": "degree", "duration": "3 years", "campus": "kampala"},
    {"name": "Bachelor of Business Administration (Marketing)", "code": "BBA-MKT", "faculty": "Faculty of Business and Management", "level": "degree", "duration": "3 years", "campus": "kampala"},
    {"name": "Bachelor of Economics and Applied Statistics", "code": "BEAS", "faculty": "Faculty of Business and Management", "level": "degree", "duration": "3 years", "campus": "kampala"},
    {"name": "Bachelor of Entrepreneurship & Small Business Management", "code": "BESBM", "faculty": "Faculty of Business and Management", "level": "degree", "duration": "3 years", "campus": "kampala"},
    {"name": "Bachelor of Human Resource Management", "code": "BHRM", "faculty": "Faculty of Business and Management", "level": "degree", "duration": "3 years", "campus": "kampala"},
    {"name": "Bachelor of Supplies and Procurement Management", "code": "BSPM", "faculty": "Faculty of Business and Management", "level": "degree", "duration": "3 years", "campus": "kampala"},
    {"name": "Bachelor of Tourism and Hotel Management", "code": "BTHM", "faculty": "Faculty of Business and Management", "level": "degree", "duration": "3 years", "campus": "kampala"},
    
    # Engineering
    {"name": "Bachelor of Science in Civil Engineering", "code": "BSc-CE", "faculty": "Faculty of Science and Technology", "level": "degree", "duration": "4 years", "campus": "kampala"},
    {"name": "Bachelor of Science in Computer Engineering", "code": "BSc-CompE", "faculty": "Faculty of Science and Technology", "level": "degree", "duration": "4 years", "campus": "kampala"},
    {"name": "Bachelor of Science in Electrical Engineering", "code": "BSc-EE", "faculty": "Faculty of Science and Technology", "level": "degree", "duration": "4 years", "campus": "kampala"},
    {"name": "Bachelor of Science in Mechanical Engineering", "code": "BSc-ME", "faculty": "Faculty of Science and Technology", "level": "degree", "duration": "4 years", "campus": "kampala"},
    {"name": "Bachelor of Science in Telecommunication Engineering", "code": "BSc-TE", "faculty": "Faculty of Science and Technology", "level": "degree", "duration": "4 years", "campus": "kampala"},
    
    # Medicine and Health Sciences
    {"name": "Bachelor of Dental Surgery", "code": "BDS-DENTAL", "faculty": "Faculty of Medicine", "level": "degree", "duration": "5 years", "campus": "western"},
    {"name": "Bachelor of Medicine and Bachelor of Surgery", "code": "MBChB", "faculty": "Faculty of Medicine", "level": "degree", "duration": "5 years", "campus": "western"},
    {"name": "Bachelor in Medical Laboratory Science (Direct)", "code": "BMLS-D", "faculty": "Faculty of Medicine", "level": "degree", "duration": "4 years", "campus": "western"},
    {"name": "Bachelor of Clinical Medicine and Community Health (Direct)", "code": "BCMCH-D", "faculty": "Faculty of Medicine", "level": "degree", "duration": "4 years", "campus": "western"},
    {"name": "Bachelor of Clinical Medicine and Community Health (Extension)", "code": "BCMCH-E", "faculty": "Faculty of Medicine", "level": "degree", "duration": "3 years", "campus": "western"},
    {"name": "Bachelor of Medical Laboratory Science (Extension)", "code": "BMLS-E", "faculty": "Faculty of Medicine", "level": "degree", "duration": "3 years", "campus": "western"},
    {"name": "Bachelor of Science in Medical Radiography and Imaging Technology", "code": "BSc-MRIT", "faculty": "Faculty of Medicine", "level": "degree", "duration": "4 years", "campus": "western"},
    {"name": "Bachelor of Science in Physiotherapy", "code": "BSc-PT", "faculty": "Faculty of Medicine", "level": "degree", "duration": "4 years", "campus": "western"},
    {"name": "Bachelor of Nursing Sciences (Direct Entry)", "code": "BNS-D", "faculty": "Faculty of Medicine", "level": "degree", "duration": "4 years", "campus": "western"},
    {"name": "Bachelor of Nursing Sciences (Extension) - Weekend", "code": "BNS-E", "faculty": "Faculty of Medicine", "level": "degree", "duration": "3 years", "campus": "western"},
    {"name": "Bachelor of Pharmacy", "code": "BPharm", "faculty": "Faculty of Medicine", "level": "degree", "duration": "4 years", "campus": "western"},
    {"name": "Bachelor of Science in Pharmacology", "code": "BSc-PHARM", "faculty": "Faculty of Medicine", "level": "degree", "duration": "3 years", "campus": "western"},
    {"name": "Bachelor of Science in Anatomy", "code": "BSc-ANAT", "faculty": "Faculty of Medicine", "level": "degree", "duration": "3 years", "campus": "western"},
    {"name": "Bachelor of Science in Biochemistry", "code": "BSc-BIOCHEM", "faculty": "Faculty of Medicine", "level": "degree", "duration": "3 years", "campus": "western"},
    {"name": "Bachelor of Science in Microbiology", "code": "BSc-MICRO", "faculty": "Faculty of Medicine", "level": "degree", "duration": "3 years", "campus": "western"},
    {"name": "Bachelor of Science in Physiology", "code": "BSc-PHYSIO", "faculty": "Faculty of Medicine", "level": "degree", "duration": "3 years", "campus": "western"},
    
    # Computer Science and IT
    {"name": "Bachelor of Computer Science", "code": "BCS", "faculty": "Faculty of Science and Technology", "level": "degree", "duration": "3 years", "campus": "kampala"},
    {"name": "Bachelor of Information Technology", "code": "BIT", "faculty": "Faculty of Science and Technology", "level": "degree", "duration": "3 years", "campus": "kampala"},
    
    # Education
    {"name": "Bachelor of Arts with Education", "code": "BA-EDU", "faculty": "Faculty of Education", "level": "degree", "duration": "3 years", "campus": "kampala"},
    {"name": "Bachelor of Arts with Education - Fine Art", "code": "BA-EDU-FA", "faculty": "Faculty of Education", "level": "degree", "duration": "3 years", "campus": "kampala"},
    {"name": "Bachelor of Education Arts Primary - Inservice", "code": "BEd-AP-I", "faculty": "Faculty of Education", "level": "degree", "duration": "3 years", "campus": "kampala"},
    {"name": "Bachelor of Education Arts Secondary - Inservice", "code": "BEd-AS-I", "faculty": "Faculty of Education", "level": "degree", "duration": "3 years", "campus": "kampala"},
    {"name": "Bachelor of Education in Early Childhood and Primary Education-Inservice", "code": "BEd-ECPE-I", "faculty": "Faculty of Education", "level": "degree", "duration": "3 years", "campus": "kampala"},
    {"name": "Bachelor of Education in Special Needs Education-Inservice", "code": "BEd-SNE-I", "faculty": "Faculty of Education", "level": "degree", "duration": "3 years", "campus": "kampala"},
]


def update_programs():
    """Update programs in database without deleting (to preserve foreign keys)."""
    app = create_app()
    
    with app.app_context():
        print("Starting program update...")
        
        # Get all programs from website
        all_website_programs = DIPLOMA_PROGRAMS + HEC_PROGRAMS + DEGREE_PROGRAMS
        
        # Create a set of website program codes for quick lookup
        website_codes = {p["code"] for p in all_website_programs}
        
        # Get existing programs from database
        existing_programs = Program.query.all()
        existing_codes = {p.code for p in existing_programs}
        
        print(f"Existing programs in database: {len(existing_programs)}")
        print(f"Programs from website: {len(all_website_programs)}")
        
        # Find programs to add (in website but not in database)
        codes_to_add = website_codes - existing_codes
        
        # Find programs to remove (in database but not in website)
        codes_to_remove = existing_codes - website_codes
        
        print(f"\nPrograms to add: {len(codes_to_add)}")
        print(f"Programs to remove: {len(codes_to_remove)}")
        
        # Add new programs
        added_count = 0
        for prog_data in all_website_programs:
            if prog_data["code"] in codes_to_add:
                program = Program(
                    name=prog_data["name"],
                    code=prog_data["code"],
                    faculty=prog_data["faculty"],
                    level=prog_data["level"],
                    duration=prog_data["duration"],
                    campus=prog_data["campus"],
                    available_slots=100
                )
                db.session.add(program)
                added_count += 1
                print(f"  Added: {prog_data['name']}")
        
        # Update existing programs
        updated_count = 0
        for prog_data in all_website_programs:
            if prog_data["code"] in existing_codes:
                program = Program.query.filter_by(code=prog_data["code"]).first()
                if program:
                    # Check if any fields need updating
                    needs_update = False
                    if program.name != prog_data["name"]:
                        program.name = prog_data["name"]
                        needs_update = True
                    if program.faculty != prog_data["faculty"]:
                        program.faculty = prog_data["faculty"]
                        needs_update = True
                    if program.duration != prog_data["duration"]:
                        program.duration = prog_data["duration"]
                        needs_update = True
                    if program.campus != prog_data["campus"]:
                        program.campus = prog_data["campus"]
                        needs_update = True
                    
                    if needs_update:
                        updated_count += 1
                        print(f"  Updated: {prog_data['name']}")
        
        # Mark programs for removal (don't delete if they have applications)
        removed_count = 0
        for code in codes_to_remove:
            program = Program.query.filter_by(code=code).first()
            if program:
                # Check if program has any applications
                from models import AdmissionApplication
                has_applications = AdmissionApplication.query.filter_by(program_id=program.id).first()
                
                if not has_applications:
                    db.session.delete(program)
                    removed_count += 1
                    print(f"  Removed: {program.name}")
                else:
                    print(f"  Kept (has applications): {program.name}")
        
        # Commit changes
        db.session.commit()
        
        # Verify counts
        total = Program.query.count()
        degree_count = Program.query.filter_by(level="degree").count()
        diploma_count = Program.query.filter_by(level="diploma").count()
        hec_count = Program.query.filter_by(level="hec").count()
        
        print(f"\nUpdate complete!")
        print(f"Added: {added_count}, Updated: {updated_count}, Removed: {removed_count}")
        print(f"\nTotal programs: {total}")
        print(f"  - Degree: {degree_count}")
        print(f"  - Diploma: {diploma_count}")
        print(f"  - HEC: {hec_count}")
        
        # Show programs by campus
        kampala_count = Program.query.filter_by(campus="kampala").count()
        western_count = Program.query.filter_by(campus="western").count()
        print(f"\nBy campus:")
        print(f"  - Kampala: {kampala_count}")
        print(f"  - Western: {western_count}")


if __name__ == "__main__":
    update_programs()