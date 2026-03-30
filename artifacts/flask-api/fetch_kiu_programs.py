#!/usr/bin/env python3
"""
Script to fetch programs from KIU website and update seed-programs.json
"""

import requests
import json
import re
from bs4 import BeautifulSoup
from typing import List, Dict, Any

def fetch_programs_from_kiu() -> List[Dict[str, Any]]:
    """
    Fetch programs from KIU website
    """
    programs = []
    
    # KIU program pages to scrape
    urls = [
        "https://kiu.ac.ug/academics/undergraduate-programs",
        "https://kiu.ac.ug/academics/diploma-programs", 
        "https://kiu.ac.ug/academics/hec-programs"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for url in urls:
        try:
            print(f"Fetching from: {url}")
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Determine program level from URL
            if "undergraduate" in url:
                level = "degree"
            elif "diploma" in url:
                level = "diploma"
            elif "hec" in url:
                level = "hec"
            else:
                level = "degree"
            
            # Find program elements - adjust selectors based on actual HTML structure
            program_elements = soup.find_all(['div', 'li', 'a'], class_=re.compile(r'program|course|degree', re.I))
            
            if not program_elements:
                # Try alternative selectors
                program_elements = soup.find_all('a', href=re.compile(r'/academics/|/programs/', re.I))
            
            for element in program_elements:
                program_name = element.get_text(strip=True)
                if program_name and len(program_name) > 5:  # Filter out short/empty names
                    program_data = {
                        "name": program_name,
                        "level": level,
                        "duration": "3 Years",  # Default, will be updated
                        "faculty": "General",  # Default, will be updated
                        "department": None,
                        "entry_requirements": "",
                        "minOlevelPoints": None,
                        "minAlevelPoints": None,
                        "availableSlots": 100,
                        "code": f"{level.upper()[:3]}{len(programs)+1:03d}",
                        "campus": "kampala"  # Default
                    }
                    programs.append(program_data)
                    print(f"Found: {program_name} ({level})")
            
        except Exception as e:
            print(f"Error fetching {url}: {e}")
    
    return programs

def update_seed_file(new_programs: List[Dict[str, Any]]):
    """
    Update seed-programs.json by merging new programs with existing ones
    """
    existing_programs = []
    
    # Load existing programs if file exists
    try:
        with open("seed-programs.json", "r", encoding="utf-8") as f:
            existing_data = json.load(f)
            existing_programs = existing_data.get("programs", [])
            print(f"Loaded {len(existing_programs)} existing programs")
    except FileNotFoundError:
        print("No existing seed-programs.json found, creating new file")
    
    # Create a set of existing program codes for deduplication
    existing_codes = {p.get("code") for p in existing_programs if p.get("code")}
    
    # Add new programs that don't already exist
    merged_programs = existing_programs.copy()
    added_count = 0
    
    for program in new_programs:
        code = program.get("code")
        if code and code not in existing_codes:
            merged_programs.append(program)
            existing_codes.add(code)
            added_count += 1
            print(f"Added: {program.get('name')} ({code})")
        elif not code:
            # If no code, generate one and add
            program["code"] = f"{program.get('level', 'PROG').upper()[:3]}{len(merged_programs)+1:03d}"
            merged_programs.append(program)
            added_count += 1
            print(f"Added (new code): {program.get('name')} ({program['code']})")
        else:
            print(f"Skipped (already exists): {program.get('name')} ({code})")
    
    seed_data = {"programs": merged_programs}
    
    with open("seed-programs.json", "w", encoding="utf-8") as f:
        json.dump(seed_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nSummary: Added {added_count} new programs. Total programs: {len(merged_programs)}")

def main():
    print("Fetching programs from KIU website...")
    programs = fetch_programs_from_kiu()
    
    if programs:
        print(f"Found {len(programs)} programs")
        update_seed_file(programs)
    else:
        print("No programs found. Using manual entry.")
        
        # Manual entry of known KIU programs
        manual_programs = [
            # Degree programs (existing)
            {"name": "Bachelor of Laws (Day)", "level": "degree", "duration": "4 Years", "faculty": "School of Law", "department": None, "entry_requirements": "", "minOlevelPoints": None, "minAlevelPoints": None, "availableSlots": 100, "code": "DEGREEBACHELOR7F3B74", "campus": "kampala"},
            {"name": "Bachelor of Medicine and Bachelor of Surgery", "level": "degree", "duration": "5.5 Years", "faculty": "Faculty of Clinical Medicine and Dentistry", "department": None, "entry_requirements": "", "minOlevelPoints": None, "minAlevelPoints": None, "availableSlots": 100, "code": "DEGREEBACHELOR9A9992", "campus": "western"},
            
            # Diploma programs
            {"name": "Diploma in Business Administration", "level": "diploma", "duration": "2 Years", "faculty": "School of Business", "department": None, "entry_requirements": "O-Level with 5 passes", "minOlevelPoints": 5, "minAlevelPoints": None, "availableSlots": 50, "code": "DIP001", "campus": "kampala"},
            {"name": "Diploma in Information Technology", "level": "diploma", "duration": "2 Years", "faculty": "School of Computing", "department": None, "entry_requirements": "O-Level with 5 passes", "minOlevelPoints": 5, "minAlevelPoints": None, "availableSlots": 50, "code": "DIP002", "campus": "kampala"},
            {"name": "Diploma in Electrical Engineering", "level": "diploma", "duration": "2 Years", "faculty": "School of Engineering", "department": None, "entry_requirements": "O-Level with 5 passes including Maths and Physics", "minOlevelPoints": 5, "minAlevelPoints": None, "availableSlots": 40, "code": "DIP003", "campus": "kampala"},
            {"name": "Diploma in Civil Engineering", "level": "diploma", "duration": "2 Years", "faculty": "School of Engineering", "department": None, "entry_requirements": "O-Level with 5 passes including Maths and Physics", "minOlevelPoints": 5, "minAlevelPoints": None, "availableSlots": 40, "code": "DIP004", "campus": "kampala"},
            {"name": "Diploma in Nursing", "level": "diploma", "duration": "3 Years", "faculty": "School of Nursing", "department": None, "entry_requirements": "O-Level with 5 passes including English, Maths, and Biology", "minOlevelPoints": 5, "minAlevelPoints": None, "availableSlots": 60, "code": "DIP005", "campus": "western"},
            {"name": "Diploma in Clinical Medicine", "level": "diploma", "duration": "3 Years", "faculty": "School of Medicine", "department": None, "entry_requirements": "O-Level with 5 passes including English, Maths, and Biology", "minOlevelPoints": 5, "minAlevelPoints": None, "availableSlots": 50, "code": "DIP006", "campus": "western"},
            {"name": "Diploma in Pharmacy", "level": "diploma", "duration": "2 Years", "faculty": "School of Pharmacy", "department": None, "entry_requirements": "O-Level with 5 passes including English, Maths, and Chemistry", "minOlevelPoints": 5, "minAlevelPoints": None, "availableSlots": 40, "code": "DIP007", "campus": "western"},
            {"name": "Diploma in Education", "level": "diploma", "duration": "2 Years", "faculty": "School of Education", "department": None, "entry_requirements": "O-Level with 5 passes", "minOlevelPoints": 5, "minAlevelPoints": None, "availableSlots": 80, "code": "DIP008", "campus": "kampala"},
            
            # HEC programs
            {"name": "HEC in Business Studies", "level": "hec", "duration": "1 Year", "faculty": "School of Business", "department": None, "entry_requirements": "O-Level with 4 passes", "minOlevelPoints": 4, "minAlevelPoints": None, "availableSlots": 100, "code": "HEC001", "campus": "kampala"},
            {"name": "HEC in Information Technology", "level": "hec", "duration": "1 Year", "faculty": "School of Computing", "department": None, "entry_requirements": "O-Level with 4 passes", "minOlevelPoints": 4, "minAlevelPoints": None, "availableSlots": 100, "code": "HEC002", "campus": "kampala"},
            {"name": "HEC in Engineering", "level": "hec", "duration": "1 Year", "faculty": "School of Engineering", "department": None, "entry_requirements": "O-Level with 4 passes including Maths", "minOlevelPoints": 4, "minAlevelPoints": None, "availableSlots": 60, "code": "HEC003", "campus": "kampala"},
            {"name": "HEC in Health Sciences", "level": "hec", "duration": "1 Year", "faculty": "School of Health Sciences", "department": None, "entry_requirements": "O-Level with 4 passes including Biology", "minOlevelPoints": 4, "minAlevelPoints": None, "availableSlots": 80, "code": "HEC004", "campus": "western"},
            {"name": "HEC in Education", "level": "hec", "duration": "1 Year", "faculty": "School of Education", "department": None, "entry_requirements": "O-Level with 4 passes", "minOlevelPoints": 4, "minAlevelPoints": None, "availableSlots": 100, "code": "HEC005", "campus": "kampala"},
        ]
        
        update_seed_file(manual_programs)

if __name__ == "__main__":
    main()