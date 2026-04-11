# User Management & Authentication System
## Django Admin Integration Guide

**Version:** 2.0.0  
**Last Updated:** April 2, 2025  
**Status:** ✅ Production Ready

---

## 📋 Overview

This guide covers the complete user management system for the Nyaradzo Assurance Management System, including:
- User creation via Django Admin panel
- Password security and hashing
- Password reset procedures
- Frontend login integration
- Role-based access control

---

## 🏗️ Architecture

### User Model
The system uses a **custom User model** that extends Django's `AbstractUser`:

```python
class User(AbstractUser):
    """Extended user model with roles and organization fields."""
    
    # Core fields (inherited from AbstractUser)
    username          # Required, unique
    email             # Required, unique  
    password          # Hashed (PBKDF2-SHA256)
    first_name        # User's first name
    last_name         # User's last name
    
    # Custom fields
    role              # SUPERUSER, ADMIN, UNDERWRITER, etc.
    phone             # Contact phone number
    department        # Organization department
    is_active         # Account status (True/False)
    is_staff          # Django admin access
    is_superuser      # Full system access
```

### Authentication Method
The system uses **email-based authentication**:
- `USERNAME_FIELD = 'email'` (configured in User model)
- Users authenticate with **email + password**, not username + password
- Backend API endpoint: `POST /api/v1/auth/token/obtain/`

---

## ✅ Password Security

### Password Hashing
All passwords are automatically hashed using **PBKDF2-SHA256**:

```
pbkdf2_sha256$600000$<salt>$<hash>
```

**Why this matters:**
- ✓ Passwords are NEVER stored in plaintext
- ✓ Even administrators CANNOT see user passwords
- ✓ Passwords are verified through secure comparison
- ✓ Meets enterprise security standards

### Password Verification Flow
```
User enters password
    ↓
Backend receives password (over HTTPS)
    ↓
System uses user.check_password(input_password)
    ↓
Django compares hashed input with stored hash
    ↓
Return True/False (no plaintext comparison)
```

---

## 🔐 Creating Users via Django Admin

### Step 1: Access Django Admin
```
1. Go to: http://localhost:8000/admin/
2. Login with superuser account
3. Navigate to "System Users" section
```

### Step 2: Create New User
**Option A: Using "Add User" Form** (Recommended)

1. Click **"+ Add System User"** button
2. Fill in the form with:
   ```
   Username:    [Unique internal identifier]
   Email:       [Unique email address]
   Password:    [Enter new password once]
   Password (again): [Confirm password]
   First Name:  [User's first name]
   Last Name:   [User's last name]
   ```
3. Scroll down and configure:
   ```
   Role:        [Select from dropdown]
   Department:  [User's department]
   Phone:       [Contact number]
   Is Active:   [Check to enable account]
   Is Staff:    [Check for admin access]
   ```
4. Click **"Save"**

### Step 3: Password Validation
Django automatically validates passwords:
```
✓ Minimum 8 characters
✓ Not entirely numeric
✓ Not similar to username
✓ Strength checking enabled
```

If validation fails, you'll see clear error messages explaining the requirement.

### Example: Creating an Underwriter User
```
Username:     underwriter_jane
Email:        jane.underwriter@nyaradzo.co.zw
Password:     SecureUnderwriter2025!
First Name:   Jane
Last Name:    Underwriter
Role:         UNDERWRITER
Department:   Underwriting
Phone:        +263771234567
Is Active:    ✓ Checked
Is Staff:     ✓ Checked
```

---

## 🔄 Password Reset (Admin Password Change)

### Scenario 1: User Forgot Password

**Steps:**
1. Go to Django Admin → "System Users"
2. Find the user by searching email or name
3. Click on the user to edit
4. Click on the password field (shows: "**Raw passwords are not stored...**")
5. Click **"this form"** link to access password reset form
6. Enter new password twice
7. Click **"Change Password"**
8. User can now login with new password

### Scenario 2: Direct Password Change

1. Go to user edit form
2. In the **"Password"** section, enter new password
3. Click **"Save and continue editing"**
4. Password is immediately updated (hashed automatically)

### Scenario 3: Account Deactivation

1. Open user in admin
2. Uncheck **"Is Active"** checkbox
3. Click **"Save"**
4. User cannot login (system rejects inactive accounts)

To reactivate:
1. Check **"Is Active"** checkbox
2. Click **"Save"**

---

## 🚀 Frontend Login Integration

### Login Form

**Location:** `Frontend/src/pages/LoginPage.tsx`

**Prerequisites:**
- User must exist in Django admin
- User must be active (`is_active = True`)
- User must have correct password

### Login Flow

```
User enters credentials
    ↓
Frontend validates email format (Zod validation)
    ↓
Frontend sends POST to /api/v1/auth/token/obtain/
    ├─ Request body: { email: "...", password: "..." }
    │
    └─ Backend processes:
        ├─ Looks up user by email
        ├─ Verifies password hash matches
        ├─ Checks if user is active
        │
        └─ Response:
            ├─ Success: { access, refresh, user }
            └─ Failure: { message, errors }
    ↓
Frontend stores JWT tokens in localStorage
    ↓
Frontend redirects to dashboard
```

### Error Messages User Receives

| Scenario | Message | Where |
|----------|---------|-------|
| Invalid email format | "Please enter a valid email address" | Email field |
| Email not registered | "Email is not registered" | Email field |
| Wrong password | "Password is incorrect" | Password field |
| Both wrong | Error on both fields | Both fields |
| Account inactive | "Your account has been deactivated" | General error |

### Test Login Credentials

After running admin tests, you can use:

```
Email:    demo@nyaradzo.co.zw
Password: Demo@Nyaradzo2025
```

**To test with different users:**
1. Create user in Django admin (as described above)
2. Use email + password in frontend login form
3. System will authenticate and generate JWT tokens

---

## 🛡️ User Roles & Permissions

### Available Roles

| Role | Description | Permissions |
|------|-------------|-------------|
| SUPERUSER | System administrator | Full access, user management |
| ADMIN | Administrator | Most operations, reports |
| UNDERWRITER | Underwriting officer | Policy underwriting, decisions |
| CLAIMS_OFFICER | Claims processor | Claims processing, approvals |
| FINANCE_OFFICER | Finance staff | Payment tracking, accounting |
| AGENT | Sales agent | Customer registration, policy sales |
| READ_ONLY | Viewer | View-only access to reports |

### Assigning Roles

In Django Admin:
1. Edit user
2. In **"Role & Department"** section
3. Select role from dropdown
4. Click **"Save"**

---

## ⚙️ Django Admin Configuration

### What We Implemented

The system now includes a **professional UserAdmin** with:

✅ **Proper Form Handling**
- Uses `UserCreationForm` for new users
- Uses `UserChangeForm` for existing users
- Automatic password hashing via `set_password()`

✅ **Clear Password Management**
- New users: Password is required
- Existing users: Password field shows it's hashed
- Password reset: Uses Django's built-in mechanism

✅ **User-Friendly Interface**
- Organized fieldsets for: Personal Info, Role, Permissions, Audit
- Search by: username, email, first name, last name
- Filter by: role, department, active status
- Readonly fields: date_joined, created_at, updated_at

✅ **Security Features**
- Passwords automatically hashed with PBKDF2-SHA256
- Password not visible in list view
- Audit trail: creation date, update date, last login

### Admin List View

**Displayed columns:**
- Username
- Email
- First Name
- Last Name
- Role
- Department
- Is Active (✓ or ✗)
- Date Joined

**Search enabled for:**
- Username
- Email
- First/Last Name

**Filters available:**
- Role (all role types)
- Department
- Is Active

---

## 🧪 Testing & Verification

### Automated Tests
Run the comprehensive test suite:

```bash
cd Backend
source env/bin/activate
python test_user_management.py
```

**Tests include:**
1. ✅ User creation with password hashing
2. ✅ Email-based authentication
3. ✅ Password change/reset functionality
4. ✅ Admin panel simulation
5. ✅ Frontend integration readiness

### Manual Testing

**Create a test user:**
```bash
cd Backend
source env/bin/activate
python manage.py shell
```

```python
from django.contrib.auth import get_user_model, authenticate

User = get_user_model()

# Create user
user = User.objects.create_user(
    username='testuser',
    email='test@nyaradzo.co.zw',
    password='TestPassword123!',
    first_name='Test',
    last_name='User',
    role='ADMIN',
    is_active=True
)

# Verify authentication
auth_user = authenticate(username='test@nyaradzo.co.zw', password='TestPassword123!')
print("Login successful!" if auth_user else "Login failed!")
```

---

## 🔍 Troubleshooting

### User Cannot Login

**Check 1:** User exists in database
```sql
SELECT email, is_active FROM auth_user WHERE email = 'user@nyaradzo.co.zw';
```

**Check 2:** User is active
- Go to Django Admin
- Find user
- Verify "Is Active" is checked

**Check 3:** Password is correct
- Use Django admin password reset
- Set new password
- User tries login again

### Password Reset Not Working

**Solution:**
1. Go to Django Admin
2. Find user in "System Users"
3. Click "this form" link next to password field
4. Enter new password
5. Click "Change Password"

### User Created But Cannot Login

**Possible causes:**
1. Email is incorrect in form
2. Password was not saved
3. `is_active` is unchecked

**Solution:**
1. Edit user in Django Admin
2. Verify email is correct
3. Check `is_active` is checked
4. Reset password using password change form

---

## 📊 Database Schema

### auth_user table

```
Column          | Type      | Constraints
─────────────────────────────────────────
id              | UUID      | PRIMARY KEY
username        | VARCHAR   | UNIQUE, NOT NULL
email           | VARCHAR   | UNIQUE, NOT NULL
password        | VARCHAR   | NOT NULL (hashed)
first_name      | VARCHAR   |
last_name       | VARCHAR   |
role            | VARCHAR   | DEFAULT: READ_ONLY
phone           | VARCHAR   |
department      | VARCHAR   |
is_active       | BOOLEAN   | DEFAULT: True
is_staff        | BOOLEAN   | DEFAULT: False
is_superuser    | BOOLEAN   | DEFAULT: False
date_joined     | TIMESTAMP | AUTO
last_login      | TIMESTAMP |
created_at      | TIMESTAMP | AUTO
updated_at      | TIMESTAMP | AUTO
```

---

## 🚀 Best Practices

### For Administrators

1. **Regular Password Audits**
   - Review inactive users quarterly
   - Remove old test accounts

2. **New Employee Setup**
   - Create user in Django admin
   - Set appropriate role
   - Share login email (password reset on first login)

3. **Security**
   - Always use strong passwords (8+ chars, mixed case, numbers, symbols)
   - Deactivate accounts rather than delete
   - Keep audit trails enabled

4. **Documentation**
   - Document role assignments
   - Note password reset dates
   - Maintain user directory

### For Users

1. **Login Process**
   - Use your assigned email address
   - Correct password (case-sensitive)
   - Check for typos in both fields

2. **Password Security**
   - Never share password
   - Don't write password in messages
   - Request reset if you forget

3. **Account Activity**
   - Logout when leaving desk
   - Report unusual activity immediately
   - Update profile information regularly

---

## 🔐 Security Summary

### What's Protected
✅ Passwords are hashed with PBKDF2-SHA256  
✅ Passwords never stored in plaintext  
✅ JWT tokens for API authentication  
✅ Session-based Django admin access  
✅ HTTPS required for production  
✅ Audit trail for user actions  

### What's Not Protected (Added Security Needed)
⚠️ Password reset emails (use email service provider)  
⚠️ API rate limiting (implement throttling)  
⚠️ 2FA/MFA (implement if needed)  

---

## 📝 Admin Checklist

Before going to production, ensure:

- [ ] Superuser account created and password secured
- [ ] All staff users created with appropriate roles
- [ ] Password policy enforced (min 8 chars)
- [ ] Email verification enabled (optional)
- [ ] Audit logging enabled
- [ ] Regular backups configured
- [ ] Test login works with frontend
- [ ] Password reset tested
- [ ] Inactive accounts deactivated
- [ ] API authentication verified

---

## 📞 Support

**For issues, check:**
1. User is in Django admin database
2. User is_active = True
3. Email and password are correct
4. Django development server is running
5. Frontend is pointing to correct API URL

**Test authentication directly:**
```bash
cd Backend
python manage.py shell
from django.contrib.auth import authenticate
user = authenticate(username='email@example.com', password='password')
print("OK" if user else "FAILED")
```

---

## 📚 Related Documentation

- [AUTHENTICATION.md](AUTHENTICATION.md) - Full authentication system overview
- [README.md](Backend/README.md) - Backend setup instructions  
- [DEVELOPER_REFERENCE.md](DEVELOPER_REFERENCE.md) - Full API reference

---

**Generated automatically by the Nyaradzo Engineering Team**  
**Last tested:** April 2, 2025  
✅ All tests passing - System ready for production
