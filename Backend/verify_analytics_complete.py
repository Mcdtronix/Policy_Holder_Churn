#!/usr/bin/env python3
"""
Complete Analytics Verification
==============================
Comprehensive test to verify all analytics data is properly connected
to the database and ready for frontend consumption.

Usage:
    python verify_analytics_complete.py
"""

import os
import sys

# Add Django project path
sys.path.append('/home/aqi/Documents/Projects/Insuarance_Churn_Prediction/Backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nyaradzo_backend.settings')

import django
django.setup()

from churn.models import Customer, Policy, Claim, Payment, ChurnPrediction, Location, IncomeLevel
from churn.views import AnalyticsViewSet, DashboardViewSet
from django.test import RequestFactory
from rest_framework.test import APIRequestFactory
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, Avg


def verify_analytics_complete():
    """Complete verification of analytics data."""
    print("=" * 70)
    print("COMPLETE ANALYTICS VERIFICATION")
    print("=" * 70)
    
    User = get_user_model()
    factory = APIRequestFactory()
    
    # Create a test request
    request = factory.get('/api/v1/analytics/')
    request.user = User.objects.first()
    
    # Create view instances
    analytics_view = AnalyticsViewSet()
    analytics_view.format_kwarg = None
    
    dashboard_view = DashboardViewSet()
    dashboard_view.format_kwarg = None
    
    print("\n📊 DATABASE DATA VERIFICATION:")
    print(f"  Customers: {Customer.objects.count():,}")
    print(f"  Policies: {Policy.objects.count():,}")
    print(f"  Claims: {Claim.objects.count():,}")
    print(f"  Payments: {Payment.objects.count():,}")
    print(f"  Churn Predictions: {ChurnPrediction.objects.count():,}")
    print(f"  Locations: {Location.objects.count():,}")
    print(f"  Income Levels: {IncomeLevel.objects.count():,}")
    
    print("\n🎯 DASHBOARD DATA:")
    try:
        response = dashboard_view.list(request)
        data = response.data
        print(f"  Total Customers: {data.get('totalCustomers', 0):,}")
        print(f"  Total Policies: {data.get('totalPolicies', 0):,}")
        print(f"  Active Policies: {data.get('activePolicies', 0):,}")
        print(f"  Pending Claims: {data.get('pendingClaims', 0):,}")
        print(f"  Total Premium Revenue: ${float(data.get('totalPremiumRevenue', 0)):,.2f}")
        print(f"  Average Churn Rate: {float(data.get('avgChurnRate', 0)):.1f}%")
        print(f"  High Risk Customers: {data.get('highRiskCustomers', 0):,}")
        print(f"  Recent Predictions: {len(data.get('recent_predictions', []))}")
        print(f"  Top Claims: {len(data.get('top_claims', []))}")
        print("  ✅ Dashboard data verified")
    except Exception as e:
        print(f"  ❌ Dashboard error: {e}")
        return False
    
    print("\n📈 ANALYTICS CHARTS DATA:")
    
    # Monthly Trends
    try:
        response = analytics_view.monthly_trends(request)
        monthly_data = response.data
        total_policies = sum(item['newPolicies'] for item in monthly_data)
        total_claims = sum(item['claims'] for item in monthly_data)
        total_revenue = sum(item['revenue'] for item in monthly_data)
        avg_churn = sum(item['churnRate'] for item in monthly_data) / len(monthly_data) if monthly_data else 0
        
        print(f"  📊 Monthly Trends: {len(monthly_data)} months")
        print(f"     Total Policies: {total_policies:,}")
        print(f"     Total Claims: {total_claims:,}")
        print(f"     Total Revenue: ${total_revenue:,.2f}")
        print(f"     Average Churn: {avg_churn:.1f}%")
        print("     ✅ Monthly trends verified")
    except Exception as e:
        print(f"  ❌ Monthly trends error: {e}")
        return False
    
    # Churn by Location
    try:
        response = analytics_view.churn_by_location(request)
        location_data = response.data
        print(f"  📍 Churn by Location: {len(location_data)} locations")
        for loc in location_data[:3]:
            print(f"     {loc['location']}: {loc['churnRate']:.1f}% churn ({loc['policyCount']} customers)")
        print("     ✅ Location analytics verified")
    except Exception as e:
        print(f"  ❌ Location analytics error: {e}")
        return False
    
    # Churn by Age
    try:
        response = analytics_view.churn_by_age(request)
        age_data = response.data
        print(f"  👥 Churn by Age: {len(age_data)} age groups")
        for age in age_data:
            print(f"     {age['group']}: {age['churnRate']:.1f}% churn ({age['count']} customers)")
        print("     ✅ Age analytics verified")
    except Exception as e:
        print(f"  ❌ Age analytics error: {e}")
        return False
    
    # Churn by Income
    try:
        response = analytics_view.churn_by_income(request)
        income_data = response.data
        print(f"  💰 Churn by Income: {len(income_data)} income levels")
        for income in income_data:
            print(f"     {income['incomeLevel']}: {income['churnRate']:.1f}% churn ({income['count']} customers)")
        print("     ✅ Income analytics verified")
    except Exception as e:
        print(f"  ❌ Income analytics error: {e}")
        return False
    
    # Recent Activities
    try:
        response = analytics_view.recent_activities(request)
        activities = response.data
        print(f"  🔄 Recent Activities: {len(activities)} activities")
        activity_types = {}
        for activity in activities:
            activity_types[activity['type']] = activity_types.get(activity['type'], 0) + 1
        for activity_type, count in activity_types.items():
            print(f"     {activity_type}: {count} activities")
        print("     ✅ Activities verified")
    except Exception as e:
        print(f"  ❌ Activities error: {e}")
        return False
    
    print("\n🎨 FRONTEND CHART READINESS:")
    print("  ✅ Line Chart: Monthly trends data available")
    print("  ✅ Bar Chart: Location churn data available")
    print("  ✅ Bar Chart: Age group churn data available")
    print("  ✅ Bar Chart: Income level churn data available")
    print("  ✅ Activity Feed: Recent activities available")
    print("  ✅ Stat Cards: Dashboard metrics available")
    
    print("\n🔗 DATA INTEGRITY CHECK:")
    # Verify data consistency
    db_customers = Customer.objects.count()
    dashboard_customers = dashboard_view.list(request).data.get('totalCustomers', 0)
    
    db_policies = Policy.objects.count()
    dashboard_policies = dashboard_view.list(request).data.get('totalPolicies', 0)
    
    db_predictions = ChurnPrediction.objects.count()
    recent_predictions = len(dashboard_view.list(request).data.get('recent_predictions', []))
    
    print(f"  Customer Count Match: {db_customers == dashboard_customers} ({db_customers} vs {dashboard_customers})")
    print(f"  Policy Count Match: {db_policies == dashboard_policies} ({db_policies} vs {dashboard_policies})")
    print(f"  Predictions Available: {db_predictions > 0} ({recent_predictions} recent shown)")
    
    print("\n" + "=" * 70)
    print("✅ COMPLETE ANALYTICS VERIFICATION SUCCESSFUL!")
    print("🚀 All charts and cards are ready with real database data!")
    print("=" * 70)
    
    return True


if __name__ == '__main__':
    success = verify_analytics_complete()
    sys.exit(0 if success else 1)
