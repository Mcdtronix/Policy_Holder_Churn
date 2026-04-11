# Authentication Implementation & Best Practices Guide

**Status**: ✅ IMPLEMENTATION COMPLETE  
**Last Updated**: March 29, 2026  
**Target Audience**: Developers, QA, DevOps

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Architecture Overview](#architecture-overview)
3. [Login Flow (Step-by-Step)](#login-flow)
4. [Error Handling](#error-handling)
5. [Security Features](#security-features)
6. [Testing](#testing)
7. [Common Issues & Solutions](#troubleshooting)
8. [Best Practices](#best-practices)

---

## 🚀 Quick Start

### Backend Setup

```bash
# 1. Apply migrations
cd Backend
python manage.py makemigrations
python manage.py migrate

# 2. Create a test user
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.create_user(
...     username='admin',
...     email='admin@nyaradzo.co.zw',
...     password='SecurePass123!',
...     first_name='John',
...     last_name='Doe',
...     is_active=True,
...     role='ADMIN'
... )
>>> exit()

# 3. Run development server
python manage.py runserver 0.0.0.0:8000
```

### Frontend Setup

```bash
# 1. Install dependencies
cd Frontend
npm install

# 2. Set environment variables (.env)
VITE_API_URL=http://localhost:8000

# 3. Run development server
npm run dev
```

---

## 🏗️ Architecture Overview

### Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    USER LOGIN FLOW                       │
└─────────────────────────────────────────────────────────┘

Frontend (React)                    Backend (Django)
─────────────────                   ──────────────────

1. User enters
   email & password
   │
   ├─► Validation
   │   (Zod schema)
   │
   ├─► POST /api/token/
   │   ────────────────►  CustomTokenObtainPairView
   │                      │
   │                      ├─► Validate email exists
   │                      ├─► Check password hash
   │                      ├─► Verify is_active
   │                      ├─► Log attempt (success/fail)
   │                      └─► Generate JWT tokens
   │
   ◄─────────────────────  Response:
   │                       {
   │                         "access": "eyJ...",
   │                         "refresh": "eyJ...",
   │                         "user": {
   │                           "id": "123",
   │                           "email": "admin@...",
   │                           "role": "ADMIN",
   │                           "first_name": "John",
   │                           "last_name": "Doe"
   │                         }
   │                       }
   │
   ├─► Store tokens
   │   (localStorage)
   │
   ├─► Set auth headers
   │   (Bearer token)
   │
   └──► Redirect to
        /dashboard

Protected Routes
────────────────
┌─────────────────────────┐
│  ProtectedRoute         │
│  checks isAuthenticated │
│  and redirects to login │
│  if needed              │
└─────────────────────────┘

Token Refresh on 401
────────────────────
┌────────────────────────────────────────┐
│ 1. Request made with expired token     │
│ 2. API interceptor catches 401         │
│ 3. POST /api/token/refresh/            │
│ 4. Get new access token                │
│ 5. Retry original request with new key │
└────────────────────────────────────────┘
```

---

## 🔄 Login Flow (Step-by-Step)

### Step 1: Frontend Validation

**File**: `Frontend/src/pages/LoginPage.tsx`

```typescript
// Zod schema validates:
const loginSchema = z.object({
  email: z.string()
    .trim()
    .email('Please enter a valid email address')
    .max(255),
  password: z.string()
    .min(6, 'Password must be at least 6 characters')
    .max(128),
});
```

**Checks**:
- ✓ Email format valid
- ✓ Password length (6+ chars)
- ✓ Not empty fields

### Step 2: Send Login Request

**File**: `Frontend/src/lib/api.ts`

```typescript
async login(credentials: LoginCredentials): Promise<User> {
  const response = await axios.post(
    `${API_BASE_URL}/api/token/`,
    credentials
  );
  
  const tokens: AuthTokens = {
    access: response.data.access,
    refresh: response.data.refresh
  };
  
  this.setTokens(tokens);  // Store in localStorage
  return response.data.user;
}
```

### Step 3: Backend Authentication

**File**: `Backend/churn/auth_urls.py`

#### CustomTokenObtainPairSerializer

```python
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    # Validates email + password
    # Returns user object with JWT tokens
    # Handles errors: invalid email, wrong password, inactive user
```

#### CustomTokenObtainPairView

```python
class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request):
        # 1. Validate credentials
        # 2. Log attempt (LoginAttempt model)
        # 3. Generate JWT tokens
        # 4. Return tokens + user data
        # 5. Handle errors with proper status codes
```

### Step 4: Response Processing

**Response Format** (Success):
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "admin@nyaradzo.co.zw",
    "username": "admin",
    "first_name": "John",
    "last_name": "Doe",
    "role": "ADMIN",
    "is_active": true,
    "department": "Management"
  }
}
```

### Step 5: Store Tokens

```typescript
// Frontend stores in localStorage
localStorage.setItem('auth_access_token', accessToken);
localStorage.setItem('auth_refresh_token', refreshToken);
```

### Step 6: Set Authorization Header

```typescript
// All subsequent requests include:
headers: {
  Authorization: `Bearer ${accessToken}`
}
```

### Step 7: Redirect to Dashboard

```typescript
navigate('/dashboard', { replace: true });
```

---

## 🚨 Error Handling

### Error Response Format

**400 Bad Request** (Validation Error):
```json
{
  "error": "Incorrect password",
  "status": "authentication_failed",
  "email": "admin@nyaradzo.co.zw"
}
```

**401 Unauthorized** (Auth Failed):
```json
{
  "error": "No account found with this email address",
  "status": "user_not_found"
}
```

### Frontend Error Handling

```typescript
// In LoginPage.tsx
try {
  await login(data);
  toast.success('Welcome!')
  navigate('/dashboard');
} catch (err) {
  // Error automatically shown in form
  // fieldErrors populated from response
}
```

### Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| Invalid email format | Bad email pattern | Enter valid email (xx@yy.zz) |
| No account found | Email doesn't exist | Check email spelling |
| Incorrect password | Wrong password | Check caps lock, try again |
| Account inactive | User disabled | Contact administrator |
| Network error | Backend offline | Start backend: `python manage.py runserver` |
| Invalid credentials | Repeated failures | Wait 15 min, check rate limiting |

---

## 🔒 Security Features

### 1. JWT Token Configuration

**Access Token**:
- Lifetime: 8 hours
- Used for API requests
- Should be kept secure

**Refresh Token**:
- Lifetime: 7 days
- Used to get new access token
- Rotated on refresh (new token on each refresh)

**Location**: `Backend/nyaradzo_backend/settings.py`

```python
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=8),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}
```

### 2. Password Validation

**Frontend**: Basic validation
```typescript
password: z.string().min(6).max(128)
```

**Backend**: Enhanced validation
- Minimum 8 characters
- Uppercase + lowercase required
- Numbers required
- Special characters required
- No common patterns

**Validator**: `Backend/nyaradzo_backend/validators.py`

### 3. Rate Limiting

**Configuration**:
```python
DEFAULT_THROTTLE_RATES = {
    "anon": "100/hour",      # 100 requests per hour for anonymous users
    "user": "1000/hour",     # 1000 requests per hour for authenticated users
}
```

**Effect**: Prevents brute force attacks on login

### 4. Security Headers

**Added by Middleware**:
```
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

### 5. Audit Logging

**Model**: `Backend/churn/models.py::LoginAttempt`

**Tracks**:
- Email address
- Success (true/false/null for logout)
- IP address
- User agent
- Error message (if failed)
- Timestamp

**Usage**:
```python
# Get failed attempts for user
failed = LoginAttempt.get_failed_attempts(
    email='admin@nyaradzo.co.zw',
    minutes=30
)

# Get attempts from IP
failed_by_ip = LoginAttempt.get_failed_attempts_by_ip(
    ip_address='192.168.1.1',
    minutes=30
)
```

### 6. CORS Configuration

**Whitelist Approach**:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8000",
]
CORS_ALLOW_CREDENTIALS = True
```

**Production**: Update with actual domain

---

## 🧪 Testing

### Run Tests

```bash
# Run all authentication tests
cd Backend
python manage.py test churn.tests.test_authentication

# Run specific test
python manage.py test churn.tests.test_authentication.AuthenticationTestCase.test_login_success

# With verbose output
python manage.py test churn.tests.test_authentication -v 2
```

### Test Coverage

- ✅ Login with valid credentials
- ✅ Login with invalid email
- ✅ Login with invalid password
- ✅ Login with inactive user
- ✅ Missing email/password
- ✅ Token refresh
- ✅ Protected endpoints
- ✅ Invalid tokens
- ✅ Logout
- ✅ Security headers
- ✅ Audit trail (success/failure)

### Manual Testing Steps

**1. Reset Database**
```bash
python manage.py migrate
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.create_user(
...     username='testadmin',
...     email='test@nyaradzo.co.zw',
...     password='TestPass123!',
...     is_active=True,
...     role='ADMIN'
... )
>>> exit()
```

**2. Start Backend**
```bash
python manage.py runserver
# Navigate to http://127.0.0.1:8000/api/docs/
```

**3. Start Frontend**
```bash
npm run dev
# Navigate to http://localhost:5173/
```

**4. Test Login**
- Email: `test@nyaradzo.co.zw`
- Password: `TestPass123!`
- Expected: Redirect to dashboard

**5. Test Invalid Credentials**
- Email: `wrong@example.com`
- Error: "No account found..."

**6. Test Logout**
- Click logout in dashboard
- Should redirect to login

---

## 🔧 Troubleshooting

### Issue: "Network Error - Backend Not Running"

**Solution**:
```bash
# Make sure backend is running
python manage.py runserver 0.0.0.0:8000

# Check backend is accessible
curl http://localhost:8000/api/auth/health/

# Should return:
# {"status": "healthy", "service": "authentication",...}
```

### Issue: CORS Error

**Solution**:
```python
# In Backend/nyaradzo_backend/settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Add your frontend URL
    "http://localhost:3000",
]
CORS_ALLOW_CREDENTIALS = True
```

### Issue: "Invalid Email" During Login

**Solution**:
```typescript
// Email validation is strict
// Valid: admin@nyaradzo.co.zw
// Invalid: admin@.co.zw (no domain)
// Invalid: @nyaradzo.co.zw (no local part)
```

### Issue: "Token Expired"

**Solution**:
```typescript
// Frontend automatically refreshes tokens
// If manual refresh needed:
POST /api/token/refresh/
{
  "refresh": "eyJ..."
}
```

### Issue: Login Works, But Can't Access Dashboard

**Causes & Fixes**:

1. **Auth context not initialized**
   ```typescript
   // Make sure AuthProvider wraps App
   <AuthProvider>
     <App />
   </AuthProvider>
   ```

2. **Token not stored in localStorage**
   ```bash
   # Check DevTools > Application > Local Storage
   # Should have: auth_access_token, auth_refresh_token
   ```

3. **ProtectedRoute not checking token**
   ```typescript
   // Verify ProtectedRoute.tsx checks isAuthenticated
   if (!isAuthenticated) {
     return <Navigate to="/" />
   }
   ```

---

## ✅ Best Practices

### 1. Password Management

**DO**:
- ✓ Enforce 8+ character passwords
- ✓ Require mixed character types
- ✓ Hash passwords (Django does this)
- ✓ Never log passwords

**DON'T**:
- ✗ Send passwords in URL parameters
- ✗ Store passwords in plain text
- ✗ Log passwords anywhere

### 2. Token Management

**DO**:
- ✓ Store tokens in secure http-only cookies (production)
- ✓ Use Bearer token in Authorization header
- ✓ Implement token rotation
- ✓ Refresh tokens before expiry

**DON'T**:
- ✗ Store tokens in sessionStorage (XSS vulnerable)
- ✗ Pass tokens in query parameters
- ✗ Use same token for multiple purposes
- ✗ Disable HTTPS in production

### 3. Error Messages

**DO**:
- ✓ Give specific errors ("Incorrect password")
- ✓ Help users solve problems

**DON'T**:
- ✗ Reveal system internals ("SQL error at...")
- ✗ Confirm account existence to attackers

### 4. Logging & Monitoring

**DO**:
- ✓ Log all login attempts (success & failure)
- ✓ Monitor for brute force patterns
- ✓ Alert on suspicious activities
- ✓ Keep audit trail for compliance

**DON'T**:
- ✗ Log sensitive data (passwords, tokens)
- ✗ Discard audit logs prematurely

### 5. HTTPS & Security

**Development**:
```
http://localhost:* (OK for dev only)
```

**Production**:
```python
# In settings.py
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
```

### 6. CORS Configuration

**Never Use Wildcard** ❌
```python
CORS_ALLOW_ALL_ORIGINS = True  # DANGEROUS!
```

**Always Whitelist** ✅
```python
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://app.yourdomain.com",
]
```

### 7. Rate Limiting

**Implement Brute Force Protection**:
```python
# After 5 failed attempts in 15 min, lock account
# Or increase wait time exponentially
# Or require CAPTCHA
```

### 8. Audit Recommendations

**Never Miss**:
1. Who logged in (email)
2. When they logged in (timestamp)
3. Where from (IP address)
4. Success or failure
5. Error reason (if failed)

---

## 📞 Support & Additional Resources

### Getting Help

1. **Read the audit report**: `AUTHENTICATION_SECURITY_AUDIT.md`
2. **Check the models**: `Backend/churn/models.py` (LoginAttempt)
3. **Review tests**: `Backend/churn/tests/test_authentication.py`
4. **Check logs**: Backend logs include detailed auth trace info

### Production Deployment Checklist

- [ ] Set `DEBUG = False`
- [ ] Change `SECRET_KEY`
- [ ] Update `ALLOWED_HOSTS`
- [ ] Update `CORS_ALLOWED_ORIGINS`
- [ ] Switch to PostgreSQL
- [ ] Enable HTTPS
- [ ] Set up environment variables
- [ ] Configure secure cookies
- [ ] Set up monitoring
- [ ] Test in staging first

---

**Report**: v1.0 | March 29, 2026  
**Contact**: security@nyaradzo.co.zw
