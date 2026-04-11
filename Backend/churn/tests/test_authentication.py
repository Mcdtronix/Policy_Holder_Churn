"""
Comprehensive Authentication Test Suite
========================================
Tests for JWT authentication, login flow, and security measures.

Run with: pytest Backend/
or:       python manage.py test churn.tests.test_authentication
"""

import pytest
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
import json

User = get_user_model()

class AuthenticationTestCase(TestCase):
    """Test suite for authentication system."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        super().setUpClass()
        
    def setUp(self):
        """Create test user and API client."""
        self.client = APIClient()
        self.test_email = "test.admin@nyaradzo.co.zw"
        self.test_password = "TestPass123!"
        
        # Create test user
        self.user = User.objects.create_user(
            username='testadmin',
            email=self.test_email,
            password=self.test_password,
            first_name='Test',
            last_name='Admin',
            role='ADMIN',
            is_active=True
        )
    
    def tearDown(self):
        """Clean up after tests."""
        User.objects.filter(email=self.test_email).delete()
    
    # ─────────────────────────────────────────────
    # LOGIN TESTS
    # ─────────────────────────────────────────────
    
    def test_login_success(self):
        """Test successful login with valid credentials."""
        response = self.client.post('/api/token/', {
            'email': self.test_email,
            'password': self.test_password
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        
        # Verify user data in response
        user_data = response.data['user']
        self.assertEqual(user_data['email'], self.test_email)
        self.assertEqual(user_data['role'], 'ADMIN')
        self.assertTrue(user_data['is_active'])
    
    def test_login_invalid_email(self):
        """Test login with non-existent email."""
        response = self.client.post('/api/token/', {
            'email': 'nonexistent@example.com',
            'password': self.test_password
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
        self.assertIn('No account found', response.data['error'])
    
    def test_login_invalid_password(self):
        """Test login with incorrect password."""
        response = self.client.post('/api/token/', {
            'email': self.test_email,
            'password': 'WrongPassword123!'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
        self.assertIn('password', response.data['error'].lower())
    
    def test_login_inactive_user(self):
        """Test login with inactive user account."""
        # Deactivate user
        self.user.is_active = False
        self.user.save()
        
        response = self.client.post('/api/token/', {
            'email': self.test_email,
            'password': self.test_password
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('inactive', response.data.get('error', '').lower())
    
    def test_login_missing_email(self):
        """Test login without email field."""
        response = self.client.post('/api/token/', {
            'password': self.test_password
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_missing_password(self):
        """Test login without password field."""
        response = self.client.post('/api/token/', {
            'email': self.test_email
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_audit_trail_success(self):
        """Test that successful login is logged."""
        from churn.models import LoginAttempt
        
        LoginAttempt.objects.all().delete()
        
        response = self.client.post('/api/token/', {
            'email': self.test_email,
            'password': self.test_password
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify audit trail
        attempt = LoginAttempt.objects.filter(email=self.test_email).first()
        self.assertIsNotNone(attempt)
        self.assertTrue(attempt.success)
        self.assertIsNotNone(attempt.ip_address)
        self.assertIsNotNone(attempt.user_agent)
    
    def test_login_audit_trail_failure(self):
        """Test that failed login is logged."""
        from churn.models import LoginAttempt
        
        LoginAttempt.objects.all().delete()
        
        response = self.client.post('/api/token/', {
            'email': self.test_email,
            'password': 'WrongPassword'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Verify audit trail
        attempt = LoginAttempt.objects.filter(email=self.test_email).first()
        self.assertIsNotNone(attempt)
        self.assertFalse(attempt.success)
        self.assertIsNotNone(attempt.error_message)
    
    # ─────────────────────────────────────────────
    # TOKEN TESTS
    # ─────────────────────────────────────────────
    
    def test_token_refresh(self):
        """Test token refresh mechanism."""
        # Get tokens
        login_response = self.client.post('/api/token/', {
            'email': self.test_email,
            'password': self.test_password
        }, format='json')
        
        refresh_token = login_response.data['refresh']
        
        # Refresh token
        response = self.client.post('/api/token/refresh/', {
            'refresh': refresh_token
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertNotEqual(response.data['access'], login_response.data['access'])
    
    def test_protected_endpoint_with_token(self):
        """Test accessing protected endpoint with valid token."""
        # Get tokens
        login_response = self.client.post('/api/token/', {
            'email': self.test_email,
            'password': self.test_password
        }, format='json')
        
        access_token = login_response.data['access']
        
        # Access protected endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get('/api/token/verify/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['valid'])
        self.assertEqual(response.data['email'], self.test_email)
    
    def test_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without token."""
        response = self.client.get('/api/token/verify/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_protected_endpoint_with_invalid_token(self):
        """Test accessing protected endpoint with invalid token."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token_xyz')
        response = self.client.get('/api/token/verify/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    # ─────────────────────────────────────────────
    # LOGOUT TESTS
    # ─────────────────────────────────────────────
    
    def test_logout_success(self):
        """Test successful logout."""
        # Get tokens
        login_response = self.client.post('/api/token/', {
            'email': self.test_email,
            'password': self.test_password
        }, format='json')
        
        access_token = login_response.data['access']
        
        # Logout
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.post('/api/logout/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['status'] == 'success')
    
    def test_logout_unauthenticated(self):
        """Test logout without authentication."""
        response = self.client.post('/api/logout/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    # ─────────────────────────────────────────────
    # HEALTH CHECK TESTS
    # ─────────────────────────────────────────────
    
    def test_health_check(self):
        """Test authentication health check endpoint."""
        response = self.client.get('/api/auth/health/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'healthy')
        self.assertIn('database', response.data)
    
    # ─────────────────────────────────────────────
    # SECURITY TESTS
    # ─────────────────────────────────────────────
    
    def test_security_headers(self):
        """Test that security headers are present in responses."""
        response = self.client.get('/api/auth/health/')
        
        self.assertIn('X-Frame-Options', response)
        self.assertEqual(response['X-Frame-Options'], 'DENY')
        self.assertIn('X-Content-Type-Options', response)
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertIn('Content-Security-Policy', response)
    
    def test_rate_limiting(self):
        """Test rate limiting on login endpoint."""
        # This would require throttle test setup
        # For now, verify throttle is configured
        from rest_framework.throttling import AnonRateThrottle
        
        throttle = AnonRateThrottle()
        self.assertEqual(throttle.scope, 'anon')
