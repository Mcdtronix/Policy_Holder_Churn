# AUTHENTICATION SYSTEM DOCUMENTATION

## Overview

The Nyaradzo Assurance Management System implements a professional, secure JWT-based authentication system with email-based login, token refresh, and role-based access control.

---

## Architecture

### Authentication Flow

```
┌─────────────────┐
│   Frontend      │
│   (React/TS)    │
└────────┬────────┘
         │ POST /api/token/ { email, password }
         ▼
┌─────────────────────────────────────────────┐
│   Backend Authentication Layer              │
│   (Django + djangorestframework-simplejwt)  │
│                                             │
│  1. Validate email exists                   │
│  2. Verify password hash                    │
│  3. Check user is_active                    │
│  4. Generate JWT tokens                     │
│  5. Return tokens to client                 │
└────────┬────────────────────────────────────┘
         │ Response: { access, refresh }
         ▼
┌─────────────────┐
│  localStorage   │
│  (Client Token  │
│   Storage)      │
└─────────────────┘
```

---

## Component Details

### 1. Backend Authentication (`churn/auth_urls.py`)

#### CustomTokenObtainPairSerializer
- **Purpose**: Validates user credentials and generates JWT tokens
- **Key Methods**:
  - `validate()`: Authenticates email/password against database
  - `get_token()`: Generates refresh and access tokens with custom claims

**Features**:
- Email-based authentication (not username)
- Password verification using Django's `check_password()`
- User active status validation
- Comprehensive error messages
- Structured logging for debugging

#### CustomTokenObtainPairView
- **Purpose**: REST API endpoint for token generation
- **Endpoint**: `POST /api/token/`
- **Request Payload**:
  ```json
  {
    "email": "admin@nyaradzo.co.zw",
    "password": "SecurePassword123!"
  }
  ```
- **Success Response (200)**:
  ```json
  {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
  ```
- **Error Response (400/401)**:
  ```json
  {
    "error": "No account found with this email address."
  }
  ```

### 2. Frontend Authentication (`src/lib/api.ts`)

#### ApiService Class
- **Purpose**: Centralized HTTP client with automatic JWT token management
- **Key Features**:
  - Automatic token injection in request headers
  - Transparent token refresh on 401 responses
  - Queue failed requests during token refresh
  - Structured error handling

**Token Storage**:
```typescript
const ACCESS_TOKEN_KEY = 'auth_access_token';       // ~15min TTL
const REFRESH_TOKEN_KEY = 'auth_refresh_token';     // ~7 day TTL
```

**Request Interceptor Flow**:
```
1. Get access token from localStorage
2. If token exists, add to Authorization header
3. Send request with Bearer token
```

**Response Interceptor Flow**:
```
1. If response is 401 (Unauthorized):
   a. Check if token refresh already in progress
   b. If yes, queue the request
   c. If no:
      - Attempt to refresh token
      - Retry original request with new token
      - Process queued requests
2. If refresh fails:
   - Clear tokens
   - Log user out
   - Redirect to login
```

#### login() Method
- Sends credentials to backend
- Stores returned tokens in localStorage
- Fetches user profile from `/api/v1/users/me/`
- Returns user data to AuthContext

#### logout() Method
- Clears tokens from localStorage
- Clears Authorization header
- No backend call required (stateless JWT)

### 3. Frontend Auth Context (`src/contexts/AuthContext.tsx`)

#### AuthContext State
```typescript
interface AuthContextType {
  user: User | null;              // Current user info
  isAuthenticated: boolean;       // Token exists & valid
  isLoading: boolean;            // Auth check in progress
  login: (credentials) => Promise<void>;
  logout: () => void;
  error: string | null;          // Auth errors
  fieldErrors: Record<string, string[]>;
  clearError: () => void;
}
```

#### checkAuthStatus()
- Called on app initialization
- Checks if token exists in localStorage
- Fetches user profile if token valid
- Handles token validation errors

#### useAuth Hook
- Provides access to auth state/methods
- Throws error if used outside AuthProvider

### 4. Protected Routes (`src/components/ProtectedRoute.tsx`)

**Flow**:
```
1. Check isLoading
   ├─ True  → Show loading spinner
   └─ False → Continue

2. Check isAuthenticated
   ├─ True  → Render protected component
   └─ False → Redirect to login with "from" state
```

The `from` state allows redirect back to original page after login.

---

## JWT Token Structure

### Access Token (Short-lived: 8 hours)
```json
{
  "token_type": "access",
  "exp": 1234567890,
  "iat": 1234567890,
  "jti": "abc123...",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "admin@nyaradzo.co.zw",
  "role": "ADMIN",
  "username": "admin"
}
```

### Refresh Token (Long-lived: 7 days)
```json
{
  "token_type": "refresh",
  "exp": 1234567890,
  "iat": 1234567890,
  "jti": "def456...",
  "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## Security Considerations

### ✓ Implemented
- [ ] Password hashing (Django's PBKDF2-SHA256)
- [ ] Secure token generation (cryptographically random)
- [ ] Token expiration (access: 8h, refresh: 7d)
- [ ] HttpOnly cookies NOT used (SPA compatibility)
- [ ] CORS validation (specific allowed origins)
- [ ] User active status validation
- [ ] Comprehensive error logging

### ⚠️ Production Considerations
- [ ] **HTTPS Required**: Always use HTTPS in production
- [ ] **Secure Cookies**: Consider storing tokens in secure HttpOnly cookies
- [ ] **Token Rotation**: Implement token rotation on refresh
- [ ] **Rate Limiting**: Limit login attempts (already configured: 100/hour for anon)
- [ ] **Audit Logging**: Log all authentication events
- [ ] **2FA**: Consider adding two-factor authentication
- [ ] **CSRF Protection**: Verify CSRF tokens for state-changing operations

---

## Configuration

### Django Settings (`settings.py`)

```python
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=8),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",      # React frontend
    "http://localhost:5173",      # Vite dev server
    "http://127.0.0.1:8000",      # Direct API testing
]

CORS_ALLOW_CREDENTIALS = True
```

### REST Framework Settings

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",  # Override per view/viewset
    ],
}
```

---

## API Endpoints

### Authentication Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/token/` | Login (email + password → tokens) |
| POST | `/api/token/refresh/` | Refresh access token |
| GET | `/api/v1/users/me/` | Get current user profile |

### Protected Endpoints (Require Authorization Header)

All endpoints under `/api/v1/` require valid JWT token:

```bash
Authorization: Bearer <access_token>
```

Examples:
- `GET /api/v1/users/`
- `GET /api/v1/customers/`
- `POST /api/v1/policies/`
- `GET /api/v1/predictions/batch/{id}/`

---

## Error Handling

### Backend Error Responses

#### 400 Bad Request (Invalid Credentials)
```json
{
  "error": "No account found with this email address."
}
```

#### 401 Unauthorized (Invalid/Expired Token)
```json
{
  "detail": "Given token not valid for any token type"
}
```

#### 403 Forbidden (Insufficient Permissions)
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### Frontend Error Handling

The ApiService class provides structured error handling:

```typescript
interface ApiError {
  message: string;           // User-friendly message
  status: number;            // HTTP status code
  errors?: Record<string, string[]>;  // Field-specific errors
}
```

---

## Usage Examples

### Backend: Creating a Test User

```python
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.create_user(
    username='admin',
    email='admin@nyaradzo.co.zw',
    password='SecurePassword123!',
    first_name='Admin',
    last_name='User',
    role='ADMIN',
    is_active=True
)
```

### Frontend: Using useAuth Hook

```typescript
import { useAuth } from '@/contexts/AuthContext';

function MyComponent() {
  const { user, isAuthenticated, login, logout } = useAuth();
  
  if (!isAuthenticated) {
    return <div>Not logged in</div>;
  }
  
  return (
    <div>
      <p>Welcome, {user?.email}</p>
      <button onClick={logout}>Logout</button>
    </div>
  );
}
```

### Frontend: Making Authenticated API Calls

```typescript
import { apiService } from '@/lib/api';

// Tokens are automatically injected by interceptor
const response = await apiService.get('/api/v1/customers/');
```

### Frontend: Manual Token Refresh

The framework handles this automatically, but you can check:

```typescript
const isAuthenticated = apiService.isAuthenticated();
```

---

## Testing

### Run Authentication Tests

```bash
# From Backend directory
python manage.py shell < test_authentication.py
```

**Test Coverage**:
1. User creation
2. Email-based login
3. Token generation validation
4. Protected endpoint access
5. Token refresh mechanism
6. Invalid token rejection
7. Wrong credentials handling
8. Non-existent user handling

### Manual Testing with cURL

```bash
# 1. Login
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@nyaradzo.co.zw","password":"SecurePassword123!"}'

# 2. Use token
curl -X GET http://localhost:8000/api/v1/users/me/ \
  -H "Authorization: Bearer <access_token>"

# 3. Refresh token
curl -X POST http://localhost:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh":"<refresh_token>"}'
```

---

## Troubleshooting

### Issue: 401 Unauthorized on Protected Endpoints

**Causes**:
1. Token not included in request
2. Token expired
3. Token malformed
4. User inactive

**Solutions**:
- Verify Authorization header: `Authorization: Bearer <token>`
- Check token expiration: 8 hours for access token
- Re-login to get fresh tokens
- Verify user account is active

### Issue: CORS Error During Login

**Causes**:
1. Frontend origin not in CORS_ALLOWED_ORIGINS
2. Credentials not enabled in frontend

**Solutions**:
- Add frontend origin to `settings.py` CORS_ALLOWED_ORIGINS
- Ensure `CORS_ALLOW_CREDENTIALS = True`
- Check browser console for specific error

### Issue: Token Refresh Fails

**Causes**:
1. Refresh token expired (> 7 days)
2. Refresh token revoked
3. User account deleted

**Solutions**:
- Re-login to get new tokens
- Check token expiration: `7 days` for refresh token
- Verify user account exists and is active

### Issue: Network Error on Login

**Causes**:
1. Backend not running
2. CORS misconfiguration
3. Network connectivity issue
4. Firewall blocking requests

**Solutions**:
- Start backend: `python manage.py runserver`
- Verify backend listening on correct port (8000)
- Check CORS configuration in settings.py
- Check browser network tab for actual error

---

## Future Enhancements

1. **Two-Factor Authentication (2FA)**
   - SMS or authenticator app
   - Recovery codes

2. **Social Authentication**
   - Google OAuth
   - Microsoft OAuth

3. **Session Management**
   - List active sessions
   - Revoke specific sessions
   - Concurrent login limits

4. **Password Management**
   - Password reset via email
   - Password expiration policies
   - Password history

5. **Audit Logging**
   - Track all login/logout events
   - IP address logging
   - Device fingerprinting

6. **Advanced Security**
   - Rate limiting per user
   - Geo-blocking
   - Anomaly detection

---

## Support & Debugging

### Enable Debug Logging

```python
# In Django settings.py
LOGGING = {
    'loggers': {
        'churn.auth_urls': {
            'level': 'DEBUG',  # Changed from INFO
        },
    }
}
```

### Check Frontend Console

Open browser DevTools (F12) → Console tab to view:
- Login attempts and responses
- Token storage/retrieval
- API request/response logs
- Authentication errors

### Backend Logs

```bash
# View real-time logs
tail -f Backend/debug.log
```

---

## Summary

The authentication system provides:

✅ **Secure**: JWT-based, hashed passwords, token expiration  
✅ **Scalable**: Stateless, horizontal scaling friendly  
✅ **User-Friendly**: Email-based login, smooth token refresh  
✅ **Production-Ready**: Error handling, logging, CORS configuration  
✅ **Well-Documented**: Clear code comments, this documentation  

For questions or issues, check the troubleshooting section above or review the test suite output.
