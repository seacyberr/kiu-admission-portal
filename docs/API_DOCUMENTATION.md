# KIU Admission Portal API Documentation

## Overview

The KIU Admission Portal API provides endpoints for student applications, program recommendations, certificate verification, and administrative functions. This document covers all available endpoints, authentication requirements, request/response formats, and error handling.

## Base URL

```
Production: https://api.kiu.ac.ug
Development: http://localhost:5000
```

## Authentication

The API uses JWT tokens for authentication. Include the token in either:

- **Cookie**: `auth_token` (automatically handled by frontend)
- **Header**: `Authorization: Bearer <token>`

### Token Lifetimes

- **Access Token**: 8 hours
- **Refresh Token**: 7 days

## Rate Limiting

The API implements intelligent rate limiting based on endpoint and user role:

| Endpoint Type | Requests per Window | Window | Admin Multiplier |
|---------------|-------------------|---------|------------------|
| Authentication | 5 requests | 5 minutes | 2x |
| Applications | 3 requests | 1 hour | 2x |
| Recommendations | 20 requests | 5 minutes | 2x |
| Certificate Verification | 5 requests | 5 minutes | 2x |
| General | 50 requests | 5 minutes | 2x |

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Unix timestamp when limit resets
- `Retry-After`: Seconds to wait when rate limited

## Response Format

All API responses follow this structure:

### Success Response
```json
{
  "data": { ... },
  "message": "Operation successful",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Error Response
```json
{
  "error": "ERROR_CODE",
  "message": "Human-readable error message",
  "details": {
    "field": "validation_error",
    "value": "invalid_value"
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## Error Codes

| Code | Description | HTTP Status |
|-------|-------------|-------------|
| `VALIDATION_ERROR` | Invalid input data | 400 |
| `UNAUTHORIZED` | Authentication required | 401 |
| `FORBIDDEN` | Access denied | 403 |
| `NOT_FOUND` | Resource not found | 404 |
| `CONFLICT` | Resource already exists | 409 |
| `RATE_LIMIT_EXCEEDED` | Too many requests | 429 |
| `INTERNAL_ERROR` | Server error | 500 |

---

## Endpoints

### Authentication

#### Register User
```http
POST /api/auth/register
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123",
  "firstName": "John",
  "lastName": "Doe",
  "phone": "+256700000000",
  "role": "applicant"
}
```

**Response:**
```json
{
  "message": "Registration successful. Please check your email for verification.",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "role": "applicant",
    "isVerified": false
  }
}
```

#### Login
```http
POST /api/auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response:**
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "role": "applicant",
    "isVerified": true
  },
  "accessToken": "jwt_token_here",
  "refreshToken": "refresh_token_here"
}
```

#### Refresh Token
```http
POST /api/auth/refresh
```

**Request Body:**
```json
{
  "refreshToken": "refresh_token_here"
}
```

#### Logout
```http
POST /api/auth/logout
```

#### Verify Email
```http
POST /api/auth/verify-email
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "otp": "123456"
}
```

#### Request OTP
```http
POST /api/auth/request-otp
```

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

---

### Programs

#### List Programs
```http
GET /api/programs
```

**Query Parameters:**
- `campus` (optional): Filter by campus
- `level` (optional): Filter by program level
- `page` (optional): Page number (default: 1)
- `perPage` (optional): Items per page (default: 20, max: 100)

**Response:**
```json
{
  "programs": [
    {
      "id": "uuid",
      "code": "BCS",
      "name": "Bachelor of Computer Science",
      "level": "degree",
      "campus": "main",
      "duration": 3,
      "minOlevelPoints": 24,
      "minAlevelPoints": 12,
      "description": "Program description...",
      "requirements": {
        "subjects": ["Mathematics", "Physics"],
        "grades": {"Mathematics": "C", "Physics": "C"}
      }
    }
  ],
  "pagination": {
    "page": 1,
    "perPage": 20,
    "total": 150,
    "pages": 8
  }
}
```

#### Get Program Details
```http
GET /api/programs/{program_id}
```

---

### Applications

#### Create Application
```http
POST /api/admission/applications
```

**Request Body:**
```json
{
  "programIds": ["uuid1", "uuid2"],
  "examLevel": "a_level",
  "examYear": 2023,
  "indexNumber": "U1234/567",
  "unebGrades": {
    "olevel": [
      {
        "subject": "Mathematics",
        "grade": "D2",
        "points": 2
      }
    ],
    "alevel": [
      {
        "subject": "Mathematics",
        "grade": "A",
        "points": 6,
        "subjectType": "principal"
      }
    ]
  },
  "dateOfBirth": "2000-01-01",
  "gender": "male",
  "nationality": "Ugandan",
  "district": "Kampala",
  "personalStatement": "I want to study...",
  "nextOfKinName": "Jane Doe",
  "nextOfKinPhone": "+256700000001",
  "nextOfKinRelationship": "parent"
}
```

**Response:**
```json
{
  "id": "uuid",
  "applicationNumber": "APP2024001",
  "status": "pending",
  "createdAt": "2024-01-01T12:00:00Z",
  "program": {
    "id": "uuid",
    "name": "Bachelor of Computer Science"
  }
}
```

#### Get My Application
```http
GET /api/admission/applications/mine
```

#### Get Application Details
```http
GET /api/admission/applications/{application_id}
```

#### List Applications (Admin)
```http
GET /api/admission/applications
```

**Query Parameters:**
- `status` (optional): Filter by status
- `search` (optional): Search term
- `page` (optional): Page number
- `perPage` (optional): Items per page

#### Update Application Status (Admin)
```http
PATCH /api/admission/applications/{application_id}/status
```

**Request Body:**
```json
{
  "status": "accepted",
  "programId": "uuid",
  "adminNotes": "Strong academic background"
}
```

#### Upload Certificate
```http
POST /api/admission/applications/{application_id}/certificate
```

**Request (multipart/form-data):**
- `file`: Certificate file (PDF, JPG, JPEG, PNG)
- `type`: Certificate type (`olevel`, `alevel`, `diploma`, `hec`)

**Response:**
```json
{
  "message": "Certificate uploaded successfully",
  "path": "/api/uploads/certificates/filename.pdf"
}
```

---

### Recommendations

#### Get Program Recommendations
```http
POST /api/admission/recommend
```

**Request Body:**
```json
{
  "alevelSubjects": [
    {
      "subject": "Mathematics",
      "grade": "A",
      "subjectType": "principal"
    },
    {
      "subject": "Physics",
      "grade": "B",
      "subjectType": "principal"
    },
    {
      "subject": "Chemistry",
      "grade": "C",
      "subjectType": "principal"
    }
  ],
  "campus": "main"
}
```

**Response:**
```json
{
  "recommendations": [
    {
      "program": {
        "id": "uuid",
        "name": "Bachelor of Computer Science",
        "code": "BCS"
      },
      "matchScore": 95,
      "matchReason": "Strong match in Mathematics and Physics",
      "eligibility": "eligible"
    }
  ],
  "ncheCompliance": {
    "compliant": true,
    "issues": []
  }
}
```

#### Get Eligibility Check
```http
POST /api/admission/eligibility
```

---

### Certificate Verification

#### Verify Certificate
```http
POST /api/certificate-verification/verify
```

**Request Body:**
```json
{
  "certificateType": "uce",
  "indexNumber": "U1234/567",
  "year": 2023,
  "school": "Example Secondary School"
}
```

**Response:**
```json
{
  "verificationId": "uuid",
  "status": "pending",
  "message": "Certificate verification initiated"
}
```

#### Verify with OCR Data
```http
POST /api/certificate-verification/verify-with-data
```

**Request Body:**
```json
{
  "certificateType": "uce",
  "ocrData": {
    "extractedText": "...",
    "subjects": ["Mathematics", "English"],
    "grades": ["D2", "C3"]
  },
  "indexNumber": "U1234/567",
  "year": 2023
}
```

#### Get Verification Status
```http
GET /api/certificate-verification/{verification_id}/status
```

#### Get NCHE Standards
```http
GET /api/certificate-verification/nche-standards
```

---

### File Uploads

#### Serve Certificate Files
```http
GET /api/uploads/certificates/{filename}
```

**Authorization**: Only file owner or admin can access

---

## Data Models

### User
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "firstName": "John",
  "lastName": "Doe",
  "phone": "+256700000000",
  "role": "applicant|admin|staff",
  "isVerified": true,
  "createdAt": "2024-01-01T12:00:00Z",
  "updatedAt": "2024-01-01T12:00:00Z"
}
```

### Program
```json
{
  "id": "uuid",
  "code": "BCS",
  "name": "Bachelor of Computer Science",
  "level": "degree|masters|phd",
  "campus": "main|kampala|mbale",
  "duration": 3,
  "minOlevelPoints": 24,
  "minAlevelPoints": 12,
  "description": "Program description...",
  "isActive": true,
  "createdAt": "2024-01-01T12:00:00Z",
  "updatedAt": "2024-01-01T12:00:00Z"
}
```

### Application
```json
{
  "id": "uuid",
  "applicationNumber": "APP2024001",
  "userId": "uuid",
  "programId": "uuid",
  "programChoices": ["uuid1", "uuid2"],
  "examLevel": "a_level|o_level|diploma|hec",
  "examYear": 2023,
  "indexNumber": "U1234/567",
  "unebGrades": { ... },
  "dateOfBirth": "2000-01-01",
  "gender": "male|female",
  "nationality": "Ugandan",
  "district": "Kampala",
  "personalStatement": "I want to study...",
  "status": "pending|under_review|accepted|rejected|waitlisted",
  "adminNotes": "",
  "olevelCertificatePath": "/api/uploads/certificates/...",
  "alevelCertificatePath": "/api/uploads/certificates/...",
  "createdAt": "2024-01-01T12:00:00Z",
  "updatedAt": "2024-01-01T12:00:00Z"
}
```

## Validation Rules

### Email
- Must be valid email format
- Maximum 255 characters

### Phone Number
- Must start with country code (+256 for Uganda)
- 9-15 digits after country code

### Password
- Minimum 8 characters
- Must contain at least one uppercase letter
- Must contain at least one lowercase letter
- Must contain at least one number

### UNEB Grades

#### O-Level (UCE)
**Old Curriculum:** D1, D2, C3, C4, C5, C6, P7, P8, F9
**New Curriculum:** D1, D2, D3, D4, D5, D6, D7, D8, F

#### A-Level (UACE)
**Principal Subjects:** A, B, C, D, E, O, F
**Subsidiary Subjects:** 1, 2, 3, 4, 5, 6, 7, 8, 9

### File Uploads
- **Allowed formats:** PDF, JPG, JPEG, PNG
- **Maximum size:** 5MB per file
- **File naming:** Secure filename generation

## Error Handling

### Validation Errors
```json
{
  "error": "VALIDATION_ERROR",
  "message": "Invalid input data",
  "details": {
    "field": "email",
    "value": "invalid-email",
    "reason": "Invalid email format"
  }
}
```

### Rate Limit Errors
```json
{
  "error": "RATE_LIMIT_EXCEEDED",
  "message": "Too many requests. Please try again later.",
  "details": {
    "limit": 5,
    "remaining": 0,
    "reset": 1704067200,
    "retryAfter": 300
  }
}
```

### Server Errors
```json
{
  "error": "INTERNAL_ERROR",
  "message": "An unexpected error occurred",
  "details": {
    "requestId": "uuid",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

## Caching

The API implements intelligent caching for frequently accessed data:

| Data Type | Cache Duration | Invalidation Trigger |
|------------|----------------|-------------------|
| Programs | 1 hour | Program update |
| User Data | 30 minutes | User profile change |
| Recommendations | 10 minutes | New recommendation request |
| Application Status | 5 minutes | Status update |
| NCHE Standards | 2 hours | Standards update |

Cache headers are included in responses:
- `X-Cache`: `HIT` or `MISS`
- `X-Cache-Key`: Cache key used
- `X-Cache-TTL`: Remaining TTL in seconds

## Security

### CORS
- Allowed origins configured per environment
- Supports preflight requests

### Security Headers
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security` (HTTPS only)

### Input Sanitization
- All text inputs are sanitized
- HTML tags removed
- JavaScript event handlers removed
- SQL injection protection

## Testing

### Environment Variables
```bash
FLASK_ENV=development
TEST_DATABASE_URL=sqlite:///test.db
REDIS_URL=redis://localhost:6379/1
```

### Test Endpoints
```bash
# Health check
GET /api/health

# Test authentication
POST /api/auth/test-login

# Database status
GET /api/health/db
```

## SDK Integration

### JavaScript/TypeScript
```typescript
import { KIUApiClient } from '@workspace/api-client-react';

const client = new KIUApiClient({
  baseURL: 'https://api.kiu.ac.ug',
  timeout: 10000
});

// Login
const user = await client.auth.login({
  email: 'user@example.com',
  password: 'password'
});

// Get programs
const programs = await client.programs.list({
  campus: 'main',
  level: 'degree'
});

// Submit application
const application = await client.applications.create({
  programIds: ['uuid'],
  examLevel: 'a_level',
  // ... other fields
});
```

### Python
```python
import requests

class KIUAPIClient:
    def __init__(self, base_url, token=None):
        self.base_url = base_url
        self.token = token
        self.session = requests.Session()
        
    def login(self, email, password):
        response = self.session.post(
            f"{self.base_url}/api/auth/login",
            json={"email": email, "password": password}
        )
        data = response.json()
        self.token = data['accessToken']
        self.session.headers.update({
            'Authorization': f'Bearer {self.token}'
        })
        return data['user']
    
    def get_programs(self, **params):
        response = self.session.get(
            f"{self.base_url}/api/programs",
            params=params
        )
        return response.json()
```

## Changelog

### v2.0.0 (Current)
- Added comprehensive rate limiting
- Implemented caching system
- Enhanced error handling
- Added certificate verification
- Improved validation

### v1.0.0
- Initial API release
- Basic authentication
- Application submission
- Program listing

## Support

For API support and questions:
- **Email**: api-support@kiu.ac.ug
- **Documentation**: https://docs.kiu.ac.ug/api
- **Status Page**: https://status.kiu.ac.ug

## License

© 2024 Kampala International University. All rights reserved.
