# KIU Admission Portal v2.0

**Kampala International University** - Professional Admission & Career Management System

A modern, industry-standard portal handling Uganda's complete education pathway system (O-Level → PhD) with NCHE compliance.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)

---

## Quick Start

```bash
# One-command setup (Windows/Linux/MacOS)
pnpm setup

# Start development
pnpm dev
```

---

## Repository Structure

| Path | Description | Tech Stack |
|------|-------------|------------|
| [`apps/kiu-portal`](apps/kiu-portal) | React frontend | Vite + React + TypeScript + Tailwind |
| [`apps/flask-api`](apps/flask-api) | REST API | Flask + SQLAlchemy + JWT |
| [`lib/api-client-react`](lib/api-client-react) | Shared API client | React Query + TypeScript |

---

## Features

### Education Pathways Supported (NCHE Compliant)

| Level | Entry Route | Programs Available |
|-------|-------------|-------------------|
| **O-Level (UCE)** | Direct | National Certificates, HEC |
| **A-Level (UACE)** | Direct | Diploma, HEC, Bachelor |
| **HEC** | Progression | Bachelor Degree |
| **National Certificate** | Progression | Diploma, HEC |
| **Diploma** | Progression | Bachelor (with credit transfer) |
| **Bachelor** | Progression | Masters |
| **Masters** | Progression | PhD |

### Key Capabilities

- ✅ **Dual Curriculum Support** - Old (Pre-2024) & New (2024+) UCE grading
- ✅ **Qualification Assessment** - Automated eligibility checking
- ✅ **Program Recommendations** - AI-powered matching
- ✅ **Online Applications** - Complete admission workflow
- ✅ **Document Management** - Secure upload & verification
- ✅ **Payment Integration** - Application fees & tuition
- ✅ **Admin Dashboard** - Application review & management

---

## Tech Stack

### Backend
- **Framework**: Flask with Application Factory pattern
- **Database**: PostgreSQL / MySQL with SQLAlchemy ORM
- **Authentication**: JWT with refresh tokens
- **Validation**: Pydantic schemas
- **Security**: Rate limiting, CORS, bcrypt

### Frontend
- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: React Query + Context API
- **Routing**: Wouter
- **Forms**: React Hook Form + Zod

---

## Documentation

| Document | Purpose |
|----------|---------|
| [`PROFESSIONAL_REORGANIZATION.md`](PROFESSIONAL_REORGANIZATION.md) | Architecture & structure |
| [`KIU_FEE_SOURCES.md`](KIU_FEE_SOURCES.md) | Verified 2025/2026 fee structure |
| [`NCHE_ADMISSION_PATHWAYS.md`](NCHE_ADMISSION_PATHWAYS.md) | Uganda education standards |
| [`APPLICATION_FORMS_DESIGN.md`](APPLICATION_FORMS_DESIGN.md) | Form specifications |
| [`DEPLOYMENT.md`](DEPLOYMENT.md) | Production deployment |

---

## Prerequisites

- **Node.js** 18+ and **pnpm**
- **Python** 3.11+
- **PostgreSQL** 14+ or **MySQL** 8

---

## Installation

### Automated Setup
```bash
pnpm setup
```

### Manual Setup
```bash
# Install Node dependencies
pnpm install

# Install Python dependencies
cd apps/flask-api
pip install -r requirements.txt

# Setup database
flask db upgrade
flask seed
```

---

## Development

```bash
# Start all services
pnpm dev

# Or individually:
pnpm --filter kiu-portal dev      # Frontend only
python apps/flask-api/run.py       # Backend only
```

---

## Configuration

Create `.env` in `apps/flask-api/`:
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/kiu_portal
JWT_SECRET=your-secret-key
FLASK_ENV=development
```

---

## API Endpoints

### Authentication
```
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
GET  /api/v1/auth/me
```

### Admissions
```
GET  /api/v1/programs
POST /api/v1/admissions/apply
GET  /api/v1/admissions/my-applications
```

### Recommendations
```
POST /api/v1/recommendations/assess
GET  /api/v1/recommendations/programs
```

Full API docs: [`docs/API_DOCUMENTATION.md`](docs/API_DOCUMENTATION.md)

---

## KIU Contact Information

| | |
|---|---|
| **Phone** | +256 414 100808 |
| **Email** | admissions@kiu.ac.ug |
| **Website** | www.kiu.ac.ug |
| **Main Campus** | Kansanga, Kampala, Uganda |
| **Western Campus** | Ishaka, Bushenyi District |

---

## License

MIT License - see [LICENSE](LICENSE) for details

---

**Kampala International University** - *The Leading Private University in Uganda*

## Supported Qualification Entry Routes

✅ **NCHE Uganda Approved Admission Pathways:**

| Qualification Level | Description |
|---------------------|-------------|
| **O-Level / UCE** | Direct entry for bridging programmes |
| **A-Level / UACE** | Standard undergraduate entry |
| **Higher Education Certificate (HEC)** | Bridging programme |
| **National Certificate** | Technical & vocational entry |
| **Diploma** | Diploma holders direct entry |
| **Bachelor's Degree** | Postgraduate entry |
| **Master's Degree** | PhD & advanced programmes |


## Prerequisites

- **Node.js** 18+ and **pnpm**
- **Python** 3.11+
- **MySQL** 8 (local or Docker; CI uses MySQL for tests)

## Install

 **ONE COMMAND FULL SETUP (WORKS ON WINDOWS / LINUX / MACOS):**

```bash
pnpm setup
```

This command automatically:
- Installs all Node.js dependencies
- Installs all Python packages
- Automatically installs correct server for your OS (gunicorn/waitress)
- Works identically on all operating systems

## Configuration

- **Database:** set `DATABASE_URL` (MySQL), e.g. `mysql+pymysql://user:pass@127.0.0.1:3306/kiu_admissions`. See [`apps/flask-api/config.py`](apps/flask-api/config.py).
- **Secrets:** set `JWT_SECRET` or `SECRET_KEY` for JWT signing.
- **CORS:** optional `CORS_ORIGINS` for allowed browser origins in production.

Further deployment notes: [`DEPLOYMENT.md`](DEPLOYMENT.md).

## Run locally

 **UNIVERSAL COMMANDS (WORK ON ALL OPERATING SYSTEMS):**

**Terminal 1 - Backend API:**
```bash
pnpm dev:api
```

**Terminal 2 - Frontend:**
```bash
pnpm dev:portal
```

 Application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:5000
- API Documentation: http://localhost:5000/docs

---

Manual run commands (not required):

**1. API** (default port 5000):
```bash
cd apps/flask-api
python run.py
```

**2. Frontend:**
```bash
pnpm --filter @workspace/kiu-portal dev
```

The Vite dev server proxies browser requests to `/api` to the Flask backend. Override the proxy target if needed:

```bash
VITE_API_PROXY_TARGET=http://127.0.0.1:5001 pnpm --filter @workspace/kiu-portal dev
```

See [`apps/kiu-portal/vite.config.ts`](apps/kiu-portal/vite.config.ts).

Authentication uses an **httpOnly** session cookie (`auth_token`); the SPA sends `credentials: 'include'` on API calls.

## Scripts (root)

| Command | Description |
|---------|-------------|
| `pnpm run typecheck` | Typecheck `apps/*` and `lib/*` packages |
| `pnpm run build` | Production build (typecheck + package builds) |
| `pnpm run test:api` | Run Flask pytest suite |

## Frontend tests

```bash
pnpm --filter @workspace/kiu-portal test
pnpm --filter @workspace/kiu-portal test:e2e   # requires dev server; see Playwright config
```

## Backend tests

From the repo root (after installing Python dependencies under `apps/flask-api`):

```bash
pnpm run test:api
```

Or directly:

```bash
cd apps/flask-api && python3 -m pytest tests/ -q
```

## CI

GitHub Actions runs backend tests (MySQL), frontend typecheck/build, and frontend unit tests. See [`.github/workflows/ci.yml`](.github/workflows/ci.yml).
