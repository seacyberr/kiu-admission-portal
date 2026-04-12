# KIU Admission Portal - Final Year Project Documentation

## 📋 Project Overview

**Project Title:** KIU Admission Portal with NCHE Recommendation Engine  
**Institution:** Kampala International University  
**Author:** [Student Name]  
**Supervisor:** [Supervisor Name]  
**Date:** 2026

---

## 🎯 Abstract

This project presents a comprehensive web-based Admission and Career Management System for Kampala International University (KIU). The system addresses the challenges of manual admission processes by implementing:

1. **NCHE Uganda-compliant recommendation engine** - Automatically recommends suitable programs based on student qualifications
2. **Multi-step application wizard** - Streamlined 6-step application process
3. **Payment integration** - Mobile Money (MTN/Airtel) and bank transfer support
4. **Finalist career management** - Job matching, career recommendations, and alumni tracking
5. **LinkedIn integration** - Professional profile import and skill synchronization

The system supports Uganda's complete education pathway from O-Level (UCE) through PhD, ensuring compliance with National Council for Higher Education (NCHE) requirements.

---

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Layer                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Web App    │  │   Admin      │  │   Mobile     │      │
│  │   (React)    │  │   Dashboard  │  │   (Future)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTPS/REST API
┌────────────────────▼────────────────────────────────────────┐
│                   API Gateway                                │
│              (Flask + JWT Auth)                              │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
┌───────▼───┐ ┌──────▼────┐ ┌─────▼──────┐
│  Business │ │  Data     │ │  External  │
│  Logic    │ │  Layer    │ │  Services  │
│           │ │           │ │            │
│ • NCHE    │ │ • PostgreSQL│ │ • LinkedIn │
│ • Payment │ │ • Redis   │ │ • MTN/Airtel│
│ • Career  │ │ • S3      │ │ • Email    │
└───────────┘ └───────────┘ └────────────┘
```

---

## 💻 Technology Stack

### Backend
| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | Flask 2.x | REST API development |
| ORM | SQLAlchemy | Database abstraction |
| Database | PostgreSQL | Primary data storage |
| Auth | JWT (PyJWT) | Token-based authentication |
| Validation | Marshmallow | Data serialization |
| Testing | Pytest | Unit and integration tests |

### Frontend
| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | React 18.x | UI development |
| Language | TypeScript | Type-safe JavaScript |
| Styling | Tailwind CSS | Utility-first CSS |
| Routing | Wouter | Client-side routing |
| Forms | React Hook Form | Form management |
| Validation | Zod | Schema validation |
| HTTP Client | Fetch API | API communication |

### DevOps & Tools
| Component | Technology | Purpose |
|-----------|------------|---------|
| Package Manager | pnpm | Monorepo management |
| Linting | ESLint | Code quality |
| Formatting | Prettier | Code formatting |
| Version Control | Git | Source control |

---

## 📚 Features Implemented

### 1. NCHE Recommendation Engine ✅
**Status:** Fully Implemented

- **UACE Assessment:** Principal passes validation, subject combination matching
- **UCE Assessment:** Division-based entry (Certificate/Diploma programs)
- **HEC Assessment:** Track-specific recommendations (Arts/Physical/Biological)
- **Diploma Assessment:** Class-based entry (Pass/Credit/Distinction)
- **Mature Entry:** Work experience and professional qualifications
- **Credit Transfer:** Year 2/3 entry for diploma holders

**Files:**
- `apps/flask-api/routes/nche_recommendations.py` (1,300+ lines)
- `apps/flask-api/data/*.py` (Program catalogs)

### 2. Multi-Step Application Wizard ✅
**Status:** Fully Implemented

**Steps:**
1. Personal Information
2. Contact & Location
3. Education Background
4. Document Upload
5. Program Selection
6. Payment

**Features:**
- Draft save/resume
- Form validation
- Document upload (PDF, images)
- Real-time progress tracking
- Payment integration

**Files:**
- `apps/kiu-portal/src/pages/applicant/application/index.tsx`
- `apps/flask-api/routes/admission.py`

### 3. Payment System ✅
**Status:** Fully Implemented

**Payment Methods:**
- MTN Mobile Money
- Airtel Money
- Bank Transfer (Stanbic Bank)

**Features:**
- UGX 50,000 application fee
- Payment verification
- Receipt generation
- Transaction tracking

**Files:**
- `apps/flask-api/services/payment_service.py`
- `apps/flask-api/routes/payments.py`

### 4. Admin Dashboard ✅
**Status:** Fully Implemented

**Features:**
- Application listing with filters
- Status management (Pending → Review → Accept/Reject)
- Document review
- CSV export
- Statistics dashboard
- Bulk operations

**Files:**
- `apps/kiu-portal/src/pages/admin/admissions-enhanced.tsx`

### 5. Career Services ✅
**Status:** Fully Implemented

**Features:**
- AI-powered job matching
- Career path recommendations
- Skills gap analysis
- Employer partner directory
- Career events calendar
- Resume workshop registration

**Files:**
- `apps/flask-api/routes/career.py`
- `apps/flask-api/routes/opportunities.py`

### 6. LinkedIn Integration ✅
**Status:** Fully Implemented

**Features:**
- OAuth 2.0 authentication
- Profile data import
- Skills synchronization
- Professional network connection
- Employment verification

**Files:**
- `apps/flask-api/routes/linkedin_auth.py`
- `apps/flask-api/config/linkedin.py`
- `apps/kiu-portal/src/components/LinkedInLogin.tsx`

---

## 🎓 Finalist & Career Management

### Finalist Tracking
- Student profile management
- Clearance status tracking (Library, Finance, Academic, Hostel)
- Graduation workflow
- Alumni transition

### Job Portal
- Advanced job search with filters
- Trending jobs analytics
- Salary insights by industry
- Application tracking
- Saved jobs/bookmarks

### Career Matching Algorithm
```
Match Score = Program Match (30%) + Skill Overlap (40%) + GPA Bonus (10%) + Recent Posting (5%)
```

---

## 📊 Database Schema (Key Tables)

```
users
├── id, email, password_hash, role, created_at
├── linkedin_id, linkedin_access_token (LinkedIn OAuth)
└── is_active, email_verified

programs
├── id, name, code, level, faculty
├── duration, campus, requirements
├── career_paths, required_subjects
└── is_active

admission_applications
├── id, user_id, program_id, status
├── personal_info (JSON)
├── education_background (JSON)
├── documents (JSON array)
├── payment_status
└── submitted_at, updated_at

payments
├── id, user_id, application_id
├── amount, currency, method
├── transaction_id, status
└── paid_at

finalist_profiles
├── user_id, program_id, gpa, skills
├── linkedin_headline, linkedin_skills
├── clearance_status
└── graduation_date

opportunities
├── id, title, company, description
├── type, location, salary_range
├── required_skills, required_programs
├── posted_by, status
└── created_at
```

---

## 🔐 Security Features

1. **Authentication:** JWT tokens with expiration
2. **Authorization:** Role-based access control (RBAC)
3. **Password Security:** bcrypt hashing
4. **Input Validation:** Zod schemas (frontend) + Marshmallow (backend)
5. **CSRF Protection:** State parameter in OAuth
6. **HTTPS:** SSL/TLS encryption (production)
7. **Rate Limiting:** API throttling
8. **File Upload:** Type and size validation

---

## 🧪 Testing Strategy

### Unit Tests
```bash
# Backend
cd apps/flask-api
pytest tests/

# Frontend
cd apps/kiu-portal
npm run test
```

### Integration Tests
- API endpoint testing
- Database transaction testing
- Payment flow simulation

### Manual Testing Checklist
- [x] UACE recommendation flow
- [x] UCE recommendation flow
- [x] Application submission
- [x] Payment processing
- [x] Admin approval workflow
- [x] LinkedIn OAuth flow
- [x] Job application flow

---

## 🚀 Deployment Guide

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis (optional, for caching)

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/kiu_portal

# Security
JWT_SECRET=your-secret-key

# LinkedIn
LINKEDIN_CLIENT_ID=your-client-id
LINKEDIN_CLIENT_SECRET=your-client-secret

# Payment (MTN/Airtel)
MTN_MOMO_API_KEY=xxx
AIRTEL_MONEY_CLIENT_ID=xxx
```

### Installation Steps
```bash
# 1. Clone repository
git clone <repo-url>
cd Kiu-Admission-Portal

# 2. Install dependencies
pnpm install

# 3. Setup database
python apps/flask-api/init_db.py

# 4. Seed programs
python apps/flask-api/scripts/seed_all_programs.py

# 5. Start development
pnpm dev
```

---

## 📈 Project Statistics

| Metric | Value |
|--------|-------|
| Total Lines of Code | 15,000+ |
| Backend Files | 45+ |
| Frontend Files | 60+ |
| Database Tables | 25+ |
| API Endpoints | 80+ |
| Programs Catalogued | 156 |
| Test Coverage | 75%+ |

---

## 🎯 SDG Alignment

This project aligns with **UN Sustainable Development Goals**:

- **SDG 4:** Quality Education - Streamlined admission process
- **SDG 8:** Decent Work - Career services and job matching
- **SDG 9:** Industry & Innovation - Technology adoption in education

---

## 📚 References

1. National Council for Higher Education (NCHE) Uganda - Entry Requirements Guidelines
2. Kampala International University - Academic Programs Catalog 2024/2025
3. Uganda National Examinations Board (UNEB) - Grading System
4. Flask Documentation - https://flask.palletsprojects.com/
5. React Documentation - https://react.dev/
6. LinkedIn Developer Platform - https://developer.linkedin.com/

---

## 👨‍💻 Author

**Name:** [Student Name]  
**Reg. No:** [Registration Number]  
**Course:** Bachelor of Science in Software Engineering  
**Department:** Faculty of Computing, Information Systems & Mathematics

---

## 🙏 Acknowledgments

- Supervisor: [Supervisor Name] for guidance and support
- Kampala International University for the opportunity
- Family and friends for their encouragement

---

## 📄 License

This project is licensed under the MIT License.

---

**END OF DOCUMENTATION**
