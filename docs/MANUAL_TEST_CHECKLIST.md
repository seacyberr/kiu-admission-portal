# Manual Testing Checklist - KIU Admission Portal

## 🔴 Critical Workflows to Test

### 1. Authentication Flow
- [ ] User Registration
  - Visit: `/register`
  - Fill: email, phone, password
  - Submit → Should redirect to `/verify-otp`
  
- [ ] OTP Verification
  - Enter OTP sent to email
  - Submit → Should redirect to `/dashboard`
  
- [ ] Login
  - Visit: `/login`
  - Enter credentials
  - Submit → Should redirect to role-based dashboard
  
- [ ] Password Reset
  - Visit: `/forgot-password`
  - Enter email
  - Check email for reset link
  - Use link → redirect to `/reset-password`
  - Set new password

### 2. Application Workflow (Applicant)
- [ ] Start New Application
  - Login as applicant
  - Visit: `/apply`
  - Select education level
  - Fill personal info
  - Upload documents
  - Submit → Should create application
  
- [ ] NCHE Recommendation
  - Visit: `/nche-recommend`
  - Enter UCE/UACE results
  - Select curriculum (Old/New)
  - Submit → Should show eligible programs
  
- [ ] Direct Application Forms
  - `/apply/degree` - Bachelor's application
  - `/apply/diploma` - Diploma application
  - `/apply/masters` - Master's application
  - `/apply/phd` - PhD application
  - Each should load correct form

### 3. Admin Workflow
- [ ] Admin Login
  - Login with admin credentials
  - Should redirect to `/admin/dashboard`
  
- [ ] View Applications
  - Visit: `/admin/admissions`
  - Should list all applications
  - Should allow filtering by status
  
- [ ] Manage Opportunities
  - Visit: `/admin/opportunities`
  - Should CRUD operations work

### 4. Finalist Workflow
- [ ] Finalist Dashboard
  - Login as finalist
  - Visit: `/finalist/dashboard`
  - Should show career paths
  
- [ ] Career Paths
  - Visit: `/finalist/career-paths`
  - Should show available opportunities

### 5. API Endpoints (Backend)
Test these directly:
```bash
# Health check
curl http://127.0.0.1:5001/api/health

# Auth
curl -X POST http://127.0.0.1:5001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123","first_name":"Test","last_name":"User"}'

# Get programs
curl http://127.0.0.1:5001/api/programs

# NCHE recommend
curl -X POST http://127.0.0.1:5001/api/nche/recommend \
  -H "Content-Type: application/json" \
  -d '{"qualification":"uace","subjects":[{"name":"Mathematics","grade":"A"}]}'
```

## 🔍 Common Failure Points

| Feature | Common Issue | Solution |
|---------|--------------|----------|
| Registration | Email not sending | Check Brevo SMTP credentials |
| OTP | Not received | Check spam folder / SMTP config |
| File Upload | Files not saving | Check upload directory permissions |
| Form Submit | Validation errors | Check required fields |
| Payments | Transaction fails | Check payment gateway config |
| NCHE Recommend | No programs shown | Check UACE/UACE subject lists |
| Login | "Invalid credentials" | Check password hashing |
| Dashboard | Blank page | Check API response / React errors |

## 🧪 Quick Diagnostic Commands

```bash
# 1. Check backend running
curl http://127.0.0.1:5001/api/health

# 2. Check database connection
python3 -c "from app import create_app; from models import db; app = create_app(); print('DB OK')"

# 3. Check Redis
curl http://127.0.0.1:5001/api/health

# 4. Test registration via API
curl -X POST http://127.0.0.1:5001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"diag@test.com","password":"Test123!","first_name":"Diag","last_name":"Test","phone":"+256700000001"}'

# 5. Check frontend build
npm run build 2>&1 | grep -i error
```

## 🚨 Report Issues

When reporting a failure, include:
1. **URL**: Which page/feature
2. **Steps**: What you did
3. **Expected**: What should happen
4. **Actual**: What actually happened
5. **Error**: Browser console / Network tab / Terminal output
