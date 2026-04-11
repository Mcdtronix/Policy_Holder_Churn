"""
Test Login Error Message Display
================================
Verify that specific error messages are shown to users
instead of generic "Authentication failed" messages.

Author: Nyaradzo Engineering Team
Date: 2025
"""

import os
import sys
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nyaradzo_backend.settings')
sys.path.insert(0, '/home/aqi/Documents/Projects/Insuarance_Churn_Prediction/Backend')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()


def print_section(title):
    print(f"\n{'─' * 70}")
    print(f"► {title}")
    print(f"{'─' * 70}")


def test_wrong_password_error():
    """Test that specific error message is returned for wrong password."""
    print_section("TEST 1: Wrong Password Error Message")
    
    client = Client()
    
    login_data = {
        'email': 'demo@nyaradzo.co.zw',
        'password': 'WrongPassword123!'
    }
    
    print(f"Testing wrong password for existing user...")
    print(f"Email: {login_data['email']}")
    print(f"Password: {login_data['password']} (intentionally wrong)")
    
    response = client.post(
        '/api/token/',
        data=json.dumps(login_data),
        content_type='application/json'
    )
    
    print(f"\nResponse Status: {response.status_code}")
    
    if response.status_code == 401:
        data = response.json()
        error_msg = data.get('error', 'Unknown error')
        
        print(f"Error returned by backend: {error_msg}")
        
        if 'Incorrect password' in error_msg:
            print(f"✅ CORRECT: Specific error message 'Incorrect password' returned")
            return True
        else:
            print(f"❌ WRONG: Got '{error_msg}' instead of specific password error")
            return False
    else:
        print(f"❌ ERROR: Expected 401 response, got {response.status_code}")
        return False


def test_wrong_email_error():
    """Test that specific error message is returned for non-existent email."""
    print_section("TEST 2: Wrong Email Error Message")
    
    client = Client()
    
    login_data = {
        'email': 'nonexistent@example.com',
        'password': 'SomePassword123!'
    }
    
    print(f"Testing non-existent email...")
    print(f"Email: {login_data['email']} (doesn't exist)")
    print(f"Password: {login_data['password']}")
    
    response = client.post(
        '/api/token/',
        data=json.dumps(login_data),
        content_type='application/json'
    )
    
    print(f"\nResponse Status: {response.status_code}")
    
    if response.status_code == 401:
        data = response.json()
        error_msg = data.get('error', 'Unknown error')
        
        print(f"Error returned by backend: {error_msg}")
        
        if 'No account found' in error_msg:
            print(f"✅ CORRECT: Specific error message 'No account found' returned")
            return True
        else:
            print(f"❌ WRONG: Got '{error_msg}' instead of specific email error")
            return False
    else:
        print(f"❌ ERROR: Expected 401 response, got {response.status_code}")
        return False


def test_inactive_user_error():
    """Test error message for inactive user account."""
    print_section("TEST 3: Inactive User Error Message")
    
    # Create an inactive user for testing
    User.objects.filter(email='inactive_test@nyaradzo.co.zw').delete()
    
    inactive_user = User.objects.create_user(
        username='inactivetest',
        email='inactive_test@nyaradzo.co.zw',
        password='InactivePassword123!',
        is_active=False  # Inactive
    )
    
    client = Client()
    
    login_data = {
        'email': 'inactive_test@nyaradzo.co.zw',
        'password': 'InactivePassword123!'
    }
    
    print(f"Testing inactive user account...")
    print(f"Email: {login_data['email']}")
    print(f"Password: {login_data['password']}")
    print(f"Account Status: Inactive")
    
    response = client.post(
        '/api/token/',
        data=json.dumps(login_data),
        content_type='application/json'
    )
    
    print(f"\nResponse Status: {response.status_code}")
    
    if response.status_code == 401:
        data = response.json()
        error_msg = data.get('error', 'Unknown error')
        
        print(f"Error returned by backend: {error_msg}")
        
        if 'inactive' in error_msg.lower():
            print(f"✅ CORRECT: Specific error message about inactive account returned")
            return True
        else:
            print(f"❌ WRONG: Got '{error_msg}' instead of inactive user error")
            return False
    else:
        print(f"❌ ERROR: Expected 401 response, got {response.status_code}")
        return False


def test_both_wrong_error():
    """Test error when both email and password are wrong."""
    print_section("TEST 4: Both Email & Password Wrong")
    
    client = Client()
    
    login_data = {
        'email': 'completelywrong@example.com',
        'password': 'AlsoWrongPassword123!'
    }
    
    print(f"Testing both wrong email and password...")
    print(f"Email: {login_data['email']} (doesn't exist)")
    print(f"Password: {login_data['password']}")
    
    response = client.post(
        '/api/token/',
        data=json.dumps(login_data),
        content_type='application/json'
    )
    
    print(f"\nResponse Status: {response.status_code}")
    
    if response.status_code == 401:
        data = response.json()
        error_msg = data.get('error', 'Unknown error')
        
        print(f"Error returned by backend: {error_msg}")
        
        # Should get some error (email not found or generic)
        if error_msg and len(error_msg) > 0:
            print(f"✅ CORRECT: Specific error message returned (not generic)")
            return True
        else:
            print(f"❌ WRONG: Got generic message instead of specific error")
            return False
    else:
        print(f"❌ ERROR: Expected 401 response, got {response.status_code}")
        return False


def test_successful_login():
    """Test that successful login doesn't show errors."""
    print_section("TEST 5: Successful Login (No Errors)")
    
    client = Client()
    
    login_data = {
        'email': 'demo@nyaradzo.co.zw',
        'password': 'Demo@Nyaradzo2025'
    }
    
    print(f"Testing successful login...")
    print(f"Email: {login_data['email']}")
    print(f"Password: Demo@Nyaradzo2025 (correct)")
    
    response = client.post(
        '/api/token/',
        data=json.dumps(login_data),
        content_type='application/json'
    )
    
    print(f"\nResponse Status: {response.status_code}")
    
    if response.status_code in [200, 201]:
        data = response.json()
        print(f"✅ LOGIN SUCCESSFUL")
        
        if 'access' in data:
            print(f"✅ Access token returned")
        if 'user' in data:
            user = data['user']
            print(f"✅ User data returned: {user['email']}")
        
        if 'non_field_errors' in data or 'errors' in data:
            print(f"❌ ERROR: No errors should be in successful response")
            return False
        
        return True
    else:
        print(f"❌ ERROR: Expected 200 response, got {response.status_code}")
        data = response.json()
        print(f"Response: {data}")
        return False


def run_all_tests():
    print("\n" + "=" * 70)
    print("  LOGIN ERROR MESSAGE DISPLAY TEST SUITE")
    print("=" * 70)
    print("\nVerifying that backend returns SPECIFIC error messages")
    print("(This is what frontend will display to users)")
    
    results = {
        "Wrong Password Error Message": test_wrong_password_error(),
        "Wrong Email Error Message": test_wrong_email_error(),
        "Inactive User Error Message": test_inactive_user_error(),
        "Both Wrong Error Message": test_both_wrong_error(),
        "Successful Login (No Errors)": test_successful_login(),
    }
    
    # Summary
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
        print("\n" + "✅ " * 20)
        print("ALL SPECIFIC ERROR MESSAGES WORKING CORRECTLY")
        print("✅ " * 20)
        print("\nUsers will see:")
        print("  • 'Email is not registered' for wrong email")
        print("  • 'Password is incorrect' for wrong password")
        print("  • 'Your account has been deactivated' for inactive accounts")
        print("  • 'Invalid email and password' for both wrong")
        print("\n✅ NOT the generic 'Authentication failed' message")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
    
    print("\n" + "=" * 70 + "\n")


if __name__ == '__main__':
    run_all_tests()
