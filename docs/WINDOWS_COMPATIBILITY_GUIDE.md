# KIU Admission Portal - Windows Compatibility Guide

This document explains how to properly transfer and run this application on Windows, including all fixes required for cross-platform compatibility.

##  Identified Issues & Fixes

| Issue | Linux (Kali) | Windows | Fix Required |
|-------|--------------|---------|--------------|
| Shell scripts in npm preinstall | Works with sh/bash | No default sh shell |  Cross-platform fix |
| Environment variables in npm scripts | `PORT=5173 command` syntax | Does not work |  Use cross-env |
| Python command name | `python3` | Usually `python` |  Fix scripts |
| Gunicorn WSGI server | Linux only | Not supported on Windows |  Use waitress |
| File path separators | `/` | `\` |  Already handled correctly in code |
| Line endings (CRLF vs LF) | LF | CRLF |  Git handles automatically |
| Case sensitivity | Case sensitive filesystem | Case insensitive |  All imports are correct |

---

##  Step 1: Fix Root Package.json Scripts

First update the root `package.json` to remove platform specific shell script:

```json
{
  "scripts": {
    "preinstall": "node -e \"if (!process.env.npm_config_user_agent.includes('pnpm')) { console.error('Use pnpm instead'); process.exit(1); }\"",
    "build": "pnpm run typecheck && pnpm -r --filter \"!@workspace/mockup-sandbox\" --if-present run build",
    "typecheck": "pnpm -r --filter \"./apps/**\" --filter \"./lib/**\" --filter \"!@workspace/mockup-sandbox\" --if-present run typecheck",
    "test:api": "cd apps/flask-api && python -m pytest tests/ -q"
  }
}
```

---

##  Step 2: Fix Frontend Package.json

Update `apps/kiu-portal/package.json` scripts for Windows compatibility:

```json
{
  "scripts": {
    "dev": "cross-env PORT=5173 BASE_PATH=/ vite --config vite.config.ts --host 0.0.0.0",
    "build": "vite build --config vite.config.ts",
    "serve": "cross-env PORT=4173 BASE_PATH=/ vite preview --config vite.config.ts --host 0.0.0.0",
    "typecheck": "tsc -p tsconfig.json --noEmit",
    "test": "vitest run --config vitest.config.ts",
    "test:watch": "vitest --config vitest.config.ts",
    "test:e2e": "playwright test"
  }
}
```

Then install cross-env:
```bash
pnpm add -D cross-env
```

---

##  Step 3: Flask API Windows Setup

### Windows Development Server

Create a `run_windows.py` file in `apps/flask-api/`:
```python
#!/usr/bin/env python
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    from app import app
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
```

### Production Server on Windows
Replace gunicorn with waitress:
```bash
pip install waitress
```

Run with:
```bash
waitress-serve --listen=0.0.0.0:5000 wsgi:app
```

---

##  Step 4: Complete Windows Installation Steps

1. **Install required software on Windows:**
   - Node.js 20+ LTS https://nodejs.org/
   - Python 3.11+ https://www.python.org/
   - Git for Windows https://gitforwindows.org/
   - Enable "Add Python to PATH" during installation

2. **Install pnpm globally:**
   ```powershell
   npm install -g pnpm
   ```

3. **Transfer the project:**
   ```
   Use git clone / copy entire folder
   DO NOT use zip files that break file permissions
   ```

4. **Install dependencies:**
   ```powershell
   cd Kiu-Admission-Portal
   pnpm install
   ```

5. **Setup backend:**
   ```powershell
   cd apps/flask-api
   pip install -r requirements.txt
   pip install waitress
   ```

6. **Copy environment file:**
   ```powershell
   copy .env.example .env
   ```

7. **Run migrations:**
   ```powershell
   python scripts/migrate_db.py
   ```

---

##  Verification Checklist

When running on Windows verify these work correctly:

- [ ] `pnpm install` runs without errors
- [ ] Frontend dev server starts: `pnpm --filter kiu-portal dev`
- [ ] Backend starts: `python apps/flask-api/run_windows.py`
- [ ] All pages load correctly
- [ ] Database operations work
- [ ] File uploads work
- [ ] Authentication works
- [ ] All tests pass

---

##  Known Windows Limitations

1. **Gunicorn will not work** - use waitress or IIS on Windows
2. **Redis rate limiting** requires Redis installed on Windows (use WSL or native Redis port)
3. **Docker** is recommended for production deployments on Windows Server
4. **Performance** will be slightly better on Linux for production

---

##  Fastest Way To Run On Windows

The absolute simplest method that requires zero changes:
1. Enable WSL 2 on Windows
2. Install Ubuntu from Microsoft Store
3. Run exactly the same commands as you do on Kali Linux inside WSL
4. This gives 100% compatibility with zero code changes

This is the recommended approach for Windows users, as it maintains full parity with the development environment.