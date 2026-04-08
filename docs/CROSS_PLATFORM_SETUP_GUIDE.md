# KIU Admission Portal - Cross Platform Setup & Database Guide

This document contains complete instructions for running this project on **Windows, Linux and macOS**, plus MySQL database configuration.

---

##  QUICK START (ALL OPERATING SYSTEMS)

All commands below work identically on **Windows, Kali Linux, Ubuntu, macOS**. There are no differences.

### Step 1: Install Prerequisites
| OS | Install these |
|----|---------------|
| **All Systems** | Node.js 20+ LTS https://nodejs.org/ |
| **All Systems** | Python 3.11+ https://www.python.org/ |
| **All Systems** | Git https://git-scm.com/ |

 **IMPORTANT**: During installation tick **"Add to PATH"** checkbox for both Node.js and Python.

### Step 2: Install pnpm
Run this command **once** on any system:
```bash
npm install -g pnpm
```

### Step 3: Get the project
```bash
git clone <repository-url>
cd Kiu-Admission-Portal
```

### Step 4: Full automatic setup
**ONE COMMAND DOES EVERYTHING:**
```bash
pnpm setup
```
 This will install:
- All Node.js dependencies
- All Python packages
- Automatically installs **gunicorn on Linux/macOS**
- Automatically installs **waitress on Windows**

### Step 5: Configure environment
```bash
# Windows:
copy .env.example .env

# Linux / macOS:
cp .env.example .env
```

### Step 6: Run the application

**Terminal 1 - Frontend:**
```bash
pnpm dev:portal
```

**Terminal 2 - Backend API:**
```bash
pnpm dev:api
```

 The application will now be running at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:5000
- API Docs: http://localhost:5000/docs

---

##  MySQL Database Setup

### Database Configuration
Edit `.env` file and set your database connection:

```env
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/kiu_admission
```

### Install MySQL Server

| OS | Instructions |
|----|--------------|
| **Windows** | Install MySQL Community Server https://dev.mysql.com/downloads/windows/installer/ |
| **Kali / Ubuntu** | `sudo apt install mysql-server` |
| **macOS** | `brew install mysql` |

### Database Operations

Run all these commands from `apps/flask-api` folder:

#### 1. Create database
```sql
CREATE DATABASE kiu_admission CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### 2. Run migrations
```bash
python scripts/migrate_db.py upgrade
```

#### 3. Seed initial data
```bash
python scripts/seed_programs.py
```

#### 4. Create admin user
```bash
python scripts/create_admin.py
```

#### Access Database Directly
| Tool | Works on all OS |
|------|-----------------|
| Command Line | `mysql -u root -p kiu_admission` |
| GUI | MySQL Workbench https://dev.mysql.com/downloads/workbench/ |
| Web UI | phpMyAdmin, Adminer |

---

##  VERIFIED WORKING ON
 Windows 10 / 11
 Kali Linux 2024.x
 Ubuntu 22.04 / 24.04
 macOS Sonoma / Sequoia

---

## ️ Production Deployment

| OS | Server | Command |
|----|--------|---------|
| Linux / macOS | Gunicorn | `gunicorn --config gunicorn.conf.py wsgi:app` |
| Windows | Waitress | `waitress-serve --listen=0.0.0.0:5000 wsgi:app` |

---

##  TROUBLESHOOTING

### Common Windows Issues:
1. **"python not found"**: Make sure you ticked "Add Python to PATH" during installation
2. **Port already in use**: Close other applications running on port 5000 / 5173
3. **Execution policy**: Run `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` in PowerShell

### Common Linux Issues:
1. **Permission denied**: Do not run with sudo, use regular user account
2. **MySQL connection**: Ensure mysql service is running `sudo systemctl start mysql`

---

All commands and functionality are identical across all operating systems.