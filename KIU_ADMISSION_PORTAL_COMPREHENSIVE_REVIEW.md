# KIU Admission Portal - Comprehensive System Review

**Generated**: April 14, 2025  
**Version**: 6.0 (Authoritative Program Structure)  
**Total Programs**: 270+ (Main & Western Campus)

---

## TABLE OF CONTENTS

1. [System Architecture](#1-system-architecture)
2. [User Roles & Workflows](#2-user-roles--workflows)
3. [Program Structure](#3-program-structure)
4. [Recommendation Engine](#4-recommendation-engine)
5. [Application Workflows](#5-application-workflows)
6. [Database Models](#6-database-models)
7. [API Structure](#7-api-structure)
8. [Integration Points](#8-integration-points)
9. [Areas for Improvement](#9-areas-for-improvement)

---

## 1. SYSTEM ARCHITECTURE

### 1.1 Technology Stack

**Frontend (apps/kiu-portal)**
- React + TypeScript
- Vite build system
- Wouter for routing
- TanStack Query for data fetching
- TailwindCSS + shadcn/ui components
- Custom UI components library (`@workspace/ui`)
- API client library (`@workspace/api-client-react`)

**Backend (apps/flask-api)**
- Python Flask
- SQLAlchemy ORM
- JWT authentication
- Custom error handling framework
- Program data module with unified source

**Shared**
- TypeScript types library (`@workspace/types`)
- PNPM workspace monorepo structure
- Docker containerization
- PostgreSQL database

### 1.2 Directory Structure

```
Kiu-Admission-Portal/
├── apps/
│   ├── flask-api/          # Python backend API
│   │   ├── routes/         # API endpoints
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   ├── data/           # Program data (seed-programs.json)
│   │   └── tests/          # Unit tests
│   └── kiu-portal/         # React frontend
│       ├── src/
│       │   ├── pages/      # Route components
│       │   ├── components/ # Shared components
│       │   └── services/   # API services
│       └── public/         # Static assets
├── lib/                    # Shared libraries
│   ├── api-client-react/   # API client hooks
│   ├── types/              # TypeScript definitions
│   └── ui/                 # UI component library
└── docs/                   # Documentation
```

### 1.3 Data Flow

```
User → React Frontend → API Client → Flask API → Database
         ↓                      ↓
    TanStack Query         SQLAlchemy
         ↓                      ↓
    UI State Management    Business Logic
```

---

## 2. USER ROLES & WORKFLOWS

### 2.1 User Roles

| Role | Description | Primary Actions |
|------|-------------|-----------------|
| **Applicant** | Prospective student applying for admission | View recommendations, submit application, track status |
| **Finalist** | Current KIU student (for career portal) | View career paths, opportunities, manage profile |
| **Admin** | Admissions staff | Review applications, update status, manage programs |
| **Examiner** | (Role defined but workflow unclear in current codebase) | Not actively implemented in current version |

### 2.2 Applicant Workflow

```
1. LANDING & AUTHENTICATION
   ├── Home page (/)
   ├── Login (/login)
   ├── Register (/register)
   └── OTP Verification (/verify-otp)

2. PROGRAM DISCOVERY (NCHE-Based)
   ├── Get Recommendations (/recommend)
   │   ├── Select qualification type:
   │   │   • UACE (A-Level)
   │   │   • UCE (O-Level)
   │   │   • HEC (Higher Education Certificate)
   │   │   • National Certificate
   │   │   • Diploma
   │   │   • Bachelor's
   │   └── Enter subject grades
   │   └── View recommended programs with match scores
   └── Alternative recommendation tools:
       • /recommend-simple
       • /realistic-recommend

3. APPLICATION SUBMISSION
   ├── Start Application (/apply)
   │   └── Select program(s)
   ├── Personal Information
   │   ├── Name, DOB, gender, nationality
   │   ├── Contact details
   │   ├── Next of kin information
   │   └── District of origin
   ├── Academic Qualifications
   │   ├── Exam level (O-Level/A-Level/HEC/etc)
   │   ├── Index number
   │   ├── Year of completion
   │   ├── Subject grades (dynamic form)
   │   └── Curriculum type (old/new)
   ├── Document Upload
   │   ├── Academic certificates
   │   ├── ID documents
   │   └── Passport photos
   └── Review & Submit

4. APPLICATION TRACKING
   ├── Dashboard (/dashboard)
   │   ├── View application status
   │   ├── Timeline visualization
   │   ├── Admin notes (if any)
   │   └── Program details
   └── Status updates via email/portal

5. DECISION OUTCOMES
   ├── Pending → Under Review → Accepted/Rejected/Waitlisted
   └── If Accepted: Enrollment instructions
```

### 2.3 Admin Workflow

```
1. ADMIN DASHBOARD (/admin)
   ├── View statistics
   │   ├── Total applications
   │   ├── Pending, Under Review, Accepted, Rejected
   │   ├── By qualification type
   │   └── Recent applications

2. APPLICATIONS MANAGEMENT (/admin/admissions)
   ├── View all applications (paginated table)
   ├── Filter by:
   │   ├── Status (pending, under_review, accepted, rejected, waitlisted)
   │   ├── Qualification type (uace, uce, hec, etc.)
   │   ├── Search (name, email, application number)
   │   └── Date range
   ├── Export to CSV
   ├── View application details (modal)
   │   ├── Personal information
   │   ├── Program details
   │   ├── Academic qualifications
   │   ├── Uploaded documents
   │   └── Admin notes
   └── Update status
       ├── Mark as Under Review
       ├── Accept (with admin notes)
       └── Reject (with admin notes)

3. PROGRAMS MANAGEMENT (/admin/programs)
   ├── View program list
   ├── Edit program details
   └── Update admission requirements

4. USERS MANAGEMENT (/admin/users)
   └── View/manage user accounts
```

### 2.4 Finalist Workflow (Career Portal)

```
1. FINALIST DASHBOARD (/career)
   ├── Career overview
   ├── Skill gap analysis
   └── Recommended opportunities

2. CAREER PATHS (/career/paths)
   ├── View career progression options
   ├── Skill requirements
   └── Industry outlook

3. OPPORTUNITIES (/career/opportunities)
   ├── Job listings
   ├── Internship opportunities
   └── Application tracking

4. PROFILE MANAGEMENT (/career/profile)
   ├── Update personal information
   ├── Add skills and certifications
   └── Upload CV/resume
```

---

## 3. PROGRAM STRUCTURE

### 3.1 Faculty-Campus Organization

**Kampala International University - Official Structure**

#### 1. FACULTY OF HEALTH SCIENCES (Western Campus)
- **Bachelor Programs (8)**
  - Bachelor of Medicine and Bachelor of Surgery (MBBS, 5 years)
  - Bachelor of Nursing Science (BNS, 4 years)
  - Bachelor of Midwifery (BMID, 4 years)
  - Bachelor of Pharmacy (BPHARM, 4 years)
  - Bachelor of Dental Surgery (BDS, 4 years)
  - Bachelor of Medical Laboratory Science (BMLS, 4 years)
  - Bachelor of Public Health (BPH, 3 years)
  - Bachelor of Biotechnology (BBT, 3 years)

- **Diploma Programs (6)**
  - Diploma in Nursing, Midwifery, Clinical Medicine, Pharmacy, Medical Laboratory Science, Radiography

- **Certificate Programs (2)**
  - Certificate in Nursing, Certificate in Midwifery

- **Master's Programs (10)**
  - Master of Medicine specializations (Internal Medicine, Surgery, Paediatrics, Obstetrics & Gynaecology, Psychiatry)
  - Master of Public Health, Nursing Science, Midwifery, Medical Laboratory Science, Dental Surgery

- **Biomedical Sciences (9)**
  - MSc in Anatomy, Physiology, Biochemistry, Microbiology
  - PhD in Anatomy, Physiology, Biochemistry, Microbiology, Biomedical Sciences

#### 2. FACULTY OF BUSINESS & MANAGEMENT (Both Campuses)
- **Bachelor Programs (6)**
  - BBA, BCOM, Accounting & Finance, Human Resource Management, Procurement & SCM, Economics

- **Diploma Programs (7)**
  - Business Administration, Accounting & Finance, HRM, Procurement & SCM, Public Administration, Banking & Finance, Insurance & Risk Management

- **Certificate (1)**
  - Certificate in Business Administration

- **Master's (8)**
  - MBA, MSc in Accounting & Finance, Marketing, HRM, Procurement & SCM, Economics, Public Administration, Development Studies

- **PhD (1)**
  - PhD in Business Administration

#### 3. FACULTY OF COMPUTING & IT (Main Campus)
- **Bachelor (4)**
  - Information Technology, Computer Science, Software Engineering, Data Communication & Networking

- **Master's (2)**
  - MSc in Information Technology, Computer Science

- **PhD (1)**
  - PhD in Computer Science

#### 4. FACULTY OF LAW (Both Campuses)
- **Bachelor (1)**
  - Bachelor of Laws (LLB, 4 years)

- **Diploma (1)**
  - Diploma in Law

- **Master's (1)**
  - Master of Laws

- **PhD (1)**
  - PhD in Law

#### 5. FACULTY OF EDUCATION (Both Campuses)
- **Bachelor (4)**
  - Education in Arts, Education in Science, Early Childhood Education, Primary Education

- **Postgraduate Diploma (1)**
  - Postgraduate Diploma in Education

- **Master's (4)**
  - Educational Administration & Management, Curriculum & Instruction, Guidance & Counselling, Early Childhood Education

- **PhD (4)**
  - Education, Educational Administration, Curriculum Studies, Educational Psychology

#### 6. FACULTY OF SOCIAL SCIENCES (Main Campus)
- **Bachelor (4)**
  - Mass Communication, International Relations, Social Work & Social Administration, Economics & Statistics

- **Master's (2)**
  - MA in International Relations, MA in Mass Communication

#### 7. FACULTY OF ENVIRONMENTAL SCIENCE (Main Campus)
- **Bachelor (1)**
  - Bachelor of Environmental Science

- **Master's (1)**
  - MSc in Environmental Science

- **PhD (1)**
  - PhD in Environmental Science

### 3.2 Program Codes

All programs now have standardized KIU codes:
- **Bachelor**: B{abbreviation} (e.g., BBA, BCS, BPHARM)
- **Diploma**: D{abbreviation} (e.g., DBA, DIT, DN)
- **Master**: MS{abbreviation} or MBA (e.g., MSIT, MBA, MPH)
- **PhD**: PhD-{abbreviation} (e.g., PhD-CS, PhD-BA, PhD-LAW)
- **Certificate**: CERT-{abbreviation}
- **National Certificate**: NC{abbreviation}
- **HEC**: HEC-{track} (HEC-HUM, HEC-PHY, HEC-BIO)

---

## 4. RECOMMENDATION ENGINE

### 4.1 Overview

The recommendation engine is NCHE-compliant and matches applicants to programs based on their academic qualifications.

**Location**: `apps/flask-api/services/recommendation_engine.py`

### 4.2 Algorithm Logic

```
INPUT: Applicant Qualifications
├── UACE (A-Level) - 2 Principal passes minimum
├── UCE (O-Level) - For HEC/Diploma entry
├── HEC Completion - For degree programs
├── National Certificate - For diploma/degree
├── Diploma - For degree programs
└── Bachelor's - For postgraduate

PROCESSING:
1. QUALIFICATION ASSESSMENT
   ├── Validate minimum requirements
   ├── Calculate points (A=6, B=5, C=4, D=3, E=2, O=1)
   ├── Check subject combinations
   └── Determine eligible entry pathways

2. PROGRAM MATCHING
   ├── Filter by campus preference
   ├── Filter by available entry pathways
   ├── Score each program match (0-100):
   │   ├── Essential subjects met (+25 each)
   │   ├── Relevant subjects (+10 each)
   │   ├── Points requirement met (+20)
   │   ├── Above cutoff (+15)
   │   ├── Special requirements (Law needs General Paper)
   │   └── Penalties for missing requirements
   └── Rank by match score

3. OUTPUT: Ranked Recommendations
   ├── Match score (0-100)
   ├── Eligibility status
   ├── Strong candidate flag (score >= 80)
   ├── Match reasons
   ├── Warnings (if any)
   ├── Required subjects met/missing
   └── Direct apply URL
```

### 4.3 Scoring System

| Factor | Points | Description |
|--------|--------|-------------|
| Essential subjects | +25 each | Required subjects for the program |
| Relevant subjects | +10 each | Related subjects that strengthen application |
| Points requirement | +20 | Minimum points threshold met |
| Above cutoff | +15 | Historical cutoff exceeded |
| General Paper (Law) | +10 | Special requirement for Law |
| Missing essential | -25 | Critical requirement not met |
| Below cutoff | -10 | Below historical performance |

### 4.4 Entry Pathways

| Qualification | Can Apply For | Notes |
|---------------|---------------|-------|
| O-Level Only | Certificate, HEC | Minimum passes required |
| A-Level (2 principals) | HEC, Diploma, Bachelor | With 2+ principal passes |
| HEC Graduate | Bachelor | In related field |
| National Certificate | Diploma, Bachelor | Relevant field |
| Diploma Holder | Bachelor | May get credit transfer |
| Bachelor's Degree | Postgraduate Diploma, Master's | Minimum class/GPA |
| Master's Degree | PhD | With research proposal |

### 4.5 Frontend Integration

```typescript
// API Call
POST /api/recommendations/assess
{
  qualification_type: "uace" | "uce" | "hec" | "national_certificate" | "diploma" | "bachelors",
  uace_subjects: ["Mathematics", "Physics", "Chemistry"],
  uace_grades: { "Mathematics": "A", "Physics": "B", "Chemistry": "B" },
  principal_passes: 3,
  uce_division: 1,
  uce_credits: 6,
  // ... other qualification data
}

// Response
{
  recommendations: [
    {
      programId: "bit",
      programCode: "BIT",
      programName: "Bachelor of Information Technology",
      faculty: "Faculty of Computing and IT",
      campus: "Main",
      matchScore: 85,
      isEligible: true,
      isStrongCandidate: true,
      matchReasons: ["Essential subjects met", "Points requirement met"],
      warnings: [],
      applyUrl: "/apply/bachelors?program=bit"
    }
  ]
}
```

---

## 5. APPLICATION WORKFLOWS

### 5.1 New Application Flow

```
START
  ↓
[Step 1: Program Selection]
  ├── Select 1-3 program choices
  ├── Preferred campus
  └── Entry level (based on qualification)
  ↓
[Step 2: Personal Information]
  ├── Full name (as on academic docs)
  ├── Date of birth
  ├── Gender
  ├── Nationality
  ├── Contact details (phone, email)
  ├── Next of kin information
  └── District of origin
  ↓
[Step 3: Academic Qualifications]
  ├── Select qualification type
  ├── Enter exam details:
  │   ├── Index number
  │   ├── Year of completion
  │   └── Curriculum type (old/new)
  ├── Subject grades entry (dynamic rows)
  │   ├── O-Level (8+ subjects)
  │   └── A-Level (3+ principals)
  └── Upload result slip
  ↓
[Step 4: Document Upload]
  ├── Academic certificates (PDF/JPG)
  ├── ID/Passport
  ├── Passport photo
  ├── Birth certificate
  └── Any other supporting docs
  ↓
[Step 5: Review & Submit]
  ├── Preview all information
  ├── Edit if needed
  ├── Confirm accuracy
  └── Submit application
  ↓
[Post-Submission]
  ├── Generate application number
  ├── Send confirmation email
  ├── Status: "Pending"
  └── Redirect to dashboard
```

### 5.2 Application Status Workflow

```
PENDING
  ↓ (Admin reviews)
UNDER_REVIEW
  ↓ (Decision made)
┌─────────┬──────────┬──────────┐
↓         ↓          ↓          ↓
ACCEPTED REJECTED WAITLISTED  (Back to pending for more info)
  ↓
Enrollment instructions sent
```

### 5.3 Manual Application Entry (Admin)

```
[Admin Creates Application]
  ↓
[Enter Applicant Details]
  ├── Manual data entry
  └── Upload documents on behalf
  ↓
[Submit]
  └── Same workflow as applicant-submitted
```

---

## 6. DATABASE MODELS

### 6.1 Core Entities

```python
# User Model
class User:
    id: int
    email: str (unique)
    password_hash: str
    first_name: str
    last_name: str
    role: enum (admin, applicant, finalist)
    is_active: bool
    created_at: datetime
    last_login: datetime

# AdmissionApplication Model
class AdmissionApplication:
    id: int
    user_id: int (FK to User)
    application_number: str (unique, auto-generated)
    program_id: int (FK to Program)
    program_choices: list[int] (JSON)
    status: enum (pending, under_review, accepted, rejected, waitlisted)
    
    # Personal Info
    date_of_birth: date
    gender: enum
    nationality: str
    phone: str
    district: str
    next_of_kin_name: str
    next_of_kin_phone: str
    next_of_kin_relationship: str
    
    # Academic Info
    exam_level: enum (o_level, a_level, hec, diploma, etc.)
    exam_year: int
    index_number: str
    uneb_grades: JSON (O-Level & A-Level subjects with grades)
    
    # Admin Fields
    admin_notes: text
    admin_id: int (FK to User)
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    submitted_at: datetime

# Program Model
class Program:
    id: int
    code: str (unique, KIU format)
    name: str
    level: enum (hec, certificate, diploma, bachelors, masters, phd)
    faculty: str
    campus: enum (Main, Western, Both)
    duration: int (years)
    tuition_ugx: int
    tuition_usd: int
    requirements: JSON
    nche_accredited: bool
    nche_status: str
    description: text

# Document Model
class ApplicationDocument:
    id: int
    application_id: int (FK)
    document_type: enum (result_slip, certificate, id, photo, etc.)
    file_url: str
    uploaded_at: datetime
```

### 6.2 Relationships

```
User 1:N AdmissionApplication
User 1:N ApplicationLog (audit trail)
AdmissionApplication N:1 Program
AdmissionApplication 1:N ApplicationDocument
Program N:N EntryRequirement (through JSON)
```

---

## 7. API STRUCTURE

### 7.1 Authentication Endpoints

```
POST /api/auth/login
POST /api/auth/register
POST /api/auth/verify-otp
POST /api/auth/forgot-password
POST /api/auth/reset-password
POST /api/auth/logout
GET  /api/auth/me
```

### 7.2 Admission Endpoints

```
# Applications
GET    /api/admission/applications          # List all (admin)
GET    /api/admission/applications/mine       # Get my application (applicant)
POST   /api/admission/applications            # Create new
PATCH  /api/admission/applications/{id}       # Update
PATCH  /api/admission/applications/{id}/status # Update status (admin)

# Documents
POST   /api/admission/applications/{id}/documents
GET    /api/admission/applications/{id}/documents

# Statistics
GET    /api/admission/stats

# Recommendations
POST   /api/recommendations/assess            # NCHE-based assessment
POST   /api/admission/recommend               # Legacy (deprecated)
```

### 7.3 Program Endpoints

```
GET /api/programs                    # List all programs
GET /api/programs/{code}             # Get program details
GET /api/programs/by-level/{level} # Filter by level
GET /api/programs/by-faculty/{fac} # Filter by faculty
GET /api/programs/by-campus/{camp} # Filter by campus
```

### 7.4 Admin Endpoints

```
GET  /api/admin/dashboard           # Dashboard stats
GET  /api/admin/users               # List users
GET  /api/admin/admissions          # All applications
POST /api/admin/admissions/{id}/status  # Update status
```

---

## 8. INTEGRATION POINTS

### 8.1 Data Sources

**seed-programs.json** (Authoritative Source)
- 270+ programs from KIU official document
- Faculty-campus organization
- NCHE accreditation status
- Entry requirements

**Program Data Loading**:
```python
# data/all_programs.py loads from seed-programs.json
# Provides unified interface for all program queries

from data import (
    ALL_PROGRAMS,
    get_programs_by_level,
    get_programs_by_campus,
    get_program_by_code,
    search_programs,
    to_nche_format  # Convert to NCHE format
)
```

### 8.2 External Integrations

| Service | Integration | Status |
|---------|-------------|--------|
| Email (SMTP) | Transactional emails | Configured |
| File Storage | Local/AWS S3 | Local storage |
| Payment Gateway | Not integrated | Future |
| UNEB Verification | Not integrated | Manual verification |

### 8.3 Frontend-Backend Communication

```
React Component
    ↓
TanStack Query Hook
    ↓
API Client (@workspace/api-client-react)
    ↓
Fetch Request → Flask API
    ↓
SQLAlchemy → PostgreSQL
```

---

## 9. AREAS FOR IMPROVEMENT

### 9.1 Critical Issues

1. **PDF Proposal Document Missing**
   - Cannot locate the proposal PDF file
   - Need to restore from backup or recreate

2. **Examiner Role Not Implemented**
   - Role defined in system but no workflow
   - No examiner-specific UI or API endpoints
   - Potential for academic review workflow

3. **Program Data Duplication Risk**
   - Multiple old program files still exist
   - Need to archive/delete legacy files:
     - `bachelors_programs.py`
     - `certificate_programs.py`
     - `diploma_programs.py`
     - `hec_programs.py`
     - `kiu_programs.py`

### 9.2 User Experience Improvements

1. **Application Process**
   - Add auto-save for multi-step forms
   - Progress indicator with % completion
   - Mobile-responsive document upload
   - Offline mode for form completion

2. **Recommendation Engine**
   - Add program comparison feature
   - Show career path visualizations
   - Include scholarship eligibility check
   - Add virtual campus tours

3. **Communication**
   - SMS notifications (currently email only)
   - In-app messaging between applicant and admin
   - WhatsApp integration for status updates
   - Automated interview scheduling

### 9.3 Technical Improvements

1. **Performance**
   - Cache program data in Redis
   - Optimize image/document uploads
   - Add database indexing for queries
   - Implement CDN for static assets

2. **Security**
   - Add rate limiting to API
   - Implement document virus scanning
   - Enhanced audit logging
   - GDPR compliance for data retention

3. **Scalability**
   - Microservices architecture for high load
   - Database read replicas
   - Load balancing
   - Auto-scaling for peak periods

### 9.4 Feature Enhancements

1. **Applicant Features**
   - Application fee payment integration
   - Document OCR for auto-fill
   - Multi-language support (Swahili)
   - Application status mobile app

2. **Admin Features**
   - Bulk application processing
   - Advanced analytics dashboard
   - Automated eligibility pre-checking
   - Integration with student information system (SIS)

3. **Reporting**
   - Enrollment forecasting
   - Program popularity analytics
   - Regional applicant distribution
   - Conversion rate tracking

### 9.5 Integration Opportunities

1. **UNEB Integration**
   - Automatic result verification
   - Real-time grade checking
   - Fraud prevention

2. **Government Systems**
   - National ID verification (NIRA)
   - Student loan application link
   - Scholarship portal integration

3. **Payment Systems**
   - Mobile Money (MTN, Airtel)
   - Bank transfers
   - Card payments
   - Installment plans

---

## APPENDICES

### A. Program Count Summary

| Level | Count |
|-------|-------|
| HEC | 3 |
| National Certificate | 9 |
| Certificate | 11 |
| Diploma | 45 |
| Bachelors | 56 |
| PGD | 14 |
| Masters | 104 |
| PhD | 35 |
| **Total** | **270+** |

### B. Campus Distribution

| Campus | Programs |
|--------|----------|
| Main Campus | ~140 |
| Western Campus | ~90 |
| Both Campuses | ~40 |

### C. Key Configuration Files

- `seed-programs.json` - Master program data
- `all_programs.py` - Program data interface
- `__init__.py` - Backward compatibility exports
- `recommendation_engine.py` - Recommendation logic
- `admission.py` (routes) - Application API

---

**Document Version**: 1.0  
**Last Updated**: April 14, 2025  
**Author**: System Analysis  
**Status**: Complete for v6.0
