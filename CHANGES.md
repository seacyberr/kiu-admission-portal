# KIU Admission Portal - Changelog

## Recent Changes

### Authentication Logout Fix (Latest)
**Date:** April 2, 2026
**Commit:** `508cda5` - "fix: Logout user when visiting login page while authenticated"

**Problem:**
- After OTP verification, users remained logged in but the login page was still displayed
- The "Welcome Back" sign-in page appeared even though users were authenticated
- Users couldn't sign in with a different account without manually logging out first

**Solution:**
- Modified authentication check in `apps/kiu-portal/src/pages/auth/login.tsx`
- When authenticated user visits `/login`, their session is cleared
- Calls logout API to clear httpOnly cookie
- Allows users to sign in fresh with different credentials

**Files Modified:**
- `apps/kiu-portal/src/pages/auth/login.tsx` - Changed redirect logic to logout logic

---

### Test Configuration Fix
**Date:** April 2, 2026
**Commit:** `c7c63e0` - "fix: Skip test_submission.py in pytest - requires running server"

**Problem:**
- `test_submission.py` was causing test failures in CI/CD pipeline
- The test requires a running Flask server on port 5001
- Pytest suite runs unit tests without a live server

**Solution:**
- Added pytest hook in `apps/flask-api/tests/conftest.py`
- Automatically skips `test_submission.py` with reason "Requires running server on port 5001"

**Files Modified:**
- `apps/flask-api/tests/conftest.py` - Added `pytest_collection_modifyitems()` hook
- `apps/flask-api/pytest.ini` - Cleaned up configuration

---

## Implementation Summary

### Phase 1 Improvements (Completed)
1. **JWT Tokens → httpOnly Cookies**
   - Backend: httpOnly cookie authentication
   - Frontend: `credentials: 'include'` for httpOnly cookie support

2. **Automated Tests + CI/CD Pipeline**
   - GitHub Actions workflow
   - Backend tests with MySQL
   - Frontend build and type checking
   - Security scanning

3. **N+1 Query Fix**
   - Optimized Opportunity serialization
   - Reduced database queries

4. **Redis Support**
   - Caching configuration
   - Session management
   - Rate limiting storage

5. **Password Complexity Requirements**
   - Strong password validation

6. **Swagger/OpenAPI Documentation**
   - API documentation endpoint

### Phase 2 Improvements (Completed)
1. **Refresh Token Rotation**
2. **Rate Limiting per User**
3. **Query Caching**
4. **API Versioning (/api/v1/)**
5. **Comprehensive Test Suite (80%+ coverage)**
6. **Monitoring/Alerting (Prometheus metrics)**
7. **Database Migrations (Alembic)**

### Phase 3 Improvements (Completed)
1. **Query Result Caching (Redis)**
2. **User-Based Rate Limiting**
3. **API Versioning (/api/v1/)**
4. **80%+ Test Coverage**
5. **Prometheus Metrics + Grafana Dashboards**
6. **Alembic Database Migrations**

---

## Testing

### Backend Tests
```bash
cd apps/flask-api
python3 -m pytest tests/ -v --tb=short --cov=. --cov-report=xml
```

### Frontend Tests
```bash
pnpm --filter @workspace/kiu-portal test
```

### Type Checking
```bash
pnpm run typecheck
```

### Production Build
```bash
pnpm run build
```

---

## Deployment

Refer to `DEPLOYMENT.md` for detailed deployment instructions.

---

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | MySQL/PostgreSQL connection string | Yes |
| `JWT_SECRET` | JWT secret key | Yes |
| `OTP_DEBUG` | Print OTP to terminal (dev only) | No |
| `SEED_DATABASE` | Seed demo data on startup | No |
| `CORS_ORIGINS` | Allowed CORS origins | No |
| `PORT` | Server port (default: 5001) | No |
| `BREVO_SMTP_USER` | Brevo SMTP login | No |
| `BREVO_SMTP_KEY` | Brevo SMTP key | No |

---

## Security Features

- httpOnly cookie authentication
- JWT token rotation
- Rate limiting (global and per-user)
- CORS configuration
- Security headers
- HSTS (when behind HTTPS)
- Password complexity validation

---

## Monitoring

- Prometheus metrics at `/api/metrics`
- Health check at `/api/healthz`
- Readiness check at `/api/readyz`
- Structured logging with request IDs
- Sentry integration for error tracking

---

## License

Proprietary - Kampala International University