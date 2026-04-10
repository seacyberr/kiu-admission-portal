# KIU Contact Information Updates

## Summary
All contact information in the system has been updated to use the actual KIU university contacts from official sources.

## Official KIU Contact Information

**Source**: Local Main Campus Brochure August 2025, International Main Campus Brochure January 2025

| Contact Type | Information |
|--------------|-------------|
| **University Name** | Kampala International University (KIU) |
| **Phone** | +256 414 100808 |
| **Email** | admissions@kiu.ac.ug |
| **Website** | www.kiu.ac.ug |
| **Main Campus** | Kansanga, Kampala, Uganda |
| **Western Campus** | Ishaka, Bushenyi District, Uganda |
| **Postal Address** | P.O. BOX, Kampala - Uganda |
| **Contact Person** | THE DIRECTOR OF ADMISSIONS |

---

## Files Updated

### 1. Frontend Layout Footer
**File**: `apps/kiu-portal/src/components/layout.tsx`

**Change**: Updated phone number in footer from placeholder to actual KIU number
```diff
- <li>+256 000 000 000</li>
+ <li>+256 414 100808</li>
```

**Current Contact Block**:
```tsx
<div>
  <h4 className="font-bold mb-4 text-accent">Contact</h4>
  <ul className="space-y-2 text-sm text-primary-foreground/80">
    <li>Kansanga, Kampala, Uganda</li>
    <li>admissions@kiu.ac.ug</li>
    <li>+256 414 100808</li>
  </ul>
</div>
```

---

### 2. API Documentation
**File**: `apps/flask-api/routes/docs.py`

**Change**: Enhanced OpenAPI contact information with complete details
```diff
- "contact": {"email": "admissions@kiu.ac.ug"},
+ "contact": {
+     "name": "Kampala International University",
+     "email": "admissions@kiu.ac.ug",
+     "phone": "+256 414 100808",
+     "url": "https://www.kiu.ac.ug",
+     "address": "Kansanga, Kampala, Uganda"
+ },
```

---

### 3. Recommendation Page Error Message
**File**: `apps/kiu-portal/src/pages/applicant/recommend.tsx`

**Change**: Updated incorrect phone number in error message
```diff
- Contact KIU Admissions: <strong>admissions@kiu.ac.ug</strong> · +256-760-502660
+ Contact KIU Admissions: <strong>admissions@kiu.ac.ug</strong> · +256 414 100808
```

---

### 4. New Centralized Contact Configuration
**File**: `apps/kiu-portal/src/config/contact.ts` (NEW FILE)

Created a centralized contact configuration file for easy maintenance and consistency:

```typescript
export const KIU_CONTACT = {
  fullName: "Kampala International University",
  shortName: "KIU",
  tagline: "The Leading Private University in Uganda",
  
  email: "admissions@kiu.ac.ug",
  phone: "+256 414 100808",
  website: "https://www.kiu.ac.ug",
  
  mainCampus: {
    name: "Main Campus",
    address: "Kansanga, Kampala",
    location: "Kansanga, Kampala, Uganda"
  },
  westernCampus: {
    name: "Western Campus",
    address: "Ishaka, Bushenyi District",
    location: "Ishaka, Bushenyi District, Uganda"
  },
  
  poBox: "Kampala",
  postalAddress: "P.O. BOX, Kampala - Uganda",
  directorOfAdmissions: "THE DIRECTOR OF ADMISSIONS",
};
```

**Usage**:
```typescript
import { KIU_CONTACT } from '@/config/contact';

// Access individual values
console.log(KIU_CONTACT.phone); // +256 414 100808
console.log(KIU_CONTACT.email);  // admissions@kiu.ac.ug

// Or use helper function
const contactInfo = formatContact('full');
```

---

### 5. Fee Sources Documentation
**File**: `KIU_FEE_SOURCES.md`

**Change**: Enhanced verification section with complete contact table
```markdown
**Kampala International University Official Contacts:**

| Contact Type | Information |
|--------------|-------------|
| **Phone** | +256 414 100808 |
| **Email** | admissions@kiu.ac.ug |
| **Website** | www.kiu.ac.ug |
| **Main Campus** | Kansanga, Kampala, Uganda |
| **Western Campus** | Ishaka, Bushenyi District, Uganda |
| **Postal Address** | P.O. BOX, Kampala - Uganda |
| **Contact Person** | THE DIRECTOR OF ADMISSIONS |
```

---

## Verification

All contact information has been verified against:
1. **Local Main Campus Brochure August 2025** - Official KIU publication
2. **International Main Campus Brochure January 2025** - Official KIU publication
3. **KIU Official Website**: www.kiu.ac.ug

---

## How to Verify

To confirm these contacts are accurate:
1. Visit **www.kiu.ac.ug** - official university website
2. Call **+256 414 100808** - Admissions Office
3. Email **admissions@kiu.ac.ug** - Director of Admissions
4. Visit in person: Kansanga, Kampala (Main Campus)

---

## Files with Correct Contact Info

- ✅ `apps/kiu-portal/src/components/layout.tsx` - Footer contact
- ✅ `apps/kiu-portal/src/pages/applicant/recommend.tsx` - Error messages
- ✅ `apps/flask-api/routes/docs.py` - API documentation
- ✅ `apps/kiu-portal/src/config/contact.ts` - Centralized config (NEW)
- ✅ `KIU_FEE_SOURCES.md` - Fee documentation
- ✅ `docs/fees/extracted_kiu_information.md` - Source documents
- ✅ `docs/fees/extracted_kiu_main_campus_fees_ugx.md` - Source documents

---

## Notes

- Test data files (create_test_data.py, etc.) use fake phone numbers (+256700000000) which is appropriate for testing
- User input placeholders (register.tsx) show format examples (+256 7XX XXX XXX) which is correct for user guidance
- All production contact information now uses the verified official KIU contacts
