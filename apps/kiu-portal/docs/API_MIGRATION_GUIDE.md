# Frontend API Migration Guide - Phase 4

## Overview

This guide documents the changes made in **Phase 4: Frontend Modernization** to support the standardized API response format implemented in **Phase 3**.

## What Changed

### Backend (Phase 3 - Completed)
All backend API routes now return responses in a standardized **JSend format**:

```typescript
// Success response (200)
{
  status: "success",
  data: { ... },           // Your actual data
  message: "...",         // Optional human-readable message
  meta: { ... }           // Optional metadata (pagination, etc.)
}

// Error response (400, 401, 403, 404, etc.)
{
  status: "fail" | "error",
  message: "Error description",
  errors: {               // Optional field-level errors
    "field_name": "Error message"
  }
}
```

### Frontend (Phase 4 - Completed)
Updated the API client to:
1. Automatically extract `data` from standardized responses
2. Handle field-level errors via new `ApiError` class
3. Provide better error messages

## Quick Start

### 1. Basic API Call

```typescript
import { apiGet, apiPost, apiPatch, apiDelete } from '../services/api';

// GET request - data is automatically extracted
const users = await apiGet<User[]>('/v1/users');
// Returns: User[] (not the full response object)

// POST request
const newUser = await apiPost<User>('/v1/users', { name: 'John' });

// PATCH request
const updated = await apiPatch<User>('/v1/users/1', { name: 'Jane' });

// DELETE request
await apiDelete('/v1/users/1');
```

### 2. Error Handling with Field-Level Errors

```typescript
import { ApiError } from '../services/api';

try {
  await apiPost('/v1/users', formData);
} catch (error) {
  if (error instanceof ApiError) {
    // General error message
    console.log(error.message); // "Validation failed"
    
    // Field-specific errors
    console.log(error.errors);  // { email: "Already exists", age: "Must be 18+" }
    
    // HTTP status code
    console.log(error.status);  // 400
  }
}
```

### 3. Using the useApi Hook

```typescript
import { useApi, useApiMutation } from '../hooks/useApi';

// For GET requests
function UserList() {
  const { data, isLoading, error, fieldErrors, execute } = useApi<User[]>(
    () => apiGet('/v1/users')
  );
  
  useEffect(() => {
    execute();
  }, [execute]);
  
  if (isLoading) return <Loading />;
  if (error) return <ErrorMessage message={error} />;
  
  return <UserTable users={data || []} />;
}

// For mutations (POST/PATCH/DELETE)
function UserForm() {
  const { mutate, isLoading, error, fieldErrors, isSuccess } = useApiMutation(
    (data) => apiPost('/v1/users', data)
  );
  
  const handleSubmit = async (formData) => {
    const result = await mutate(formData);
    if (result) {
      // Success - redirect or show message
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input name="email" />
      {fieldErrors?.email && <span className="error">{fieldErrors.email}</span>}
      
      <button disabled={isLoading}>Submit</button>
      {error && <div className="error">{error}</div>}
    </form>
  );
}
```

### 4. Using Auth Context with Error Handling

```typescript
import { useAuth } from '../features/auth/hooks/useAuth';

function LoginForm() {
  const { login, authError, fieldErrors, isLoading, clearErrors } = useAuth();
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    clearErrors();
    
    try {
      await login(email, password);
      // Success - redirect
    } catch (error) {
      // Error is already displayed via authError/fieldErrors
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input name="email" />
      {fieldErrors?.email && <span className="error">{fieldErrors.email}</span>}
      
      <input type="password" name="password" />
      {fieldErrors?.password && <span className="error">{fieldErrors.password}</span>}
      
      {authError && <div className="error">{authError}</div>}
      
      <button disabled={isLoading}>
        {isLoading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
}
```

## Migration Checklist

When updating existing components:

- [ ] Import `ApiError` from services if doing custom error handling
- [ ] Update error handling to check for `error.errors` for field-level validation
- [ ] Remove any manual `response.data.data` extraction (now handled automatically)
- [ ] Update pagination handling to use new meta format if applicable
- [ ] Test error scenarios to ensure field-level errors display correctly

## API Response Types

```typescript
// Types are in src/types/api.ts

interface ApiResponse<T> {
  status: 'success' | 'fail' | 'error';
  data: T;
  message?: string;
  errors?: Record<string, string>;
  meta?: {
    total?: number;
    page?: number;
    per_page?: number;
    pages?: number;
  };
}

class ApiError extends Error {
  status: number;           // HTTP status code
  errors?: Record<string, string>;  // Field-level errors
}
```

## Common Patterns

### Pattern 1: Form with Validation

```typescript
function MyForm() {
  const [formData, setFormData] = useState({});
  const { mutate, error, fieldErrors, isLoading } = useApiMutation(
    (data) => apiPost('/v1/endpoint', data)
  );
  
  return (
    <form onSubmit={(e) => { e.preventDefault(); mutate(formData); }}>
      <div>
        <input 
          value={formData.email} 
          onChange={e => setFormData({...formData, email: e.target.value})}
        />
        {fieldErrors?.email && <span className="text-red-500">{fieldErrors.email}</span>}
      </div>
      
      <button disabled={isLoading}>Submit</button>
      {error && <div className="text-red-500">{error}</div>}
    </form>
  );
}
```

### Pattern 2: Paginated List

```typescript
function UserList() {
  const { items, total, page, setPage, isLoading, error } = usePaginatedApi<User>(
    (page, perPage) => apiGet(`/v1/users?page=${page}&perPage=${perPage}`)
  );
  
  if (isLoading) return <Loading />;
  if (error) return <ErrorMessage message={error} />;
  
  return (
    <>
      <UserTable users={items} />
      <Pagination 
        currentPage={page} 
        totalPages={Math.ceil(total / 20)} 
        onPageChange={setPage}
      />
    </>
  );
}
```

### Pattern 3: Manual Error Handling

```typescript
async function handleAction() {
  try {
    const result = await apiPost('/v1/action', data);
    showSuccess('Action completed');
    return result;
  } catch (error) {
    if (error instanceof ApiError) {
      if (error.status === 409) {
        showError('Conflict: ' + error.message);
      } else if (error.errors) {
        // Handle field errors
        Object.entries(error.errors).forEach(([field, message]) => {
          showFieldError(field, message);
        });
      }
    } else {
      showError('Unexpected error');
    }
  }
}
```

## Files Changed in Phase 4

1. `src/types/api.ts` - Updated API response types
2. `src/services/api.ts` - Updated client with standardized response handling
3. `src/features/auth/context/AuthContext.tsx` - Updated auth with error handling
4. `src/hooks/useApi.ts` - New hooks for standardized API usage (created)

## Backward Compatibility

The new API client is **backward compatible** with existing code, but you'll get better error handling by migrating to the new patterns.

## Support

For questions or issues with the migration:
1. Check this guide first
2. Look at the example hooks in `src/hooks/useApi.ts`
3. Review the updated AuthContext for reference implementation
