# KIU Admission Portal API - File Structure

## Overview
This Flask API powers the KIU Admission Portal. It handles:
- User authentication (register, login, OTP)
- Program management (288 programs)
- Application submissions
- Admin dashboard
- Finalist/Career services

## Directory Structure

```
apps/flask-api/
├── app.py                    # Main Flask app factory
├── models.py                 # Database models (User, Program, Application, etc.)
├── seed.py                   # Database seeding script
├── pytest.ini               # Test configuration
│
├── config_modules/            # Configuration
│   ├── __init__.py
│   ├── app_config.py        # App settings
│   ├── database_config.py   # Database config
│   ├── redis_config.py      # Redis config
│   └── email_config.py      # Email config
│
├── data/                     # Seed data
│   └── seed-programs.json   # 288 programs (main seed file)
│
├── routes/                   # API Endpoints
│   ├── __init__.py
│   ├── admission.py         # Program listing, applications
│   ├── admin.py             # Admin dashboard stats
│   ├── auth.py              # Login, register, OTP
│   ├── career.py            # Career paths, jobs
│   ├── docs.py              # API documentation
│   ├── finalist.py          # Finalist portal
│   ├── notifications.py     # Email notifications
│   ├── opportunities.py     # Job opportunities
│   ├── recommendations_v2.py # Program recommendations
│   ├── reports.py           # Admin reports
│   └── users.py             # User management
│
├── services/                # Business logic
│   ├── caching.py           # Redis caching
│   ├── email_service.py     # Email sending
│   ├── otp_service.py       # OTP generation
│   ├── qualification_service.py # UNEB qualification logic
│   └── storage.py           # File uploads
│
├── tests/                   # Test suite
│   ├── test_core_functionality.py   # 11 core tests
│   └── test_comprehensive.py        # 23 comprehensive tests
│
├── utils/                   # Utilities
│   ├── api_response.py      # API response helpers
│   ├── decorators.py        # Route decorators
│   └── error_handling.py    # Error handlers
│
└── archive_2024_04_14/      # Backed up old files
    ├── recommendation_engine.py
    ├── kiu_programs_database.py
    ├── conftest.py
    └── (other old files)
```

## Key Files

### Database Models (models.py)
- **User**: Applicants, admins, finalists
- **Program**: 288 academic programs (no codes, no fees)
- **AdmissionApplication**: Student applications
- **FinalistProfile**: Graduating students
- **CareerPath**: Career guidance
- **Opportunity**: Job/internship postings

### Main Routes
- `GET /api/health` - Health check
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/admission/programs` - List programs
- `POST /api/admission/applications` - Submit application
- `GET /api/admin/dashboard` - Admin stats

## Removed Features
The following were removed per requirements:
- ❌ Program codes (all programs identified by name)
- ❌ Tuition/fees fields
- ❌ Payment system
- ❌ LinkedIn integration

## Running Tests

```bash
# Run all tests
cd apps/flask-api
source venv/bin/activate
pytest tests/ -v

# Run specific test file
pytest tests/test_core_functionality.py -v
pytest tests/test_comprehensive.py -v
```

## API Health Check
```bash
curl http://localhost:5001/api/health
```
