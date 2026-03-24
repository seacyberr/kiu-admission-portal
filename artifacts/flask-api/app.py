import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from models import db, bcrypt

# ---------------------------------------------------------------------------
# Database URL resolution
# ---------------------------------------------------------------------------
def _resolve_db_url():
    url = os.environ.get("DATABASE_URL", "").strip()

    # Heroku / Render style: postgres:// → postgresql://
    if url.startswith("postgres://"):
        url = "postgresql" + url[8:]

    # Plain mysql:// → mysql+pymysql:// for PyMySQL driver
    if url.startswith("mysql://"):
        url = "mysql+pymysql" + url[5:]

    return url


DATABASE_URL = _resolve_db_url()

# Local MySQL fallback when DATABASE_URL is empty
if not DATABASE_URL:
    DATABASE_URL = "mysql+pymysql://admin:adekunle%2312@localhost/kiu_admissions"

IS_MYSQL = "mysql" in DATABASE_URL

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}
MAX_CONTENT_MB = 5


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }
    app.config["SECRET_KEY"] = os.environ.get("JWT_SECRET", "kiu-portal-secret-key-2024")
    app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_MB * 1024 * 1024
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    app.config["ALLOWED_EXTENSIONS"] = ALLOWED_EXTENSIONS

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(os.path.join(UPLOAD_FOLDER, "certificates"), exist_ok=True)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    db.init_app(app)
    bcrypt.init_app(app)

    from routes.auth import auth_bp
    from routes.admission import admission_bp
    from routes.career import career_bp
    from routes.opportunities import opportunities_bp
    from routes.users import users_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(admission_bp, url_prefix="/api/admission")
    app.register_blueprint(career_bp, url_prefix="/api/career")
    app.register_blueprint(opportunities_bp, url_prefix="/api/opportunities")
    app.register_blueprint(users_bp, url_prefix="/api/users")

    @app.route("/api/healthz")
    def healthz():
        return jsonify({"status": "ok", "db": "mysql" if IS_MYSQL else "postgresql"}), 200

    @app.route("/api/uploads/certificates/<path:filename>")
    def serve_certificate(filename):
        cert_dir = os.path.join(UPLOAD_FOLDER, "certificates")
        return send_from_directory(cert_dir, filename)

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found", "message": str(e)}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method not allowed", "message": str(e)}), 405

    @app.errorhandler(413)
    def file_too_large(e):
        return jsonify({"error": "File too large", "message": f"Max file size is {MAX_CONTENT_MB}MB"}), 413

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error": "Internal server error", "message": str(e)}), 500

    with app.app_context():
        db.create_all()
        _run_migrations()
        _seed_data()

    return app


# ---------------------------------------------------------------------------
# Column migrations — safe to run on every startup
# ---------------------------------------------------------------------------
def _run_migrations():
    from sqlalchemy import inspect, text
    from models import User

    insp = inspect(db.engine)

    # ── users table ────────────────────────────────────────────────────────
    user_cols = {c["name"] for c in insp.get_columns("users")}
    col_added = False
    with db.engine.begin() as conn:
        if "is_verified" not in user_cols:
            conn.execute(text(
                "ALTER TABLE users ADD COLUMN is_verified BOOLEAN NOT NULL DEFAULT FALSE"
            ))
            col_added = True

    # Existing users (pre-OTP era) are auto-verified so they are not locked out
    if col_added:
        with db.engine.begin() as conn:
            conn.execute(text("UPDATE users SET is_verified = TRUE"))

    # ── admission_applications table ───────────────────────────────────────
    app_cols = {c["name"] for c in insp.get_columns("admission_applications")}
    with db.engine.begin() as conn:
        if "olevel_certificate_path" not in app_cols:
            conn.execute(text(
                "ALTER TABLE admission_applications ADD COLUMN olevel_certificate_path TEXT"
            ))
        if "alevel_certificate_path" not in app_cols:
            conn.execute(text(
                "ALTER TABLE admission_applications ADD COLUMN alevel_certificate_path TEXT"
            ))

    # Ensure admin is always verified
    with db.engine.begin() as conn:
        conn.execute(text(
            "UPDATE users SET is_verified = TRUE WHERE role = 'admin'"
        ))


# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------
def _seed_data():
    from models import Program, CareerPath, Opportunity, User
    from datetime import date, timedelta

    if Program.query.count() > 0:
        return

    programs = [
        Program(name="Bachelor of Medicine and Bachelor of Surgery (MBChB)", code="MBBCH", faculty="Faculty of Medicine", department="Medicine", level="degree", duration="5 years", description="A comprehensive medical degree program.", entry_requirements="3 principal passes at A-Level including Biology and Chemistry. Minimum 15 points.", min_olevel_points=32, min_alevel_points=15, available_slots=60),
        Program(name="Bachelor of Laws (LLB)", code="LLB", faculty="Faculty of Law", department="Law", level="degree", duration="4 years", description="A rigorous law degree preparing students for legal practice.", entry_requirements="2 principal passes at A-Level. Minimum 10 points.", min_olevel_points=36, min_alevel_points=10, available_slots=80),
        Program(name="Bachelor of Business Administration (BBA)", code="BBA", faculty="Faculty of Business", department="Business Administration", level="degree", duration="3 years", description="A comprehensive business degree covering management, finance, and marketing.", entry_requirements="2 principal passes at A-Level. Minimum 8 points.", min_olevel_points=40, min_alevel_points=8, available_slots=120),
        Program(name="Bachelor of Science in Information Technology (BSc IT)", code="BSCIT", faculty="Faculty of Science and Technology", department="Information Technology", level="degree", duration="3 years", description="Covers software development, networking, databases, and IT management.", entry_requirements="2 principal passes at A-Level including Mathematics or Physics. Minimum 8 points.", min_olevel_points=42, min_alevel_points=8, available_slots=100),
        Program(name="Bachelor of Science in Computer Science (BSc CS)", code="BSCCS", faculty="Faculty of Science and Technology", department="Computer Science", level="degree", duration="3 years", description="Foundational and advanced computer science theory and practice.", entry_requirements="2 principal passes at A-Level including Mathematics. Minimum 10 points.", min_olevel_points=40, min_alevel_points=10, available_slots=80),
        Program(name="Bachelor of Education (BEd)", code="BED", faculty="Faculty of Education", department="Education", level="degree", duration="3 years", description="Trains professional teachers for secondary schools.", entry_requirements="2 principal passes at A-Level. Minimum 8 points.", min_olevel_points=42, min_alevel_points=8, available_slots=100),
        Program(name="Bachelor of Engineering (Civil) (BEng)", code="BENGCIV", faculty="Faculty of Engineering", department="Civil Engineering", level="degree", duration="4 years", description="Civil engineering covering structural design, water resources and transport.", entry_requirements="3 principal passes at A-Level including Mathematics and Physics. Minimum 12 points.", min_olevel_points=40, min_alevel_points=12, available_slots=60),
        Program(name="Bachelor of Nursing Science (BNSc)", code="BNSC", faculty="Faculty of Medicine", department="Nursing", level="degree", duration="4 years", description="Professional nursing degree with clinical training.", entry_requirements="2 principal passes at A-Level including Biology. Minimum 8 points.", min_olevel_points=40, min_alevel_points=8, available_slots=80),
        Program(name="Bachelor of Commerce (BCom)", code="BCOM", faculty="Faculty of Business", department="Commerce", level="degree", duration="3 years", description="Commerce degree covering accounting, finance and economics.", entry_requirements="2 principal passes at A-Level. Minimum 8 points.", min_olevel_points=42, min_alevel_points=8, available_slots=100),
        Program(name="Diploma in Business Administration", code="DBA", faculty="Faculty of Business", department="Business Administration", level="diploma", duration="2 years", description="Foundation business skills for entry-level management.", entry_requirements="UCE with at least 5 passes including English. Points: 24 or below.", min_olevel_points=24, min_alevel_points=None, available_slots=150),
        Program(name="Diploma in Information Technology", code="DIT", faculty="Faculty of Science and Technology", department="Information Technology", level="diploma", duration="2 years", description="Practical IT skills in networking, software, and databases.", entry_requirements="UCE with passes in Mathematics and English.", min_olevel_points=28, min_alevel_points=None, available_slots=120),
        Program(name="Diploma in Clinical Medicine", code="DCM", faculty="Faculty of Medicine", department="Clinical Medicine", level="diploma", duration="3 years", description="Clinical medical skills for health facilities.", entry_requirements="UCE with Biology, Chemistry and English passes.", min_olevel_points=30, min_alevel_points=None, available_slots=80),
        Program(name="Diploma in Education", code="DPED", faculty="Faculty of Education", department="Education", level="diploma", duration="2 years", description="Prepares teachers for primary and lower secondary school.", entry_requirements="UCE with passes in at least 5 subjects including English.", min_olevel_points=28, min_alevel_points=None, available_slots=100),
        Program(name="Diploma in Accounting", code="DACC", faculty="Faculty of Business", department="Accounting", level="diploma", duration="2 years", description="Accounting and bookkeeping skills for business practice.", entry_requirements="UCE with Mathematics and English passes.", min_olevel_points=30, min_alevel_points=None, available_slots=100),
        Program(name="Bachelor of Public Health (BPH)", code="BPH", faculty="Faculty of Medicine", department="Public Health", level="degree", duration="3 years", description="Prepares health professionals for community and public health roles.", entry_requirements="2 principal passes at A-Level including Biology. Minimum 8 points.", min_olevel_points=40, min_alevel_points=8, available_slots=80),
    ]
    db.session.add_all(programs)
    db.session.flush()

    career_paths = [
        CareerPath(title="Software Engineer / Developer", description="Design and build software applications for businesses, government, and individuals.", related_programs=["BSc IT", "BSc CS", "BBA"], skills=["Python", "JavaScript", "Java", "SQL", "Git", "Problem Solving", "Agile/Scrum"], potential_roles=["Software Developer", "Full Stack Developer", "Backend Engineer", "Frontend Developer", "Mobile Developer"], average_salary_range="UGX 1,500,000 – 6,000,000/month", growth_outlook="Very High", industry_field="Technology"),
        CareerPath(title="Data Analyst / Data Scientist", description="Analyze data to help organizations make informed decisions.", related_programs=["BSc CS", "BSc IT", "BCom", "BBA"], skills=["Python", "R", "SQL", "Power BI", "Tableau", "Statistics", "Machine Learning"], potential_roles=["Data Analyst", "Business Intelligence Analyst", "Data Scientist", "Research Analyst"], average_salary_range="UGX 2,000,000 – 7,000,000/month", growth_outlook="High", industry_field="Technology"),
        CareerPath(title="Medical Doctor / Physician", description="Diagnose and treat patients across various specialties in hospitals and clinics.", related_programs=["MBChB", "BNSc", "BPH"], skills=["Clinical Diagnosis", "Patient Care", "Medical Ethics", "Research", "Communication"], potential_roles=["General Practitioner", "Surgeon", "Pediatrician", "Obstetrician", "Internist"], average_salary_range="UGX 2,500,000 – 15,000,000/month", growth_outlook="High", industry_field="Healthcare"),
        CareerPath(title="Lawyer / Legal Counsel", description="Represent clients in court, provide legal advice, and draft legal documents.", related_programs=["LLB"], skills=["Legal Research", "Advocacy", "Drafting", "Negotiation", "Critical Thinking"], potential_roles=["Advocate", "State Attorney", "Corporate Counsel", "Legal Aid Lawyer", "Magistrate"], average_salary_range="UGX 2,000,000 – 12,000,000/month", growth_outlook="Stable", industry_field="Law"),
        CareerPath(title="Accountant / Financial Analyst", description="Manage financial records, prepare reports, and advise on financial planning.", related_programs=["BCom", "BBA", "DACC"], skills=["Financial Reporting", "Taxation", "Auditing", "Excel", "IFRS", "Budgeting"], potential_roles=["Accountant", "Auditor", "Financial Analyst", "Tax Consultant", "CFO"], average_salary_range="UGX 1,500,000 – 6,000,000/month", growth_outlook="Stable", industry_field="Finance"),
        CareerPath(title="Civil Engineer", description="Design and oversee construction of infrastructure such as roads, bridges, and buildings.", related_programs=["BEng"], skills=["AutoCAD", "Structural Analysis", "Project Management", "Survey", "Construction Management"], potential_roles=["Civil Engineer", "Structural Engineer", "Project Manager", "Site Engineer", "Urban Planner"], average_salary_range="UGX 2,000,000 – 8,000,000/month", growth_outlook="High", industry_field="Engineering"),
        CareerPath(title="Teacher / Education Professional", description="Teach and mentor students at secondary and tertiary levels.", related_programs=["BEd", "DPED"], skills=["Curriculum Development", "Classroom Management", "Assessment", "Communication"], potential_roles=["Secondary School Teacher", "University Lecturer", "Education Officer", "Curriculum Developer"], average_salary_range="UGX 700,000 – 3,500,000/month", growth_outlook="Stable", industry_field="Education"),
        CareerPath(title="Public Health Officer / Epidemiologist", description="Work to improve community health outcomes through disease surveillance and health promotion.", related_programs=["BPH", "MBChB", "BNSc"], skills=["Epidemiology", "Health Promotion", "Data Collection", "Community Engagement", "Policy Analysis"], potential_roles=["Public Health Officer", "Epidemiologist", "Health Educator", "Environmental Health Officer"], average_salary_range="UGX 1,500,000 – 5,000,000/month", growth_outlook="High", industry_field="Healthcare"),
        CareerPath(title="Business Manager / Entrepreneur", description="Lead teams, manage business operations, and build your own enterprise.", related_programs=["BBA", "BCom", "DBA"], skills=["Leadership", "Strategic Planning", "Marketing", "Financial Management", "Negotiation"], potential_roles=["Business Manager", "Entrepreneur", "Operations Manager", "HR Manager", "Sales Manager"], average_salary_range="UGX 1,800,000 – 10,000,000/month", growth_outlook="High", industry_field="Business"),
        CareerPath(title="IT Support Specialist / Network Engineer", description="Provide technical support, manage networks, and ensure IT systems run smoothly.", related_programs=["DIT", "BSc IT"], skills=["Networking (CCNA)", "Linux", "Windows Server", "Troubleshooting", "VPN", "Cloud Computing"], potential_roles=["IT Support Officer", "Network Engineer", "Systems Administrator", "Help Desk Technician"], average_salary_range="UGX 1,000,000 – 4,000,000/month", growth_outlook="Moderate", industry_field="Technology"),
    ]
    db.session.add_all(career_paths)

    today = date.today()
    from datetime import timedelta
    opportunities = [
        Opportunity(title="Software Developer Intern", organization="MTN Uganda", type="internship", description="Join MTN Uganda's technology team to develop and maintain internal applications.", requirements="Final year student in CS or IT. Knowledge of Python or JavaScript.", required_programs=["BSc IT", "BSc CS"], required_skills=["Python", "JavaScript", "SQL"], location="Kampala, Uganda", salary_range="UGX 400,000/month", application_deadline=today + timedelta(days=30), contact_email="hr@mtn.ug", is_active=True),
        Opportunity(title="Junior Accountant", organization="Stanbic Bank Uganda", type="job", description="Stanbic Bank is looking for a dynamic Junior Accountant to join our finance team.", requirements="Bachelor's degree in Accounting, Commerce, or Finance. Strong attention to detail.", required_programs=["BCom", "BBA", "DACC"], required_skills=["Financial Reporting", "Excel", "IFRS", "Auditing"], location="Kampala, Uganda", salary_range="UGX 1,800,000 – 2,500,000/month", application_deadline=today + timedelta(days=21), contact_email="careers@stanbic.co.ug", is_active=True),
        Opportunity(title="Legal Intern", organization="Uganda Law Society", type="internship", description="Gain valuable practical legal experience with Uganda's premier legal professional body.", requirements="Final year LLB student. Strong research and writing skills.", required_programs=["LLB"], required_skills=["Legal Research", "Drafting", "Advocacy"], location="Kampala, Uganda", salary_range="UGX 300,000/month", application_deadline=today + timedelta(days=14), contact_email="info@ugandabar.org", is_active=True),
        Opportunity(title="Graduate Teacher (Mathematics & Sciences)", organization="St. Mary's College Kisubi", type="job", description="We seek a passionate Mathematics and Sciences teacher for A-Level classes.", requirements="Bachelor of Education with Mathematics/Sciences specialization.", required_programs=["BEd", "DPED"], required_skills=["Classroom Management", "Subject Expertise", "Curriculum Development"], location="Wakiso, Uganda", salary_range="UGX 900,000 – 1,400,000/month", application_deadline=today + timedelta(days=45), contact_email="principal@smck.ac.ug", is_active=True),
        Opportunity(title="Clinical Officer Intern", organization="Mulago National Referral Hospital", type="internship", description="Supervised clinical internships for medical and nursing graduates.", requirements="Graduate of MBChB, BNSc or DCM program.", required_programs=["MBChB", "BNSc", "DCM"], required_skills=["Clinical Diagnosis", "Patient Care", "Medical Ethics"], location="Kampala, Uganda", salary_range="UGX 500,000/month", application_deadline=today + timedelta(days=10), contact_email="internships@mulago.go.ug", is_active=True),
        Opportunity(title="Business Development Officer", organization="DFCU Bank", type="job", description="Drive business growth by identifying and acquiring new customers.", requirements="Bachelor's degree in Business Administration, Commerce or Marketing.", required_programs=["BBA", "BCom", "DBA"], required_skills=["Sales", "Negotiation", "Communication", "Marketing"], location="Kampala, Uganda", salary_range="UGX 1,500,000 – 2,200,000/month", application_deadline=today + timedelta(days=25), contact_email="careers@dfcubank.com", is_active=True),
        Opportunity(title="Graduate Engineer (Civil)", organization="Uganda National Roads Authority (UNRA)", type="job", description="UNRA seeks motivated graduate civil engineers for our road construction team.", requirements="Bachelor of Engineering (Civil). Knowledge of AutoCAD and surveying tools.", required_programs=["BEng"], required_skills=["AutoCAD", "Survey", "Project Management", "Structural Analysis"], location="Various - Uganda", salary_range="UGX 2,200,000 – 3,000,000/month", application_deadline=today + timedelta(days=35), contact_email="hr@unra.go.ug", is_active=True),
        Opportunity(title="IT Support Intern", organization="Airtel Uganda", type="internship", description="Support Airtel Uganda's IT infrastructure team.", requirements="Diploma or Degree in IT. Basic networking knowledge preferred.", required_programs=["BSc IT", "DIT"], required_skills=["Networking", "Linux", "Troubleshooting", "Windows Server"], location="Kampala, Uganda", salary_range="UGX 350,000/month", application_deadline=today + timedelta(days=20), contact_email="careers@ug.airtel.com", is_active=True),
        Opportunity(title="Public Health Officer", organization="Ministry of Health Uganda", type="job", description="Implement health programs and coordinate health education campaigns.", requirements="Bachelor of Public Health or related health degree.", required_programs=["BPH", "BNSc", "MBChB"], required_skills=["Epidemiology", "Health Promotion", "Community Engagement", "Data Collection"], location="Various Districts - Uganda", salary_range="UGX 1,200,000 – 1,800,000/month", application_deadline=today + timedelta(days=40), contact_email="hr@health.go.ug", is_active=True),
    ]
    db.session.add_all(opportunities)

    admin = User(
        email="admin@kiu.ac.ug",
        first_name="KIU",
        last_name="Administrator",
        role="admin",
        phone="+256700000000",
        is_verified=True,
    )
    admin.set_password("admin123")
    db.session.add(admin)

    db.session.commit()
    print("\n[KIU] ✓ Database seeded with programs, career paths, opportunities, and admin account.")
    print("[KIU] ✓ Admin login: admin@kiu.ac.ug / admin123\n", flush=True)


app = create_app()

if __name__ == "__main__":
    # Default port: 5001 for MySQL local dev, 8080 for PostgreSQL/Replit
    default_port = 5001 if IS_MYSQL else 8080
    port = int(os.environ.get("PORT", default_port))
    db_label = "MySQL (local)" if IS_MYSQL else "PostgreSQL (Replit)"
    print(f"\n{'='*60}")
    print(f"  KIU Portal API Server")
    print(f"  Database : {db_label}")
    print(f"  Port     : {port}")
    print(f"  Upload   : {UPLOAD_FOLDER}")
    print(f"{'='*60}\n", flush=True)
    app.run(host="0.0.0.0", port=port, debug=False)
