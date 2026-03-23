# KIU Admission & Career Portal

## Overview

Kampala International University (KIU) two-part web portal:
1. **Admission Portal** — for A-Level/O-Level graduates to apply, track admission status
2. **Career Portal** — for enrolled final-year finalists to explore careers and apply for jobs/internships

## Stack

- **Frontend**: React + Vite + TypeScript (artifacts/kiu-portal)
- **Backend**: Python Flask + SQLAlchemy (artifacts/flask-api)
- **Database**: PostgreSQL (via DATABASE_URL)
- **Routing**: Wouter (client-side), reverse proxy (path-based)
- **API**: REST, all routes under `/api`
- **Auth**: JWT (Bearer tokens stored in localStorage as `kiu_token`)
- **ORM**: SQLAlchemy (Flask-SQLAlchemy)
- **Monorepo**: pnpm workspaces

## Architecture

```
artifacts/
├── flask-api/            # Python Flask backend (/api routes)
│   ├── app.py            # Main Flask app + seeding
│   ├── models.py         # SQLAlchemy models
│   └── routes/
│       ├── auth.py       # /api/auth/* (register, login, logout, me)
│       ├── admission.py  # /api/admission/* (programs, applications)
│       ├── career.py     # /api/career/* (paths, finalist profile)
│       ├── opportunities.py # /api/opportunities/* (jobs/internships + applications)
│       └── users.py      # /api/users/* (admin user list)
├── kiu-portal/           # React + Vite frontend (/)
│   └── src/
│       ├── pages/
│       │   ├── auth/     # Login, Register
│       │   ├── applicant/  # Dashboard, Apply form
│       │   ├── finalist/   # Career dashboard, Career Paths, Opportunities
│       │   └── admin/    # Admin dashboard
│       ├── components/   # Layout, shared UI
│       └── lib/          # fetch-patch (auto-inject Bearer token)
└── api-server/           # Artifact config for Flask (runs flask-api/app.py)
```

## User Roles

| Role | Access |
|------|--------|
| `applicant` | Register, submit admission application, track progress |
| `finalist` | Career paths, job/internship opportunities, apply for opportunities |
| `admin` | All above + manage all applications, post opportunities |

## UNEB Grading System

- **O-Level (UCE)**: D1 (best, 1 pt) → D9 (worst, 9 pts). Pass: D1-D6
- **A-Level (UACE)**: A (6 pts), B (5), C (4), D (3), E (2), O (1), F (fail, 0 pts)

## Seed Data

On first startup, the app seeds:
- 15 KIU programs (degree + diploma across all faculties)
- 10 career paths (Technology, Healthcare, Law, Finance, Engineering, Education, Business)
- 9 job/internship opportunities from real Ugandan employers
- 1 admin account: `admin@kiu.ac.ug` / `admin123`

## Running

- Flask backend: `python artifacts/flask-api/app.py` (PORT 8080)
- Frontend: `pnpm --filter @workspace/kiu-portal run dev` (PORT 26243)
- Both are wired to the reverse proxy: Flask at `/api`, Frontend at `/`

## Key Routes

### API
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `GET /api/admission/programs`
- `POST /api/admission/applications`
- `GET /api/admission/applications/my`
- `GET/PUT /api/career/my-profile`
- `GET /api/career/paths`
- `GET /api/opportunities`
- `POST /api/opportunities/:id/apply`
- `GET /api/opportunities/applications/my`

### Frontend Pages
- `/` — Landing/Home
- `/login`, `/register` — Auth
- `/dashboard` — Applicant dashboard + application tracking
- `/apply` — Multi-step admission application form
- `/career` — Finalist dashboard
- `/career/paths` — Career path recommendations
- `/career/opportunities` — Job/internship board + applications
- `/admin` — Admin dashboard
