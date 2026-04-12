# 🧪 Testing Guide - Docker Based (Cross-Platform)

Run all tests with one command using Docker! Works on **Windows**, **Linux**, and **macOS**.

## 🚀 Quick Start

### Linux / macOS / WSL (Bash)
```bash
# Run ALL tests (backend + frontend)
./test.sh

# Or run separately:
./test.sh backend    # API tests only (34 tests)
./test.sh frontend   # E2E tests only (40 tests)
```

### Windows (PowerShell)
```powershell
# Run ALL tests
.\test.ps1

# Or run separately:
.\test.ps1 backend   # API tests only (34 tests)
.\test.ps1 frontend  # E2E tests only (40 tests)
```

### Windows (Git Bash / WSL)
```bash
# Same as Linux - use test.sh
./test.sh
```

## 📊 What Gets Tested

### Backend (34 tests)
- ✅ Authentication (JWT, login, register, OTP)
- ✅ Admission (programs, applications)
- ✅ Health checks
- ✅ Opportunities

### Frontend (40 E2E tests)
- ✅ Page rendering & navigation
- ✅ Form validation
- ✅ Authentication flows
- ✅ Responsive design
- ✅ Accessibility

## 🐳 Docker Services

| Service | Port | Purpose |
|---------|------|---------|
| MySQL | 3307 | Test database |
| Redis | 6380 | Caching |
| Flask API | 5001 | Backend API |
| Frontend | 5173 | React dev server |
| Playwright Report | 9323 | Test results |

## 🔧 Requirements

### All Platforms
- **Docker 20.10+** (Desktop or Engine)
- **Docker Compose 2.0+**

### Platform-Specific Setup

#### Windows
1. Install **Docker Desktop for Windows**
   - Download: https://www.docker.com/products/docker-desktop
   - Enable WSL2 backend (recommended)
   - Start Docker Desktop

2. Open **PowerShell** or **Git Bash** (as Administrator)

3. Navigate to project folder:
   ```powershell
   cd C:\path\to\Kiu-Admission-Portal
   ```

#### Linux (Ubuntu/Debian)
1. Install Docker:
   ```bash
   sudo apt update
   sudo apt install -y docker.io docker-compose
   sudo usermod -aG docker $USER
   # Log out and back in for group changes
   ```

2. Start Docker service:
   ```bash
   sudo systemctl start docker
   ```

#### Linux (Kali)
```bash
sudo apt update
sudo apt install -y docker.io docker-compose
sudo systemctl enable docker --now
```

#### macOS
1. Install **Docker Desktop for Mac**
   - Download: https://www.docker.com/products/docker-desktop
   - Drag to Applications and start

2. Open Terminal

3. Navigate to project:
   ```bash
   cd /path/to/Kiu-Admission-Portal
   ```

## 📈 View Results

After tests complete:

```bash
# Backend results (in terminal)
# Shows: "34 passed"

# Frontend results
open http://localhost:9323
# Shows: Playwright HTML report
```

## 🧹 Cleanup

Tests automatically cleanup on exit, but if needed:

### Linux/macOS
```bash
docker-compose -f docker-compose.test.yml down -v
```

### Windows (PowerShell)
```powershell
docker-compose -f docker-compose.test.yml down -v
```

## 🐛 Troubleshooting

### Issue: "Docker is not running"
**Windows:** Start Docker Desktop from Start Menu
**Linux:** `sudo systemctl start docker`
**macOS:** Start Docker Desktop from Applications

### Issue: "Permission denied" (Linux)
```bash
sudo usermod -aG docker $USER
# Then log out and back in
```

### Issue: "Port already in use"
```bash
# Check what's using the port
# Linux/macOS:
lsof -i :5173

# Windows (PowerShell):
Get-Process -Id (Get-NetTCPConnection -LocalPort 5173).OwningProcess

# Kill the process or use different ports in docker-compose.test.yml
```

### Issue: Tests timeout on Windows
Make sure Docker Desktop has enough resources:
1. Docker Desktop → Settings → Resources
2. Increase CPU to 4 cores
3. Increase Memory to 4GB
4. Apply & Restart

### Issue: "docker-compose command not found" (Windows)
Use `docker compose` (with space) instead:
```powershell
docker compose -f docker-compose.test.yml up
```

### Debugging Failed Tests

```bash
# Keep containers running for debugging
# Linux/macOS:
docker-compose -f docker-compose.test.yml up

# Windows:
docker compose -f docker-compose.test.yml up

# Run specific test (in another terminal)
# Linux/macOS:
docker-compose -f docker-compose.test.yml exec api python -m pytest tests/test_auth.py::TestLogin -v

# Windows:
docker compose -f docker-compose.test.yml exec api python -m pytest tests/test_auth.py::TestLogin -v
```

## ✨ Benefits

- **Consistent**: Same environment everywhere
- **Isolated**: No conflicts with local installs
- **Fast**: Parallel testing
- **Easy**: One command to test everything
- **CI/CD Ready**: Works in GitHub Actions, GitLab CI, etc.
