# KIU Admission Portal - Test Plan

## ✅ Pre-Test Verification

### Backend Tests
- [x] Flask app starts without errors
- [x] Database connection works
- [x] All blueprints registered
- [x] 156 programs seeded in database

### Frontend Tests  
- [x] TypeScript compilation successful
- [x] Build completes without errors
- [x] All components render

---

## 🧪 Test Scenarios

### 1. NCHE Recommendation Engine

#### Test 1.1: UACE Recommendations
```
Steps:
1. Navigate to /nche-recommend
2. Select "UACE (A-Level)" qualification
3. Enter 3 principal subjects (e.g., Physics, Chemistry, Biology)
4. Enter grades (A, B, C)
5. Submit

Expected: Bachelor's degree programs recommended
```

#### Test 1.2: UCE Recommendations  
```
Steps:
1. Select "UCE (O-Level)" qualification
2. Enter division (1, 2, or 3)
3. Enter credits (5-9)
4. Submit

Expected: Certificate/Diploma programs only
```

#### Test 1.3: HEC Recommendations
```
Steps:
1. Select "HEC" qualification
2. Choose track (Arts/Physical/Biological)
3. Submit

Expected: Track-specific programs
```

---

### 2. Application Wizard

#### Test 2.1: Complete Application Flow
```
Steps:
1. Start new application
2. Fill Personal Details
3. Fill Contact Information
4. Select Education Background (UACE)
5. Upload Documents (passport photo, transcripts)
6. Select Program (Bachelor of Business Administration)
7. Pay Application Fee (UGX 50,000)
8. Submit

Expected: Application saved, confirmation shown
```

#### Test 2.2: Draft Save
```
Steps:
1. Start application
2. Fill personal details
3. Click "Save Draft"
4. Refresh page

Expected: Draft data persists
```

---

### 3. Admin Dashboard

#### Test 3.1: View Applications
```
Steps:
1. Login as admin
2. Navigate to /admin/admissions
3. View applications list

Expected: List shows all submitted applications
```

#### Test 3.2: Filter Applications
```
Steps:
1. Filter by status "Pending"
2. Filter by qualification "UACE"
3. Search by applicant name

Expected: Filters work correctly
```

#### Test 3.3: Export CSV
```
Steps:
1. Apply filters
2. Click "Export CSV"

Expected: CSV file downloads with correct data
```

#### Test 3.4: Approve Application
```
Steps:
1. Click on application
2. Click "Accept" button
3. Verify status changes to "accepted"

Expected: Status updated, toast notification shown
```

---

### 4. Payment Integration

#### Test 4.1: Mobile Money Payment (MTN)
```
Steps:
1. At payment step, select "MTN Mobile Money"
2. Enter phone: 256712345678
3. Click "Pay Now"

Expected: Payment request sent, success message shown
```

#### Test 4.2: Bank Transfer
```
Steps:
1. Select "Bank Transfer"
2. View account details
3. Note reference format
4. Submit transfer confirmation

Expected: Transfer recorded, pending verification
```

---

### 5. End-to-End Flows

#### Test 5.1: Full Admission Journey
```
Steps:
1. Student visits portal
2. Gets NCHE recommendations
3. Starts application
4. Saves draft
5. Completes and pays
6. Admin reviews and accepts
7. Student receives confirmation

Expected: Complete flow works end-to-end
```

---

## 🔍 Known Issues to Verify

### Critical
- [ ] Payment verification works correctly
- [ ] Document uploads persist
- [ ] Email notifications sent (if configured)

### Medium
- [ ] CSV export includes all fields
- [ ] Pagination works with >100 applications
- [ ] Search returns correct results

### Low
- [ ] UI responsive on mobile
- [ ] Loading states visible
- [ ] Error messages clear

---

## 📊 Test Results Summary

| Component | Tests Passed | Tests Failed | Status |
|-----------|--------------|--------------|--------|
| NCHE Engine | 0/3 | 0/3 | ⏳ Pending |
| Application Wizard | 0/2 | 0/2 | ⏳ Pending |
| Admin Dashboard | 0/4 | 0/4 | ⏳ Pending |
| Payment System | 0/2 | 0/2 | ⏳ Pending |
| E2E Flows | 0/1 | 0/1 | ⏳ Pending |

**Overall Status**: Ready for testing ⏳
