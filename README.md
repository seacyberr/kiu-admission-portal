# Kampala International University (KIU) Admission Portal

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)

**Official digital admission and career placement platform for Kampala International University (KIU)**  
Comprehensive NCHE-compliant application system with programme guidance, career opportunities, and administrative oversight.  

Built specifically for KIU's admission workflow and student career development needs.  

---
### Prerequisites

| Tool | Version | KIU Requirement |
|------|---------|----------------|
| **Python** | 3.11+ | For KIU API backend |
| **Node.js** | 18+ | For KIU frontend build tools |
| **pnpm** | Latest | Required package manager for KIU project |
| **MySQL** | 8.x+ | Production database for KIU systems |
| **Git** | Latest | Version control for KIU codebase |
| **Docker** | Latest | Optional for KIU containerized deployment |

---

## System Architecture

```mermaid
graph TB
    subgraph "KIU Frontend"
        A[React + TypeScript] --> B[Vite Dev Server]
    end
    
    subgraph "KIU Backend Services"
        C[Python + Flask] --> D[MySQL Database]
        C --> E[Redis Cache]
    end
    
    A --> F[Nginx Reverse Proxy]
    F --> C
    F --> D
```

### Component Overview
| Layer | Technology | KIU Purpose |
|--------|------------|---------|
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS | KIU Student Portal Interface |
| **API** | Python 3.11+, Flask 3, SQLAlchemy | KIU Admission System Backend |
| **Database** | MySQL 8.0 | KIU Student Data & Application Records |
| **Cache** | Redis 7 | KIU Session Management |

---

## Features

### Modern UI/UX
- Dark/light themes, responsive layout, animations, progress indicators, toast and inline validation.

### Authentication & Security
- JWT sessions (cookies + headers), refresh flow, OTP verification, role-based access (applicant / finalist / admin).

### Admin & analytics
- Programme applications dashboards, filtering, status updates, exports/reporting hooks.

### Academic & Career Features
- **NCHE Compliance**: Full alignment with National Council for Higher Education standards
- **Programme Guidance**: Intelligent recommendation system based on KIU's academic programmes
- **Multi-path Applications**: Support for O-Level, A-Level, Diploma, HEC, and Postgraduate pathways
- **Career Integration**: Direct connection to KIU's career services and industry partnerships
- **Finalist Opportunities**: Specialized career placement for KIU graduates

---

## Tech stack

| Layer | Technology | Purpose |
|--------|------------|---------|
| **API** | Python 3.11+, Flask 3, SQLAlchemy, Alembic, Flask-JWT-Extended | KIU Admission System Backend |
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS, Radix UI | KIU Student Portal Interface |
| **Database** | **MySQL 8.0** (production); SQLite for development | KIU Student Data & Application Records |
| **Testing** | pytest (API), Vitest + Playwright (frontend) | Quality Assurance for KIU Systems |
| **Containers** | Docker Compose under `scripts/` | KIU Deployment & Development Environment |

---

## Repository layout

```
kiu-admission-portal/  # KIU Admission Portal Repository
├── apps/
│   ├── flask-api/           # KIU Admission API (Flask)
│   │   ├── requirements.txt  # Python dependencies for KIU systems
│   │   └── run.py           # KIU API server entrypoint
│   └── kiu-portal/          # KIU Student Portal (React SPA)
├── lib/api-client-react/    # KIU API client library
├── scripts/                 # KIU deployment configurations
├── database_schema.sql      # KIU database schema (MySQL)
├── .env.example             # KIU environment template
---

## Quick Start Guide

**Get your KIU Admission Portal running in 5 minutes**

Choose your preferred setup method below:

### Option A — Local Development

**For development environments with Python and Node.js**

```bash
# Clone KIU repository
git clone https://github.com/seacyberr/kiu-admission-portal.git
cd kiu-admission-portal

# Install dependencies
pnpm install

# Setup Python environment
cd apps/flask-api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Start services (two terminals)
pnpm dev:api      # Starts KIU API on port 5001
pnpm dev:portal    # Starts KIU Student Portal on port 5173
```

**Access Points**
- KIU Student Portal: http://localhost:5173
- KIU Admission API: http://localhost:5001
- API Documentation: http://localhost:5001/api/docs/openapi.json OpenAPI specification |

---

### Option B — Docker Setup

**Great for consistent environments, team collaboration, or if you prefer containers**

#### Quick Start
```bash
# Start all KIU services (database, API, frontend)
docker compose -f scripts/docker-compose.dev.yml up --build -d
```

#### Stop Services
```bash
docker compose -f scripts/docker-compose.dev.yml down
```

**Access Points**
- KIU Student Portal: http://localhost:5173
- KIU Admission API: http://localhost:5001
- KIU Database: localhost:3307 (user: `kiu_dev`, password: `kiu_dev_password`)
- Redis Cache: localhost:6379

---

### Option C — Production Deployment

**For production/staging environments with Docker**

#### Production Setup
```bash
# Set KIU production environment variables
cp .env.example .env
# Edit .env with your production KIU secrets

# Deploy KIU services
docker compose -f scripts/docker-compose.yml --env-file .env build
docker compose -f scripts/docker-compose.yml --env-file .env up -d
```

**Production Access Points**
- KIU Portal: http://localhost:80 (Nginx)
- KIU API: http://localhost:5001
- KIU Database: localhost:3306
- Redis: localhost:6379

---

### Option D — Hybrid Development

**KIU database in Docker, API + frontend on host**

```bash
# Start KIU database and Redis
docker compose -f scripts/docker-compose.dev.yml up db redis -d

# Point local .env to KIU Docker services
DATABASE_URL=mysql+pymysql://kiu_dev:kiu_dev_password@127.0.0.1:3307/kiu_portal_dev

# Start services locally (with venv activated)
pnpm dev:api      # KIU API
pnpm dev:portal    # KIU Portal
```

---

### Option E — Testing

**Run KIU test suite with Docker**

```bash
docker compose -f scripts/docker-compose.test.yml up --build
```

---

## Troubleshooting

- **`pip install` fails on Linux:** create and activate **`apps/flask-api/.venv`** first (PEP 668) for KIU development.
- **Docker build cannot find `apps/flask-api`:** ensure **`-f scripts/docker-compose*.yml`** is run from the **KIU repository root**, not from inside `scripts/`.
- **`pnpm install` fails:** use **pnpm**, not npm/yarn (enforced by KIU root `package.json`).
- **API errors after switching SQLite ↔ MySQL:** align **`DATABASE_URL`** with KIU database schema and run appropriate migrations.

---

## Scripts (root package.json)

| Command | Description | KIU Purpose |
|---------|-------------|-------------|
| `pnpm install` | Install JS/TS workspace dependencies | KIU Frontend Setup |
| `pnpm dev:portal` | Start Vite dev server | KIU Student Portal |
| `pnpm dev:api` | Start Flask dev server (`apps/flask-api/run.py`) | KIU Admission API |
| `pnpm setup` | `pnpm install` + `pip install -r apps/flask-api/requirements.txt` | Complete KIU Development Setup |
| `pnpm build` | Typecheck + build apps | KIU Production Build |
| `pnpm typecheck` | TypeScript check | KIU Code Quality |
| `pnpm test:api` | pytest in `apps/flask-api` | KIU API Testing |
| `pnpm --filter @workspace/kiu-portal test` | Frontend unit tests (Vitest) | KIU Frontend Testing |
| `pnpm --filter @workspace/kiu-portal test:e2e` | E2E tests (Playwright; install browsers once via `pnpm exec playwright install`) | KIU End-to-End Testing |

---

## API Tests

**macOS / Linux**

```bash
cd apps/flask-api
source .venv/bin/activate   # if you use a venv
python -m pytest tests/ -v
```

**Windows**

```powershell
cd apps\flask-api
.\.venv\Scripts\Activate.ps1
python -m pytest tests\ -v
```

---

## Contributing

1. Fork the repository  
2. Branch (`git checkout -b feature/your-feature`)  
3. Commit with clear messages  
4. Push and open a Pull Request  

---

## License

MIT — see [LICENSE](LICENSE) if present in the repo.

---

## Support

Open an issue in this repository or contact **KIU ICT Department** for technical support. For admission-related inquiries, please contact the **KIU Admissions Office** directly.
