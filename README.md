# KIU Admission Portal

Monorepo for the Kampala International University admissions and careers portal: a **React (Vite)** SPA and a **Flask** API, with a shared TypeScript API client.

## Repository layout

| Path | Description |
|------|----------------|
| [`apps/kiu-portal`](apps/kiu-portal) | Vite + React frontend (`@workspace/kiu-portal`) |
| [`apps/flask-api`](apps/flask-api) | Flask REST API |
| [`lib/api-client-react`](lib/api-client-react) | Shared React Query hooks and types (`@workspace/api-client-react`) |

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
