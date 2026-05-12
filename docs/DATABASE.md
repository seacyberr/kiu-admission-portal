# KIU Admission Portal - Database Schema Documentation

## Overview

The KIU Admission Portal uses MySQL 8.0 as its primary database, designed to handle student applications, user management, programme information, and career services for Kampala International University.

## Database Configuration

### Connection String Format
```
mysql+pymysql://username:password@host:port/database_name
```

### Environment Variables
```env
DATABASE_URL=mysql+pymysql://kiu_user:password@localhost:3306/kiu_portal
DB_HOST=localhost
DB_PORT=3306
DB_NAME=kiu_portal
DB_USER=kiu_user
DB_PASSWORD=secure_password
```

## Core Tables

### Users Table (`users`)

```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    role ENUM('applicant', 'finalist', 'admin') DEFAULT 'applicant',
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_role (role)
);
```

**Purpose**: Stores all user accounts for the KIU admission system.

**Fields**:
- `id`: Primary key
- `email`: Unique email address for login
- `password_hash`: Bcrypt-hashed password
- `first_name`, `last_name`: User's full name
- `phone`: Uganda phone number format
- `role`: User type (applicant/finalist/admin)
- `is_active`: Account status
- `email_verified`: Email verification status

### Programs Table (`programs`)

```sql
CREATE TABLE programs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(20) UNIQUE NOT NULL,
    level ENUM('bachelor', 'diploma', 'masters', 'phd') NOT NULL,
    faculty VARCHAR(100) NOT NULL,
    duration_years INT NOT NULL,
    description TEXT,
    entry_requirements JSON,
    career_paths JSON,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_code (code),
    INDEX idx_level (level),
    INDEX idx_faculty (faculty)
);
```

**Purpose**: Stores all KIU academic programmes.

**Fields**:
- `id`: Primary key
- `name`: Full programme name
- `code`: Unique programme code (e.g., "BCS", "MCS")
- `level`: Programme level
- `faculty`: Academic faculty
- `duration_years`: Programme duration
- `entry_requirements`: JSON with O/A-Level requirements
- `career_paths`: JSON with possible career paths
- `is_active`: Programme availability status

### Admission Applications Table (`admission_applications`)

```sql
CREATE TABLE admission_applications (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    program_id INT NOT NULL,
    application_type ENUM('olevel', 'alevel', 'diploma', 'hec', 'bachelor', 'masters') NOT NULL,
    status ENUM('pending', 'under_review', 'accepted', 'rejected', 'deferred') DEFAULT 'pending',
    personal_info JSON NOT NULL,
    education JSON NOT NULL,
    documents JSON,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (program_id) REFERENCES programs(id) ON DELETE CASCADE,
    INDEX idx_user (user_id),
    INDEX idx_program (program_id),
    INDEX idx_status (status)
);
```

**Purpose**: Stores all student applications to KIU programmes.

**Fields**:
- `id`: Primary key
- `user_id`: Reference to user table
- `program_id`: Reference to programs table
- `application_type`: Type of application (O-Level, A-Level, etc.)
- `status`: Current application status
- `personal_info`: JSON with personal details
- `education`: JSON with educational background
- `documents`: JSON with uploaded document references
- `submitted_at`, `updated_at`: Timestamps

### Finalist Profiles Table (`finalist_profiles`)

```sql
CREATE TABLE finalist_profiles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    student_number VARCHAR(20) UNIQUE,
    gpa DECIMAL(3,2),
    graduation_year INT,
    degree_class VARCHAR(20),
    specializations TEXT,
    interests TEXT,
    skills TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_student_number (student_number),
    INDEX idx_user (user_id)
);
```

**Purpose**: Stores KIU finalist student profiles for career services.

**Fields**:
- `id`: Primary key
- `user_id`: Reference to user table
- `student_number`: KIU student ID
- `gpa`: Grade point average
- `graduation_year`: Year of graduation
- `degree_class`: Classification (First Class, Second Class, etc.)
- `specializations`: Academic specializations
- `interests`: Career interests
- `skills`: Technical and soft skills

### Career Paths Table (`career_paths`)

```sql
CREATE TABLE career_paths (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    required_skills JSON,
    average_salary_range VARCHAR(100),
    growth_potential ENUM('low', 'medium', 'high'),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_name (name)
);
```

**Purpose**: Defines career progression paths for KIU students.

**Fields**:
- `id`: Primary key
- `name`: Career path name
- `description`: Path description
- `required_skills`: JSON with required skills
- `average_salary_range`: Expected salary range
- `growth_potential`: Career growth potential
- `is_active`: Path availability status

### Opportunities Table (`opportunities`)

```sql
CREATE TABLE opportunities (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    type ENUM('internship', 'fulltime', 'parttime', 'contract') DEFAULT 'fulltime',
    description TEXT,
    requirements JSON,
    deadline DATE,
    salary_range VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_type (type),
    INDEX idx_deadline (deadline)
);
```

**Purpose**: Stores career opportunities for KIU students and finalists.

**Fields**:
- `id`: Primary key
- `title`: Opportunity title
- `company`: Company name
- `location`: Geographic location
- `type`: Employment type
- `description`: Opportunity description
- `requirements`: JSON with required qualifications
- `deadline`: Application deadline
- `salary_range`: Expected salary range
- `is_active`: Opportunity availability status

### Opportunity Applications Table (`opportunity_applications`)

```sql
CREATE TABLE opportunity_applications (
    id INT PRIMARY KEY AUTO_INCREMENT,
    opportunity_id INT NOT NULL,
    user_id INT NOT NULL,
    status ENUM('pending', 'accepted', 'rejected', 'withdrawn') DEFAULT 'pending',
    cover_letter TEXT,
    resume_file_id VARCHAR(255),
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (opportunity_id) REFERENCES opportunities(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_opportunity (opportunity_id),
    INDEX idx_user (user_id)
);
```

**Purpose**: Tracks student applications to career opportunities.

**Fields**:
- `id`: Primary key
- `opportunity_id`: Reference to opportunities table
- `user_id`: Reference to users table
- `status`: Application status
- `cover_letter`: Application cover letter
- `resume_file_id`: Reference to uploaded resume
- `applied_at`, `updated_at`: Timestamps

### Notifications Table (`notifications`)

```sql
CREATE TABLE notifications (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    message TEXT NOT NULL,
    type ENUM('info', 'success', 'warning', 'error') DEFAULT 'info',
    is_read BOOLEAN DEFAULT FALSE,
    link VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user (user_id),
    INDEX idx_read (is_read)
);
```

**Purpose**: Manages user notifications within the KIU system.

**Fields**:
- `id`: Primary key
- `user_id`: Reference to users table
- `message`: Notification content
- `type`: Notification type
- `is_read`: Read status
- `link`: Optional link for action
- `created_at`: Timestamp

### OTP Codes Table (`otp_codes`)

```sql
CREATE TABLE otp_codes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    code VARCHAR(10) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user (user_id),
    INDEX idx_code (code)
);
```

**Purpose**: Stores one-time passwords for secure authentication.

**Fields**:
- `id`: Primary key
- `user_id`: Reference to users table
- `code`: 6-10 digit OTP code
- `expires_at`: Expiration timestamp
- `is_used`: Usage status
- `created_at`: Creation timestamp

### Refresh Tokens Table (`refresh_tokens`)

```sql
CREATE TABLE refresh_tokens (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_token (token),
    INDEX idx_user (user_id)
);
```

**Purpose**: Manages JWT refresh tokens for secure authentication.

**Fields**:
- `id`: Primary key
- `user_id`: Reference to users table
- `token`: Unique refresh token
- `expires_at`: Token expiration
- `is_used`: Usage status
- `created_at`: Creation timestamp

### Audit Logs Table (`audit_logs`)

```sql
CREATE TABLE audit_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    action VARCHAR(100) NOT NULL,
    table_name VARCHAR(100),
    record_id INT,
    old_values JSON,
    new_values JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user (user_id),
    INDEX idx_action (action),
    INDEX idx_created (created_at)
);
```

**Purpose**: Comprehensive audit trail for all KIU system actions.

**Fields**:
- `id`: Primary key
- `user_id`: Reference to users table (nullable for system actions)
- `action`: Action performed
- `table_name`: Affected database table
- `record_id`: Affected record ID
- `old_values`, `new_values`: Before/after states
- `ip_address`: Source IP
- `user_agent`: Browser/client information
- `created_at`: Timestamp

## Relationships

```mermaid
erDiagram
    users ||--o{ creates }--| admission_applications
    users ||--o{ creates }--| finalist_profiles
    users ||--o{ creates }--| opportunity_applications
    users ||--o{ creates }--| notifications
    users ||--o{ creates }--| otp_codes
    users ||--o{ creates }--| refresh_tokens
    users ||--o{ creates }--| audit_logs
    
    programs ||--o{ references }--| admission_applications
    opportunities ||--o{ references }--| opportunity_applications
    career_paths ||--o{ references }--| opportunities
```

## Data Types

### JSON Fields Examples

#### Personal Information
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "phone": "+256123456789",
  "date_of_birth": "2000-01-01",
  "gender": "male",
  "nationality": "Ugandan"
}
```

#### Educational Background
```json
{
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
  ],
  "diploma_results": {
    "institution": "Makerere University",
    "program": "Computer Science",
    "year": "2020",
    "class": "Credit"
  }
}
```

#### Entry Requirements
```json
{
  "olevel_points": 24,
  "alevel_points": 12,
  "subjects": ["Mathematics", "Physics", "Chemistry"],
  "minimum_gpa": 3.0
}
```

## Indexes

### Performance Indexes
```sql
-- User queries
CREATE INDEX idx_users_email_role ON users(email, role);
CREATE INDEX idx_users_active ON users(is_active);

-- Application queries
CREATE INDEX idx_applications_user_status ON admission_applications(user_id, status);
CREATE INDEX idx_applications_program ON admission_applications(program_id);

-- Notification queries
CREATE INDEX idx_notifications_user_read ON notifications(user_id, is_read);
```

## Migration Strategy

### Version Control
```sql
-- Migration version tracking
CREATE TABLE migration_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    version VARCHAR(20) NOT NULL,
    description TEXT,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Rollback Support
- All schema changes include rollback scripts
- Migration files stored in `apps/flask-api/migrations/`
- Automatic rollback on failure

## Security Considerations

### Data Protection
- Passwords hashed with Bcrypt
- PII encrypted at rest
- Audit trail for all data changes
- Regular backup schedules

### Access Control
- Role-based permissions through user roles
- Row-level security for sensitive data
- API-level authentication for all endpoints

## Performance Optimization

### Query Optimization
- Proper indexing on foreign keys
- JSON field indexing for common queries
- Partitioning for large tables (applications by year)

### Connection Pooling
```python
# SQLAlchemy configuration
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_timeout=30
)
```

## Backup Strategy

### Automated Backups
```bash
# Daily backup script
mysqldump -u root -p kiu_portal > backup_$(date +%Y%m%d).sql
```

### Retention Policy
- Application data: 7 years
- User accounts: 10 years after inactivity
- Audit logs: 2 years
- Notifications: 6 months

---

*Last Updated: January 2024*
