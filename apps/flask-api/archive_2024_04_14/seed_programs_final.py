"""
KIU FINAL PROGRAM STRUCTURE
Generated from definitive master list provided by user
"""

import json
import uuid

FINAL_STRUCTURE = [
    # 1. FACULTY OF HEALTH SCIENCES - WESTERN CAMPUS
    {
        "faculty": "Faculty of Health Sciences",
        "campus": "Western",
        "programs": [
            # Bachelor Programmes
            ("Bachelor of Medicine and Bachelor of Surgery", "bachelors", "MBBS", 5),
            ("Bachelor of Nursing Science", "bachelors", "BNS", 4),
            ("Bachelor of Midwifery", "bachelors", "BMID", 4),
            ("Bachelor of Pharmacy", "bachelors", "BPHARM", 4),
            ("Bachelor of Dental Surgery", "bachelors", "BDS", 4),
            ("Bachelor of Medical Laboratory Science", "bachelors", "BMLS", 4),
            ("Bachelor of Public Health", "bachelors", "BPH", 3),
            ("Bachelor of Biotechnology", "bachelors", "BBT", 3),
            # Diploma Programmes
            ("Diploma in Nursing", "diploma", "DN", 3),
            ("Diploma in Midwifery", "diploma", "DMID", 3),
            ("Diploma in Clinical Medicine", "diploma", "DCM", 3),
            ("Diploma in Pharmacy", "diploma", "DPHARM", 3),
            ("Diploma in Medical Laboratory Science", "diploma", "DMLS", 3),
            ("Diploma in Radiography", "diploma", "DRAD", 3),
            # Certificate Programmes
            ("Certificate in Nursing", "certificate", "CERT-N", 2),
            ("Certificate in Midwifery", "certificate", "CERT-MID", 2),
            # Master's Programmes - Medicine
            ("Master of Medicine in Internal Medicine", "masters", "MM-IM", 3),
            ("Master of Medicine in Surgery", "masters", "MM-SURG", 3),
            ("Master of Medicine in Paediatrics and Child Health", "masters", "MM-PCH", 3),
            ("Master of Medicine in Obstetrics and Gynaecology", "masters", "MM-OG", 3),
            ("Master of Medicine in Psychiatry", "masters", "MM-PSY", 3),
            ("Master of Public Health", "masters", "MPH", 2),
            ("Master of Science in Nursing", "masters", "MSN", 2),
            ("Master of Science in Midwifery", "masters", "MSM", 2),
            ("Master of Science in Medical Laboratory Science", "masters", "MSMLS", 2),
            ("Master of Dental Surgery", "masters", "MDS", 2),
            # Biomedical Sciences (Postgraduate)
            ("Master of Science in Anatomy", "masters", "MS-ANAT", 2),
            ("Master of Science in Physiology", "masters", "MS-PHYS", 2),
            ("Master of Science in Biochemistry", "masters", "MS-BIOC", 2),
            ("Master of Science in Microbiology", "masters", "MS-MICRO", 2),
            ("Doctor of Philosophy in Anatomy", "phd", "PhD-ANAT", 3),
            ("Doctor of Philosophy in Physiology", "phd", "PhD-PHYS", 3),
            ("Doctor of Philosophy in Biochemistry", "phd", "PhD-BIOC", 3),
            ("Doctor of Philosophy in Microbiology", "phd", "PhD-MICRO", 3),
            ("Doctor of Philosophy in Biomedical Sciences", "phd", "PhD-BMS", 3),
        ]
    },
    # 2. FACULTY OF BUSINESS & MANAGEMENT - MAIN & WESTERN
    {
        "faculty": "Faculty of Business and Management",
        "campus": "Both",
        "programs": [
            # Bachelor Programmes
            ("Bachelor of Business Administration", "bachelors", "BBA", 3),
            ("Bachelor of Commerce", "bachelors", "BCOM", 3),
            ("Bachelor of Accounting and Finance", "bachelors", "BAF", 3),
            ("Bachelor of Human Resource Management", "bachelors", "BHRM", 3),
            ("Bachelor of Procurement and Supply Chain Management", "bachelors", "BPSCM", 3),
            ("Bachelor of Economics", "bachelors", "BECO", 3),
            # Diploma Programmes
            ("Diploma in Business Administration", "diploma", "DBA", 2),
            ("Diploma in Accounting and Finance", "diploma", "DAF", 2),
            ("Diploma in Human Resource Management", "diploma", "DHRM", 2),
            ("Diploma in Procurement and Supply Chain Management", "diploma", "DPSCM", 2),
            ("Diploma in Public Administration", "diploma", "DPA", 2),
            ("Diploma in Banking and Finance", "diploma", "DBF", 2),
            ("Diploma in Insurance and Risk Management", "diploma", "DIRM", 2),
            # Certificate Programmes
            ("Certificate in Business Administration", "certificate", "CERT-BA", 1),
            # Master's Programmes
            ("Master of Business Administration", "masters", "MBA", 2),
            ("Master of Science in Accounting and Finance", "masters", "MSAF", 2),
            ("Master of Science in Marketing", "masters", "MSMKT", 2),
            ("Master of Science in Human Resource Management", "masters", "MSHRM", 2),
            ("Master of Science in Procurement and Supply Chain Management", "masters", "MSPSCM", 2),
            ("Master of Science in Economics", "masters", "MSEC", 2),
            ("Master of Public Administration", "masters", "MPA", 2),
            ("Master of Development Studies", "masters", "MDS", 2),
            # PhD Programmes
            ("Doctor of Philosophy in Business Administration", "phd", "PhD-BA", 3),
        ]
    },
    # 3. FACULTY OF COMPUTING & IT - MAIN CAMPUS
    {
        "faculty": "Faculty of Computing and IT",
        "campus": "Main",
        "programs": [
            # Bachelor Programmes
            ("Bachelor of Information Technology", "bachelors", "BIT", 3),
            ("Bachelor of Computer Science", "bachelors", "BCS", 3),
            ("Bachelor of Software Engineering", "bachelors", "BSE", 3),
            ("Bachelor of Data Communication and Networking", "bachelors", "BDCN", 3),
            # Master's Programmes
            ("Master of Science in Information Technology", "masters", "MSIT", 2),
            ("Master of Science in Computer Science", "masters", "MSCS", 2),
            # PhD Programmes
            ("Doctor of Philosophy in Computer Science", "phd", "PhD-CS", 3),
        ]
    },
    # 4. FACULTY OF LAW - BOTH CAMPUSES
    {
        "faculty": "Faculty of Law",
        "campus": "Both",
        "programs": [
            # Bachelor Programmes
            ("Bachelor of Laws", "bachelors", "LLB", 4),
            # Diploma Programmes
            ("Diploma in Law", "diploma", "DLAW", 2),
            # Master's Programmes
            ("Master of Laws", "masters", "LLM", 2),
            # PhD Programmes
            ("Doctor of Philosophy in Law", "phd", "PhD-LAW", 3),
        ]
    },
    # 5. FACULTY OF EDUCATION - BOTH CAMPUSES
    {
        "faculty": "Faculty of Education",
        "campus": "Both",
        "programs": [
            # Bachelor Programmes
            ("Bachelor of Education in Arts", "bachelors", "BED-ARTS", 3),
            ("Bachelor of Education in Science", "bachelors", "BED-SCI", 3),
            ("Bachelor of Early Childhood Education", "bachelors", "BECE", 3),
            ("Bachelor of Primary Education", "bachelors", "BPE", 3),
            # Postgraduate Diploma
            ("Postgraduate Diploma in Education", "pgd", "PGDE", 1),
            # Master's Programmes
            ("Master of Education in Educational Administration and Management", "masters", "MED-EAM", 2),
            ("Master of Education in Curriculum and Instruction", "masters", "MED-CI", 2),
            ("Master of Education in Guidance and Counselling", "masters", "MED-GC", 2),
            ("Master of Education in Early Childhood Education", "masters", "MED-ECE", 2),
            # PhD Programmes
            ("Doctor of Philosophy in Education", "phd", "PhD-ED", 3),
            ("Doctor of Philosophy in Educational Administration", "phd", "PhD-EA", 3),
            ("Doctor of Philosophy in Curriculum Studies", "phd", "PhD-CS", 3),
            ("Doctor of Philosophy in Educational Psychology", "phd", "PhD-EP", 3),
        ]
    },
    # 6. FACULTY OF SOCIAL SCIENCES - MAIN CAMPUS
    {
        "faculty": "Faculty of Social Sciences",
        "campus": "Main",
        "programs": [
            # Bachelor Programmes
            ("Bachelor of Mass Communication", "bachelors", "BMC", 3),
            ("Bachelor of International Relations", "bachelors", "BIR", 3),
            ("Bachelor of Social Work and Social Administration", "bachelors", "BSWSA", 3),
            ("Bachelor of Economics and Statistics", "bachelors", "BES", 3),
            # Master's Programmes
            ("Master of Arts in International Relations", "masters", "MA-IR", 2),
            ("Master of Arts in Mass Communication", "masters", "MA-MC", 2),
        ]
    },
    # 7. FACULTY OF ENVIRONMENTAL SCIENCE - MAIN CAMPUS
    {
        "faculty": "Faculty of Environmental Science",
        "campus": "Main",
        "programs": [
            # Bachelor Programmes
            ("Bachelor of Environmental Science", "bachelors", "BENV", 3),
            # Master's Programmes
            ("Master of Science in Environmental Science", "masters", "MSES", 2),
            # PhD Programmes
            ("Doctor of Philosophy in Environmental Science", "phd", "PhD-ENV", 3),
        ]
    },
]

# Generate all programs
new_programs = []
code_tracker = {}

for faculty_data in FINAL_STRUCTURE:
    faculty = faculty_data["faculty"]
    campus = faculty_data["campus"]
    
    for prog_name, level, code, duration in faculty_data["programs"]:
        # Ensure unique code
        base_code = code
        counter = 1
        while code in code_tracker:
            code = f"{base_code}-{counter}"
            counter += 1
        code_tracker[code] = prog_name
        
        # Create program entry
        program = {
            "id": str(uuid.uuid4()),
            "name": prog_name,
            "code": code,
            "level": level,
            "campus": campus,
            "duration": duration,
            "faculty": faculty,
            "nche_accredited": True,
            "nche_status": "Fully Accredited",
            "tuition_ugx": 0,
            "tuition_usd": 0,
            "intake_months": [8, 1],
            "requirements": {
                "min_points": 4,
                "min_principals": 2
            },
            "required_subjects": [],
            "description": f"{prog_name} program at KIU {campus} Campus"
        }
        
        new_programs.append(program)

# Save to seed-programs.json
output_data = {
    "metadata": {
        "version": "5.0",
        "last_updated": "2025-04-14",
        "total_programs": len(new_programs),
        "source": "KIU Final Faculty Structure 2025"
    },
    "programs": new_programs
}

with open('seed-programs.json', 'w') as f:
    json.dump(output_data, f, indent=2)

print(f"✅ Generated {len(new_programs)} programs")
print(f"✅ Saved to seed-programs.json")
