import os
import sys
import secrets
import random

sys.path.insert(0, os.path.dirname(__file__))

# Load .env file if present
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
except ImportError:
    pass  # dotenv not installed, rely on system env vars

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
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

# Local SQLite fallback when DATABASE_URL is empty (zero setup for development)
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///kiu_admissions.db"

IS_MYSQL = "mysql" in DATABASE_URL
IS_SQLITE = "sqlite" in DATABASE_URL

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}
MAX_CONTENT_MB = 5


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    if IS_SQLITE:
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {}
    else:
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "pool_pre_ping": True,
            "pool_recycle": 300,
        }
    jwt_secret = os.environ.get("JWT_SECRET", "")
    if not jwt_secret or jwt_secret == "change-me-to-a-random-secret-key":
        jwt_secret = secrets.token_hex(32)
        print("[WARNING] JWT_SECRET not set — using auto-generated key. Sessions will not persist across restarts.", flush=True)
    app.config["SECRET_KEY"] = jwt_secret
    app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_MB * 1024 * 1024
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    app.config["ALLOWED_EXTENSIONS"] = ALLOWED_EXTENSIONS

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(os.path.join(UPLOAD_FOLDER, "certificates"), exist_ok=True)

    cors_origins = os.environ.get("CORS_ORIGINS", "*")
    if cors_origins == "*":
        origins = "*"
    else:
        origins = [o.strip() for o in cors_origins.split(",") if o.strip()]
    CORS(app, resources={r"/api/*": {"origins": origins}})

    db.init_app(app)
    bcrypt.init_app(app)

    # Rate limiting — production-ready defaults
    Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://",
    )

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
        if IS_SQLITE:
            db_label = "sqlite"
        elif IS_MYSQL:
            db_label = "mysql"
        else:
            db_label = "postgresql"
        return jsonify({"status": "ok", "db": db_label}), 200

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
        # ── Faculty of Medicine ──────────────────────────────────────────
        Program(name="Bachelor of Medicine and Bachelor of Surgery", code="MBChB", faculty="Faculty of Medicine", department="Department of Medicine and Surgery", level="degree", duration="5 years", description="A comprehensive five-year medical degree program that prepares students for medical practice, covering clinical medicine, surgery, pediatrics, obstetrics and gynecology, and community health.", entry_requirements="UACE: 3 principal passes in Biology, Chemistry, and Physics/Mathematics with at least 15 points. UCE: At least 8 passes including English, Mathematics, Biology, Chemistry, and Physics.", min_olevel_points=32, min_alevel_points=15, available_slots=60),
        Program(name="Bachelor of Nursing Science", code="BNSc", faculty="Faculty of Medicine", department="Department of Nursing", level="degree", duration="4 years", description="Professional nursing degree program that trains students in patient care, community health nursing, midwifery, and healthcare management with extensive clinical rotations.", entry_requirements="UACE: 2 principal passes including Biology with at least 8 points. UCE: At least 5 passes including English, Biology, and Chemistry.", min_olevel_points=40, min_alevel_points=8, available_slots=80),
        Program(name="Bachelor of Pharmacy", code="BPharm", faculty="Faculty of Medicine", department="Department of Pharmacy", level="degree", duration="4 years", description="Pharmaceutical sciences program covering drug development, pharmacology, clinical pharmacy, and pharmaceutical care in hospital and community settings.", entry_requirements="UACE: 2 principal passes in Chemistry and Biology with at least 10 points. UCE: At least 5 passes including English, Mathematics, Chemistry, and Biology.", min_olevel_points=36, min_alevel_points=10, available_slots=60),
        Program(name="Bachelor of Public Health", code="BPH", faculty="Faculty of Medicine", department="Department of Public Health", level="degree", duration="3 years", description="Prepares health professionals for community health promotion, disease prevention, epidemiology, health policy, and environmental health management.", entry_requirements="UACE: 2 principal passes including Biology with at least 8 points. UCE: At least 5 passes including English and Biology.", min_olevel_points=40, min_alevel_points=8, available_slots=80),
        Program(name="Bachelor of Dental Surgery", code="BDS", faculty="Faculty of Medicine", department="Department of Dentistry", level="degree", duration="5 years", description="Comprehensive dental training covering oral health, restorative dentistry, oral surgery, orthodontics, and pediatric dentistry.", entry_requirements="UACE: 3 principal passes in Biology, Chemistry, and Physics with at least 15 points. UCE: At least 8 passes including English, Mathematics, Biology, Chemistry, and Physics.", min_olevel_points=32, min_alevel_points=15, available_slots=40),
        Program(name="Bachelor of Medical Laboratory Science", code="BMLS", faculty="Faculty of Medicine", department="Department of Medical Laboratory", level="degree", duration="4 years", description="Laboratory medicine program covering clinical chemistry, hematology, microbiology, histopathology, and immunology with hands-on lab training.", entry_requirements="UACE: 2 principal passes in Biology and Chemistry with at least 10 points. UCE: At least 5 passes including English, Biology, Chemistry, and Mathematics.", min_olevel_points=36, min_alevel_points=10, available_slots=50),

        # ── Faculty of Law ───────────────────────────────────────────────
        Program(name="Bachelor of Laws", code="LLB", faculty="Faculty of Law", department="Department of Law", level="degree", duration="4 years", description="Rigorous legal education covering constitutional law, criminal law, contract law, tort law, property law, international law, and legal research and writing.", entry_requirements="UACE: 2 principal passes with at least 10 points, including Literature in English or History. UCE: At least 6 passes including English and Literature.", min_olevel_points=36, min_alevel_points=10, available_slots=80),
        Program(name="Diploma in Law", code="DLAW", faculty="Faculty of Law", department="Department of Law", level="diploma", duration="2 years", description="Foundation legal studies covering legal principles, legal writing, and basic legal practice for paralegal and legal assistant roles.", entry_requirements="UCE: At least 5 passes including English and Literature.", min_olevel_points=28, min_alevel_points=None, available_slots=60),

        # ── Faculty of Business and Management ───────────────────────────
        Program(name="Bachelor of Business Administration", code="BBA", faculty="Faculty of Business and Management", department="Department of Business Administration", level="degree", duration="3 years", description="Comprehensive business degree covering management, finance, marketing, human resources, entrepreneurship, and strategic planning.", entry_requirements="UACE: 2 principal passes with at least 8 points. UCE: At least 5 passes including English and Mathematics.", min_olevel_points=40, min_alevel_points=8, available_slots=120),
        Program(name="Bachelor of Commerce", code="BCom", faculty="Faculty of Business and Management", department="Department of Commerce", level="degree", duration="3 years", description="Commerce degree covering accounting, finance, economics, taxation, auditing, and financial management.", entry_requirements="UACE: 2 principal passes including Economics or Mathematics with at least 8 points. UCE: At least 5 passes including English and Mathematics.", min_olevel_points=40, min_alevel_points=8, available_slots=100),
        Program(name="Bachelor of Human Resource Management", code="BHRM", faculty="Faculty of Business and Management", department="Department of Human Resources", level="degree", duration="3 years", description="HR management program covering recruitment, training, compensation, labor relations, and organizational development.", entry_requirements="UACE: 2 principal passes with at least 8 points. UCE: At least 5 passes including English.", min_olevel_points=40, min_alevel_points=8, available_slots=80),
        Program(name="Bachelor of Procurement and Supply Chain Management", code="BPSCM", faculty="Faculty of Business and Management", department="Department of Procurement", level="degree", duration="3 years", description="Supply chain program covering procurement, logistics, inventory management, and vendor relations.", entry_requirements="UACE: 2 principal passes with at least 8 points. UCE: At least 5 passes including English and Mathematics.", min_olevel_points=40, min_alevel_points=8, available_slots=60),
        Program(name="Diploma in Business Administration", code="DBA", faculty="Faculty of Business and Management", department="Department of Business Administration", level="diploma", duration="2 years", description="Foundation business skills for entry-level management, administration, and entrepreneurship.", entry_requirements="UCE: At least 5 passes including English.", min_olevel_points=24, min_alevel_points=None, available_slots=150),
        Program(name="Diploma in Accounting", code="DACC", faculty="Faculty of Business and Management", department="Department of Accounting", level="diploma", duration="2 years", description="Accounting and bookkeeping skills for business practice, financial reporting, and tax compliance.", entry_requirements="UCE: At least 5 passes including English and Mathematics.", min_olevel_points=28, min_alevel_points=None, available_slots=100),

        # ── Faculty of Science and Technology ────────────────────────────
        Program(name="Bachelor of Science in Information Technology", code="BSc IT", faculty="Faculty of Science and Technology", department="Department of Information Technology", level="degree", duration="3 years", description="IT degree covering software development, networking, databases, cybersecurity, cloud computing, and IT project management.", entry_requirements="UACE: 2 principal passes including Mathematics or Physics with at least 8 points. UCE: At least 5 passes including English, Mathematics, and Physics.", min_olevel_points=40, min_alevel_points=8, available_slots=100),
        Program(name="Bachelor of Science in Computer Science", code="BSc CS", faculty="Faculty of Science and Technology", department="Department of Computer Science", level="degree", duration="3 years", description="Computer science program covering algorithms, data structures, artificial intelligence, machine learning, and software engineering.", entry_requirements="UACE: 2 principal passes including Mathematics with at least 10 points. UCE: At least 5 passes including English, Mathematics, and Physics.", min_olevel_points=40, min_alevel_points=10, available_slots=80),
        Program(name="Bachelor of Science in Software Engineering", code="BSc SE", faculty="Faculty of Science and Technology", department="Department of Software Engineering", level="degree", duration="4 years", description="Software engineering program covering full-stack development, DevOps, testing, and software architecture.", entry_requirements="UACE: 2 principal passes including Mathematics with at least 10 points. UCE: At least 5 passes including English, Mathematics, and Physics.", min_olevel_points=40, min_alevel_points=10, available_slots=60),
        Program(name="Bachelor of Engineering (Civil)", code="BEng Civ", faculty="Faculty of Science and Technology", department="Department of Civil Engineering", level="degree", duration="4 years", description="Civil engineering covering structural design, water resources, transportation engineering, geotechnical engineering, and construction management.", entry_requirements="UACE: 3 principal passes in Mathematics, Physics, and Chemistry with at least 12 points. UCE: At least 6 passes including English, Mathematics, Physics, and Chemistry.", min_olevel_points=40, min_alevel_points=12, available_slots=60),
        Program(name="Bachelor of Engineering (Electrical)", code="BEng Elec", faculty="Faculty of Science and Technology", department="Department of Electrical Engineering", level="degree", duration="4 years", description="Electrical engineering covering power systems, electronics, telecommunications, control systems, and renewable energy.", entry_requirements="UACE: 3 principal passes in Mathematics, Physics, and Chemistry with at least 12 points. UCE: At least 6 passes including English, Mathematics, Physics, and Chemistry.", min_olevel_points=40, min_alevel_points=12, available_slots=50),
        Program(name="Bachelor of Engineering (Mechanical)", code="BEng Mech", faculty="Faculty of Science and Technology", department="Department of Mechanical Engineering", level="degree", duration="4 years", description="Mechanical engineering covering thermodynamics, manufacturing, robotics, automotive engineering, and energy systems.", entry_requirements="UACE: 3 principal passes in Mathematics, Physics, and Chemistry with at least 12 points. UCE: At least 6 passes including English, Mathematics, Physics, and Chemistry.", min_olevel_points=40, min_alevel_points=12, available_slots=50),
        Program(name="Bachelor of Science in Biotechnology", code="BSc BT", faculty="Faculty of Science and Technology", department="Department of Biotechnology", level="degree", duration="3 years", description="Biotechnology program covering genetic engineering, bioinformatics, industrial biotechnology, and agricultural biotechnology.", entry_requirements="UACE: 2 principal passes in Biology and Chemistry with at least 10 points. UCE: At least 5 passes including English, Biology, Chemistry, and Mathematics.", min_olevel_points=38, min_alevel_points=10, available_slots=40),
        Program(name="Diploma in Information Technology", code="DIT", faculty="Faculty of Science and Technology", department="Department of Information Technology", level="diploma", duration="2 years", description="Practical IT skills in networking, software installation, database management, and technical support.", entry_requirements="UCE: At least 5 passes including English and Mathematics.", min_olevel_points=28, min_alevel_points=None, available_slots=120),
        Program(name="Diploma in Computer Science", code="DCS", faculty="Faculty of Science and Technology", department="Department of Computer Science", level="diploma", duration="2 years", description="Foundation computer science covering programming, web development, and basic networking.", entry_requirements="UCE: At least 5 passes including English, Mathematics, and Physics.", min_olevel_points=28, min_alevel_points=None, available_slots=80),

        # ── Faculty of Education ─────────────────────────────────────────
        Program(name="Bachelor of Education (Secondary)", code="BEd Sec", faculty="Faculty of Education", department="Department of Secondary Education", level="degree", duration="3 years", description="Teacher training for secondary schools with specialization in subject teaching methods, curriculum development, and educational psychology.", entry_requirements="UACE: 2 principal passes with at least 8 points. UCE: At least 5 passes including English.", min_olevel_points=40, min_alevel_points=8, available_slots=100),
        Program(name="Bachelor of Education (Primary)", code="BEd Pri", faculty="Faculty of Education", department="Department of Primary Education", level="degree", duration="3 years", description="Teacher training for primary schools covering child development, literacy, numeracy, and classroom management.", entry_requirements="UACE: 2 principal passes with at least 8 points. UCE: At least 5 passes including English.", min_olevel_points=40, min_alevel_points=8, available_slots=100),
        Program(name="Bachelor of Education (Special Needs)", code="BEd SNE", faculty="Faculty of Education", department="Department of Special Needs Education", level="degree", duration="3 years", description="Special education training for teaching children with disabilities, learning difficulties, and special educational needs.", entry_requirements="UACE: 2 principal passes with at least 8 points. UCE: At least 5 passes including English.", min_olevel_points=40, min_alevel_points=8, available_slots=40),
        Program(name="Diploma in Education (Primary)", code="DipEd Pri", faculty="Faculty of Education", department="Department of Primary Education", level="diploma", duration="2 years", description="Foundation teaching skills for primary school education.", entry_requirements="UCE: At least 5 passes including English.", min_olevel_points=28, min_alevel_points=None, available_slots=100),

        # ── Faculty of Social Sciences ───────────────────────────────────
        Program(name="Bachelor of Social Work and Social Administration", code="BSWSA", faculty="Faculty of Social Sciences", department="Department of Social Work", level="degree", duration="3 years", description="Social work program covering community development, counseling, social policy, and human rights advocacy.", entry_requirements="UACE: 2 principal passes with at least 8 points. UCE: At least 5 passes including English.", min_olevel_points=40, min_alevel_points=8, available_slots=60),
        Program(name="Bachelor of Journalism and Mass Communication", code="BJMC", faculty="Faculty of Social Sciences", department="Department of Journalism", level="degree", duration="3 years", description="Media and communication program covering print, broadcast, digital journalism, public relations, and media ethics.", entry_requirements="UACE: 2 principal passes with at least 8 points. UCE: At least 5 passes including English and Literature.", min_olevel_points=40, min_alevel_points=8, available_slots=60),
        Program(name="Bachelor of International Relations", code="BIR", faculty="Faculty of Social Sciences", department="Department of Political Science", level="degree", duration="3 years", description="International relations covering diplomacy, global politics, conflict resolution, and international organizations.", entry_requirements="UACE: 2 principal passes including History or Economics with at least 8 points. UCE: At least 5 passes including English and History.", min_olevel_points=40, min_alevel_points=8, available_slots=50),
        Program(name="Bachelor of Psychology", code="BPsy", faculty="Faculty of Social Sciences", department="Department of Psychology", level="degree", duration="3 years", description="Psychology program covering clinical, developmental, organizational, and forensic psychology.", entry_requirements="UACE: 2 principal passes with at least 8 points. UCE: At least 5 passes including English and Mathematics.", min_olevel_points=40, min_alevel_points=8, available_slots=50),
    ]
    db.session.add_all(programs)
    db.session.flush()

    career_paths = [
        # ── Healthcare & Medicine ────────────────────────────────────────
        CareerPath(title="Medical Doctor / Physician", description="Diagnose and treat patients across various specialties including internal medicine, surgery, pediatrics, and obstetrics.", related_programs=["MBChB", "BPharm", "BPH"], skills=["Clinical Diagnosis", "Patient Care", "Medical Ethics", "Research", "Communication", "Surgery"], potential_roles=["General Practitioner", "Surgeon", "Pediatrician", "Obstetrician", "Cardiologist", "Neurologist"], average_salary_range="UGX 2,500,000 – 15,000,000/month", growth_outlook="High", industry_field="Healthcare"),
        CareerPath(title="Pharmacist", description="Dispense medications, advise patients on drug use, and ensure pharmaceutical safety in hospitals and community pharmacies.", related_programs=["BPharm"], skills=["Pharmacology", "Drug Safety", "Patient Counseling", "Prescription Review", "Inventory Management"], potential_roles=["Hospital Pharmacist", "Community Pharmacist", "Clinical Pharmacist", "Pharmaceutical Researcher"], average_salary_range="UGX 1,500,000 – 6,000,000/month", growth_outlook="High", industry_field="Healthcare"),
        CareerPath(title="Nurse / Midwife", description="Provide patient care, assist in surgeries, conduct health education, and support maternal and child health.", related_programs=["BNSc"], skills=["Patient Care", "Clinical Skills", "Health Education", "Midwifery", "Emergency Response"], potential_roles=["Registered Nurse", "Midwife", "Nurse Manager", "Community Health Nurse", "ICU Nurse"], average_salary_range="UGX 1,000,000 – 4,000,000/month", growth_outlook="High", industry_field="Healthcare"),
        CareerPath(title="Public Health Officer", description="Implement disease prevention programs, conduct epidemiological investigations, and promote community health.", related_programs=["BPH", "BNSc"], skills=["Epidemiology", "Health Promotion", "Data Collection", "Community Engagement", "Policy Analysis"], potential_roles=["Public Health Officer", "Epidemiologist", "Health Educator", "Environmental Health Officer", "Disease Surveillance Officer"], average_salary_range="UGX 1,500,000 – 5,000,000/month", growth_outlook="High", industry_field="Healthcare"),
        CareerPath(title="Medical Laboratory Scientist", description="Perform diagnostic tests, analyze samples, and support clinical diagnosis in hospital laboratories.", related_programs=["BMLS"], skills=["Laboratory Techniques", "Clinical Chemistry", "Microbiology", "Hematology", "Quality Control"], potential_roles=["Lab Technologist", "Lab Manager", "Research Scientist", "Quality Assurance Officer"], average_salary_range="UGX 1,200,000 – 4,500,000/month", growth_outlook="High", industry_field="Healthcare"),
        CareerPath(title="Dentist", description="Provide oral health care including diagnosis, treatment, and prevention of dental diseases.", related_programs=["BDS"], skills=["Dental Surgery", "Restorative Dentistry", "Oral Diagnosis", "Patient Care", "Orthodontics"], potential_roles=["General Dentist", "Oral Surgeon", "Orthodontist", "Pediatric Dentist"], average_salary_range="UGX 2,000,000 – 10,000,000/month", growth_outlook="High", industry_field="Healthcare"),

        # ── Law & Legal ─────────────────────────────────────────────────
        CareerPath(title="Lawyer / Legal Counsel", description="Represent clients in court, provide legal advice, draft legal documents, and handle litigation.", related_programs=["LLB", "DLAW"], skills=["Legal Research", "Advocacy", "Drafting", "Negotiation", "Critical Thinking", "Court Procedure"], potential_roles=["Advocate", "State Attorney", "Corporate Counsel", "Legal Aid Lawyer", "Magistrate", "Paralegal"], average_salary_range="UGX 2,000,000 – 12,000,000/month", growth_outlook="Stable", industry_field="Law"),

        # ── Business & Commerce ──────────────────────────────────────────
        CareerPath(title="Business Manager / Entrepreneur", description="Lead teams, manage business operations, develop strategies, and build enterprises.", related_programs=["BBA", "BCom", "BHRM", "BPSCM"], skills=["Leadership", "Strategic Planning", "Marketing", "Financial Management", "Negotiation", "Project Management"], potential_roles=["Business Manager", "Entrepreneur", "Operations Manager", "HR Manager", "Sales Manager", "CEO"], average_salary_range="UGX 1,800,000 – 10,000,000/month", growth_outlook="High", industry_field="Business"),
        CareerPath(title="Accountant / Financial Analyst", description="Manage financial records, prepare reports, conduct audits, and advise on financial planning.", related_programs=["BCom", "BBA", "DACC"], skills=["Financial Reporting", "Taxation", "Auditing", "Excel", "IFRS", "Budgeting", "QuickBooks"], potential_roles=["Accountant", "Auditor", "Financial Analyst", "Tax Consultant", "CFO", "Finance Manager"], average_salary_range="UGX 1,500,000 – 6,000,000/month", growth_outlook="Stable", industry_field="Finance"),
        CareerPath(title="Human Resource Manager", description="Manage recruitment, training, employee relations, compensation, and organizational development.", related_programs=["BHRM", "BBA"], skills=["Recruitment", "Training & Development", "Labor Relations", "Compensation Management", "Conflict Resolution"], potential_roles=["HR Manager", "HR Officer", "Recruitment Specialist", "Training Manager", "HR Consultant"], average_salary_range="UGX 1,500,000 – 6,000,000/month", growth_outlook="Stable", industry_field="Business"),
        CareerPath(title="Procurement & Supply Chain Manager", description="Manage procurement processes, supplier relationships, logistics, and inventory systems.", related_programs=["BPSCM", "BBA"], skills=["Procurement", "Vendor Management", "Logistics", "Inventory Control", "Contract Negotiation"], potential_roles=["Procurement Officer", "Supply Chain Manager", "Logistics Coordinator", "Warehouse Manager"], average_salary_range="UGX 1,500,000 – 5,000,000/month", growth_outlook="Moderate", industry_field="Business"),

        # ── Technology & Engineering ─────────────────────────────────────
        CareerPath(title="Software Engineer / Developer", description="Design, build, and maintain software applications for businesses, government, and individuals.", related_programs=["BSc IT", "BSc CS", "BSc SE", "DCS"], skills=["Python", "JavaScript", "Java", "SQL", "Git", "Problem Solving", "Agile/Scrum", "React", "Node.js"], potential_roles=["Software Developer", "Full Stack Developer", "Backend Engineer", "Frontend Developer", "Mobile Developer", "DevOps Engineer"], average_salary_range="UGX 1,500,000 – 6,000,000/month", growth_outlook="Very High", industry_field="Technology"),
        CareerPath(title="Data Analyst / Data Scientist", description="Analyze data to help organizations make informed decisions using statistical and machine learning techniques.", related_programs=["BSc CS", "BSc IT", "BCom"], skills=["Python", "R", "SQL", "Power BI", "Tableau", "Statistics", "Machine Learning", "Excel"], potential_roles=["Data Analyst", "Business Intelligence Analyst", "Data Scientist", "Research Analyst", "Data Engineer"], average_salary_range="UGX 2,000,000 – 7,000,000/month", growth_outlook="High", industry_field="Technology"),
        CareerPath(title="IT Support Specialist / Network Engineer", description="Provide technical support, manage networks, ensure IT security, and maintain systems.", related_programs=["BSc IT", "DIT", "DCS"], skills=["Networking (CCNA)", "Linux", "Windows Server", "Troubleshooting", "VPN", "Cloud Computing", "Cybersecurity"], potential_roles=["IT Support Officer", "Network Engineer", "Systems Administrator", "Help Desk Technician", "IT Manager"], average_salary_range="UGX 1,000,000 – 4,000,000/month", growth_outlook="Moderate", industry_field="Technology"),
        CareerPath(title="Civil Engineer", description="Design and oversee construction of roads, bridges, buildings, water systems, and other infrastructure.", related_programs=["BEng Civ"], skills=["AutoCAD", "Structural Analysis", "Project Management", "Survey", "Construction Management", "Water Resources"], potential_roles=["Civil Engineer", "Structural Engineer", "Project Manager", "Site Engineer", "Urban Planner", "Quantity Surveyor"], average_salary_range="UGX 2,000,000 – 8,000,000/month", growth_outlook="High", industry_field="Engineering"),
        CareerPath(title="Electrical Engineer", description="Design and maintain electrical systems, power distribution, electronics, and telecommunications.", related_programs=["BEng Elec"], skills=["Circuit Design", "Power Systems", "Electronics", "PLC Programming", "Renewable Energy"], potential_roles=["Electrical Engineer", "Power Engineer", "Telecom Engineer", "Control Systems Engineer"], average_salary_range="UGX 2,000,000 – 8,000,000/month", growth_outlook="High", industry_field="Engineering"),
        CareerPath(title="Mechanical Engineer", description="Design, develop, and maintain mechanical systems including machines, engines, and manufacturing equipment.", related_programs=["BEng Mech"], skills=["CAD/CAM", "Thermodynamics", "Manufacturing", "Robotics", "Automotive Engineering"], potential_roles=["Mechanical Engineer", "Design Engineer", "Production Manager", "R&D Engineer"], average_salary_range="UGX 2,000,000 – 8,000,000/month", growth_outlook="High", industry_field="Engineering"),

        # ── Education ───────────────────────────────────────────────────
        CareerPath(title="Teacher / Education Professional", description="Teach and mentor students, develop curriculum, and contribute to educational development.", related_programs=["BEd Sec", "BEd Pri", "BEd SNE", "DipEd Pri"], skills=["Curriculum Development", "Classroom Management", "Assessment", "Communication", "Subject Expertise", "Special Needs Education"], potential_roles=["Secondary School Teacher", "Primary School Teacher", "University Lecturer", "Education Officer", "Curriculum Developer", "Special Needs Teacher"], average_salary_range="UGX 700,000 – 3,500,000/month", growth_outlook="Stable", industry_field="Education"),

        # ── Social Sciences & Media ──────────────────────────────────────
        CareerPath(title="Social Worker / Community Developer", description="Support vulnerable populations, manage social programs, and advocate for community development.", related_programs=["BSWSA"], skills=["Counseling", "Community Development", "Social Policy", "Case Management", "Human Rights Advocacy"], potential_roles=["Social Worker", "Community Developer", "Program Manager", "Counselor", "NGO Officer"], average_salary_range="UGX 1,000,000 – 4,000,000/month", growth_outlook="Moderate", industry_field="Social Services"),
        CareerPath(title="Journalist / Media Professional", description="Report news, create content, and communicate information through print, broadcast, and digital media.", related_programs=["BJMC"], skills=["Writing", "Reporting", "Video Production", "Digital Media", "Public Relations", "Media Ethics"], potential_roles=["Journalist", "News Anchor", "Content Creator", "PR Officer", "Editor", "Media Consultant"], average_salary_range="UGX 1,000,000 – 5,000,000/month", growth_outlook="Moderate", industry_field="Media & Communications"),
        CareerPath(title="Diplomat / International Relations Specialist", description="Work in diplomacy, foreign affairs, international organizations, and conflict resolution.", related_programs=["BIR"], skills=["Diplomacy", "International Law", "Conflict Resolution", "Political Analysis", "Foreign Languages"], potential_roles=["Diplomat", "Foreign Service Officer", "International Organization Officer", "Policy Analyst"], average_salary_range="UGX 2,000,000 – 8,000,000/month", growth_outlook="Moderate", industry_field="Government & International"),
        CareerPath(title="Psychologist / Counselor", description="Provide mental health support, conduct assessments, and help individuals cope with life challenges.", related_programs=["BPsy"], skills=["Counseling", "Psychological Assessment", "Research Methods", "Crisis Intervention", "Group Therapy"], potential_roles=["Clinical Psychologist", "Counselor", "HR Psychologist", "School Psychologist", "Research Psychologist"], average_salary_range="UGX 1,500,000 – 6,000,000/month", growth_outlook="High", industry_field="Healthcare & Social Services"),
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

    import string as _string
    # Check if admin already exists
    admin = User.query.filter_by(email="admin@kiu.ac.ug").first()
    if not admin:
        admin_pw = "".join(random.choices(_string.ascii_letters + _string.digits + "!@#$%", k=12))
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
    else:
        admin_pw = "(existing - use current password)"

    db.session.commit()
    print(f"\n{'='*60}", flush=True)
    print(f"  KIU PORTAL — DATABASE SEEDED", flush=True)
    print(f"{'='*60}", flush=True)
    print(f"  Programs     : {len(programs)}", flush=True)
    print(f"  Career Paths : {len(career_paths)}", flush=True)
    print(f"  Opportunities: {len(opportunities)}", flush=True)
    print(f"{'='*60}", flush=True)
    print(f"  Admin Login", flush=True)
    print(f"  Email    : admin@kiu.ac.ug", flush=True)
    print(f"  Password : {admin_pw}", flush=True)
    print(f"{'='*60}\n", flush=True)


app = create_app()

if __name__ == "__main__":
    # Default port: 5001 for local dev, 8080 for PostgreSQL/Replit
    default_port = 5001
    port = int(os.environ.get("PORT", default_port))
    if IS_SQLITE:
        db_label = "SQLite (local)"
    elif IS_MYSQL:
        db_label = "MySQL (local)"
    else:
        db_label = "PostgreSQL (Replit)"
    print(f"\n{'='*60}")
    print(f"  KIU Portal API Server")
    print(f"  Database : {db_label}")
    print(f"  Port     : {port}")
    print(f"  Upload   : {UPLOAD_FOLDER}")
    print(f"{'='*60}\n", flush=True)
    app.run(host="0.0.0.0", port=port, debug=False)
