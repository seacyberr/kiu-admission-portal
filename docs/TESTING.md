# KIU Admission Portal - Testing & Quality Assurance Guide

## Overview

Comprehensive testing and quality assurance strategy for the KIU Admission Portal, ensuring reliability, security, and performance for Kampala International University's digital admission system.

## Testing Strategy

### 1. Unit Testing

#### Backend Testing (Python/Flask)

#### Test Structure
```
apps/flask-api/tests/
├── unit/                 # Individual component tests
│   ├── test_auth.py    # Authentication logic
│   ├── test_models.py   # Database models
│   ├── test_services.py # Business logic
│   └── test_routes.py   # API endpoints
├── integration/           # Service integration tests
│   ├── test_api_client.py # API client integration
│   └── test_database.py   # Database operations
├── fixtures/             # Test data
└── conftest.py           # Test configuration
```

#### Testing Framework
```python
# pytest configuration
[tool:pytest]
testpaths = tests
python_files = .py
python_functions = tests.conftest.py
addopts = -v --tb=short --strict-markers
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
```

#### Example Unit Test
```python
# tests/unit/test_auth.py
import pytest
from app import create_app
from services.auth_service import AuthService

class TestAuthService:
    def test_user_registration_success(self):
        """Test successful user registration"""
        app = create_app()
        auth_service = AuthService()
        
        user_data = {
            "email": "test@kiu.ac.ug",
            "password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "User"
        }
        
        result = auth_service.register_user(user_data)
        assert result["success"] is True
        assert "user_id" in result
        
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        app = create_app()
        auth_service = AuthService()
        
        # Should raise exception for invalid login
        with pytest.raises(Exception):
            auth_service.authenticate_user("invalid@kiu.ac.ug", "wrongpassword")
```

#### Running Tests
```bash
# Run all tests
cd apps/flask-api
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/unit/test_auth.py::TestAuthService::test_user_registration_success -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=html

# Run integration tests
python -m pytest tests/integration/ -v
```

#### Test Coverage Requirements
- **Unit Tests**: Minimum 80% line coverage
- **Integration Tests**: Minimum 70% line coverage
- **Critical Paths**: 100% coverage for authentication and admission logic
- **API Endpoints**: 100% coverage for all public endpoints

### 2. Frontend Testing (React/TypeScript)

#### Test Structure
```
apps/kiu-portal/
├── src/
│   ├── __tests__/           # Component tests
│   │   ├── components/    # UI component tests
│   │   ├── pages/         # Page component tests
│   │   └── utils/          # Utility function tests
│   └── e2e/               # End-to-end tests
│       ├── fixtures/         # Test data
│       ├── specs/            # Test specifications
│       └── config/           # Playwright config
├── package.json               # Test scripts
└── vitest.config.ts           # Test configuration
```

#### Testing Framework
```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/__tests__/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'src/__tests__/**',
        'src/**/*.stories.tsx',
        'src/**/*.d.ts'
      ],
      thresholds: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80
        }
      }
    }
  }
});
```

#### Example Component Test
```typescript
// src/__tests__/components/Button.test.tsx
import { render, screen } from '@testing-library/react';
import { Button } from '@/components/ui/shared';
import { describe, it, expect } from 'vitest';

describe('Button Component', () => {
  it('renders KIU-styled button correctly', () => {
    render(<Button variant="primary">Apply to KIU</Button>);
    
    const button = screen.getByRole('button');
    expect(button).toBeInTheDocument();
    expect(button).toHaveTextContent('Apply to KIU');
    expect(button).toHaveClass('bg-primary');
  });
  
  it('handles click events', async () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    
    await userEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

#### Running Tests
```bash
# Run unit tests
pnpm test

# Run tests with coverage
pnpm test --coverage

# Run specific test file
pnpm test Button.test.tsx

# Run tests in watch mode
pnpm test --watch
```

#### E2E Testing with Playwright

##### Test Configuration
```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './src/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
  },
});
```

##### Example E2E Test
```typescript
// src/e2e/specs/admission.spec.ts
import { test, expect } from '@playwright/test';
import { LoginPage } from '../fixtures/LoginPage';

test('KIU admission application flow', async ({ page }) => {
  const loginPage = new LoginPage(page);
  
  await page.goto('/login');
  await loginPage.fillLoginForm({
    email: 'applicant@kiu.ac.ug',
    password: 'TestPass123!'
  });
  
  await loginPage.submit();
  await expect(page).toHaveURL('/dashboard');
  
  // Navigate to application
  await page.goto('/apply');
  await expect(page).toHaveTitle(/Apply to KIU/);
});
```

#### Running E2E Tests
```bash
# Install Playwright browsers
pnpm exec playwright install

# Run E2E tests
pnpm test:e2e

# Run E2E tests with UI
pnpm test:e2e --ui

# Run E2E tests in debug mode
pnpm test:e2e --debug
```

#### Frontend Coverage Requirements
- **Components**: Minimum 85% line coverage
- **Pages**: Minimum 80% line coverage
- **User Flows**: 100% coverage for authentication and application flows
- **Accessibility**: WCAG 2.1 AA compliance for all interactive elements

### 3. Integration Testing

#### API Integration Tests
```python
# tests/integration/test_admission_flow.py
import pytest
from app import create_app

class TestAdmissionFlow:
    def test_complete_application_flow(self):
        """Test complete admission application from registration to submission"""
        app = create_app()
        
        with app.test_client() as client:
            # Step 1: Register user
            register_data = {
                "email": "test.applicant@kiu.ac.ug",
                "password": "TestPass123!",
                "first_name": "Test",
                "last_name": "Applicant"
            }
            response = client.post('/api/auth/register', json=register_data)
            assert response.status_code == 201
            
            # Step 2: Login user
            login_data = {
                "email": "test.applicant@kiu.ac.ug",
                "password": "TestPass123!"
            }
            response = client.post('/api/auth/login', json=login_data)
            assert response.status_code == 200
            token = response.json['access_token']
            
            # Step 3: Submit application
            application_data = {
                "program_id": 1,
                "application_type": "olevel"
            }
            headers = {'Authorization': f'Bearer {token}'}
            response = client.post('/api/admissions/apply', json=application_data, headers=headers)
            assert response.status_code == 201
```

#### Database Integration Tests
```python
# tests/integration/test_database_operations.py
import pytest
from app import create_app
from models import db, User, AdmissionApplication

class TestDatabaseOperations:
    def test_user_application_relationship(self):
        """Test database relationship between users and applications"""
        app = create_app()
        
        with app.app_context():
            # Create test user
            user = User(
                email="test@kiu.ac.ug",
                first_name="Test",
                last_name="User"
            )
            db.session.add(user)
            db.session.commit()
            
            # Create application for user
            application = AdmissionApplication(
                user_id=user.id,
                program_id=1,
                status="pending"
            )
            db.session.add(application)
            db.session.commit()
            
            # Verify relationship
            retrieved_user = User.query.filter_by(id=user.id).first()
            retrieved_application = AdmissionApplication.query.filter_by(user_id=user.id).first()
            
            assert retrieved_user is not None
            assert retrieved_application is not None
            assert retrieved_application.user_id == user.id
```

#### Frontend-Backend Integration
```typescript
// src/__tests__/integration/api_integration.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useGetCurrentUser } from '@workspace/api-client-react';

// Mock API responses
vi.mock('@workspace/api-client-react', () => ({
  useGetCurrentUser: vi.fn(),
}));

describe('Frontend-Backend Integration', () => {
  it('displays user data from API', async () => {
    const queryClient = new QueryClient();
    const mockUser = { id: 1, email: 'test@kiu.ac.ug' };
    
    vi.mocked(useGetCurrentUser).mockReturnValue({
      data: mockUser,
      isLoading: false,
      error: null
    });
    
    render(
      <QueryClientProvider client={queryClient}>
        <TestComponent />
      </QueryClientProvider>
    );
    
    await waitFor(() => {
      expect(screen.getByText('test@kiu.ac.ug')).toBeInTheDocument();
    });
  });
});
```

### 4. Performance Testing

#### Load Testing

##### Backend Load Testing
```python
# tests/performance/test_api_load.py
import pytest
import asyncio
import aiohttp
import time

class TestAPILoad:
    async def test_login_endpoint_load(self):
        """Test login endpoint under load"""
        url = "http://localhost:5001/api/auth/login"
        concurrent_requests = 50
        
        async def make_request():
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json={"email": "test@kiu.ac.ug", "password": "TestPass123!"}
                ) as response:
                    return response.status
        
        start_time = time.time()
        tasks = [make_request() for _ in range(concurrent_requests)]
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Assertions
        success_count = sum(1 for r in results if r == 200)
        avg_response_time = (end_time - start_time) / concurrent_requests
        
        assert success_count >= 45  # 90% success rate
        assert avg_response_time < 2.0  # Under 2 seconds
```

##### Frontend Performance Testing
```bash
# Lighthouse performance testing
npm install -g lighthouse

# Run performance audit
lighthouse http://localhost:5173 \
  --output=json \
  --chrome-flags="--headless" \
  --quiet

# Performance budgets
{
  "performance": 90,     # Performance score
  "accessibility": 95,  # Accessibility score
  "best-practices": 85,   # Best practices score
  "seo": 90             # SEO score
}
```

#### Stress Testing
```bash
# Backend stress testing
artillery run tests/performance/stress_test.yml

# Frontend memory testing
node --max-old-space-size=4096 apps/kiu-portal/src/main.tsx
```

### 5. Security Testing

#### OWASP ZAP Security Testing
```bash
# Automated security scanning
docker run -t owasp/zap2docker-stable \
  -v /zap/wrk:/zap/wrk/:ro \
  zap-baseline.py -t http://localhost:5001 \
  -g gen.conf -x

# Generate security report
docker run -t owasp/zap2docker-stable \
  zap-baseline.py -t http://localhost:5001 \
  -g gen.conf -x -r html,xml -json
```

#### SQL Injection Testing
```python
# tests/security/test_sql_injection.py
import pytest
from app import create_app

class TestSQLInjection:
    def test_sql_injection_protection(self):
        """Test SQL injection protection"""
        app = create_app()
        
        with app.test_client() as client:
            # Attempt SQL injection
            malicious_payload = "'; DROP TABLE users; --"
            
            response = client.post('/api/auth/login', json={
                "email": f"test@kiu.ac.ug{malicious_payload}",
                "password": "password"
            })
            
            # Should not succeed and should not crash server
            assert response.status_code in [400, 422]
            
            # Check that no SQL was executed
            assert "DROP TABLE" not in response.data.get('message', '').lower()
```

#### XSS Protection Testing
```javascript
// tests/security/test_xss_protection.test.tsx
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from '@playwright/test';

describe('XSS Protection', () => {
  it('sanitizes user input', async ({ page }) => {
    await page.goto('/register');
    
    // Attempt XSS injection
    const xssPayload = '<script>alert("XSS")</script>';
    await page.fill('[data-testid="first_name"]', xssPayload);
    await page.fill('[data-testid="last_name"]', 'Test');
    await page.click('[data-testid="register-button"]');
    
    // Should not execute script
    expect(page.locator('script')).not.toBeVisible();
    
    // Should display sanitized content
    const firstName = page.locator('[data-testid="first_name"]');
    await expect(firstName).toHaveValue('');
  });
});
```

### 6. Quality Assurance

#### Code Quality Standards

##### Backend Code Quality
```python
# .flake8 configuration
[flake8]
max-line-length = 88
max-complexity = 10
exclude = venv,__pycache__
ignore = E501,W503

# Black code formatting
[tool.black]
line-length = 88
target-version = ['py38', 'py39', 'py310', 'py311']

# isort import sorting
[tool.isort]
profile = black
multi_line_output = 3
```

##### Frontend Code Quality
```json
// package.json scripts
{
  "scripts": {
    "lint": "eslint src --ext .ts,.tsx --fix",
    "lint:fix": "eslint src --ext .ts,.tsx --fix",
    "format": "prettier --write src/**/*.{ts,tsx}",
    "type-check": "tsc --noEmit",
    "quality": "npm run lint && npm run format && npm run type-check"
  }
}

// ESLint configuration
module.exports = {
  extends: [
    '@typescript-eslint/recommended',
    'plugin:react-hooks/recommended'
  ],
  rules: {
    'react-hooks/exhaustive-deps': 'warn',
    '@typescript-eslint/no-unused-vars': 'error',
    'react/prop-types': 'error'
  }
};
```

#### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v3.4.1
    hooks:
      - id: black
        language_version: python3
        entry: black
        files: ^apps/flask-api/
      - id: isort
        language_version: python3
        entry: isort
        files: ^apps/flask-api/
      - id: eslint
        language_version: node
        entry: eslint
        files: ^apps/kiu-portal/src/
      - id: prettier
        language_version: node
        entry: prettier
        files: ^apps/kiu-portal/src/
      - id: playwright-check
        language_version: node
        entry: playwright install --with-deps
        files: ^apps/kiu-portal/src/
        pass: true
```

### 7. Test Data Management

#### Test Fixtures
```python
# tests/fixtures/test_data.py
import factory
from models import User, Program, AdmissionApplication

class TestFixtures:
    @staticmethod
    def create_test_user():
        """Create test user with KIU email"""
        return User(
            email="test.user@kiu.ac.ug",
            first_name="Test",
            last_name="User",
            role="applicant",
            is_active=True,
            email_verified=True
        )
    
    @staticmethod
    def create_test_program():
        """Create test KIU program"""
        return Program(
            name="Bachelor of Computer Science",
            code="BCS",
            level="bachelor",
            faculty="Science & Technology",
            duration_years=4,
            is_active=True
        )
    
    @staticmethod
    def create_test_application():
        """Create test admission application"""
        return AdmissionApplication(
            application_type="olevel",
            status="pending",
            personal_info={
                "first_name": "Test",
                "last_name": "User",
                "email": "test.user@kiu.ac.ug"
            }
        )
```

#### Database Seeding
```python
# tests/conftest.py
import pytest
from app import create_app
from models import db, User, Program

@pytest.fixture(scope='session')
def test_db():
    app = create_app()
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()

@pytest.fixture
def sample_user(test_db):
    user = User(
        email="test@kiu.ac.ug",
        first_name="Test",
        last_name="User",
        role="applicant"
    )
    test_db.session.add(user)
    test_db.session.commit()
    return user

@pytest.fixture
def sample_program(test_db):
    program = Program(
        name="Bachelor of Computer Science",
        code="BCS",
        level="bachelor",
        faculty="Science & Technology"
    )
    test_db.session.add(program)
    test_db.session.commit()
    return program
```

### 8. Continuous Integration/Continuous Deployment (CI/CD)

#### GitHub Actions Workflow
```yaml
# .github/workflows/ci.yml
name: KIU Admission Portal CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [18.x, 20.x]
        python-version: [3.11]
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
          
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'
          
      - name: Install Dependencies
        run: |
          python -m pip install -r apps/flask-api/requirements.txt
          npm install -g pnpm
          pnpm install
          
      - name: Run Backend Tests
        run: |
          cd apps/flask-api
          python -m pytest tests/ --cov=app --cov-report=xml
          
      - name: Run Frontend Tests
        run: |
          cd apps/kiu-portal
          pnpm test --coverage
          
      - name: Upload Coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          token: ${{ secrets.CODECOV_TOKEN }}
```

#### Docker CI Pipeline
```dockerfile
# Dockerfile.ci
FROM node:20-alpine AS frontend
WORKDIR /app
COPY package*.json ./
RUN npm ci
RUN npm run build

FROM python:3.11-slim AS backend
WORKDIR /app
COPY apps/flask-api/requirements.txt .
RUN pip install -r requirements.txt
COPY apps/flask-api/ .
RUN python -m pytest tests/ --cov=app --cov-report=xml
```

### 9. Test Reporting

#### Coverage Reporting
```bash
# Generate coverage reports
python -m pytest tests/ --cov=app --cov-report=html --cov-report=xml
pnpm test --coverage --reporter=html --reporter=json

# Coverage thresholds
{
  "backend": {
    "statements": 85,
    "branches": 80,
    "functions": 80,
    "lines": 85
  },
  "frontend": {
    "statements": 90,
    "branches": 85,
    "functions": 90,
    "lines": 90
  }
}
```

#### Test Result Dashboard
```python
# Generate test dashboard
python scripts/generate_test_dashboard.py --output-dir test-results --format html
```

## Quality Gates

### Pre-deployment Checklist

#### Code Quality
- [ ] All tests passing
- [ ] Code coverage thresholds met
- [ ] No linting errors
- [ ] No security vulnerabilities
- [ ] Documentation updated

#### Performance
- [ ] API response times < 2s
- [ ] Frontend Lighthouse score > 90
- [ ] Database queries optimized
- [ ] Memory usage within limits

#### Security
- [ ] No OWASP Top 10 vulnerabilities
- [ ] All dependencies up to date
- [ ] SSL certificates valid
- [ ] Authentication properly implemented

#### Functionality
- [ ] User registration/login working
- [ ] Application submission successful
- [ ] File upload/download working
- [ ] Email notifications functional
- [ ] Admin dashboard accessible

## Testing Tools & Commands

### Quick Test Commands
```bash
# Run all tests
make test

# Run backend tests only
make test-backend

# Run frontend tests only
make test-frontend

# Run E2E tests
make test-e2e

# Run security tests
make test-security

# Generate coverage report
make coverage

# Run performance tests
make test-performance
```

### Environment-Specific Testing
```bash
# Development testing
make test-dev

# Staging testing
make test-staging

# Production smoke tests
make test-prod-smoke
```

## Best Practices

### Test-Driven Development
1. **Write tests first** - Before implementing new features
2. **Red-Green-Refactor** - Keep code clean and maintainable
3. **Test coverage** - Aim for high coverage on critical paths
4. **Automated testing** - Integrate into CI/CD pipeline
5. **Regular testing** - Run tests frequently during development

### Security Testing
1. **Security-first development** - Consider security from design phase
2. **Regular audits** - Schedule periodic security assessments
3. **Dependency scanning** - Keep third-party dependencies updated
4. **Penetration testing** - Conduct regular security assessments
5. **OWASP compliance** - Follow OWASP security guidelines

---

*Last Updated: January 2024*
