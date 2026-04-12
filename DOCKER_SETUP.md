# Docker Development Guide

Complete cross-platform development environment for KIU Admission Portal. Works identically on Windows, macOS, and Linux.

## Prerequisites

1. **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
   - Windows: [Download Docker Desktop](https://www.docker.com/products/docker-desktop)
   - macOS: [Download Docker Desktop](https://www.docker.com/products/docker-desktop)
   - Linux: `sudo apt install docker.io docker-compose` (Ubuntu/Debian)

2. **Git** for cloning the repository

## Quick Start (Any Platform)

### Windows (Command Prompt or PowerShell)
```cmd
# Navigate to project directory
cd Kiu-Admission-Portal

# Start development environment
scripts\dev-start.bat
```

### macOS / Linux (Terminal)
```bash
# Navigate to project directory
cd Kiu-Admission-Portal

# Make scripts executable (first time only)
chmod +x scripts/*.sh

# Start development environment
./scripts/dev-start.sh
```

## What Gets Started

| Service | URL | Purpose |
|---------|-----|---------|
| **API Backend** | http://localhost:5001 | Flask API with auto-reload |
| **Frontend** | http://localhost:5173 | React dev server with HMR |
| **MySQL** | localhost:3306 | Database (consistent across platforms) |
| **Redis** | localhost:6379 | Caching & session store |

## Development Workflow

### Start Developing
```bash
# Windows
scripts\dev-start.bat

# Mac/Linux
./scripts/dev-start.sh
```

### View Logs
```bash
# All services
docker-compose -f docker-compose.dev.yml logs -f

# Just API
docker-compose -f docker-compose.dev.yml logs -f api

# Just frontend
docker-compose -f docker-compose.dev.yml logs -f frontend
```

### Stop Everything
```bash
# Windows
scripts\dev-stop.bat

# Mac/Linux
./scripts/dev-stop.sh
```

### Reset Everything (Fresh Start)
Use this when you have dependency issues or database corruption:
```bash
# Windows
scripts\dev-reset.bat

# Mac/Linux
./scripts/dev-reset.sh
```

## Directory Structure in Containers

```
/app                    # Flask API working directory
├── /app/venv          # Python virtual environment (isolated)
├── /app/uploads       # Uploaded files (persistent volume)
└── /app/logs          # Application logs (persistent volume)

/app                   # Frontend working directory
├── /app/node_modules  # Node packages (cached volume)
└── /app/node_modules/.vite  # Vite cache (cached volume)
```

## Hot Reload / File Watching

✅ **Backend (Flask)**: Changes to Python files trigger automatic restart
✅ **Frontend (React)**: Changes trigger instant browser refresh via Vite

### Windows-Specific Notes
- File watching uses polling mode for reliability on Windows
- May use slightly more CPU than native file watching
- If changes aren't detected, restart the specific service:
  ```bash
  docker-compose -f docker-compose.dev.yml restart api
  ```

## Database Access

### From Application
The database is automatically configured - no setup needed!

### From Your Machine (for debugging)
```bash
# Connect via MySQL client
mysql -h localhost -P 3306 -u kiu_dev -p
# Password: kiu_dev_password

# Or use Docker
docker exec -it kiu-mysql-dev mysql -u kiu_dev -p kiu_portal_dev
```

### Database Credentials
| Environment | User | Password | Database |
|-------------|------|----------|----------|
| Development | `kiu_dev` | `kiu_dev_password` | `kiu_portal_dev` |
| Development | `root` | `root_dev_password` | all |

## Common Issues & Solutions

### Port Already in Use
If you see `Bind for 0.0.0.0:XXXX failed: port is already allocated`:

```bash
# Find what's using the port (Windows)
netstat -ano | findstr :5001
# Then kill the process or use a different port in docker-compose.dev.yml

# Find what's using the port (Mac/Linux)
lsof -i :5001
kill -9 <PID>
```

### Permission Denied (Windows)
If you see permission errors:
1. Run Docker Desktop as Administrator
2. Ensure your Windows user is in the `docker-users` group
3. Try resetting Docker Desktop: Settings → Troubleshoot → Reset to factory defaults

### Slow File Performance (Windows)
If hot reload is slow on Windows:
1. Ensure WSL2 is enabled in Docker Desktop settings
2. Move project to WSL filesystem (`\\wsl$\Ubuntu\home\...`) for better performance
3. Use `docker-compose -f docker-compose.dev.yml restart` after bulk file changes

### Database Won't Start
```bash
# Check logs
docker-compose -f docker-compose.dev.yml logs db

# If corrupted, reset data:
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up -d
```

### Node Modules Issues
```bash
# Clean and reinstall frontend dependencies
docker-compose -f docker-compose.dev.yml down
docker volume rm kiu-admission-portal_frontend_node_modules
docker-compose -f docker-compose.dev.yml up -d frontend
```

## Advanced Commands

### Run One-Time Commands

```bash
# Run database migrations manually
docker-compose -f docker-compose.dev.yml exec api flask db upgrade

# Open Python shell in API container
docker-compose -f docker-compose.dev.yml exec api python

# Install new Python package
docker-compose -f docker-compose.dev.yml exec api pip install package-name
# Then update requirements.txt!

# Run tests
docker-compose -f docker-compose.dev.yml exec api pytest
```

### Debug Mode
To attach a debugger:
```bash
# Start with stdin attached
docker-compose -f docker-compose.dev.yml run --rm api

# Or use VS Code Docker extension for debugging
```

## Switching Between Local and Docker

### Develop Locally (without Docker)
If you prefer local development:

**Backend:**
```bash
cd apps/flask-api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
flask run
```

**Frontend:**
```bash
cd apps/kiu-portal
npm install -g pnpm
pnpm install
pnpm dev
```

**But we recommend Docker** to avoid:
- Python version conflicts
- MySQL/Redis installation issues
- Different behavior between Windows/Mac/Linux
- "Works on my machine" problems

## Environment Variables

Create a `.env` file in the project root (optional for development):

```env
# Optional: Override defaults
cp .env.example .env
# Edit .env with your preferences
```

| Variable | Default | Description |
|----------|---------|-------------|
| `JWT_SECRET` | `dev-jwt-secret-change-in-production` | JWT signing key |
| `SECRET_KEY` | `dev-secret-key-change-in-production` | Flask secret key |
| `LOG_LEVEL` | `DEBUG` | Logging verbosity |

## Production Deployment

For production, use the main `docker-compose.yml` (not the dev version):

```bash
# Copy and configure environment
cp .env.example .env
# Edit .env with production secrets

# Start production stack
docker-compose up -d
```

See production deployment guide in `docs/DEPLOYMENT.md`

## Getting Help

- Check logs: `docker-compose -f docker-compose.dev.yml logs -f`
- Reset environment: Use `dev-reset` script
- Port conflicts: Check what's using ports 3306, 5001, 5173, 6379
- File a bug: Include `docker-compose -f docker-compose.dev.yml logs` output
