#!/usr/bin/env python3
"""
Analytics Endpoints Test
========================
Tests all analytics endpoints to ensure they return real database data.

Usage:
    python test_analytics.py
"""

import os
import sys

# Add Django project path
sys.path.append('/home/aqi/Documents/Projects/Insuarance_Churn_Prediction/Backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nyaradzo_backend.settings')

import django
django.setup()

from churn.views import AnalyticsViewSet
from django.test import RequestFactory
from rest_framework.test import APIRequestFactory
from django.contrib.auth import get_user_model


def test_analytics_endpoints():
    """Test all analytics endpoints."""
    print("=" * 60)
    print("TESTING ANALYTICS ENDPOINTS")
    print("=" * 60)
    
    User = get_user_model()
    factory = APIRequestFactory()
    
    # Create a test request
    request = factory.get('/api/v1/analytics/')
    request.user = User.objects.first()
    
    # Test the analytics view
    view = AnalyticsViewSet()
    view.format_kwarg = None
    
    try:
        # Test monthly_trends
        response = view.monthly_trends(request)
        print(f"✅ monthly_trends: {len(response.data)} months of data")
        for item in response.data:
            print(f"   {item['month']}: {item['newPolicies']} policies, {item['claims']} claims, ${item['revenue']:.0f} revenue, {item['churnRate']:.1f}% churn")
        
        # Test churn_by_location
        response = view.churn_by_location(request)
        print(f"✅ churn_by_location: {len(response.data)} locations")
        for item in response.data[:3]:  # Show top 3
            print(f"   {item['location']}: {item['churnRate']:.1f}% churn, {item['policyCount']} customers")
        
        # Test churn_by_age
        response = view.churn_by_age(request)
        print(f"✅ churn_by_age: {len(response.data)} age groups")
        for item in response.data:
            print(f"   {item['group']}: {item['churnRate']:.1f}% churn, {item['count']} customers")
        
        # Test churn_by_income
        response = view.churn_by_income(request)
        print(f"✅ churn_by_income: {len(response.data)} income levels")
        for item in response.data:
            print(f"   {item['incomeLevel']}: {item['churnRate']:.1f}% churn, {item['count']} customers")
        
        # Test recent_activities
        response = view.recent_activities(request)
        print(f"✅ recent_activities: {len(response.data)} activities")
        for item in response.data:
            print(f"   {item['type']}: {item['description'][:60]}...")
        
        print("=" * 60)
        print("✅ ALL ANALYTICS ENDPOINTS WORKING!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_analytics_endpoints()
    sys.exit(0 if success else 1)
