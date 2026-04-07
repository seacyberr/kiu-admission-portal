# KIU Admission Portal — Full Bug Fix Patch Guide

## How to apply these fixes

Each section below lists the **exact file to replace**, what was wrong, and what changed.
The fixed files are provided as drop-in replacements.

---

## 1. `apps/kiu-portal/vite.config.ts` → replace with `vite.config.ts`

### Bugs fixed

#### 🔴 httpOnly cookie proxy bug (root cause of the hard-reload login issue)
Vite's proxy was forwarding Set-Cookie headers from Flask unmodified. Flask sets
`Secure; SameSite=None` on the auth cookie, which the browser rejects over plain
HTTP (localhost). The result: cookie never stored → every API call returns 401 →
browser caches the 401 → normal reload replays the cached failure → must hard-reload
to clear cache.

**Fix:** Added a `proxyRes` handler that strips `Secure` and rewrites `SameSite=None`
to `SameSite=Lax` in-flight, plus `cookieDomainRewrite: "localhost"`. Now the cookie
is accepted on first load, every time.

#### 🔴 Port mismatch
Proxy was targeting `http://127.0.0.1:5001` but Flask defaults to `5000`. Every API
call in dev was routing to the wrong port.

**Fix:** Default changed to `http://127.0.0.1:5000`.

#### 🟡 Dev cache causing stale 401 replay
Even with cookies working, the browser could cache a 401 response and replay it on
normal reload. Added `Cache-Control: no-store` header to the dev server.

**Fix:** Added `server.headers: { "Cache-Control": "no-store" }`.

#### 🟡 Replit-specific plugins on non-Replit machines
`@replit/vite-plugin-runtime-error-modal`, `@replit/vite-plugin-cartographer`, and
`@replit/vite-plugin-dev-banner` are Replit dependencies that will fail or warn on
any standard dev machine (Windows/Linux/Mac).

**Fix:** Removed. If you run on Replit, add them back conditionally via
`process.env.REPL_ID !== undefined`.

#### 🟡 `@assets` alias pointing to Replit path
`@assets` was aliased to `../../attached_assets` — a Replit-specific directory that
doesn't exist on local machines.

**Fix:** Removed. Import assets from `src/assets/` instead.

#### 🟢 Chunk size warning limit too low
`chunkSizeWarningLimit: 250` triggered constant false warnings. React + ReactDOM alone
exceed 250KB in development.

**Fix:** Raised to `500` (Vite default).

#### 🟢 Proxy config duplicated
`server.proxy` and `preview.proxy` had identical config copy-pasted. One change
would drift from the other.

**Fix:** Extracted to a shared `apiProxy` const used by both.

---

## 2. `apps/flask-api/config.py` → replace with `config.py`

### Bugs fixed

#### 🔴 Empty JWT secret allowed at startup
If neither `JWT_SECRET` nor `SECRET_KEY` env var was set, the secret fell through to
`""`. JWTs signed with an empty secret are trivially forgeable. Also caused subtle
"invalid signature" errors because Flask's session cookie is also signed with
`SECRET_KEY`.

**Fix:** Added `validate_config(app)` function that raises `RuntimeError` at startup
if no secret is set. Call it from your Flask app factory:
```python
# In apps/flask-api/app/__init__.py or wherever create_app() lives:
from config import validate_config
validate_config(app)
```

#### 🔴 Wildcard CORS with credentials
`CORS_ORIGINS = "*"` is blocked by browsers when the request includes
`credentials: 'include'` (which your frontend uses for httpOnly cookie auth). This
was silently breaking cross-origin cookie passing.

**Fix:** Default changed to `"http://localhost:5173"`. Set `CORS_ORIGINS` env var to
your production domain in deployment.

#### 🟡 `SEED_DATABASE` defaulted to `true` in production
Any server without `SEED_DATABASE=false` explicitly set would re-seed on every
restart. In production this risks overwriting or duplicating real applicant data.

**Fix:** Base `Config` now defaults to `false`. `DevelopmentConfig` overrides to
`true` so local fresh installs still get demo data automatically.

#### 🟡 `validate_config()` added
New helper function `validate_config(app)` performs startup checks after the Flask
app is configured. Add one call in `create_app()` and you get hard-fail-fast
behaviour instead of silent misconfigurations.

#### 🟢 `TestingConfig` gets safe JWT secret
Test runs no longer need `JWT_SECRET` set in the environment. Testing config provides
`"test-secret-key-not-for-production"` as a fallback so pytest runs cleanly on any
machine including CI.

---

## 3. `apps/kiu-portal/src/pages/auth/login.tsx` → replace with `login.tsx`

### Bug fixed

#### 🔴 Silent logout on accidental navigation to /login
The April 2 commit introduced logic to call the logout API whenever an authenticated
user visited `/login`. The intent was to allow re-login with a different account, but
the side effect is:

- User is logged in
- They click a /login bookmark, back button, or email link
- Their session is **silently destroyed**
- They land on the login form confused

**Fix:** Authenticated users are now **redirected** to their dashboard (`/admin/dashboard`
or `/applicant/dashboard` based on role). They are never logged out by navigating to
/login. If a user genuinely wants to switch accounts, they should use the logout button
in the UI.

Also added a loading spinner while auth state is being determined, preventing the
login form from flashing for ~200ms before the redirect fires.

---

## 4. Additional fixes to apply manually (no full file replacement needed)

### 4a. Call `validate_config` in your app factory

Find your `create_app()` function (likely in `apps/flask-api/app/__init__.py`) and add:

```python
from config import validate_config

def create_app(config_class=None):
    app = Flask(__name__)
    # ... existing config loading ...
    validate_config(app)  # ← add this line after config is applied
    return app
```

### 4b. Update Flask CORS call

Find wherever you call `CORS(app, ...)` and ensure it matches:

```python
from flask_cors import CORS

CORS(
    app,
    origins=app.config["CORS_ORIGINS"],
    supports_credentials=True,
    expose_headers=["Set-Cookie"],
)
```

Without `supports_credentials=True` and `expose_headers=["Set-Cookie"]`, the browser
cannot read or store the auth cookie even when the proxy is fixed.

### 4c. Move doc files out of root

The following files have no place in the repo root and add noise to every `ls` / IDE
file picker. Move to `docs/` or delete:

```
extracted_fees_raw.txt
extracted_kiu_information.md
extracted_kiu_main_campus_fees_ugx.md
extracted_kiu_main_campus_fees_usd.md
kiu_fees_compiled.md
kiu_programs_fees_detailed.md
IMPLEMENTATION_PHASE2.md
IMPLEMENTATION_PHASE3.md
IMPLEMENTATION_PLAN.md
PROPOSAL_VS_IMPLEMENTATION_COMPARISON.md
CHANGES_README.md
CROSS_PLATFORM_SETUP_GUIDE.md
WINDOWS_COMPATIBILITY_GUIDE.md
```

Run:
```bash
mkdir -p docs
git mv extracted_*.* kiu_*.* IMPLEMENTATION_*.md PROPOSAL_*.md CHANGES_README.md \
        CROSS_PLATFORM_*.md WINDOWS_*.md docs/
git commit -m "chore: move doc files into docs/"
```

### 4d. Add `.env.local` to `.gitignore`

Your `.gitignore` should include:
```
.env.local
.env.*.local
apps/flask-api/uploads/
node_modules/
.vite/
__pycache__/
*.pyc
```

---

## 5. Cross-platform startup verification

After applying all fixes, verify startup on each OS:

**Windows (PowerShell):**
```powershell
$env:JWT_SECRET = "your-secret-here"
$env:DATABASE_URL = "mysql+pymysql://root@localhost:3306/kiu_admissions"
$env:CORS_ORIGINS = "http://localhost:5173"
pnpm setup
# Terminal 1:
pnpm dev:api
# Terminal 2:
pnpm dev:portal
```

**Linux / macOS:**
```bash
export JWT_SECRET="your-secret-here"
export DATABASE_URL="mysql+pymysql://root@localhost:3306/kiu_admissions"
export CORS_ORIGINS="http://localhost:5173"
pnpm setup
pnpm dev:api   # Terminal 1
pnpm dev:portal # Terminal 2
```

**Expected result:** Login works on first attempt, survives normal refresh (F5),
no hard reload required.

---

## Summary table

| # | File | Severity | Issue | Fix |
|---|------|----------|-------|-----|
| 1 | vite.config.ts | 🔴 Critical | httpOnly cookie stripped by proxy | proxyRes handler + cookieDomainRewrite |
| 2 | vite.config.ts | 🔴 Critical | Proxy port 5001 vs Flask port 5000 | Default changed to 5000 |
| 3 | vite.config.ts | 🟡 Serious | 401 responses cached by browser | Cache-Control: no-store in dev headers |
| 4 | vite.config.ts | 🟡 Serious | Replit plugins break on all other OS | Removed |
| 5 | vite.config.ts | 🟢 Minor | chunkSizeWarningLimit too low | 250 → 500 |
| 6 | config.py | 🔴 Critical | Empty JWT secret allowed | validate_config() hard startup check |
| 7 | config.py | 🔴 Critical | Wildcard CORS blocks cookies | Default to localhost:5173 |
| 8 | config.py | 🟡 Serious | SEED_DATABASE=true in production | Default false, dev overrides to true |
| 9 | login.tsx | 🔴 Critical | Visiting /login silently logs out users | Redirect to dashboard instead |
| 10 | Repo root | 🟢 Minor | 13 doc files cluttering root | Move to docs/ |
