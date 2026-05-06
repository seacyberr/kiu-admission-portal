# KIU Admission Portal

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node 18+](https://img.shields.io/badge/node-18+-green.svg)](https://www.python.org/downloads/)
[![Node 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)

**A cross-platform admission management system for Kampala International University**  
Compliant with NCHE Uganda requirements. Works on Windows, macOS, Linux, and mobile devices.

---

## ✨ Features

### 🎨 Modern UI/UX
- **Dark Mode Support**: Toggle between light and dark themes with persistent preferences
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **Animated Interactions**: Smooth transitions and scroll-triggered animations
- **Page Progress Bar**: Visual indicator showing scroll progress on pages

### 🔐 Authentication & Security
- **JWT-based Authentication**: Secure token-based user sessions
- **Password Strength Meter**: Real-time password validation during registration
- **Role-based Access Control**: Separate dashboards for applicants, finalists, and admins
- **OTP Verification**: Email-based one-time password verification

### 📊 Admin Dashboard
- **Programme Applications Dashboard**: Comprehensive analytics with interactive charts
  - Pie charts for application status distribution
  - Bar charts for programme popularity
  - Timeline charts for application trends
  - Advanced filtering and search functionality
- **Real-time Statistics**: Live metrics for applications, approvals, and rejections
- **Status Management**: One-click status updates with API integration
- **Export Capabilities**: Data export functionality for reporting

### 📱 User Experience
- **Notifications System**: Dropdown notifications with unread badges
- **Toast Notifications**: User feedback for actions and errors
- **Loading States**: Skeleton screens and progress indicators
- **Error Boundaries**: Graceful error handling with recovery options
- **Form Validation**: Real-time validation with helpful error messages

### 🎓 Academic Features
- **NCHE Recommendations**: AI-powered programme recommendations based on exam results
- **Qualification Checker**: Automatic eligibility verification for programmes
- **Multiple Exam Support**: O-Level, A-Level, Diploma, and Degree qualification handling
- **Programme Matching**: Intelligent programme suggestions based on academic performance

---

## 🚀 Quick Start (Cross-Platform)

### Option 1: Docker Development (Recommended for Teams)
The easiest way to get started without installing dependencies locally. Works identically on Windows, macOS, and Linux.

**Step 1: Install Docker**
- [Docker Desktop](https://www.docker.com/products/docker-desktop) (Windows/Mac)
- Or `sudo apt install docker.io docker-compose` (Linux)

**Step 2: Start Development Environment**
```bash
# Windows (Command Prompt or PowerShell)
scripts\dev-start.bat

# macOS / Linux
chmod +x scripts/*.sh
./scripts/dev-start.sh
```

That's it! Access:
- **Frontend**: http://localhost:5173
- **API**: http://localhost:5001
- **Database**: localhost:3306 (MySQL)

See [DOCKER_SETUP.md](DOCKER_SETUP.md) for detailed instructions.

### Option 2: Local Development (Advanced Users)
Install dependencies directly on your machine. Requires Python 3.11+, Node.js 18+, MySQL, and Redis.

**Step 1: Install Prerequisites**
- [Node.js 18+](https://nodejs.org) (LTS version)
- [Python 3.11+](https://python.org)
- [MySQL 8.0](https://mysql.com)
- [pnpm](https://pnpm.io) (`npm install -g pnpm`)

**Step 2: Install Dependencies**
```bash
# Install frontend dependencies
pnpm install

# Install Python dependencies (cross-platform)
cd apps/flask-api
pip install -r requirements.txt
```

**Step 3: Configure**
Create `apps/flask-api/.env`:
```env
# Database - Works with SQLite (no setup), PostgreSQL, or MySQL
DATABASE_URL=sqlite:///kiu_portal.db

# Or for PostgreSQL:
# DATABASE_URL=postgresql://user:pass@localhost:5432/kiu_portal

# Security
JWT_SECRET=your-secret-key-here
FLASK_ENV=development
```

**Step 4: Initialize Database**
```bash
cd apps/flask-api
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
python scripts/seed_all_programs.py
```

**Step 5: Start Development**
```bash
# Terminal 1 - Backend (Port 5000)
cd apps/flask-api
python run.py

# Terminal 2 - Frontend (Port 5173)
pnpm --filter kiu-portal dev
```

**Access:**
- Frontend: http://localhost:5173
- API: http://localhost:5000

---

## 📱 Mobile & Responsive Design

The application is fully responsive and works on:
- ✅ Desktop (Windows, macOS, Linux)
- ✅ Tablets (iPad, Android tablets)
- ✅ Mobile phones (iOS Safari, Android Chrome)
- ✅ No app installation required - works in browser

**Key Responsive Features:**
- Mobile-optimized forms
- Touch-friendly buttons
- Responsive tables with horizontal scroll
- Optimized image uploads
- Mobile payment flow

---

## 🗂️ Project Structure

```
Kiu-Admission-Portal/
├── apps/
│   ├── kiu-portal/          # React frontend (Vite + TypeScript)
│   └── flask-api/           # Flask backend API
│       ├── requirements.txt # Python dependencies
│       ├── run.py          # Entry point
│       └── .env            # Configuration
├── lib/
│   └── api-client-react/    # Shared API client
├── package.json             # Node.js dependencies
└── README.md               # This file
```

---

## 🔧 System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Node.js | 18.x LTS | 20.x LTS |
| Python | 3.11 | 3.12 |
| RAM | 4 GB | 8 GB |
| Storage | 2 GB free | 5 GB free |
| Browser | Chrome 90+ | Latest Chrome/Firefox/Safari |

### Optional for Production
- **Redis** - For caching and rate limiting (falls back to memory if not available)
- **PostgreSQL** - For production database (SQLite works for development)
- **Sentry** - For error tracking (optional)

---

## 🧪 Testing

```bash
# Backend tests (all platforms)
cd apps/flask-api
python -m pytest tests/ -v

# Frontend tests
pnpm --filter kiu-portal test

# Type checking
pnpm run typecheck
```

---

## 📦 Production Deployment

**Simple deployment on any platform:**

```bash
# Build for production
pnpm run build

# Start production server
cd apps/flask-api
pip install gunicorn  # Linux/Mac
# OR
pip install waitress  # Windows

# Run with production server
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app  # Linux/Mac
# OR
waitress-serve --host 0.0.0.0 --port=5000 wsgi:app  # Windows
```

---

## 📄 Documentation

- **API Docs:** http://localhost:5000/docs (when running)
- **Architecture:** `docs/ARCHITECTURE.md`
- **NCHE Standards:** `docs/NCHE_STANDARDS.md`
- **Deployment:** `docs/DEPLOYMENT.md`

---

## 🐛 Troubleshooting

**Issue: `pnpm` command not found**
```bash
npm install -g pnpm
```

**Issue: Database connection fails**
- Use SQLite for easiest setup: `DATABASE_URL=sqlite:///kiu_portal.db`

**Issue: Port already in use**
```bash
# Find and kill process on port 5000
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:5000 | xargs kill -9
```

**Issue: Python packages fail to install**
```bash
# Upgrade pip first
python -m pip install --upgrade pip setuptools wheel
```

---

## 🤝 Contributing

This is a final year project. For issues or improvements, please document them for academic review.

---

## 📧 Support

- **KIU IT Support:** itsupport@kiu.ac.ug
- **Project Author:** [Student Email]
- **Documentation:** See `docs/` folder

---

## 📜 License

MIT License - See [LICENSE](LICENSE) file

---

**Kampala International University** - The Leading Private University in Uganda
