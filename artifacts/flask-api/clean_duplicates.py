#!/usr/bin/env python3
"""
Clean up duplicate programs from the database.
Keeps only the programs that match the website codes.
"""

from app import create_app
from models import db, Program, AdmissionApplication

# Correct program codes from website
CORRECT_DIPLOMA_CODES = {
    "DIP-LAW-DAY", "DIP-DS", "DIP-GC", "DIP-IR", "DIP-MC", "DIP-PA", "DIP-SCD", "DIP-SWSA",
    "DIP-BA", "DIP-HRM", "DIP-SS", "DIP-SPM", "DIP-THM", "DIP-AE", "DIP-CE", "DIP-EE",
    "DIP-ME", "DIP-TE", "DIP-CMCH", "DIP-MLS", "DIP-MR", "DIP-NUR-D", "DIP-NUR-E", "DIP-PHARM",
    "DIP-CS", "DIP-EDU-SA"
}

CORRECT_HEC_CODES = {
    "HEC-BC", "HEC-BP", "HEC-CM", "HEC-EM", "HEC-GE", "HEC-GEnt", "HEC-GH", "HEC-GM",
    "HEC-HE", "HEC-HEnt", "HEC-HRE", "HEC-LG", "HEC-LH", "HEC-LRE", "HEC-MEnt", "HEC-PM",
    "HEC-REE", "HEC-REEnt"
}

CORRECT_DEGREE_CODES = {
    "LLB-DAY", "LLB-WE", "BA-IRDS", "BA-MC", "BA-PA", "BA-SWSA", "BDS", "BGC", "BSCD",
    "BA-ECON", "BBA-FA", "BBA-FB", "BBA-IB", "BBA-MKT", "BEAS", "BESBM", "BHRM", "BSPM",
    "BTHM", "BSc-CE", "BSc-CompE", "BSc-EE", "BSc-ME", "BSc-TE", "BDS-DENTAL", "MBChB",
    "BMLS-D", "BCMCH-D", "BCMCH-E", "BMLS-E", "BSc-MRIT", "BSc-PT", "BNS-D", "BNS-E",
    "BPharm", "BSc-PHARM", "BSc-ANAT", "BSc-BIOCHEM", "BSc-MICRO", "BSc-PHYSIO", "BCS",
    "BIT", "BA-EDU", "BA-EDU-FA", "BEd-AP-I", "BEd-AS-I", "BEd-ECPE-I", "BEd-SNE-I"
}

ALL_CORRECT_CODES = CORRECT_DIPLOMA_CODES | CORRECT_HEC_CODES | CORRECT_DEGREE_CODES


def clean_duplicates():
    """Remove duplicate programs from database."""
    app = create_app()
    
    with app.app_context():
        print("Starting duplicate cleanup...")
        
        # Get all programs
        all_programs = Program.query.all()
        print(f"Total programs before cleanup: {len(all_programs)}")
        
        # Find duplicates
        code_counts = {}
        for program in all_programs:
            code_counts[program.code] = code_counts.get(program.code, 0) + 1
        
        duplicates = {code: count for code, count in code_counts.items() if count > 1}
        print(f"Found {len(duplicates)} duplicate codes:")
        for code, count in duplicates.items():
            print(f"  - {code}: {count} copies")
        
        # Remove duplicates (keep the first one)
        removed_count = 0
        for code, count in duplicates.items():
            programs_with_code = Program.query.filter_by(code=code).all()
            # Keep the first one, remove the rest
            for program in programs_with_code[1:]:
                # Check if program has applications
                has_applications = AdmissionApplication.query.filter_by(program_id=program.id).first()
                if not has_applications:
                    db.session.delete(program)
                    removed_count += 1
                    print(f"  Removed duplicate: {program.name} ({program.code})")
                else:
                    print(f"  Kept duplicate (has applications): {program.name} ({program.code})")
        
        # Also remove programs with incorrect codes (not in website)
        incorrect_codes_removed = 0
        for program in all_programs:
            if program.code not in ALL_CORRECT_CODES:
                # Check if program has applications
                has_applications = AdmissionApplication.query.filter_by(program_id=program.id).first()
                if not has_applications:
                    db.session.delete(program)
                    incorrect_codes_removed += 1
                    print(f"  Removed incorrect code: {program.name} ({program.code})")
                else:
                    print(f"  Kept incorrect code (has applications): {program.name} ({program.code})")
        
        # Commit changes
        db.session.commit()
        
        # Verify counts
        total = Program.query.count()
        degree_count = Program.query.filter_by(level="degree").count()
        diploma_count = Program.query.filter_by(level="diploma").count()
        hec_count = Program.query.filter_by(level="hec").count()
        
        print(f"\nCleanup complete!")
        print(f"Removed {removed_count} duplicates and {incorrect_codes_removed} incorrect codes")
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
    clean_duplicates()