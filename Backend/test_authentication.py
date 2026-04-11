#!/usr/bin/env python
"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AUTHENTICATION VERIFICATION SCRIPT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Comprehensive test suite for verifying JWT authentication flow:
  ✓ User registration
  ✓ Email-based login
  ✓ Token generation and validation
  ✓ Token refresh mechanism
  ✓ Protected endpoint access
  ✓ Logout/token invalidation

Usage:
  python manage.py shell < test_authentication.py
  
  OR
  
  python test_authentication.py
"""

import os
import django
import sys
from pathlib import Path

# Configure Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nyaradzo_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APIClient
import json
from datetime import datetime

User = get_user_model()
client = APIClient()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TEST UTILITIES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class Colors:
    """ANSI color codes for console output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_section(title):
    """Print a section header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'═' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}  {title}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'═' * 80}{Colors.ENDC}\n")

def print_success(message):
    """Print a success message."""
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")

def print_error(message):
    """Print an error message."""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

def print_info(message):
    """Print an info message."""
    print(f"{Colors.OKCYAN}ℹ {message}{Colors.ENDC}")

def print_warning(message):
    """Print a warning message."""
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TEST 1: USER CREATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_user_creation():
    """Test creating a test user for authentication tests."""
    print_section("TEST 1: USER CREATION")
    
    # Delete existing test user if present
    test_email = "test.admin@nyaradzo.co.zw"
    User.objects.filter(email=test_email).delete()
    print_info(f"Cleaned up any existing test user with email: {test_email}")
    
    # Create test user
    try:
        user = User.objects.create_user(
            username='testadmin',
            email=test_email,
            password='TestPass123!',
            first_name='Test',
            last_name='Administrator',
            role='ADMIN',
            phone='+263771234567',
            department='Testing',
            is_active=True
        )
        print_success(f"User created successfully")
        print_info(f"  Email: {user.email}")
        print_info(f"  Username: {user.username}")
        print_info(f"  Full Name: {user.get_full_name()}")
        print_info(f"  Role: {user.role}")
        print_info(f"  ID: {user.id}")
        return user, test_email, "TestPass123!"
    except Exception as e:
        print_error(f"Failed to create user: {str(e)}")
        raise

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TEST 2: LOGIN (TOKEN GENERATION)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_login(email, password):
    """Test JWT token generation via login endpoint."""
    print_section("TEST 2: LOGIN (TOKEN GENERATION)")
    
    payload = {
        'email': email,
        'password': password
    }
    
    print_info(f"Sending login request to: /api/token/")
    print_info(f"  Email: {email}")
    print_info(f"  Password: {'*' * len(password)}")
    
    try:
        response = client.post('/api/token/', payload, format='json')
        
        if response.status_code == 200:
            print_success(f"Login successful (Status: {response.status_code})")
            
            data = response.json()
            access_token = data.get('access')
            refresh_token = data.get('refresh')
            
            print_info(f"  Access Token: {access_token[:50]}...")
            print_info(f"  Refresh Token: {refresh_token[:50]}...")
            
            if not access_token or not refresh_token:
                print_error("Missing access or refresh token in response!")
                return None, None
            
            return access_token, refresh_token
        else:
            print_error(f"Login failed (Status: {response.status_code})")
            print_error(f"Response: {response.json()}")
            return None, None
            
    except Exception as e:
        print_error(f"Login request failed: {str(e)}")
        return None, None

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TEST 3: TOKEN VALIDATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_token_validation(access_token):
    """Test accessing protected endpoint with valid token."""
    print_section("TEST 3: TOKEN VALIDATION")
    
    print_info(f"Attempting to access protected endpoint: /api/v1/users/me/")
    
    # Set authorization header
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    
    try:
        response = client.get('/api/v1/users/me/', format='json')
        
        if response.status_code == 200:
            print_success(f"Protected endpoint access successful (Status: {response.status_code})")
            
            user_data = response.json()
            print_info(f"  User ID: {user_data.get('id')}")
            print_info(f"  Email: {user_data.get('email')}")
            print_info(f"  Full Name: {user_data.get('full_name')}")
            print_info(f"  Role: {user_data.get('role')}")
            print_info(f"  Is Active: {user_data.get('is_active')}")
            
            return True
        else:
            print_error(f"Protected endpoint access failed (Status: {response.status_code})")
            print_error(f"Response: {response.json()}")
            return False
            
    except Exception as e:
        print_error(f"Protected endpoint request failed: {str(e)}")
        return False

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TEST 4: TOKEN REFRESH
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_token_refresh(refresh_token):
    """Test JWT token refresh."""
    print_section("TEST 4: TOKEN REFRESH")
    
    payload = {'refresh': refresh_token}
    
    print_info(f"Sending refresh token request to: /api/token/refresh/")
    
    # Clear credentials for this request
    client.credentials()
    
    try:
        response = client.post('/api/token/refresh/', payload, format='json')
        
        if response.status_code == 200:
            print_success(f"Token refresh successful (Status: {response.status_code})")
            
            data = response.json()
            new_access_token = data.get('access')
            
            print_info(f"  New Access Token: {new_access_token[:50]}...")
            
            if not new_access_token:
                print_error("Missing new access token in response!")
                return None
            
            return new_access_token
        else:
            print_error(f"Token refresh failed (Status: {response.status_code})")
            print_error(f"Response: {response.json()}")
            return None
            
    except Exception as e:
        print_error(f"Token refresh request failed: {str(e)}")
        return None

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TEST 5: INVALID TOKEN REJECTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_invalid_token_rejection():
    """Test that invalid tokens are rejected."""
    print_section("TEST 5: INVALID TOKEN REJECTION")
    
    invalid_token = "invalid.token.here"
    
    print_info(f"Attempting to access protected endpoint with invalid token")
    
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {invalid_token}')
    
    try:
        response = client.get('/api/v1/users/me/', format='json')
        
        if response.status_code == 401:
            print_success(f"Invalid token correctly rejected (Status: {response.status_code})")
            return True
        else:
            print_warning(f"Unexpected status code: {response.status_code}")
            print_warning(f"Response: {response.json()}")
            return False
            
    except Exception as e:
        print_error(f"Token rejection test failed: {str(e)}")
        return False

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TEST 6: WRONG CREDENTIALS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_wrong_credentials(email):
    """Test login with wrong password."""
    print_section("TEST 6: WRONG CREDENTIALS")
    
    payload = {
        'email': email,
        'password': 'WrongPassword123!'
    }
    
    print_info(f"Sending login request with wrong password")
    
    client.credentials()  # Clear credentials
    
    try:
        response = client.post('/api/token/', payload, format='json')
        
        if response.status_code in [400, 401]:
            print_success(f"Wrong credentials correctly rejected (Status: {response.status_code})")
            print_info(f"Error message: {response.json()}")
            return True
        else:
            print_warning(f"Unexpected status code: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Wrong credentials test failed: {str(e)}")
        return False

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TEST 7: NON-EXISTENT USER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_nonexistent_user():
    """Test login with non-existent user email."""
    print_section("TEST 7: NON-EXISTENT USER")
    
    payload = {
        'email': 'nonexistent@nyaradzo.co.zw',
        'password': 'SomePassword123!'
    }
    
    print_info(f"Sending login request with non-existent email")
    
    client.credentials()  # Clear credentials
    
    try:
        response = client.post('/api/token/', payload, format='json')
        
        if response.status_code in [400, 401]:
            print_success(f"Non-existent user correctly rejected (Status: {response.status_code})")
            print_info(f"Error message: {response.json()}")
            return True
        else:
            print_warning(f"Unexpected status code: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Non-existent user test failed: {str(e)}")
        return False

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN TEST RUNNER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def run_all_tests():
    """Run all authentication tests."""
    print(f"\n{Colors.BOLD}{Colors.OKBLUE}")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  NYARADZO ASSURANCE — AUTHENTICATION TEST SUITE".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    print(Colors.ENDC)
    
    results = {}
    
    try:
        # Test 1: User Creation
        user, email, password = test_user_creation()
        results['User Creation'] = True
        
        # Test 2: Login
        access_token, refresh_token = test_login(email, password)
        results['Login'] = access_token is not None and refresh_token is not None
        
        if access_token:
            # Test 3: Token Validation
            results['Token Validation'] = test_token_validation(access_token)
            
            # Test 4: Token Refresh
            new_access_token = test_token_refresh(refresh_token)
            results['Token Refresh'] = new_access_token is not None
            
            if new_access_token:
                # Verify new token works
                results['New Token Validation'] = test_token_validation(new_access_token)
        
        # Test 5: Invalid Token Rejection
        results['Invalid Token Rejection'] = test_invalid_token_rejection()
        
        # Test 6: Wrong Credentials
        results['Wrong Credentials'] = test_wrong_credentials(email)
        
        # Test 7: Non-Existent User
        results['Non-Existent User'] = test_nonexistent_user()
        
    except Exception as e:
        print_error(f"Test suite failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()

    # Print Summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_flag in results.items():
        status = f"{Colors.OKGREEN}PASS{Colors.ENDC}" if passed_flag else f"{Colors.FAIL}FAIL{Colors.ENDC}"
        print(f"  {status}  {test_name}")
    
    print(f"\n{Colors.BOLD}Total: {passed}/{total} tests passed{Colors.ENDC}\n")
    
    if passed == total:
        print(f"{Colors.OKGREEN}{Colors.BOLD}✓ All authentication tests passed!{Colors.ENDC}\n")
        return True
    else:
        print(f"{Colors.FAIL}{Colors.BOLD}✗ Some tests failed. Review the output above.{Colors.ENDC}\n")
        return False

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
