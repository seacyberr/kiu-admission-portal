# KIU Admission Portal - Frontend Documentation

## Architecture Overview

The KIU Admission Portal frontend is built with React 18, TypeScript, and Vite for optimal development experience and performance.

## Technology Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite 7.3+
- **Styling**: Tailwind CSS 4.1+
- **UI Components**: Radix UI primitives
- **State Management**: TanStack Query for server state
- **Routing**: Wouter for client-side navigation
- **Animations**: Framer Motion for smooth transitions
- **Icons**: Lucide React
- **Forms**: React Hook Form with Zod validation

## Component Structure

```
src/
├── components/           # Reusable UI components
│   ├── ui/            # Base UI primitives (Button, Input, etc.)
│   ├── layout.tsx     # Main application layout
│   ├── notifications-dropdown.tsx
│   └── page-progress-bar.tsx
├── pages/               # Route-based page components
│   ├── home.tsx        # Landing page
│   ├── auth/            # Authentication pages
│   ├── applicant/       # Applicant dashboard
│   ├── finalist/        # Finalist dashboard
│   └── admin/           # Admin dashboard
├── context/             # React contexts
│   ├── ThemeProvider.tsx
│   └── auth/
├── lib/                 # Utilities and helpers
└── assets/              # Static assets (images, fonts)
```

## Core Components

### Layout Component (`src/components/layout.tsx`)

Main application wrapper providing:
- Navigation header with KIU branding
- Theme switching (dark/light mode)
- Mobile responsive menu
- Notification system
- User authentication state
- Page progress indicators

**Props:**
```typescript
interface LayoutProps {
  children: React.ReactNode;
}
```

### UI Components (`src/components/ui/`)

Base UI components built on Radix UI:

#### Button
```typescript
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'accent' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  onClick?: () => void;
}
```

#### Input
```typescript
interface InputProps {
  type?: 'text' | 'email' | 'password' | 'tel';
  placeholder?: string;
  value?: string;
  onChange?: (value: string) => void;
  error?: string;
}
```

### Authentication Components

#### Login Form (`src/pages/auth/login.tsx`)
- Email and password fields
- Form validation with Zod schemas
- Remember me functionality
- Error handling and display
- Redirect after successful login

#### Register Form (`src/pages/auth/register.tsx`)
- Multi-step registration process
- Personal information collection
- Phone number validation (Uganda format)
- Email verification integration
- Password strength requirements

### Dashboard Components

#### Applicant Dashboard (`src/pages/applicant/dashboard.tsx`)
- Application status tracking
- Document upload management
- Profile information display
- Application progress indicators
- Programme recommendations

#### Finalist Dashboard (`src/pages/finalist/dashboard.tsx`)
- Career opportunity browsing
- Application tracking
- Profile management
- Skills and interests display
- Job application tracking

#### Admin Dashboard (`src/pages/admin/dashboard.tsx`)
- Application management interface
- User management tools
- Analytics and reporting
- Programme management
- Bulk operations support

## State Management

### TanStack Query Configuration

```typescript
// API Client Setup
import { useGetCurrentUser, useLogin } from '@workspace/api-client-react';

// Query Example
const { data: user, error, isLoading } = useGetCurrentUser({
  query: { retry: 3 }
});

// Mutation Example
const login = useLogin({
  onSuccess: () => {
    queryClient.invalidateQueries(['user']);
    navigate('/dashboard');
  }
});
```

## Routing

### Wouter Configuration

```typescript
// Route definitions
const routes = [
  { path: '/', component: Home },
  { path: '/login', component: Login },
  { path: '/dashboard', component: Dashboard },
  { path: '/admin', component: AdminDashboard }
];

// Navigation
<Link href="/dashboard">Dashboard</Link>
```

## Styling System

### Tailwind CSS Configuration

```javascript
// tailwind.config.js
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#0D6EFD',  // KIU Blue
          500: '#0EA5E9',
          600: '#0284C7',
          700: '#0369A1'
        }
      }
    }
  }
}
```

### Theme System

```typescript
// context/ThemeProvider.tsx
interface ThemeContextType {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
}

const ThemeProvider = ({ children }: { children: React.ReactNode }) => {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  
  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      <div className={theme}>
        {children}
      </div>
    </ThemeContext.Provider>
  );
};
```

## Performance Optimizations

### Code Splitting
```typescript
// Lazy loading for dashboard routes
const AdminDashboard = lazy(() => import('./pages/admin/dashboard'));
const ApplicantDashboard = lazy(() => import('./pages/applicant/dashboard'));
```

### Image Optimization
- Assets served from `/assets` directory
- WebP format for modern browsers
- Responsive images with srcset
- Lazy loading for off-screen images

### Bundle Analysis
```json
// package.json build scripts
{
  "build": "vite build --config vite.config.ts",
  "serve": "vite preview --config vite.config.ts"
}
```

## Accessibility Features

### ARIA Support
- Semantic HTML5 elements
- Screen reader friendly navigation
- Keyboard navigation support
- Focus management for forms
- Color contrast compliance (WCAG 2.1 AA)

### Responsive Design
- Mobile-first approach
- Breakpoint system:
  - Mobile: < 768px
  - Tablet: 768px - 1024px
  - Desktop: > 1024px

## Development Workflow

### Local Development
```bash
# Start development server
pnpm dev:portal

# Build for production
pnpm build

# Preview production build
pnpm serve
```

### Environment Variables
```typescript
// vite.config.ts
export default defineConfig({
  define: {
    VITE_API_URL: JSON.stringify(process.env.VITE_API_URL || 'http://localhost:5001/api'),
    VITE_APP_NAME: JSON.stringify(process.env.VITE_APP_NAME || 'KIU Admission Portal')
  }
});
```

## Testing

### Unit Testing with Vitest
```typescript
// Example test
import { render, screen } from '@testing-library/react';
import { Button } from '@/components/ui/shared';

test('renders button with KIU styling', () => {
  render(<Button>Apply Now</Button>);
  expect(screen.getByRole('button')).toBeInTheDocument();
  expect(screen.getByRole('button')).toHaveTextContent('Apply Now');
});
```

### E2E Testing with Playwright
```typescript
// Example E2E test
import { test, expect } from '@playwright/test';

test('KIU login flow', async ({ page }) => {
  await page.goto('/login');
  await page.fill('[data-testid="email"]', 'user@kiu.ac.ug');
  await page.fill('[data-testid="password"]', 'password');
  await page.click('[data-testid="login-button"]');
  
  await expect(page).toHaveURL('/dashboard');
});
```

## Browser Support

### Target Browsers
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### Progressive Enhancement
- Core functionality works without JavaScript
- Enhanced features with JavaScript enabled
- Service Worker for offline support

## Security Considerations

### Content Security Policy
```javascript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom']
        }
      }
    }
  }
});
```

### XSS Prevention
- React's built-in XSS protection
- Input sanitization for user content
- CSRF token implementation
- Content Security Policy headers

## Deployment

### Build Configuration
```json
// vite.config.ts
export default defineConfig({
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    minify: 'esbuild'
  }
});
```

### Environment-Specific Builds
```bash
# Development
VITE_API_URL=http://localhost:5001/api pnpm dev:portal

# Production
VITE_API_URL=https://api.kiu.ac.ug/api pnpm build
```

---

*Last Updated: January 2024*
