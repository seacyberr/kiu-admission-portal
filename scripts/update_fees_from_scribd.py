#!/usr/bin/env python3
"""Update seed-programs.json with actual KIU fees from scribd.com brochures."""

import json
import os

# Actual fees from KIU Main Campus Brochure January 2025
# Based on the provided fee data from scribd.com screenshots

MAIN_CAMPUS_FEES = {
    # Certificate Programs - 330,000 UGX per semester (National Certificates)
    "certificate": {
        "tuition_per_semester_ugx": 330000,
        "functional_fees_ugx": 200000,  # Standard functional fees
    },
    
    # Diploma Programs - 500,000 UGX per semester
    "diploma": {
        "tuition_per_semester_ugx": 500000,
        "functional_fees_ugx": 350000,
    },
    
    # Bachelor's Degrees - varies by program
    "degree": {
        # College of Economics and Management
        "BBA": {"tuition": 700, "functional": 353},
        "BBA-FA": {"tuition": 700, "functional": 353},
        "BBA-FB": {"tuition": 700, "functional": 353},
        "BBA-IB": {"tuition": 700, "functional": 353},
        "BBA-MKT": {"tuition": 700, "functional": 353},
        "BAEC": {"tuition": 700, "functional": 353},
        "BAME": {"tuition": 700, "functional": 353},
        "BAE": {"tuition": 700, "functional": 353},
        "BAERI": {"tuition": 700, "functional": 353},
        "BHRM": {"tuition": 700, "functional": 353},
        "BSPM": {"tuition": 700, "functional": 353},
        "BTHM": {"tuition": 700, "functional": 353},
        "BESBM": {"tuition": 700, "functional": 353},
        "BEAS": {"tuition": 700, "functional": 353},
        "BCOM-DL": {"tuition": 700, "functional": 353},
        "BBA-DL": {"tuition": 700, "functional": 353},
        
        # College of Humanities and Social Sciences
        "BAIRDS": {"tuition": 700, "functional": 353},
        "BAMC": {"tuition": 700, "functional": 353},
        "BAPA": {"tuition": 700, "functional": 353},
        "BASWSA": {"tuition": 700, "functional": 353},
        "BDS": {"tuition": 700, "functional": 353},
        "BGC": {"tuition": 700, "functional": 353},
        "BSCD": {"tuition": 700, "functional": 353},
        "BLIS": {"tuition": 700, "functional": 353},
        "BPA": {"tuition": 700, "functional": 353},
        
        # School of Law
        "LLB-DAY": {"tuition": 700, "functional": 353},
        "LLB-WE": {"tuition": 700, "functional": 353},
        
        # School of Mathematics & Computing
        "DCS": {"tuition": 500, "functional": 350},  # Diploma
        "DLIS": {"tuition": 500, "functional": 350},  # Diploma
        "DIT": {"tuition": 500, "functional": 350},  # Diploma
        "BCS": {"tuition": 700, "functional": 353},
        "BIT": {"tuition": 700, "functional": 353},
        "BSE": {"tuition": 700, "functional": 353},
        
        # College of Education
        "BAED": {"tuition": 700, "functional": 353},
        "BSED": {"tuition": 700, "functional": 353},
        "BCSED": {"tuition": 700, "functional": 353},
        "BEd-SNE": {"tuition": 700, "functional": 353},
        
        # Faculty of Engineering
        "BCE": {"tuition": 700, "functional": 353},
        "BEE": {"tuition": 700, "functional": 353},
        "BME": {"tuition": 700, "functional": 353},
        "BCmpE": {"tuition": 700, "functional": 353},
        "BTE": {"tuition": 700, "functional": 353},
        
        # Faculty of Science and Technology
        "BSc-PHYS": {"tuition": 700, "functional": 353},
        "BSc-CHEM": {"tuition": 700, "functional": 353},
        "BSc-MATH": {"tuition": 700, "functional": 353},
        "BSc-STAT": {"tuition": 700, "functional": 353},
        "BSc-ENVM": {"tuition": 700, "functional": 353},
        "BSc-WMCM": {"tuition": 700, "functional": 353},
        "BSc-IC": {"tuition": 700, "functional": 353},
        
        # Health Sciences (Western Campus) - Higher fees
        "MBChB": {"tuition": 2852300, "functional": 700},
        "BPharm": {"tuition": 2852300, "functional": 700},
        "BDS-DENT": {"tuition": 2852300, "functional": 700},
        "BNS-DIRECT": {"tuition": 2852300, "functional": 700},
        "BNS-EXT": {"tuition": 2852300, "functional": 700},
        "BCMCH-DIRECT": {"tuition": 2852300, "functional": 700},
        "BCMCH-EXT": {"tuition": 2852300, "functional": 700},
        "BMLS-DIRECT": {"tuition": 2852300, "functional": 700},
        "BMLS-EXT": {"tuition": 2852300, "functional": 700},
        "BPH": {"tuition": 2852300, "functional": 700},
        "BSc-ANAT": {"tuition": 2852300, "functional": 700},
        "BSc-BIOCHEM": {"tuition": 2852300, "functional": 700},
        "BSc-PHYSIO": {"tuition": 2852300, "functional": 700},
        "BSc-MICRO": {"tuition": 2852300, "functional": 700},
        "BSc-PHARM": {"tuition": 2852300, "functional": 700},
        "BSc-MRIT": {"tuition": 2852300, "functional": 700},
        "BSc-PHT": {"tuition": 2852300, "functional": 700},
    },
    
    # Postgraduate Diploma
    "postgraduate_diploma": {
        "tuition_per_semester_usd": 660,
        "functional_fees_usd": 500,  # Research fee paid once
    },
    
    # Master's Degrees
    "masters": {
        "tuition_per_semester_usd": 825,  # Most programs
        "mba_tuition_per_semester_usd": 1188,  # MBA programs
        "functional_fees_usd": 500,  # Research fee paid once
        "other_fees_per_semester": 150,
    },
    
    # PhD Programs
    "phd": {
        "tuition_per_semester_usd": 3300,
        "functional_fees_usd": 650,  # Research fee paid once
    },
}

# Convert semester fees to annual (multiply by 2 for 2 semesters per year)
def convert_to_annual(semester_fee):
    """Convert semester fee to annual fee."""
    return semester_fee * 2

def update_fees():
    """Update seed-programs.json with actual fees."""
    seed_path = os.path.join(os.path.dirname(__file__), '..', 'apps', 'flask-api', 'data', 'seed-programs.json')
    
    with open(seed_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    updated_count = 0
    
    for program in data.get('programs', []):
        code = program.get('code', '').upper()
        level = program.get('level', '')
        
        # Update fees based on program level and code
        if level == 'certificate':
            fees = MAIN_CAMPUS_FEES['certificate']
            program['feesInternational'] = convert_to_annual(fees['tuition_per_semester_ugx'])
            program['functionalFeesInternational'] = fees['functional_fees_ugx']
            updated_count += 1
            
        elif level == 'diploma':
            fees = MAIN_CAMPUS_FEES['diploma']
            program['feesInternational'] = convert_to_annual(fees['tuition_per_semester_ugx'])
            program['functionalFeesInternational'] = fees['functional_fees_ugx']
            updated_count += 1
            
        elif level == 'degree':
            degree_fees = MAIN_CAMPUS_FEES['degree']
            if code in degree_fees:
                program['feesInternational'] = convert_to_annual(degree_fees[code]['tuition'])
                program['functionalFeesInternational'] = degree_fees[code]['functional']
                updated_count += 1
            else:
                # Default degree fees
                program['feesInternational'] = convert_to_annual(836)
                program['functionalFeesInternational'] = 353
                updated_count += 1
                
        elif level == 'masters':
            fees = MAIN_CAMPUS_FEES['masters']
            if 'MBA' in code or 'mba' in code.lower():
                program['feesInternational'] = convert_to_annual(fees['mba_tuition_per_semester_usd'])
            else:
                program['feesInternational'] = convert_to_annual(fees['tuition_per_semester_usd'])
            program['functionalFeesInternational'] = fees['functional_fees_usd']
            updated_count += 1
            
        elif level == 'phd':
            fees = MAIN_CAMPUS_FEES['phd']
            program['feesInternational'] = convert_to_annual(fees['tuition_per_semester_usd'])
            program['functionalFeesInternational'] = fees['functional_fees_usd']
            updated_count += 1
    
    # Save updated data
    with open(seed_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Updated {updated_count} programs with actual KIU fees from scribd.com")
    print(f"📁 File saved: {seed_path}")

if __name__ == '__main__':
    update_fees()