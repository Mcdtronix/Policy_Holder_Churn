#!/usr/bin/env python3
"""
Dashboard Fix Verification
=========================
Tests that the dashboard serializers work correctly after fixing UUID issues.

Usage:
    python test_dashboard_fix.py
"""

import os
import sys

# Add Django project path
sys.path.append('/home/aqi/Documents/Projects/Insuarance_Churn_Prediction/Backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nyaradzo_backend.settings')

import django
django.setup()

from churn.serializers import DashboardStatsSerializer, ChurnPredictionListSerializer, ClaimListSerializer
from churn.models import ChurnPrediction, Claim, Customer, Policy
from django.contrib.auth import get_user_model
from django.db import models


def test_dashboard_fix():
    """Test that dashboard serializers work correctly."""
    print("=" * 50)
    print("DASHBOARD FIX VERIFICATION")
    print("=" * 50)
    
    try:
        # Test data availability
        print(f"\n📊 Data Availability:")
        print(f"  Customers: {Customer.objects.count()}")
        print(f"  Policies: {Policy.objects.count()}")
        print(f"  Churn Predictions: {ChurnPrediction.objects.count()}")
        print(f"  Claims: {Claim.objects.count()}")
        
        # Test ChurnPredictionListSerializer
        print(f"\n🔮 Testing ChurnPredictionListSerializer...")
        pred = ChurnPrediction.objects.first()
        if pred:
            serializer = ChurnPredictionListSerializer(pred)
            data = serializer.data
            print(f"  ✅ Sample prediction: {data['customer_number']} - {data['risk_level']['label']} - {data['churn_percentage']}%")
        
        # Test ClaimListSerializer
        print(f"\n📄 Testing ClaimListSerializer...")
        claim = Claim.objects.first()
        if claim:
            serializer = ClaimListSerializer(claim)
            data = serializer.data
            print(f"  ✅ Sample claim: {data['claim_number']} - {data['claim_type']} - ${data['amount_claimed']}")
        
        # Test dashboard data structure
        print(f"\n📈 Testing Dashboard Data Structure...")
        
        # Create sample dashboard data
        dashboard_data = {
            'totalCustomers': Customer.objects.count(),
            'totalPolicies': Policy.objects.count(),
            'activePolicies': Policy.objects.filter(status='ACTIVE').count(),
            'pendingClaims': Claim.objects.filter(status='PENDING').count(),
            'totalPremiumRevenue': Policy.objects.aggregate(total=models.Sum('premium_amount'))['total'] or 0,
            'avgChurnRate': ChurnPrediction.objects.aggregate(avg=models.Avg('churn_percentage'))['avg'] or 0,
            'newPoliciesThisMonth': 0,
            'claimsProcessed': Claim.objects.filter(status='SETTLED').count(),
            'maturedPolicies': Policy.objects.filter(status='MATURED').count(),
            'highRiskCustomers': ChurnPrediction.objects.filter(risk_level__code='HIGH').count(),
            'recent_predictions': ChurnPredictionListSerializer(
                ChurnPrediction.objects.order_by('-predicted_at')[:5], many=True
            ).data,
            'top_claims': ClaimListSerializer(
                Claim.objects.order_by('-amount_claimed')[:5], many=True
            ).data
        }
        
        # Test DashboardStatsSerializer
        dashboard_serializer = DashboardStatsSerializer(dashboard_data)
        dashboard_result = dashboard_serializer.data
        
        print(f"  ✅ Dashboard data keys: {list(dashboard_result.keys())}")
        print(f"  ✅ Total customers: {dashboard_result['totalCustomers']}")
        print(f"  ✅ Total policies: {dashboard_result['totalPolicies']}")
        print(f"  ✅ High risk customers: {dashboard_result['highRiskCustomers']}")
        print(f"  ✅ Recent predictions: {len(dashboard_result['recent_predictions'])}")
        print(f"  ✅ Top claims: {len(dashboard_result['top_claims'])}")
        
        print(f"\n" + "=" * 50)
        print("✅ ALL TESTS PASSED - DASHBOARD FIX WORKING!")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == '__main__':
    success = test_dashboard_fix()
    sys.exit(0 if success else 1)
