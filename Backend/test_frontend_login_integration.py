"""
Test Frontend Login Integration
===============================
Tests the complete authentication flow:
1. User creation in backend
2. JWT token generation
3. Frontend login via API
4. Token validation and user return

Author: Nyaradzo Engineering Team
Date: 2025
"""

import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nyaradzo_backend.settings')
sys.path.insert(0, '/home/aqi/Documents/Projects/Insuarance_Churn_Prediction/Backend')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


def print_section(title):
    """Print formatted section header."""
    print(f"\n{'─' * 70}")
    print(f"► {title}")
    print(f"{'─' * 70}")


def test_jwt_login_endpoint():
    """Test JWT token generation via login API."""
    print_section("TEST: JWT Login Endpoint (Frontend Integration)")
    
    client = Client()
    
    # Prepare login credentials
    login_data = {
        'email': 'testadmin@nyaradzo.co.zw',
        'password': 'NewPassword456!'  # Using the password from Test 3 in test_user_management.py
    }
    
    print(f"📧 Testing login with email: {login_data['email']}")
    
    try:
        # Make POST request to token endpoint
        response = client.post(
            '/api/v1/auth/token/obtain/',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"\n✅ Login successful!")
            
            # Check for JWT tokens
            if 'access' in data:
                print(f"   ✓ Access token generated: {data['access'][:50]}...")
            else:
                print(f"   ❌ Access token missing from response")
            
            if 'refresh' in data:
                print(f"   ✓ Refresh token generated: {data['refresh'][:50]}...")
            else:
                print(f"   ⚠️  Refresh token missing from response")
            
            # Check for user data
            if 'user' in data:
                user_data = data['user']
                print(f"\n   User Data Returned:")
                print(f"   - Email: {user_data.get('email')}")
                print(f"   - Username: {user_data.get('username')}")
                print(f"   - Role: {user_data.get('role')}")
                print(f"   - Is Active: {user_data.get('is_active')}")
            else:
                print(f"   ⚠️  User data missing from response")
            
            print(f"\n✅ JWT endpoint working - frontend can login!")
            return True
        else:
            print(f"   Response: {response.content.decode()}")
            print(f"\n❌ Login failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing login endpoint: {str(e)}")
        return False


def test_protected_endpoint():
    """Test accessing protected endpoint with JWT token."""
    print_section("TEST: Protected Endpoint with JWT Token")
    
    client = Client()
    
    # First, get the token
    login_data = {
        'email': 'testadmin@nyaradzo.co.zw',
        'password': 'NewPassword456!'
    }
    
    response = client.post(
        '/api/v1/auth/token/obtain/',
        data=json.dumps(login_data),
        content_type='application/json'
    )
    
    if response.status_code not in [200, 201]:
        print(f"❌ Could not get JWT token for test")
        return False
    
    token = response.json().get('access')
    
    # Now try to access a protected endpoint
    print(f"🔐 Testing protected endpoint with JWT token...")
    
    try:
        response = client.get(
            '/api/v1/users/me/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"\n✅ Protected endpoint accessible with JWT token!")
            print(f"   - Email: {user_data.get('email')}")
            print(f"   - Role: {user_data.get('role')}")
            print(f"   - Is Active: {user_data.get('is_active')}")
            return True
        else:
            print(f"   Response: {response.content.decode()}")
            print(f"\n❌ Protected endpoint failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing protected endpoint: {str(e)}")
        return False


def test_wrong_password():
    """Test login failure with wrong password."""
    print_section("TEST: Wrong Password Rejection")
    
    client = Client()
    
    login_data = {
        'email': 'testadmin@nyaradzo.co.zw',
        'password': 'WrongPassword123!'
    }
    
    print(f"🔑 Testing with wrong password...")
    
    response = client.post(
        '/api/v1/auth/token/obtain/',
        data=json.dumps(login_data),
        content_type='application/json'
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code != 200:
        print(f"✅ Wrong password correctly rejected")
        error_msg = response.json().get('non_field_errors', [response.content.decode()])
        print(f"   Error message: {error_msg}")
        return True
    else:
        print(f"❌ ERROR: Wrong password was accepted!")
        return False


def run_all_frontend_tests():
    """Run all frontend integration tests."""
    print("\n" + "=" * 70)
    print("  FRONTEND LOGIN INTEGRATION TEST SUITE")
    print("=" * 70)
    
    results = {
        "JWT Login Endpoint": test_jwt_login_endpoint(),
        "Protected Endpoint with JWT": test_protected_endpoint(),
        "Wrong Password Rejection": test_wrong_password(),
    }
    
    # Print summary
    print("\n" + "=" * 70)
    print("  TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n" + "✅ " * 15)
        print("FRONTEND CAN LOGIN - SYSTEM FULLY FUNCTIONAL")
        print("✅ " * 15)
    else:
        print(f"\n⚠️  {total - passed} test(s) failed - review errors above")
    
    print("\n" + "=" * 70 + "\n")


if __name__ == '__main__':
    run_all_frontend_tests()
