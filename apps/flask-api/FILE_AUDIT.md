# KIU Admission Portal - File Audit
## Which Files Are Needed vs Can Be Removed

### ✅ CORE FILES (Keep These - Required for app to run)

| File | Purpose | Status |
|------|---------|--------|
| `app.py` | Main Flask application factory | **REQUIRED** |
| `models.py` | Database models (User, Program, Application, etc.) | **REQUIRED** |
| `seed.py` | Seeds database with programs and admin user | **REQUIRED** |
| `requirements.txt` | Python dependencies | **REQUIRED** |
| `config.py` | App configuration settings | **REQUIRED** |
| `run.py` | Development server runner | **REQUIRED** |

### ✅ ROUTES (Keep These - API Endpoints)

| File | Purpose | Status |
|------|---------|--------|
| `routes/auth.py` | Login, register, OTP | **REQUIRED** |
| `routes/admission.py` | Programs listing, applications | **REQUIRED** |
| `routes/admin.py` | Admin dashboard stats | **REQUIRED** |
| `routes/finalist.py` | Finalist portal | **REQUIRED** |
| `routes/career.py` | Career paths, jobs | **REQUIRED** |
| `routes/opportunities.py` | Job opportunities | **REQUIRED** |
| `routes/reports.py` | Admin reports | **REQUIRED** |
| `routes/users.py` | User management | **REQUIRED** |
| `routes/docs.py` | API documentation | Optional (can keep) |
| `routes/notifications.py` | Email notifications | **REQUIRED** |
| `routes/__init__.py` | Route package init | **REQUIRED** |

### ✅ SERVICES (Keep These - Business Logic)

| File | Purpose | Status |
|------|---------|--------|
| `services/email_service.py` | Send emails | **REQUIRED** |
| `services/otp_service.py` | OTP generation/verification | **REQUIRED** |
| `services/qualification_service.py` | UNEB qualification logic | **REQUIRED** |
| `services/notification_service.py` | Notification queue | **REQUIRED** |

### ✅ CONFIG (Keep These - Settings)

| File | Purpose | Status |
|------|---------|--------|
| `config_modules/app_config.py` | App settings | **REQUIRED** |
| `config_modules/database_config.py` | DB configuration | **REQUIRED** |
| `config_modules/email_config.py` | Email settings | **REQUIRED** |
| `config_modules/redis_config.py` | Redis/caching config | **REQUIRED** |
| `config_modules/__init__.py` | Package init | **REQUIRED** |

### ✅ DATA (Keep These - Seed Data)

| File | Purpose | Status |
|------|---------|--------|
| `data/seed-programs.json` | 288 programs (main seed) | **REQUIRED** |
| `data/seed-career-paths.json` | Career paths data | **REQUIRED** |
| `data/seed-opportunities.json` | Job opportunities data | **REQUIRED** |
| `data/all_programs.py` | Program loader (restored) | **REQUIRED** |
| `data/__init__.py` | Package init | **REQUIRED** |

### ✅ TESTS (Keep These)

| File | Purpose | Status |
|------|---------|--------|
| `tests/test_core_functionality.py` | 11 core tests | **REQUIRED** |
| `tests/test_comprehensive.py` | 23 comprehensive tests | **REQUIRED** |
| `tests/conftest.py` | Test fixtures | **REQUIRED** |

### ⚠️ CAN BE REMOVED (Not Needed)

| File | Purpose | Action |
|------|---------|--------|
| `full_test.py` | Old test runner | **DELETE** |
| `metrics.py` | Prometheus metrics (unused) | **DELETE** |
| `run_tests.py` | Test runner (unused) | **DELETE** |
| `data/bachelors_programs.py` | Duplicate data | **DELETE** |
| `data/certificate_programs.py` | Duplicate data | **DELETE** |
| `data/diploma_programs.py` | Duplicate data | **DELETE** |
| `data/hec_programs.py` | Duplicate data | **DELETE** |
| `data/kiu_programs.py` | Duplicate data | **DELETE** |
| `data/missing_programs_report.json` | Old report | **DELETE** |
| `routes/audit.py` | Audit logging (unused) | **DELETE** |
| `routes/bulk_operations.py` | Bulk operations (unused) | **DELETE** |
| `routes/certificate_verification.py` | Cert verification (unused) | **DELETE** |
| `routes/nche_recommendations.py` | NCHE recommendations (unused) | **DELETE** |
| `routes/recommendations_v2.py` | Recommendations (needs fix) | **DELETE or FIX** |
| `scripts/create_admin.py` | Admin creation script | Optional |
| `scripts/migrate_db.py` | DB migration script | Optional |
| `scripts/reset_password.py` | Password reset script | Optional |
| `scripts/seed_all_programs.py` | Old seed script | **DELETE** |
| `scripts/seed_programs.py` | Old seed script | **DELETE** |
| `services/certificate_verification.py` | Unused service | **DELETE** |
| `services/opportunity_matching_service.py` | Unused service | **DELETE** |
| `services/reporting_service.py` | Unused service | **DELETE** |
| `lib/qualification_checker.py` | Duplicate logic | **DELETE** |
| `tests/test_health.py` | Redundant tests | **DELETE** |
| `tests/locustfile.py` | Load testing (unused) | **DELETE** |
| `tests/README_TESTS.md` | Old test docs | **DELETE** |
| `gunicorn.conf.py` | Gunicorn config (unused) | **DELETE** |
| `static/openapi.yaml` | API docs (unused) | **DELETE** |

### 📊 SUMMARY

**Total Files: ~65**
- **Keep: ~35 files** (Required for app to function)
- **Can Delete: ~30 files** (Duplicates, unused, old scripts)

**Clean Structure After Removal:**
```
flask-api/
├── app.py, models.py, seed.py, config.py
├── routes/ (11 files)
├── services/ (4 files)
├── config_modules/ (5 files)
├── data/ (5 files)
├── tests/ (3 files)
├── utils/ (helpers)
└── requirements.txt
```

## Finalist Logout Issue

The finalist page logout issue is likely due to:

1. **JWT token expiration (8 hours)** - Should be fine for normal use
2. **Missing refresh token logic** - Frontend should auto-refresh
3. **Cookie vs Header mismatch** - Check if frontend sends token correctly

**Quick fix to try:**
- Clear browser cookies for localhost
- Login again and check if token persists
- Check browser dev tools Network tab for Authorization header

## Recommendation

**Option A - Conservative:**
- Keep all files, just don't use the unused ones
- Risk: Cluttered codebase

**Option B - Aggressive Cleanup:**
- Delete all 30 "Can Be Removed" files
- Risk: Might delete something needed later

**My Recommendation:** Do Option B with backup - all files are in git history if needed.
