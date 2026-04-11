#!/usr/bin/env python3
"""
Simple Customer Import Verification
==================================
Quick verification of imported customer data.

Usage:
    python simple_verify.py
"""

import os
import sys

# Add Django project path
sys.path.append('/home/aqi/Documents/Projects/Insuarance_Churn_Prediction/Backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nyaradzo_backend.settings')

import django
django.setup()

from churn.models import Customer, Gender, Location, IncomeLevel, Policy, PolicyType, CustomerEngagement, ChurnPrediction
from django.db.models import Count, Avg


def simple_verify():
    """Simple verification of imported data."""
    print("=" * 50)
    print("NYARADZO CUSTOMER IMPORT VERIFICATION")
    print("=" * 50)
    
    # Customer counts
    total_customers = Customer.objects.count()
    active_customers = Customer.objects.filter(is_active=True).count()
    
    print(f"\n📊 CUSTOMERS:")
    print(f"  Total: {total_customers}")
    print(f"  Active: {active_customers}")
    
    # Gender distribution
    print(f"\n👥 GENDER DISTRIBUTION:")
    gender_stats = Customer.objects.values('gender__label').annotate(count=Count('id')).order_by('-count')
    for stat in gender_stats:
        print(f"  {stat['gender__label']}: {stat['count']}")
    
    # Location distribution (top 5)
    print(f"\n📍 TOP LOCATIONS:")
    location_stats = Customer.objects.values('location__city').annotate(count=Count('id')).order_by('-count')[:5]
    for stat in location_stats:
        print(f"  {stat['location__city']}: {stat['count']}")
    
    # Income levels
    print(f"\n💰 INCOME LEVELS:")
    income_stats = Customer.objects.values('income_level__label').annotate(count=Count('id')).order_by('-count')
    for stat in income_stats:
        print(f"  {stat['income_level__label']}: {stat['count']}")
    
    # Reference data counts
    print(f"\n📋 REFERENCE DATA:")
    print(f"  Genders: {Gender.objects.count()}")
    print(f"  Locations: {Location.objects.count()}")
    print(f"  Income Levels: {IncomeLevel.objects.count()}")
    print(f"  Policy Types: {PolicyType.objects.count()}")
    
    # Related data
    print(f"\n🔗 RELATED DATA:")
    print(f"  Policies: {Policy.objects.count()}")
    print(f"  Engagement Records: {CustomerEngagement.objects.count()}")
    print(f"  Churn Predictions: {ChurnPrediction.objects.count()}")
    
    # Sample customers
    print(f"\n👤 SAMPLE CUSTOMERS:")
    sample_customers = Customer.objects.all()[:3]
    for customer in sample_customers:
        print(f"\n  {customer.first_name} {customer.last_name}")
        print(f"    ID: {customer.customer_number}")
        print(f"    Email: {customer.email}")
        print(f"    Location: {customer.location.city}")
        print(f"    Gender: {customer.gender.label}")
        print(f"    Income: {customer.income_level.label}")
    
    # Churn risk
    if ChurnPrediction.objects.exists():
        print(f"\n⚠️  CHURN RISK:")
        churn_stats = ChurnPrediction.objects.values('risk_level').annotate(
            count=Count('id')
        ).order_by('-count')
        
        for stat in churn_stats:
            print(f"  {stat['risk_level']}: {stat['count']} customers")
        
        avg_churn = ChurnPrediction.objects.aggregate(avg_churn=Avg('churn_percentage'))['avg_churn']
        print(f"  Average churn risk: {avg_churn:.1f}%")
    
    print(f"\n" + "=" * 50)
    print("✅ VERIFICATION COMPLETE")
    print("=" * 50)


if __name__ == '__main__':
    try:
        simple_verify()
    except Exception as e:
        print(f"❌ Verification failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
