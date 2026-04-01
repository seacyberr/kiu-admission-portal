"""Database seeding logic."""
import os
import json
import random
import string
import logging
from datetime import date, timedelta
from models import db, Program, CareerPath, Opportunity, User

log = logging.getLogger(__name__)


def seed_database(replace_programs=False, seed_enabled=True):
    """Seed the database with initial data."""
    if not seed_enabled:
        return

    programs_count = Program.query.count()
    seed_programs_path = os.path.join(os.path.dirname(__file__), "data", "seed-programs.json")

    # If programs already exist and we are not replacing them, still add missing ones
    if programs_count > 0 and not replace_programs:
        _add_missing_programs(seed_programs_path)
        return

    if replace_programs:
        Program.query.delete()
        db.session.commit()

    # Load programs from JSON file
    programs = _load_programs_from_json(seed_programs_path)

    db.session.add_all(programs)
    db.session.flush()

    # Seed career paths
    career_paths = _get_career_paths()
    db.session.add_all(career_paths)

    # Seed opportunities
    opportunities = _get_opportunities()
    db.session.add_all(opportunities)

    # Create admin user
    _create_admin_user()

    db.session.commit()

    log.info(
        "Database seeded: %d programs, %d career paths, %d opportunities",
        len(programs), len(career_paths), len(opportunities)
    )


def _load_programs_from_json(filepath):
    """Load programs from seed-programs.json."""
    if not os.path.exists(filepath):
        log.warning("Seed programs file not found: %s", filepath)
        return []

    with open(filepath, "r", encoding="utf-8") as f:
        seed = json.load(f)

    programs = []
    for p in seed.get("programs", []):
        # Handle both snake_case and camelCase field names for compatibility
        entry_reqs = p.get("entry_requirements") or p.get("entryRequirements", "")
        
        program = Program(
            name=p.get("name", ""),
            code=p.get("code", ""),
            faculty=p.get("faculty", "") or "",
            department=p.get("department"),
            level=p.get("level", ""),
            duration=p.get("duration"),
            description=p.get("description"),
            entry_requirements=entry_reqs,
            min_olevel_points=p.get("minOlevelPoints"),
            min_alevel_points=p.get("minAlevelPoints"),
            available_slots=p.get("availableSlots", 100) or 100,
        )
        programs.append(program)
    
    return programs


def _add_missing_programs(filepath):
    """Add missing programs without replacing existing ones."""
    if not os.path.exists(filepath):
        return

    with open(filepath, "r", encoding="utf-8") as f:
        seed = json.load(f)

    existing_codes = {p.code for p in Program.query.all()}
    missing = []

    for p in seed.get("programs", []):
        code = p.get("code")
        if not code or code in existing_codes:
            continue
        
        # Handle both snake_case and camelCase field names for compatibility
        entry_reqs = p.get("entry_requirements") or p.get("entryRequirements", "")
        
        missing.append(
            Program(
                name=p.get("name", ""),
                code=code,
                faculty=p.get("faculty", "") or "",
                department=p.get("department"),
                level=p.get("level", ""),
                duration=p.get("duration"),
                description=p.get("description"),
                entry_requirements=entry_reqs,
                min_olevel_points=p.get("minOlevelPoints"),
                min_alevel_points=p.get("minAlevelPoints"),
                available_slots=p.get("availableSlots", 100) or 100,
            )
        )

    if missing:
        db.session.add_all(missing)
        db.session.commit()
        log.info("Added %d missing programs", len(missing))


def _get_career_paths():
    """Load career paths from JSON file."""
    filepath = os.path.join(os.path.dirname(__file__), "data", "seed-career-paths.json")
    if not os.path.exists(filepath):
        log.warning("Career paths file not found: %s", filepath)
        return []

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    return [
        CareerPath(
            title=cp["title"],
            description=cp["description"],
            related_programs=cp.get("relatedPrograms", []),
            skills=cp.get("skills", []),
            potential_roles=cp.get("potentialRoles", []),
            average_salary_range=cp.get("averageSalaryRange"),
            growth_outlook=cp.get("growthOutlook"),
            industry_field=cp["industryField"],
        )
        for cp in data.get("careerPaths", [])
    ]


def _get_opportunities():
    """Load opportunities from JSON file."""
    filepath = os.path.join(os.path.dirname(__file__), "data", "seed-opportunities.json")
    if not os.path.exists(filepath):
        log.warning("Opportunities file not found: %s", filepath)
        return []

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    today = date.today()
    return [
        Opportunity(
            title=opp["title"],
            organization=opp["organization"],
            type=opp["type"],
            description=opp["description"],
            requirements=opp["requirements"],
            required_programs=opp.get("requiredPrograms", []),
            required_skills=opp.get("requiredSkills", []),
            location=opp.get("location"),
            salary_range=opp.get("salaryRange"),
            application_deadline=today + timedelta(days=opp.get("deadlineDays", 30)),
            contact_email=opp.get("contactEmail"),
            is_active=True,
        )
        for opp in data.get("opportunities", [])
    ]


def _create_admin_user():
    """Create admin user if not exists."""
    admin = User.query.filter_by(email="admin@kiu.ac.ug").first()
    if admin:
        return

    admin_pw = "".join(random.choices(string.ascii_letters + string.digits + "!@#$%", k=12))
    admin = User(
        email="admin@kiu.ac.ug",
        first_name="KIU",
        last_name="Administrator",
        role="admin",
        phone="+256700000000",
        is_verified=True,
    )
    admin.set_password(admin_pw)
    db.session.add(admin)

    log.info("Admin user created: admin@kiu.ac.ug / %s", admin_pw)