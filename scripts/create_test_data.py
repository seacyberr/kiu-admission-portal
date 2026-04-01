#!/usr/bin/env python3
"""
KIU Portal - Test Data Creation Script

Creates test applicants for all qualification paths, admin user,
submits applications, admin reviews them, creates finalists for
approved applications, and posts job opportunities.

Usage:
    cd apps/flask-api
    python ../../scripts/create_test_data.py
"""

import os
import sys
import json
import random
import string
from datetime import date, datetime, timedelta

# Add flask-api to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "apps", "flask-api"))

from app import create_app
from models import db, User, AdmissionApplication, Program, FinalistProfile, Opportunity, RefreshToken, OtpCode


def delete_old_users():
    """Delete all users except the ones we'll recreate."""
    print("🗑️  Deleting old users and related data...")
    
    # Delete all non-admin users and their data
    AdmissionApplication.query.delete()
    FinalistProfile.query.delete()
    Opportunity.query.delete()
    RefreshToken.query.delete()
    OtpCode.query.delete()
    
    # Delete all users (we'll recreate admin)
    User.query.delete()
    db.session.commit()
    print("   ✅ Old data cleared")


def create_admin():
    """Create admin user."""
    print("👨‍💼 Creating admin user...")
    
    admin = User(
        email="admin@kiu.ac.ug",
        first_name="KIU",
        last_name="Administrator",
        role="admin",
        phone="+256700000000",
        is_verified=True,
    )
    admin.set_password("Admin123!")
    db.session.add(admin)
    db.session.commit()
    print("   ✅ Admin created: admin@kiu.ac.ug / Admin123!")
    return admin


def create_applicant(email, first_name, last_name, phone="+256700000001"):
    """Create a verified applicant user."""
    user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        role="applicant",
        phone=phone,
        is_verified=True,
    )
    user.set_password("Test123!")
    db.session.add(user)
    db.session.flush()
    return user


def get_program_by_code(code):
    """Get program by code."""
    return Program.query.filter_by(code=code).first()


def get_programs_by_level(level):
    """Get first program by level."""
    return Program.query.filter_by(level=level).first()


def generate_application_number():
    """Generate unique application number."""
    year = datetime.now().year
    suffix = "".join(random.choices(string.digits, k=6))
    return f"KIU/{year}/{suffix}"


def create_application(user, program, exam_level, exam_year, index_number, 
                       uneb_grades, dob, gender="male", district="Kampala",
                       session="day", nationality="Ugandan"):
    """Create an admission application."""
    app_number = generate_application_number()
    while AdmissionApplication.query.filter_by(application_number=app_number).first():
        app_number = generate_application_number()
    
    application = AdmissionApplication(
        application_number=app_number,
        user_id=user.id,
        program_id=program.id,
        program_choices=[program.id],
        exam_level=exam_level,
        exam_year=exam_year,
        index_number=index_number,
        uneb_grades=uneb_grades,
        date_of_birth=dob,
        gender=gender,
        nationality=nationality,
        district=district,
        session_of_study=session,
        personal_statement=f"I am {user.first_name} {user.last_name}, applying for {program.name}.",
        next_of_kin_name=f"Parent of {user.first_name}",
        next_of_kin_phone="+256700000099",
        next_of_kin_relationship="Parent",
        status="pending",
    )
    db.session.add(application)
    db.session.flush()
    return application


def make_olevel_grades():
    """Create good O-Level grades (D1-D3 range)."""
    return [
        {"subject": "English Language", "grade": "D1", "points": 1},
        {"subject": "Mathematics", "grade": "D1", "points": 1},
        {"subject": "Physics", "grade": "D2", "points": 2},
        {"subject": "Chemistry", "grade": "D2", "points": 2},
        {"subject": "Biology", "grade": "D1", "points": 1},
        {"subject": "Geography", "grade": "D3", "points": 3},
        {"subject": "History", "grade": "D2", "points": 2},
        {"subject": "Christian Religious Education (CRE)", "grade": "D1", "points": 1},
    ]


def make_alevel_grades():
    """Create good A-Level grades (A-C range)."""
    return [
        {"subject": "Mathematics", "grade": "A", "points": 6, "subjectType": "principal"},
        {"subject": "Physics", "grade": "B", "points": 5, "subjectType": "principal"},
        {"subject": "Chemistry", "grade": "B", "points": 5, "subjectType": "principal"},
        {"subject": "General Paper", "grade": "C", "points": 4, "subjectType": "subsidiary"},
    ]


def create_all_applicants():
    """Create all test applicants with their applications."""
    print("\n📝 Creating test applicants and applications...")
    
    dob = date(2000, 1, 15)
    
    # ── 1. A-Level → Degree (SHOULD SUCCEED) ─────────────────────────────
    print("\n   1️⃣  A-Level → Degree (Bachelor of Computer Science)")
    user1 = create_applicant("alevel-degree@kiu.ac.ug", "Alice", "A-Level", "+256700000001")
    prog1 = get_program_by_code("BCS")
    app1 = create_application(
        user1, prog1, "a_level", 2023, "U0001/001",
        {"olevel": make_olevel_grades(), "alevel": make_alevel_grades()},
        dob
    )
    print(f"      ✅ Application {app1.application_number} created (A-Level → Degree)")
    
    # ── 2. A-Level → HEC (SHOULD SUCCEED) ────────────────────────────────
    print("\n   2️⃣  A-Level → HEC (Certificate in ICT)")
    user2 = create_applicant("alevel-hec@kiu.ac.ug", "Bob", "A-Level", "+256700000002")
    prog2 = get_program_by_code("CERT-ICT")
    app2 = create_application(
        user2, prog2, "a_level", 2023, "U0002/002",
        {"olevel": make_olevel_grades(), "alevel": make_alevel_grades()},
        dob
    )
    print(f"      ✅ Application {app2.application_number} created (A-Level → HEC)")
    
    # ── 3. A-Level → Diploma (SHOULD SUCCEED) ────────────────────────────
    print("\n   3️⃣  A-Level → Diploma (Diploma in IT)")
    user3 = create_applicant("alevel-diploma@kiu.ac.ug", "Charlie", "A-Level", "+256700000003")
    prog3 = get_program_by_code("DIT")
    app3 = create_application(
        user3, prog3, "a_level", 2023, "U0003/003",
        {"olevel": make_olevel_grades(), "alevel": make_alevel_grades()},
        dob
    )
    print(f"      ✅ Application {app3.application_number} created (A-Level → Diploma)")
    
    # ── 4. O-Level → Diploma (SHOULD SUCCEED) ────────────────────────────
    print("\n   4️⃣  O-Level → Diploma (Diploma in Business Admin)")
    user4 = create_applicant("olevel-diploma@kiu.ac.ug", "Diana", "O-Level", "+256700000004")
    prog4 = get_program_by_code("DBA")
    app4 = create_application(
        user4, prog4, "o_level", 2023, "U0004/004",
        {"olevel": make_olevel_grades()},
        dob
    )
    print(f"      ✅ Application {app4.application_number} created (O-Level → Diploma)")
    
    # ── 5. O-Level → HEC (SHOULD SUCCEED) ────────────────────────────────
    print("\n   5️⃣  O-Level → HEC (Certificate in Business Admin)")
    user5 = create_applicant("olevel-hec@kiu.ac.ug", "Edward", "O-Level", "+256700000005")
    prog5 = get_program_by_code("CERT-BA")
    app5 = create_application(
        user5, prog5, "o_level", 2023, "U0005/005",
        {"olevel": make_olevel_grades()},
        dob
    )
    print(f"      ✅ Application {app5.application_number} created (O-Level → HEC)")
    
    # ── 6. HEC → Diploma (SHOULD SUCCEED) ────────────────────────────────
    print("\n   6️⃣  HEC → Diploma (Diploma in Computer Science)")
    user6 = create_applicant("hec-diploma@kiu.ac.ug", "Fiona", "HEC", "+256700000006")
    prog6 = get_program_by_code("DCS")
    app6 = create_application(
        user6, prog6, "hec", 2022, "H0001/001",
        {},
        dob
    )
    print(f"      ✅ Application {app6.application_number} created (HEC → Diploma)")
    
    # ── 7. HEC → Degree (SHOULD SUCCEED) ─────────────────────────────────
    print("\n   7️⃣  HEC → Degree (Bachelor of IT)")
    user7 = create_applicant("hec-degree@kiu.ac.ug", "George", "HEC", "+256700000007")
    prog7 = get_program_by_code("BIT")
    app7 = create_application(
        user7, prog7, "hec", 2022, "H0002/002",
        {},
        dob
    )
    print(f"      ✅ Application {app7.application_number} created (HEC → Degree)")
    
    # ── 8. Masters Applicant (SHOULD SUCCEED) ────────────────────────────
    print("\n   8️⃣  Masters Applicant (MBA)")
    user8 = create_applicant("masters@kiu.ac.ug", "Helen", "Masters", "+256700000008")
    prog8 = get_program_by_code("MBA")
    app8 = create_application(
        user8, prog8, "masters", 2022, "M0001/001",
        {},
        dob
    )
    print(f"      ✅ Application {app8.application_number} created (Masters → MBA)")
    
    # ── 9. PhD Applicant (SHOULD SUCCEED) ────────────────────────────────
    print("\n   9️⃣  PhD Applicant (PhD in Business Admin)")
    user9 = create_applicant("phd@kiu.ac.ug", "Ian", "PhD", "+256700000009")
    prog9 = get_program_by_code("PHDBA")
    app9 = create_application(
        user9, prog9, "phd", 2022, "P0001/001",
        {},
        dob
    )
    print(f"      ✅ Application {app9.application_number} created (PhD)")
    
    # ── 10. O-Level → Degree (SHOULD FAIL - wrong qualification) ─────────
    print("\n   🔴 O-Level → Degree (SHOULD BE REJECTED)")
    user10 = create_applicant("olevel-degree-fail@kiu.ac.ug", "Jack", "Fail", "+256700000010")
    prog10 = get_program_by_code("BBA")
    app10 = create_application(
        user10, prog10, "o_level", 2023, "U0010/010",
        {"olevel": make_olevel_grades()},
        dob
    )
    print(f"      ⚠️  Application {app10.application_number} created (O-Level → Degree - will be rejected)")
    
    db.session.commit()
    
    return [
        (app1, "approve"), (app2, "approve"), (app3, "approve"),
        (app4, "approve"), (app5, "approve"), (app6, "approve"),
        (app7, "approve"), (app8, "approve"), (app9, "approve"),
        (app10, "reject"),  # O-Level cannot apply for Degree
    ]


def admin_review_applications(admin, applications_with_actions):
    """Admin reviews and approves/rejects applications."""
    print("\n👨‍💼 Admin reviewing applications...")
    
    for app, action in applications_with_actions:
        if action == "approve":
            app.status = "accepted"
            app.admin_notes = f"Application approved. Qualification ({app.exam_level}) meets requirements for {app.program.level} program."
            print(f"   ✅ Approved: {app.application_number} - {app.user.first_name} {app.user.last_name} ({app.exam_level} → {app.program.level})")
        else:
            app.status = "rejected"
            app.admin_notes = f"Application rejected. {app.exam_level.upper()} qualification does not meet requirements for {app.program.level} program. Degree programs require A-Level, Diploma, or HEC."
            print(f"   ❌ Rejected: {app.application_number} - {app.user.first_name} {app.user.last_name} ({app.exam_level} → {app.program.level})")
    
    db.session.commit()
    print("   ✅ All applications reviewed")


def create_finalists(applications_with_actions):
    """Create FinalistProfile for accepted applicants."""
    print("\n🎓 Creating Finalist profiles for accepted applicants...")
    
    for app, action in applications_with_actions:
        if action != "approve":
            continue
        
        user = app.user
        
        # Skip if already a finalist
        if user.role == "finalist":
            continue
        
        # Update user role to finalist
        user.role = "finalist"
        
        # Create finalist profile
        profile = FinalistProfile(
            user_id=user.id,
            program_id=app.program_id,
            student_number=f"KIU/{datetime.now().year}/{random.randint(10000, 99999)}",
            year_of_study=random.randint(1, 3),
            graduation_year=datetime.now().year + random.randint(1, 2),
            gpa=round(random.uniform(3.0, 4.5), 2),
            skills=["Communication", "Problem Solving", "Teamwork", "Microsoft Office"],
            bio=f"I am {user.first_name} {user.last_name}, a dedicated student at KIU.",
            is_finalist=True,
        )
        db.session.add(profile)
        print(f"   ✅ Finalist created: {user.email} ({app.program.name})")
    
    db.session.commit()
    print("   ✅ All finalists created")


def create_opportunities(admin):
    """Create job and internship opportunities."""
    print("\n💼 Creating job opportunities...")
    
    today = date.today()
    
    opportunities = [
        {
            "title": "Graduate Trainee - Software Development",
            "organization": "KIU IT Department",
            "type": "job",
            "description": "Join our IT team as a graduate trainee. Work on real-world software projects.",
            "requirements": "Bachelor's degree in Computer Science, IT, or Software Engineering. Strong programming skills.",
            "required_programs": ["BCS", "BIT", "BSSE"],
            "required_skills": ["Python", "JavaScript", "Problem Solving"],
            "location": "Kampala Campus",
            "salary_range": "UGX 800,000 - 1,200,000/month",
            "deadline_days": 30,
            "contact_email": "hr@kiu.ac.ug",
        },
        {
            "title": "Business Analyst Intern",
            "organization": "KIU Business School",
            "type": "internship",
            "description": "Gain practical experience in business analysis and data-driven decision making.",
            "requirements": "Currently enrolled in BBA, MBA, or related business program.",
            "required_programs": ["BBA", "MBA"],
            "required_skills": ["Excel", "Data Analysis", "Communication"],
            "location": "Kampala Campus",
            "salary_range": "UGX 300,000/month (stipend)",
            "deadline_days": 45,
            "contact_email": "careers@kiu.ac.ug",
        },
        {
            "title": "Nursing Assistant",
            "organization": "KIU Teaching Hospital",
            "type": "job",
            "description": "Support nursing staff in patient care at our teaching hospital.",
            "requirements": "Diploma or Bachelor's in Nursing Sciences. Current practicing license.",
            "required_programs": ["DNS", "BNS"],
            "required_skills": ["Patient Care", "Medical Records", "Teamwork"],
            "location": "Western Campus",
            "salary_range": "UGX 600,000 - 900,000/month",
            "deadline_days": 60,
            "contact_email": "hospital-hr@kiu.ac.ug",
        },
    ]
    
    for opp_data in opportunities:
        opp = Opportunity(
            title=opp_data["title"],
            organization=opp_data["organization"],
            type=opp_data["type"],
            description=opp_data["description"],
            requirements=opp_data["requirements"],
            required_programs=opp_data["required_programs"],
            required_skills=opp_data["required_skills"],
            location=opp_data["location"],
            salary_range=opp_data["salary_range"],
            application_deadline=today + timedelta(days=opp_data["deadline_days"]),
            contact_email=opp_data["contact_email"],
            is_active=True,
        )
        db.session.add(opp)
        print(f"   ✅ Created: {opp_data['title']} ({opp_data['type']})")
    
    db.session.commit()
    print("   ✅ All opportunities created")


def print_summary():
    """Print summary of created data."""
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    
    users = User.query.all()
    print(f"\n👥 Users: {len(users)}")
    for u in users:
        print(f"   • {u.email:35s} | Role: {u.role:10s} | Verified: {u.is_verified}")
    
    apps = AdmissionApplication.query.all()
    print(f"\n📝 Applications: {len(apps)}")
    for a in apps:
        status_icon = "✅" if a.status == "accepted" else "❌" if a.status == "rejected" else "⏳"
        print(f"   {status_icon} {a.application_number} | {a.user.email:30s} | {a.exam_level:10s} → {a.program.level:8s} | Status: {a.status}")
    
    finalists = FinalistProfile.query.all()
    print(f"\n🎓 Finalists: {len(finalists)}")
    for f in finalists:
        print(f"   • {f.user.email:35s} | Program: {f.program.name:30s} | GPA: {f.gpa}")
    
    opps = Opportunity.query.all()
    print(f"\n💼 Opportunities: {len(opps)}")
    for o in opps:
        print(f"   • {o.title:40s} | Type: {o.type:12s} | Org: {o.organization}")
    
    print("\n" + "=" * 70)
    print("🔑 LOGIN CREDENTIALS")
    print("=" * 70)
    print("\n   Admin:")
    print("      Email: admin@kiu.ac.ug")
    print("      Password: Admin123!")
    print("\n   All Applicants/Finalists:")
    print("      Password: Test123!")
    print("      Emails:")
    for u in users:
        if u.role != "admin":
            print(f"         • {u.email}")
    print("\n" + "=" * 70)


def main():
    """Main function."""
    print("=" * 70)
    print("🚀 KIU Portal - Test Data Creation Script")
    print("=" * 70)
    
    app = create_app()
    
    with app.app_context():
        delete_old_users()
        admin = create_admin()
        applications_with_actions = create_all_applicants()
        admin_review_applications(admin, applications_with_actions)
        create_finalists(applications_with_actions)
        create_opportunities(admin)
        print_summary()
    
    print("\n✅ Script completed successfully!")


if __name__ == "__main__":
    main()
