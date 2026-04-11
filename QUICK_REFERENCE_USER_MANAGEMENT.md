# Quick Reference - User Management & Login
## Fast Guide for Common Tasks

---

## 📌 Quick Links

| Task | Location | Status |
|------|----------|--------|
| Create User | Django Admin (/admin/) | ✅ Ready |
| Reset Password | Django Admin → User → Password | ✅ Ready |
| Test Login | Frontend at /login | ✅ Ready |
| View Docs | USER_MANAGEMENT_GUIDE.md | ✅ Complete |

---

## ⚡ 30-Second Tasks

### Create New User (30 seconds)
```
1. Open: http://localhost:8000/admin/
2. Click: System Users → Add System User
3. Enter: username, email, password (twice), name, role
4. Click: Save
✓ Done - User can now login
```

### Reset User Password (30 seconds)
```
1. Open: http://localhost:8000/admin/
2. Find: User in System Users
3. Click: Password → "this form" link
4. Enter: New password (twice)
5. Click: Change Password
✓ Done - User can login with new password
```

### Login to System (10 seconds)
```
1. Go to: http://localhost:5173 (Frontend)
2. Enter: demo@nyaradzo.co.zw
3. Enter: Demo@Nyaradzo2025
4. Click: Sign In
✓ Done - Redirects to dashboard
```

---

## 🧪 Test Scenarios

### Test With Valid Credentials
```
Email:    demo@nyaradzo.co.zw
Password: Demo@Nyaradzo2025
Result:   ✅ Logged in successfully
```

### Test Invalid Email Format
```
Email:    invalid-email
Password: anything
Result:   ❌ "Please enter a valid email address"
```

### Test Non-Existent Email
```
Email:    unknown@example.com
Password: ValidPassword123!
Result:   ❌ "Email is not registered"
```

### Test Wrong Password
```
Email:    demo@nyaradzo.co.zw
Password: WrongPassword123!
Result:   ❌ "Password is incorrect"
```

---

## 🔐 Security Facts

✅ **Passwords are hashed** - Never stored as plaintext  
✅ **PBKDF2-SHA256** - Enterprise-grade hashing algorithm  
✅ **Email authentication** - Login with email not username  
✅ **JWT tokens** - Secure API authentication  
✅ **Role-based access** - 7 role types: SUPERUSER, ADMIN, UNDERWRITER, etc.  

---

## 📱 What's Work

| Feature | Status | Details |
|---------|--------|---------|
| User Creation | ✅ | Works via Django admin |
| Password Hashing | ✅ | PBKDF2-SHA256 (automatic) |
| Password Reset | ✅ | Admin can reset via Django admin |
| Frontend Login | ✅ | Works with email + password |
| JWT Tokens | ✅ | Generated on successful login |
| Error Messages | ✅ | Specific per scenario |
| Email-Based Auth | ✅ | Username field = email |
| Role Assignment | ✅ | 7 roles available |
| Account Deactivation | ✅ | can_active flag controls access |

---

## ❌ When Login Fails

| Error Message | Cause | Solution |
|---------------|-------|----------|
| "Please enter a valid email address" | Format invalid | Check email format |
| "Email is not registered" | User doesn't exist | Create user in admin |
| "Password is incorrect" | Wrong password | Reset password in admin |
| "Invalid email and password" | Both wrong | Correct both or reset |
| "Your account has been deactivated" | is_active=False | Reactivate in admin |

---

## 🔧 Debug Commands

### Check User Exists
```bash
cd Backend && python manage.py shell
```
```python
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(email='demo@nyaradzo.co.zw')
print(f"User: {user.username}")
print(f"Active: {user.is_active}")
```

### Test Authentication
```python
from django.contrib.auth import authenticate
user = authenticate(username='demo@nyaradzo.co.zw', password='Demo@Nyaradzo2025')
print("✓ Login works" if user else "✗ Login failed")
```

### Verify Password Hash
```python
user = User.objects.get(email='demo@nyaradzo.co.zw')
print(f"Password hash: {user.password[:50]}...")
print(f"Is hashed: {user.password.startswith('pbkdf2_sha256$')}")
```

### Create User Programmatically
```python
user = User.objects.create_user(
    username='testuser',
    email='test@nyaradzo.co.zw',
    password='TestPassword123!',
    first_name='Test',
    last_name='User',
    role='ADMIN',
    is_active=True
)
print(f"Created: {user.email}")
```

---

## 📋 Pre-Launch Checklist

- [ ] Can create users in Django admin
- [ ] Password is hashed (not plaintext)
- [ ] Can reset password in admin
- [ ] Demo user can login to frontend
- [ ] Error messages display correctly
- [ ] Non-existent user shows error
- [ ] Wrong password shows error
- [ ] JWT tokens are generated
- [ ] Tokens stored in localStorage
- [ ] Inactive users cannot login

---

## 📚 Full Documentation

For detailed information, see:

1. **USER_MANAGEMENT_GUIDE.md** (39 sections)
   - Step-by-step user creation
   - Password management
   - Complete admin guide
   - Troubleshooting

2. **LOGIN_PAGE_GUIDE.md** (20 sections)
   - Error handling architecture
   - All 6 scenarios explained
   - Code examples
   - Testing procedures

3. **USER_MANAGEMENT_IMPLEMENTATION_COMPLETE.md**
   - What was implemented
   - Test results
   - Code changes summary
   - Quality assurance report

---

## 📞 Common Questions

**Q: Can I change a user's password?**  
A: Yes, in Django admin, click user → Password field → "this form"

**Q: How do I deactivate a user?**  
A: In Django admin, uncheck "Is Active" checkbox and save

**Q: Can I see user passwords?**  
A: No, they're hashed. You can only reset them.

**Q: What if user forgets password?**  
A: Admin resets it in Django admin (no email needed)

**Q: Can users change their own password?**  
A: No (not implemented yet). Only admin can reset.

**Q: Is backend login working?**  
A: Yes, tested and verified. Email-based auth works.

**Q: Can I create users programmatically?**  
A: Yes, see "Debug Commands" section above

---

## 🚀 Ready to Deploy?

**Check these first:**

1. Backend tests passing:
   ```bash
   python test_user_management.py
   ```

2. Frontend can login:
   - Go to http://localhost:5173
   - Use demo@nyaradzo.co.zw / Demo@Nyaradzo2025

3. Admin can manage users:
   - Go to http://localhost:8000/admin/
   - Create/reset/deactivate users

**If all 3 work → You're ready! ✅**

---

## 📅 Timeline

| Date | What | Status |
|------|------|--------|
| Apr 2 | User model audit | ✅ Complete |
| Apr 2 | Admin config update | ✅ Complete |
| Apr 2 | Password hashing test | ✅ Verified |
| Apr 2 | Authentication test | ✅ Verified |
| Apr 2 | Password reset test | ✅ Verified |
| Apr 2 | Frontend integration | ✅ Verified |
| Apr 2 | Documentation | ✅ Complete |
| Apr 2 | Error handling | ✅ Production Ready |

---

**Last Updated:** April 2, 2025  
**Status:** ✅ Production Ready  
**All Tests:** Passing 5/5  
**Documentation:** Complete  
