import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, jsonify
from flask_cors import CORS
from models import db, bcrypt

DATABASE_URL = os.environ.get("DATABASE_URL", "")


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }
    app.config["SECRET_KEY"] = os.environ.get("JWT_SECRET", "kiu-portal-secret-key-2024")

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
        return jsonify({"status": "ok"}), 200

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found", "message": str(e)}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method not allowed", "message": str(e)}), 405

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error": "Internal server error", "message": str(e)}), 500

    with app.app_context():
        db.create_all()
        _seed_data()

    return app


def _seed_data():
    from models import Program, CareerPath, Opportunity, User
    from datetime import date, timedelta, datetime

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
        Program(name="Diploma in Business Administration", code="DBA", faculty="Faculty of Business", department="Business Administration", level="diploma", duration="2 years", description="Foundation business skills for entry-level management.", entry_requirements="Uganda Certificate of Education (UCE) with at least 5 passes including English. Points: 24 or below.", min_olevel_points=24, min_alevel_points=None, available_slots=150),
        Program(name="Diploma in Information Technology", code="DIT", faculty="Faculty of Science and Technology", department="Information Technology", level="diploma", duration="2 years", description="Practical IT skills in networking, software, and databases.", entry_requirements="Uganda Certificate of Education (UCE) with passes in Mathematics and English.", min_olevel_points=28, min_alevel_points=None, available_slots=120),
        Program(name="Diploma in Clinical Medicine", code="DCM", faculty="Faculty of Medicine", department="Clinical Medicine", level="diploma", duration="3 years", description="Clinical medical skills for health facilities.", entry_requirements="UCE with Biology, Chemistry and English passes.", min_olevel_points=30, min_alevel_points=None, available_slots=80),
        Program(name="Diploma in Education", code="DPED", faculty="Faculty of Education", department="Education", level="diploma", duration="2 years", description="Prepares teachers for primary and lower secondary school.", entry_requirements="UCE with passes in at least 5 subjects including English.", min_olevel_points=28, min_alevel_points=None, available_slots=100),
        Program(name="Diploma in Accounting", code="DACC", faculty="Faculty of Business", department="Accounting", level="diploma", duration="2 years", description="Accounting and bookkeeping skills for business practice.", entry_requirements="UCE with Mathematics and English passes.", min_olevel_points=30, min_alevel_points=None, available_slots=100),
        Program(name="Bachelor of Public Health (BPH)", code="BPH", faculty="Faculty of Medicine", department="Public Health", level="degree", duration="3 years", description="Prepares health professionals for community and public health roles.", entry_requirements="2 principal passes at A-Level including Biology. Minimum 8 points.", min_olevel_points=40, min_alevel_points=8, available_slots=80),
    ]
    db.session.add_all(programs)
    db.session.flush()

    career_paths = [
        CareerPath(title="Software Engineer / Developer", description="Design and build software applications for businesses, government, and individuals. This path leads to roles in web development, mobile apps, and enterprise systems.", related_programs=["BSc IT", "BSc CS", "BBA"], skills=["Python", "JavaScript", "Java", "SQL", "Git", "Problem Solving", "Agile/Scrum"], potential_roles=["Software Developer", "Full Stack Developer", "Backend Engineer", "Frontend Developer", "Mobile Developer"], average_salary_range="UGX 1,500,000 – 6,000,000/month", growth_outlook="Very High - rapidly growing demand across all sectors", industry_field="Technology"),
        CareerPath(title="Data Analyst / Data Scientist", description="Analyze data to help organizations make informed decisions. Use statistics, machine learning, and visualization tools.", related_programs=["BSc CS", "BSc IT", "BCom", "BBA"], skills=["Python", "R", "SQL", "Power BI", "Tableau", "Statistics", "Machine Learning"], potential_roles=["Data Analyst", "Business Intelligence Analyst", "Data Scientist", "Research Analyst"], average_salary_range="UGX 2,000,000 – 7,000,000/month", growth_outlook="High - increasing reliance on data-driven decisions", industry_field="Technology"),
        CareerPath(title="Medical Doctor / Physician", description="Diagnose and treat patients across various specialties in hospitals and clinics. The foundation of Uganda's healthcare system.", related_programs=["MBChB", "BNSc", "BPH"], skills=["Clinical Diagnosis", "Patient Care", "Medical Ethics", "Research", "Communication", "Surgery basics"], potential_roles=["General Practitioner", "Surgeon", "Pediatrician", "Obstetrician", "Internist"], average_salary_range="UGX 2,500,000 – 15,000,000/month", growth_outlook="High - critical shortage of doctors in Uganda and East Africa", industry_field="Healthcare"),
        CareerPath(title="Lawyer / Legal Counsel", description="Represent clients in court, provide legal advice, and draft legal documents. Practice in corporate, criminal, civil or international law.", related_programs=["LLB"], skills=["Legal Research", "Advocacy", "Drafting", "Negotiation", "Critical Thinking", "Contract Law"], potential_roles=["Advocate", "State Attorney", "Corporate Counsel", "Legal Aid Lawyer", "Magistrate"], average_salary_range="UGX 2,000,000 – 12,000,000/month", growth_outlook="Stable - legal services always in demand", industry_field="Law"),
        CareerPath(title="Accountant / Financial Analyst", description="Manage financial records, prepare reports, and advise on financial planning for businesses and government agencies.", related_programs=["BCom", "BBA", "DACC"], skills=["Financial Reporting", "Taxation", "Auditing", "Excel", "IFRS", "Budgeting", "Tally/QuickBooks"], potential_roles=["Accountant", "Auditor", "Financial Analyst", "Tax Consultant", "CFO"], average_salary_range="UGX 1,500,000 – 6,000,000/month", growth_outlook="Stable - needed in every organization", industry_field="Finance"),
        CareerPath(title="Civil Engineer", description="Design and oversee construction of infrastructure such as roads, bridges, water systems and buildings.", related_programs=["BEng"], skills=["AutoCAD", "Structural Analysis", "Project Management", "Survey", "Construction Management", "Mathematics"], potential_roles=["Civil Engineer", "Structural Engineer", "Project Manager", "Site Engineer", "Urban Planner"], average_salary_range="UGX 2,000,000 – 8,000,000/month", growth_outlook="High - massive infrastructure projects across Uganda", industry_field="Engineering"),
        CareerPath(title="Teacher / Education Professional", description="Teach and mentor students at secondary and tertiary levels. Shape the next generation of Ugandan professionals.", related_programs=["BEd", "DPED"], skills=["Curriculum Development", "Classroom Management", "Assessment", "Communication", "Subject Expertise"], potential_roles=["Secondary School Teacher", "University Lecturer", "Education Officer", "Curriculum Developer", "Head Teacher"], average_salary_range="UGX 700,000 – 3,500,000/month", growth_outlook="Stable - education sector always hiring", industry_field="Education"),
        CareerPath(title="Public Health Officer / Epidemiologist", description="Work to improve community health outcomes through disease surveillance, health promotion, and policy implementation.", related_programs=["BPH", "MBChB", "BNSc"], skills=["Epidemiology", "Health Promotion", "Data Collection", "Community Engagement", "Policy Analysis"], potential_roles=["Public Health Officer", "Epidemiologist", "Health Educator", "Environmental Health Officer", "WHO/NGO Staff"], average_salary_range="UGX 1,500,000 – 5,000,000/month", growth_outlook="High - post-COVID global health awareness increased demand", industry_field="Healthcare"),
        CareerPath(title="Business Manager / Entrepreneur", description="Lead teams, manage business operations, and build your own enterprise. Uganda's growing economy creates many business opportunities.", related_programs=["BBA", "BCom", "DBA"], skills=["Leadership", "Strategic Planning", "Marketing", "Financial Management", "Negotiation", "Communication"], potential_roles=["Business Manager", "Entrepreneur", "Operations Manager", "HR Manager", "Sales Manager"], average_salary_range="UGX 1,800,000 – 10,000,000/month", growth_outlook="High - growing private sector in Uganda", industry_field="Business"),
        CareerPath(title="IT Support Specialist / Network Engineer", description="Provide technical support, manage networks, and ensure IT systems run smoothly in organizations.", related_programs=["DIT", "BSc IT"], skills=["Networking (CCNA)", "Linux", "Windows Server", "Troubleshooting", "VPN", "Cloud Computing"], potential_roles=["IT Support Officer", "Network Engineer", "Systems Administrator", "Help Desk Technician"], average_salary_range="UGX 1,000,000 – 4,000,000/month", growth_outlook="Moderate - needed in all digitizing organizations", industry_field="Technology"),
    ]
    db.session.add_all(career_paths)

    today = date.today()
    opportunities = [
        Opportunity(title="Software Developer Intern", organization="MTN Uganda", type="internship", description="Join MTN Uganda's technology team to develop and maintain internal applications. You will work with experienced developers on real projects that impact millions of users.", requirements="Final year student in Computer Science, Information Technology or related field. Knowledge of Python or JavaScript. Good communication skills.", required_programs=["BSc IT", "BSc CS"], required_skills=["Python", "JavaScript", "SQL"], location="Kampala, Uganda", salary_range="UGX 400,000/month", application_deadline=today + timedelta(days=30), contact_email="hr@mtn.ug", is_active=True),
        Opportunity(title="Junior Accountant", organization="Stanbic Bank Uganda", type="job", description="Stanbic Bank is looking for a dynamic Junior Accountant to join our finance team. You will assist with financial reporting, reconciliations and audit preparations.", requirements="Bachelor's degree in Accounting, Commerce, or Finance. CPA certification is an added advantage. Strong attention to detail.", required_programs=["BCom", "BBA", "DACC"], required_skills=["Financial Reporting", "Excel", "IFRS", "Auditing"], location="Kampala, Uganda", salary_range="UGX 1,800,000 – 2,500,000/month", application_deadline=today + timedelta(days=21), contact_email="careers@stanbic.co.ug", is_active=True),
        Opportunity(title="Legal Intern", organization="Uganda Law Society", type="internship", description="Gain valuable practical legal experience with Uganda's premier legal professional body. You will assist with research, drafting, and client advocacy.", requirements="Final year LLB student. Strong research and writing skills. Interest in advocacy and human rights.", required_programs=["LLB"], required_skills=["Legal Research", "Drafting", "Advocacy"], location="Kampala, Uganda", salary_range="UGX 300,000/month", application_deadline=today + timedelta(days=14), contact_email="info@ugandabar.org", is_active=True),
        Opportunity(title="Graduate Teacher (Mathematics & Sciences)", organization="St. Mary's College Kisubi", type="job", description="We seek a passionate Mathematics and Sciences teacher for our A-Level classes. Full-time permanent position with competitive benefits.", requirements="Bachelor of Education or related degree with specialization in Mathematics and/or Sciences. Teaching experience preferred.", required_programs=["BEd", "DPED"], required_skills=["Classroom Management", "Subject Expertise", "Curriculum Development"], location="Wakiso, Uganda", salary_range="UGX 900,000 – 1,400,000/month", application_deadline=today + timedelta(days=45), contact_email="principal@smck.ac.ug", is_active=True),
        Opportunity(title="Clinical Officer Intern", organization="Mulago National Referral Hospital", type="internship", description="Mulago Hospital offers supervised clinical internships for medical and nursing graduates. Gain hands-on patient care experience under specialist doctors.", requirements="Graduate of MBChB, BNSc or DCM program. Must be registered or provisionally registered with the Allied Health Professionals Council.", required_programs=["MBChB", "BNSc", "DCM"], required_skills=["Clinical Diagnosis", "Patient Care", "Medical Ethics"], location="Kampala, Uganda", salary_range="UGX 500,000/month", application_deadline=today + timedelta(days=10), contact_email="internships@mulago.go.ug", is_active=True),
        Opportunity(title="Business Development Officer", organization="DFCU Bank", type="job", description="Drive business growth by identifying and acquiring new customers, managing relationships, and promoting our products to individuals and SMEs.", requirements="Bachelor's degree in Business Administration, Commerce or Marketing. Strong interpersonal and sales skills. Experience is an advantage.", required_programs=["BBA", "BCom", "DBA"], required_skills=["Sales", "Negotiation", "Communication", "Marketing"], location="Kampala, Uganda", salary_range="UGX 1,500,000 – 2,200,000/month", application_deadline=today + timedelta(days=25), contact_email="careers@dfcubank.com", is_active=True),
        Opportunity(title="Graduate Engineer (Civil)", organization="Uganda National Roads Authority (UNRA)", type="job", description="UNRA seeks motivated graduate civil engineers to join our road construction and maintenance team across Uganda's highway network.", requirements="Bachelor of Engineering (Civil). Must have graduated within the last 2 years. Knowledge of AutoCAD and surveying tools.", required_programs=["BEng"], required_skills=["AutoCAD", "Survey", "Project Management", "Structural Analysis"], location="Various - Uganda", salary_range="UGX 2,200,000 – 3,000,000/month", application_deadline=today + timedelta(days=35), contact_email="hr@unra.go.ug", is_active=True),
        Opportunity(title="IT Support Intern", organization="Airtel Uganda", type="internship", description="Support Airtel Uganda's IT infrastructure team by troubleshooting systems, managing user accounts, and maintaining network equipment.", requirements="Diploma or Degree in IT. Basic networking knowledge (CCNA preferred). Ability to work in a fast-paced environment.", required_programs=["BSc IT", "DIT"], required_skills=["Networking", "Linux", "Troubleshooting", "Windows Server"], location="Kampala, Uganda", salary_range="UGX 350,000/month", application_deadline=today + timedelta(days=20), contact_email="careers@ug.airtel.com", is_active=True),
        Opportunity(title="Public Health Officer", organization="Ministry of Health Uganda", type="job", description="Join the Ministry of Health team to implement health programs, conduct disease surveillance, and coordinate health education campaigns at district level.", requirements="Bachelor of Public Health or related health degree. Strong communication skills. Willingness to work in field conditions.", required_programs=["BPH", "BNSc", "MBChB"], required_skills=["Epidemiology", "Health Promotion", "Community Engagement", "Data Collection"], location="Various Districts - Uganda", salary_range="UGX 1,200,000 – 1,800,000/month", application_deadline=today + timedelta(days=40), contact_email="hr@health.go.ug", is_active=True),
    ]
    db.session.add_all(opportunities)

    admin = User(email="admin@kiu.ac.ug", first_name="KIU", last_name="Administrator", role="admin", phone="+256700000000")
    admin.set_password("admin123")
    db.session.add(admin)

    db.session.commit()


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
