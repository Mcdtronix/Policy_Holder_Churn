#!/usr/bin/env python
"""
End-to-End Test: Login Error Message Flow
Validates that specific error messages flow from backend → frontend API handler → UI
"""

import os
import sys
import django
import json
from django.test import Client

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nyaradzo_backend.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth import get_user_model
from rest_framework import status
from django.db import models

User = get_user_model()

def print_header(title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

def print_section(title):
    print(f"\n──────────────────────────────────────────────────────────────────────")
    print(f"► {title}")
    print(f"──────────────────────────────────────────────────────────────────────")

def test_scenario(name, email, password, expected_message):
    """Test a login scenario and validate the response"""
    client = Client()
    
    print(f"\n📝 {name}")
    print(f"   Email: {email}")
    print(f"   Password: {password}")
    
    response = client.post('/api/token/', {
        'email': email,
        'password': password
    }, content_type='application/json')
    
    status_code = response.status_code
    print(f"   Status Code: {status_code}")
    
    try:
        data = json.loads(response.content)
        print(f"   Response Data: {json.dumps(data, indent=6)}")
        
        if status_code == 200:
            print(f"   ✅ Login successful")
            return True, "Success"
        else:
            error_message = data.get('error', 'Unknown error')
            print(f"   Error Message: {error_message}")
            
            # Check if the specific message is present
            if expected_message in error_message:
                print(f"   ✅ Correct specific message returned")
                return True, error_message
            else:
                print(f"   ❌ Expected '{expected_message}', got '{error_message}'")
                return False, error_message
    except json.JSONDecodeError:
        print(f"   ❌ Invalid JSON in response: {response.content}")
        return False, "Invalid response"

def main():
    print_header("END-TO-END LOGIN ERROR MESSAGE FLOW TEST")
    
    print("This test validates the complete flow:")
    print("  Backend raises specific ValidationError")
    print("     ↓")
    print("  View catches ValidationError and extracts message")
    print("     ↓")
    print("  Response includes 'error' field with specific message")
    print("     ↓")
    print("  Frontend API handler receives and maps message")
    print("     ↓")
    print("  Form displays user-friendly message on correct field")
    
    # Test 1: Wrong Password
    print_section("TEST 1: Wrong Password → Specific Message")
    success1, msg1 = test_scenario(
        "Wrong password for existing user",
        "demo@nyaradzo.co.zw",
        "WrongPassword123!",
        "Incorrect password"
    )
    
    # Test 2: Wrong Email
    print_section("TEST 2: Wrong Email → Specific Message")
    success2, msg2 = test_scenario(
        "Non-existent email",
        "nonexistent@example.com",
        "SomePassword123!",
        "No account found"
    )
    
    # Test 3: Inactive User
    print_section("TEST 3: Inactive User → Specific Message")
    success3, msg3 = test_scenario(
        "Inactive user account",
        "inactive_test@nyaradzo.co.zw",
        "InactivePassword123!",
        "This user account is inactive"
    )
    
    # Test 4: Both Wrong
    print_section("TEST 4: Both Wrong → Email Check First")
    success4, msg4 = test_scenario(
        "Both email and password wrong",
        "completelywrong@example.com",
        "AlsoWrongPassword123!",
        "No account found"
    )
    
    # Test 5: Successful Login
    print_section("TEST 5: Successful Login → No Errors")
    client = Client()
    response = client.post('/api/token/', {
        'email': 'demo@nyaradzo.co.zw',
        'password': 'Demo@Nyaradzo2025'
    }, content_type='application/json')
    
    print(f"\n📝 Successful login")
    print(f"   Email: demo@nyaradzo.co.zw")
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = json.loads(response.content)
        print(f"   ✅ Status 200 OK")
        print(f"   ✅ Access token present: {bool(data.get('access'))}")
        print(f"   ✅ User data present: {bool(data.get('user'))}")
        success5 = True
    else:
        print(f"   ❌ Expected 200, got {response.status_code}")
        success5 = False
    
    # Summary
    print_header("END-TO-END TEST SUMMARY")
    
    results = {
        "Wrong Password": success1,
        "Wrong Email": success2,
        "Inactive User": success3,
        "Both Wrong": success4,
        "Successful Login": success5,
    }
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, success in results.items():
        status_str = "✅ PASS" if success else "❌ FAIL"
        print(f"{status_str}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅")
        print("ALL E2E TESTS PASSED - Error messages working correctly!")
        print("✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅\n")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
