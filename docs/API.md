# KIU Admission Portal - API Documentation

## Overview

The KIU Admission Portal API provides comprehensive endpoints for student applications, authentication, programme management, and career services for Kampala International University.

## Base URL

```
Production: https://api.kiu.ac.ug
Development: http://localhost:5001
```

## Authentication

All API endpoints require JWT authentication except public endpoints.

### Authentication Flow

1. **Login**: POST `/api/auth/login`
2. **Access Token**: Include `Authorization: Bearer <token>` header
3. **Refresh**: POST `/api/auth/refresh`
4. **Logout**: POST `/api/auth/logout`

## API Endpoints

### Authentication Endpoints

#### POST `/api/auth/login`
Authenticate user and return JWT tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "refresh_token_here",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "role": "applicant"
  }
}
```

#### POST `/api/auth/refresh`
Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "refresh_token_here"
}
```

#### POST `/api/auth/logout`
Logout user and invalidate tokens.

**Headers:** `Authorization: Bearer <access_token>`

#### POST `/api/auth/register`
Register new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+256123456789"
}
```

### User Management

#### GET `/api/users/profile`
Get current user profile.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+256123456789",
  "role": "applicant"
}
```

#### PUT `/api/users/profile`
Update user profile.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+256123456789"
}
```

### Programme Management

#### GET `/api/programs`
List all available KIU programmes.

**Query Parameters:**
- `level`: Filter by programme level (bachelor, diploma, masters, phd)
- `faculty`: Filter by faculty
- `page`: Page number for pagination
- `limit`: Items per page

**Response:**
```json
{
  "programs": [
    {
      "id": 1,
      "name": "Bachelor of Computer Science",
      "code": "BCS",
      "level": "bachelor",
      "faculty": "Science & Technology",
      "duration": "4 years",
      "description": "Comprehensive computer science program..."
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 45
  }
}
```

#### GET `/api/programs/{id}`
Get specific programme details.

**Response:**
```json
{
  "id": 1,
  "name": "Bachelor of Computer Science",
  "code": "BCS",
  "level": "bachelor",
  "faculty": "Science & Technology",
  "duration": "4 years",
  "description": "Comprehensive computer science program...",
  "entry_requirements": {
    "olevel_points": 24,
    "alevel_points": 12,
    "subjects": ["Mathematics", "Physics", "Chemistry"]
  },
  "career_paths": ["Software Development", "Data Science", "IT Management"]
}
```

### Admission Applications

#### POST `/api/admissions/apply`
Submit new admission application.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "program_id": 1,
  "application_type": "olevel",
  "personal_info": {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone": "+256123456789",
    "date_of_birth": "2000-01-01",
    "gender": "male",
    "nationality": "Ugandan"
  },
  "education": {
    "olevel_results": [
      {
        "subject": "Mathematics",
        "grade": "A",
        "points": 6
      }
    ],
    "alevel_results": [
      {
        "subject": "Mathematics",
        "grade": "B",
        "points": 4
      }
    ]
  },
  "documents": {
    "birth_certificate": "file_id_123",
    "olevel_certificate": "file_id_124"
  }
}
```

#### GET `/api/admissions/my-applications`
Get user's admission applications.

**Headers:** `Authorization: Bearer <token>`
**Query Parameters:** `status`, `page`, `limit`
**Response:** Applications list with pagination details

#### GET `/api/admissions/{id}`
Get specific application details.

**Headers:** `Authorization: Bearer <token>`

#### PUT `/api/admissions/{id}`
Update application details.

**Headers:** `Authorization: Bearer <token>`
**Request Body:** Application updates

### File Management

#### POST `/api/files/upload`
Upload supporting documents.

**Headers:** `Authorization: Bearer <token>`, `Content-Type: multipart/form-data`
**Request Body:** File data + document type
**Response:** File metadata with ID and download URL

#### GET `/api/files/{file_id}`
Download uploaded file.

**Headers:** `Authorization: Bearer <token>`

### Career Services

#### GET `/api/career/opportunities`
Get career opportunities.

**Query Parameters:** `program_level`, `industry`, `location`, `page`, `limit`
**Response:** Opportunities list with pagination

#### POST `/api/career/opportunities/{id}/apply`
Apply for career opportunity.

**Headers:** `Authorization: Bearer <token>`
**Request Body:** Cover letter, availability, salary expectations

### Notifications

#### GET `/api/notifications`
Get user notifications.

**Headers:** `Authorization: Bearer <token>`
**Query Parameters:** `read`, `type`, `page`, `limit`
**Response:** Notifications list with unread count

#### PUT `/api/notifications/{id}/read`
Mark notification as read.

**Headers:** `Authorization: Bearer <token>`

### Admin Endpoints

#### GET `/api/admin/applications`
Get all applications (admin only).

**Headers:** `Authorization: Bearer <admin_token>`
**Query Parameters:** `status`, `program_id`, `date_from`, `date_to`, `page`, `limit`

#### PUT `/api/admin/applications/{id}/status`
Update application status (admin only).

**Headers:** `Authorization: Bearer <admin_token>`
**Request Body:** Status updates and admin notes

#### GET `/api/admin/analytics`
Get admission analytics (admin only).

**Headers:** `Authorization: Bearer <admin_token>`
**Response:** Application statistics and analytics

## Error Responses

All endpoints return consistent error format with error codes and messages.

### Common Error Codes
- `VALIDATION_ERROR`: Invalid input data
- `AUTHENTICATION_REQUIRED`: No valid token provided
- `AUTHENTICATION_INVALID`: Token is invalid or expired
- `AUTHORIZATION_DENIED`: User lacks permission
- `RESOURCE_NOT_FOUND`: Requested resource doesn't exist
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `SERVER_ERROR`: Internal server error

## Rate Limiting

- **Standard**: 100 requests per minute per user
- **File Upload**: 10 requests per minute
- **Admin Endpoints**: 200 requests per minute

## Data Models

### User Model
```json
{
  "id": "integer", "email": "string (unique)", "password_hash": "string",
  "first_name": "string", "last_name": "string", "phone": "string",
  "role": "enum (applicant, finalist, admin)",
  "created_at": "datetime", "updated_at": "datetime"
}
```

### Application Model
```json
{
  "id": "integer", "user_id": "integer (foreign key)",
  "program_id": "integer (foreign key)",
  "status": "enum (pending, under_review, accepted, rejected)",
  "application_data": "json",
  "submitted_at": "datetime", "updated_at": "datetime"
}
```

### Program Model
```json
{
  "id": "integer", "name": "string", "code": "string (unique)",
  "level": "enum (bachelor, diploma, masters, phd)",
  "faculty": "string", "duration": "string", "requirements": "json"
}
```

## Testing

### Authentication
```bash
# Test login
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}'

# Test protected endpoint
curl -X GET http://localhost:5001/api/users/profile \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### File Upload
```bash
# Upload file
curl -X POST http://localhost:5001/api/files/upload \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@document.pdf" \
  -F "document_type=birth_certificate"
```

## SDK/Client Libraries

### JavaScript/TypeScript
```bash
npm install @workspace/api-client-react
```

```typescript
import { useGetCurrentUser, useLogin } from '@workspace/api-client-react';

function MyComponent() {
  const { data: user, error } = useGetCurrentUser();
  const login = useLogin();
  
  return (
    <div>
      {user ? <p>Welcome, {user.first_name}!</p> : <button onClick={() => login({email: 'test@example.com', password: 'password'})}>Login</button>}
    </div>
  );
}
```

## WebSocket Events

Real-time updates via WebSocket connection for application status and notifications.

## Versioning

API version included in response headers: `API-Version: 1.0.0`

## Support

- **Technical Issues**: api-support@kiu.ac.ug
- **Documentation**: docs@kiu.ac.ug
- **Status Page**: https://status.kiu.ac.ug

---

*Last Updated: January 2024*
