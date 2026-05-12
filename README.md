# KIU Admission Portal

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)

**Admission and career-placement platform for Kampala International University**  
NCHE-oriented programme guidance, applications, finalist career features, and admin reporting.  

---

## Features

### Modern UI/UX
- Dark/light themes, responsive layout, animations, progress indicators, toast and inline validation.

### Authentication & Security
- JWT sessions (cookies + headers), refresh flow, OTP verification, role-based access (applicant / finalist / admin).

### Admin & analytics
- Programme applications dashboards, filtering, status updates, exports/reporting hooks.

### Academic & career
- NCHE-weighted recommendations, qualification checks, multi-path applications (O-Level, A-Level, diploma, HEC, postgraduate where configured), career opportunities for finalists.

---

## Tech stack

| Layer | Technology |
|--------|------------|
| **API** | Python 3.11+, Flask 3, SQLAlchemy, Alembic, Flask-JWT-Extended |
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS, Radix UI |
| **Database** | **MySQL** (production target); **SQLite** optional for local-only API smoke tests (`DATABASE_URL=sqlite:///...`). PostgreSQL is **not** supported by the API config. |
| **Testing** | pytest (API), Vitest + Playwright (frontend) |
| **Containers** | Docker Compose under `scripts/` |

---

## Repository layout

```
kiu-admission-portal/
├── apps/
│   ├── flask-api/           # REST API (Flask)
│   │   ├── requirements.txt  # Python deps (Windows + Unix markers)
│   │   └── run.py           # Cross-platform dev server entrypoint
│   └── kiu-portal/          # React SPA (Vite)
├── lib/api-client-react/    # Shared API client (workspace package)
├── scripts/                 # docker-compose*.yml
├── database_schema.sql      # MySQL-oriented reference schema
├── .env.example             # Root env template
├── package.json             # pnpm workspace scripts
└── README.md
```

---

## Installation and setup

All commands below assume you are in the **repository root** (`kiu-admission-portal/`) unless noted. Compose paths use **`-f scripts/...`**: this is intentional so build contexts resolve to `apps/` and `database_schema.sql` at the repo root.

### Recommendation (read this first)

| If you… | Use |
|--------|-----|
| Want the **smoothest everyday development** (IDE debugging, fast Vite reload) on **Windows, macOS, or Linux** | **Option A — Manual installation** (**recommended**) |
| Prefer **not** to install MySQL (and optionally Python/Node) on the host | **Option B — Docker Compose (development)** (**recommended alternative**) |
| Need a **demo or staging-like** full stack with reverse proxy | **Option C — Docker Compose (production-like)** |
| Want **MySQL/Redis in Docker** but API + SPA **on the host** | **Option D — Hybrid** |

---

### Quick comparison

| Option | What runs on the host | Typical use |
|--------|----------------------|-------------|
| **A. Manual** | Python (venv), Node/pnpm, MySQL | Primary development |
| **B. Docker dev** | Docker only | Shared/reproducible dev environment |
| **C. Docker prod-like** | Docker + `.env` secrets | Demos / integration testing |
| **D. Hybrid** | Docker + Python + Node/pnpm | Debug API/UI locally against container DB |
| **E. Docker test** | Docker | Automated test compose (`docker-compose.test.yml`) |

---

### Option A — Manual installation (**recommended**)

**Prerequisites**

| Tool | Notes |
|------|--------|
| **Python 3.11+** | [python.org](https://www.python.org/downloads/) — Windows: enable “Add python to PATH”. |
| **Node.js 18+** | [nodejs.org](https://nodejs.org/) |
| **pnpm** | `npm install -g pnpm` — **pnpm is required** (npm/yarn blocked by `preinstall`). |
| **MySQL 8.x** | Recommended for parity with production. |
| **Git** | |

#A.1 Clone (all OS)

```bash
git clone <repository-url>
cd kiu-admission-portal
```

# A.2 JavaScript dependencies

```bash
pnpm install
```

# A.3 Python virtual environment (all OS — **required** on many Linux distros)

On **macOS / Linux**:

```bash
cd apps/flask-api
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -r requirements.txt
cd ../..
```

On **Windows (PowerShell)**:

```powershell
cd apps\flask-api
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -r requirements.txt
cd ..\..
```

If PowerShell blocks scripts:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

On **Windows (cmd.exe)**:

```cmd
cd apps\flask-api
py -3.11 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -U pip
pip install -r requirements.txt
cd ..\..
```

> **Linux note (PEP 668):** system `pip install` is often blocked. Always use an **activated `.venv`** before installing Python packages.

> **Production-style serving:** Linux/macOS images install **Gunicorn**; Windows installs **Waitress** via environment markers in `requirements.txt`. For local dev, `pnpm dev:api` / `python run.py` is enough.

#### A.4 Environment files

```bash
cp .env.example .env
```

Set **`JWT_SECRET`**, **`DATABASE_URL`** (MySQL), and optionally entries from `apps/flask-api/.env.example`.

#### A.5 Database

**MySQL**

```bash
mysql -u root -p < database_schema.sql
```

Align credentials with `DATABASE_URL` (format `mysql+pymysql://user:pass@host:3306/dbname`).

**SQLite (limited / smoke tests only)**

```env
DATABASE_URL=sqlite:///./kiu_local.db
```

#### A.6 Run (two terminals, repo root)

With **`apps/flask-api/.venv` activated** for terminal 1:

```bash
pnpm dev:api
```

```bash
pnpm dev:portal
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| API | http://localhost:5001 (override with `PORT`) |
| OpenAPI JSON | http://localhost:5001/api/docs/openapi.json |

---

### Option B — Docker Compose development (**recommended alternative**)

**Host prerequisite:** [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/macOS) or **Docker Engine + Compose** (Linux).

Brings up **MySQL (port 3307)**, **Redis**, **Flask API (5001)**, and **Vite (5173)** with bind mounts for live code (`scripts/docker-compose.dev.yml`).

**All OS — from repo root:**

```bash
docker compose -f scripts/docker-compose.dev.yml up --build -d
```

**Helpers**

- **macOS / Linux:** `./scripts/dev-start.sh`
- **Windows:** `scripts\dev-start.bat`

**Stop**

```bash
docker compose -f scripts/docker-compose.dev.yml down
```

(or `scripts/dev-stop.sh` / `scripts/dev-stop.bat`)

**Default dev DB credentials** (compose file only — not for production):

| | |
|--|--|
| MySQL host (from host machine) | `127.0.0.1` **:** `3307` |
| Database | `kiu_portal_dev` |
| User / password | `kiu_dev` / `kiu_dev_password` |

**URLs:** same as manual mode — http://localhost:5173 and http://localhost:5001

---

### Option C — Docker Compose production-like stack

**Host prerequisite:** Docker. **Requires** `.env` at repo root with at least **`DB_PASSWORD`**, **`DB_ROOT_PASSWORD`**, **`JWT_SECRET`**, **`SECRET_KEY`** (see `.env.example`).

From repo root:

```bash
docker compose -f scripts/docker-compose.yml --env-file .env build
docker compose -f scripts/docker-compose.yml --env-file .env up -d
```

**Typical published ports**

| Service | Port |
|---------|------|
| Nginx (gateway) | **8080** |
| Frontend container (standalone) | **80** |
| API | **5001** |
| MySQL | **3306** |
| Redis | **6379** |

Tune **`CORS_ORIGINS`** in `.env` for your hostname.

---

### Option D — Hybrid (database in Docker, API + SPA on host)

1. Start only infra:

```bash
docker compose -f scripts/docker-compose.dev.yml up db redis -d
```

2. Point local `.env` at the forwarded MySQL port (**3307**) and dev credentials from `docker-compose.dev.yml`, for example:

```env
DATABASE_URL=mysql+pymysql://kiu_dev:kiu_dev_password@127.0.0.1:3307/kiu_portal_dev
```

3. Activate your **venv**, then from repo root run **`pnpm dev:api`** and **`pnpm dev:portal`** as in Option A.

---

### Option E — Test / CI-style stack

```bash
docker compose -f scripts/docker-compose.test.yml up --build
```

Uses `scripts/Dockerfile.api.test` with build context **repo root**. Adjust ports in the file if they conflict with local services.

---

### Troubleshooting

- **`pip install` fails on Linux:** create and activate **`apps/flask-api/.venv`** first (PEP 668).
- **Docker build cannot find `apps/flask-api`:** ensure **`-f scripts/docker-compose*.yml`** is run from the **repository root**, not from inside `scripts/`.
- **`pnpm install` fails:** use **pnpm**, not npm/yarn (enforced by root `package.json`).
- **API errors after switching SQLite ↔ MySQL:** align **`DATABASE_URL`** and run migrations / schema appropriate for your engine.

---

## Scripts (root `package.json`)

| Command | Description |
|---------|-------------|
| `pnpm install` | Install JS/TS workspace dependencies |
| `pnpm dev:portal` | Start Vite dev server |
| `pnpm dev:api` | Start Flask dev server (`apps/flask-api/run.py`) |
| `pnpm setup` | `pnpm install` + `pip install -r apps/flask-api/requirements.txt` (uses **current** `python`; prefer the venv steps above first) |
| `pnpm build` | Typecheck + build apps |
| `pnpm typecheck` | TypeScript check |
| `pnpm test:api` | pytest in `apps/flask-api` |
| `pnpm --filter @workspace/kiu-portal test` | Frontend unit tests (Vitest) |
| `pnpm --filter @workspace/kiu-portal test:e2e` | E2E tests (Playwright; install browsers once via `pnpm exec playwright install`) |

---

## API tests

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

Open an issue in this repository or contact your project supervisor / KIU ICT as appropriate.
