# Frontend API Integration - Developer Quick Reference

## Quick Start Guide

### Using the Custom Hook Pattern

#### Example 1: Dashboard Page Pattern
```typescript
import { useApiData } from '@/hooks/useApiData';
import { apiService } from '@/lib/api';

export default function MyPage() {
  // Single API call
  const { data, loading, error } = useApiData(
    () => apiService.getDashboardStats(),
    []
  );

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorDisplay error={error} />;
  
  return <Dashboard stats={data} />;
}
```

#### Example 2: Multiple API Calls in Parallel
```typescript
import { useState, useEffect } from 'react';
import { apiService } from '@/lib/api';

export default function ReportsPage() {
  const [stats, setStats] = useState(null);
  const [trends, setTrends] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        // Execute all calls in parallel
        const [statsRes, trendsRes] = await Promise.all([
          apiService.getDashboardStats(),
          apiService.getMonthlyTrends()
        ]);
        setStats(statsRes);
        setTrends(trendsRes);
      } catch (err) {
        setError(err.message);
        toast.error('Failed to load data');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  // Render logic with loading/error states
}
```

#### Example 3: Form Submission with Loading State
```typescript
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { apiService } from '@/lib/api';
import { toast } from 'sonner';

export default function ClaimForm() {
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const { register, handleSubmit, formState: { errors }, reset } = useForm({
    resolver: zodResolver(claimSchema)
  });

  const onSubmit = async (data) => {
    try {
      setSubmitting(true);
      setError(null);
      
      const response = await apiService.createClaim(data);
      
      toast.success('Claim submitted successfully!');
      reset();
      // Auto-redirect after success
      setTimeout(() => navigate('/claims'), 2000);
    } catch (err) {
      const message = err.message || 'Failed to submit claim';
      setError(message);
      toast.error(message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      {error && <ErrorAlert error={error} />}
      {/* Form fields */}
      <button 
        type="submit" 
        disabled={submitting}
      >
        {submitting ? 'Submitting...' : 'Submit'}
      </button>
    </form>
  );
}
```

---

## Adding New API Endpoints

### Step 1: Add Backend Endpoint in `Backend/churn/views.py`
```python
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

class AnalyticsViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def my_new_endpoint(self, request):
        """Description of what this endpoint does."""
        # Your logic here
        data = {
            'field1': 'value1',
            'field2': 'value2'
        }
        return Response(data)
```

### Step 2: Register in Router (`Backend/churn/urls.py`)
```python
router = DefaultRouter()
router.register(r'analytics', views.AnalyticsViewSet, basename='analytics')
# The route will automatically be: /api/v1/analytics/my_new_endpoint/
```

### Step 3: Add API Method in `Frontend/src/lib/api.ts`
```typescript
class ApiService {
  async getMyNewData() {
    return this.get('/api/v1/analytics/my_new_endpoint/');
  }
}
```

### Step 4: Create Hook in `Frontend/src/hooks/useApiData.ts`
```typescript
export function useMyNewData() {
  return useApiData(
    () => apiService.getMyNewData(),
    []
  );
}
```

### Step 5: Use in Component
```typescript
import { useMyNewData } from '@/hooks/useApiData';

export default function MyComponent() {
  const { data, loading, error } = useMyNewData();
  
  if (loading) return <Loader2 className="animate-spin" />;
  if (error) return <AlertTriangle />;
  
  return <div>{/* Render your data */}</div>;
}
```

---

## Error Handling Patterns

### Pattern 1: Simple Error Display
```typescript
if (error) {
  return (
    <div className="text-center p-8">
      <AlertTriangle className="h-8 w-8 text-destructive mx-auto mb-4" />
      <p className="text-destructive">{error}</p>
      <button 
        onClick={() => window.location.reload()}
        className="mt-4 px-4 py-2 bg-primary rounded"
      >
        Retry
      </button>
    </div>
  );
}
```

### Pattern 2: Toast Notifications
```typescript
try {
  await apiService.createClaim(data);
  toast.success('Claim submitted!');
} catch (err) {
  toast.error('Failed to submit claim', {
    description: err.message
  });
}
```

### Pattern 3: Form-Level Error Messages
```typescript
const [error, setError] = useState(null);

const onSubmit = async (data) => {
  try {
    setError(null);
    await apiService.createClaim(data);
  } catch (err) {
    setError(err.message);
  }
};

return (
  <>
    {error && (
      <div className="bg-destructive/10 border border-destructive p-4 rounded">
        <AlertTriangle className="inline mr-2" />
        {error}
      </div>
    )}
  </>
);
```

---

## Loading State Patterns

### Pattern 1: Skeleton Loading
```typescript
import { Skeleton } from '@/components/ui/skeleton';

if (loading) {
  return (
    <div className="space-y-4">
      <Skeleton className="h-12 w-full" />
      <Skeleton className="h-64 w-full" />
    </div>
  );
}
```

### Pattern 2: Spinner with Message
```typescript
import { Loader2 } from 'lucide-react';

if (loading) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px]">
      <Loader2 className="h-8 w-8 animate-spin text-primary mb-4" />
      <p className="text-muted-foreground">Loading dashboard data...</p>
    </div>
  );
}
```

### Pattern 3: Button Loading State
```typescript
<button 
  disabled={submitting}
  className="disabled:opacity-50 disabled:cursor-not-allowed"
>
  {submitting ? (
    <>
      <Loader2 className="h-4 w-4 mr-2 animate-spin inline" />
      Processing...
    </>
  ) : (
    'Submit'
  )}
</button>
```

---

## API Response Handling

### Pattern 1: Paginated List Response
```typescript
// Response structure
{
  results: [...items],
  count: 100,
  next: "url_to_next_page",
  previous: "url_to_previous_page"
}

// Usage
const response = await apiService.getCustomers({ page_size: 20 });
const items = response.results || response;
```

### Pattern 2: Single Object Response
```typescript
// Response structure
{
  id: "123",
  claim_number: "CLM-001",
  status: "approved"
}

// Usage
const claim = await apiService.getClaim(id);
console.log(claim.claim_number);
```

### Pattern 3: List Response
```typescript
// Response structure
[
  { id: 1, name: "Item 1" },
  { id: 2, name: "Item 2" }
]

// Usage
const items = await apiService.getMonthlyTrends();
items.forEach(item => console.log(item.month));
```

---

## Testing Patterns

### Unit Test Example
```typescript
import { renderHook, waitFor } from '@testing-library/react';
import { useApiData } from '@/hooks/useApiData';

describe('useApiData', () => {
  it('should fetch data successfully', async () => {
    const mockFetch = jest.fn().mockResolvedValue({ data: 'test' });
    const { result } = renderHook(() => useApiData(mockFetch, []));
    
    expect(result.current.loading).toBe(true);
    
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
      expect(result.current.data).toEqual({ data: 'test' });
    });
  });

  it('should handle errors', async () => {
    const error = new Error('API Error');
    const mockFetch = jest.fn().mockRejectedValue(error);
    const { result } = renderHook(() => useApiData(mockFetch, []));
    
    await waitFor(() => {
      expect(result.current.error).toBe(error.message);
    });
  });
});
```

---

## Common Gotchas

### ❌ Don't: Hardcode API URLs
```typescript
// BAD
const response = await fetch('http://localhost:8000/api/v1/users/');
```

### ✅ Do: Use apiService
```typescript
// GOOD
const response = await apiService.getUsers();
```

### ❌ Don't: Forget error handling
```typescript
// BAD
const data = await apiService.getData();
return <div>{data.name}</div>;
```

### ✅ Do: Handle all states
```typescript
// GOOD
const { data, loading, error } = useApiData(() => apiService.getData(), []);
if (loading) return <Loader />;
if (error) return <Error />;
return <div>{data?.name}</div>;
```

### ❌ Don't: Make API calls directly in render
```typescript
// BAD
function MyComponent() {
  const [data, setData] = useState(null);
  
  setData(await apiService.getData()); // Called every render!
  
  return <div>{data}</div>;
}
```

### ✅ Do: Use useEffect with dependencies
```typescript
// GOOD
function MyComponent() {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    apiService.getData().then(setData);
  }, []);
  
  return <div>{data}</div>;
}
```

---

## Browser DevTools Tips

### Check Network Requests
1. Open DevTools → Network tab
2. Make an API call
3. Look for requests to `/api/v1/`
4. Check response status and body
5. Check Authorization header

### View JWT Token
1. Open DevTools → Application tab
2. Check localStorage
3. Look for `auth_access_token` and `auth_refresh_token`

### Debug Component State
1. Install React DevTools extension
2. Inspect component
3. Check hooks state
4. Verify loading/error states

---

## Performance Tips

1. **Use Parallel Loading**: Fetch multiple independent data sources simultaneously
2. **Implement Pagination**: Load data in chunks, not all at once
3. **Use Memoization**: Prevent unnecessary recalculations
4. **Lazy Load Components**: Split code for large pages
5. **Cache API Responses**: Consider using react-query or SWR
6. **Debounce Search**: Limit API calls on search input

---

## Resources & Links

- API Documentation: [Backend API Docs](../Backend/churn/urls.py)
- TypeScript Guide: [Official TypeScript Handbook](https://www.typescriptlang.org/docs/)
- React Hooks: [React Hooks Documentation](https://react.dev/reference/react/hooks)
- DRF Documentation: [Django REST Framework](https://www.django-rest-framework.org/)

---

Generated: 30 March 2026
Version: 1.0.0
Status: ✅ Ready for Implementation
