import json
import uuid
import re

# Load authoritative programs from user's JSON
with open('authoritative_programs.json', 'r') as f:
    AUTH_DATA = json.load(f)

# Process all programs
all_programs = []
seen_names = {}
code_tracker = {}

def normalize_name(name):
    normalized = name.lower().strip()
    normalized = normalized.replace("(by research)", "").replace("(in-service)", "").replace("(regular)", "")
    normalized = normalized.replace("(direct)", "").replace("(extension)", "").replace("-weekend", "")
    normalized = normalized.replace("day & evening", "").replace("areas of specialisation:", "")
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    return normalized

def get_level(name):
    name_lower = name.lower()
    if "certificate" in name_lower and "higher education" in name_lower:
        return "hec"
    elif "national certificate" in name_lower:
        return "national_certificate"
    elif "certificate" in name_lower:
        return "certificate"
    elif "postgraduate diploma" in name_lower:
        return "pgd"
    elif "diploma" in name_lower:
        return "diploma"
    elif "bachelor" in name_lower:
        return "bachelors"
    elif "master" in name_lower:
        return "masters"
    elif "phd" in name_lower or "doctor of philosophy" in name_lower:
        return "phd"
    return "unknown"

def generate_code(name, level):
    name_clean = name.replace("&", "and").replace("(", "").replace(")", "").replace("  ", " ")
    words = name_clean.split()
    keywords = [w for w in words if w[0].isalpha() and w.lower() not in 
                ['in', 'of', 'and', 'the', 'with', 'for', 'to', 'a', 'an', 'by', 'research']]
    
    if level == "hec":
        if "humanities" in name.lower():
            return "HEC-HUM"
        elif "physical" in name.lower():
            return "HEC-PHY"
        elif "biological" in name.lower():
            return "HEC-BIO"
        return "HEC"
    
    abbr = ''.join([w[0].upper() for w in keywords[:5] if w[0].isalpha()])
    
    if level == "national_certificate":
        return f"NC{abbr[:4]}"
    elif level == "certificate":
        return f"CERT{abbr[:4]}"
    elif level == "diploma":
        return f"D{abbr[:5]}"
    elif level == "pgd":
        return f"PGD{abbr[:4]}"
    elif level == "bachelors":
        return f"B{abbr[:5]}"
    elif level == "masters":
        if "business administration" in name.lower():
            return "MBA"
        return f"MS{abbr[:4]}"
    elif level == "phd":
        return f"PhD{abbr[:4]}"
    
    return f"PROG{abbr[:4]}"

def get_faculty(college):
    cl = college.lower()
    if "health" in cl or "clinical" in cl or "medical" in cl or "nursing" in cl or "pharmacy" in cl:
        return "College of Health Sciences"
    elif "business" in cl or "economics" in cl or "management" in cl:
        return "Faculty of Business and Management"
    elif "engineering" in cl or "applied sciences" in cl:
        return "Faculty of Engineering"
    elif "law" in cl:
        return "Faculty of Law"
    elif "education" in cl:
        return "Faculty of Education"
    elif "humanities" in cl or "social" in cl:
        return "Faculty of Social Sciences"
    elif "science" in cl or "technology" in cl or "computing" in cl or "mathematics" in cl:
        return "Faculty of Science and Technology"
    elif "agricultural" in cl:
        return "School of Agricultural Sciences"
    elif "biomedical" in cl:
        return "Faculty of Biomedical Sciences"
    elif "allied health" in cl:
        return "School of Allied Health Sciences"
    elif "public health" in cl:
        return "School of Public Health"
    return "Faculty of Business and Management"

def get_duration(name, level):
    if level == "hec":
        return 1
    elif level == "national_certificate":
        return 2
    elif level == "certificate":
        return 1
    elif level == "diploma":
        return 2
    elif level == "bachelors":
        if "medicine" in name.lower():
            return 5
        elif "engineering" in name.lower() or "architecture" in name.lower():
            return 4
        return 3
    elif level == "pgd":
        return 1
    elif level == "masters":
        if "medicine" in name.lower():
            return 3
        return 2
    elif level == "phd":
        return 3
    return 3

for campus, colleges in AUTH_DATA.items():
    campus_name = "Main" if "kampala" in campus.lower() else "Western"
    
    for college, programs in colleges.items():
        faculty = get_faculty(college)
        for prog_name in programs:
            normalized = normalize_name(prog_name)
            if normalized in seen_names:
                continue
            
            seen_names[normalized] = prog_name
            level = get_level(prog_name)
            
            base_code = generate_code(prog_name, level)
            code = base_code
            counter = 1
            while code in code_tracker:
                code = f"{base_code}-{counter}"
                counter += 1
            code_tracker[code] = prog_name
            
            duration = get_duration(prog_name, level)
            
            program = {
                "id": str(uuid.uuid4()),
                "name": prog_name,
                "code": code,
                "level": level,
                "campus": campus_name,
                "duration": duration,
                "faculty": faculty,
                "nche_accredited": True,
                "nche_status": "Fully Accredited",
                "tuition_ugx": 0,
                "tuition_usd": 0,
                "intake_months": [8, 1],
                "requirements": {"min_points": 4, "min_principals": 2},
                "required_subjects": [],
                "description": f"{prog_name} program at KIU {campus_name} Campus"
            }
            all_programs.append(program)

output_data = {
    "metadata": {
        "version": "6.0",
        "last_updated": "2025-04-14",
        "total_programs": len(all_programs),
        "source": "KIU Authoritative Program Document 2025"
    },
    "programs": all_programs
}

with open('seed-programs.json', 'w') as f:
    json.dump(output_data, f, indent=2)

print(f"Generated {len(all_programs)} programs")
print(f"Main: {len([p for p in all_programs if p['campus']=='Main'])}")
print(f"Western: {len([p for p in all_programs if p['campus']=='Western'])}")
