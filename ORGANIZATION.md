# 📁 Project Organization Guide

## Proposed Clean Structure

```
Kiu-Admission-Portal/
├── 📄 README.md                    # Main project readme
├── 📄 QUICKSTART.md                # Getting started guide
├── 📄 TESTING.md                   # Testing documentation
├── 🐳 docker/                      # Docker configurations
│   ├── docker-compose.yml          # Main production compose
│   ├── docker-compose.dev.yml      # Development compose
│   ├── docker-compose.test.yml     # Testing compose
│   ├── Dockerfile                  # Production API
│   ├── Dockerfile.api.test         # Test API
│   └── Dockerfile.frontend.test    # Test Frontend
├── 🧪 scripts/                     # Utility scripts
│   ├── test.sh                     # Run tests (Linux/macOS)
│   ├── test.ps1                    # Run tests (Windows)
│   ├── cleanup.sh                  # Cleanup (Linux/macOS)
│   ├── cleanup.ps1                 # Cleanup (Windows)
│   ├── setup.sh                    # Initial setup
│   └── backup/                     # Backup scripts
├── 📚 docs/                          # Documentation
│   ├── ARCHITECTURE.md             # System architecture
│   ├── API.md                      # API documentation
│   ├── DEPLOYMENT.md               # Deployment guide
│   ├── TESTING.md                  # Testing guide
│   └── archived/                   # Old docs (for reference)
├── 🗃️ archive/                      # Archived files
│   ├── auth_service_custom.py
│   ├── old_tests/
│   └── deprecated/
├── 📦 apps/                          # Applications
│   ├── flask-api/                  # Backend
│   └── kiu-portal/                 # Frontend
├── 🔧 config/                        # Configuration files
│   ├── nginx.conf
│   ├── .env.example
│   └── database_schema.sql
└── ⚙️ .github/                       # GitHub workflows
    └── workflows/
        ├── ci.yml
        └── cd.yml
```

## 🧹 Cleanup Actions Needed

### 1. Root Directory Files to Move:

| Current Location | Move To | Action |
|-----------------|---------|--------|
| `docker-compose*.yml` | `docker/` | Move |
| `Dockerfile*` | `docker/` | Move |
| `test.sh`, `test.ps1` | `scripts/testing/` | Move |
| `cleanup.sh`, `cleanup.ps1` | `scripts/testing/` | Move |
| `database_schema.sql` | `config/` | Move |
| `nginx.conf` | `config/` | Move |
| `*.md` (except README) | `docs/` | Move |
| `full_app_test.py` | `scripts/` or `archive/` | Move |
| `cookies.txt` | Delete | Not needed |
| `4_5791831366513466403.pdf` | `docs/assets/` or Delete | Archive |

### 2. Documentation Consolidation:

**Keep in root:**
- `README.md` - Main entry point
- `QUICKSTART.md` - Getting started (create from README)

**Move to `docs/`:**
- `TESTING.md` → `docs/TESTING.md`
- `DOCKER_SETUP.md` → `docs/DOCKER.md`
- `CLEANUP_SUMMARY.md` → `docs/archived/`
- `MANUAL_TEST_CHECKLIST.md` → `docs/archived/`
- `FINAL_SUMMARY.md` → `docs/archived/`
- All other `*.md` files

### 3. Docker Organization:

```docker/
docker-compose.yml           # Production
docker-compose.dev.yml       # Development
docker-compose.test.yml      # Testing
Dockerfile                   # API production
Dockerfile.api.test          # API testing
Dockerfile.frontend          # Frontend production
Dockerfile.frontend.test     # Frontend testing
```

### 4. Scripts Organization:

```scripts/
testing/
    ├── test.sh              # Linux/macOS test runner
    ├── test.ps1             # Windows test runner
    ├── cleanup.sh             # Linux/macOS cleanup
    └── cleanup.ps1          # Windows cleanup
backup/
    ├── backup_database.py
    └── restore_database.py
deployment/
    └── deploy.sh
utils/
    └── generate_secrets.sh
```

### 5. Archive Organization:

```archive/
2024-04-12/
    ├── README.md            # What was archived and why
    ├── auth_service_custom.py
    ├── test_recommendations.py
    └── old_documentation/
```

## 🎯 Implementation Plan

### Phase 1: Create Structure
```bash
mkdir -p docker scripts/testing scripts/backup docs/archived config
```

### Phase 2: Move Files
```bash
# Docker files
mv docker-compose*.yml docker/
mv Dockerfile* docker/

# Scripts
mv test.sh test.ps1 cleanup.sh cleanup.ps1 scripts/testing/

# Config
mv database_schema.sql nginx.conf config/

# Docs (keep README.md in root)
mv *.md docs/
mv README.md .  # Move back to root
```

### Phase 3: Update References
- Update paths in `docker-compose.yml` files
- Update paths in scripts
- Update documentation links

### Phase 4: Clean Root
```bash
rm -f cookies.txt  # Not needed
rm -f 4_5791831366513466403.pdf  # Archive or delete
```

## ✅ Benefits

1. **Clean Root Directory** - Only essential files visible
2. **Logical Grouping** - Related files together
3. **Easy Navigation** - Find what you need quickly
4. **Better Onboarding** - New devs understand structure
5. **CI/CD Ready** - Organized for automation
