#!/usr/bin/env python3
"""
Customer Import Verification Script
==================================
Verify and report on the imported customer data.

Usage:
    python verify_import.py
"""

import os
import sys
from decimal import Decimal

# Add Django project path
sys.path.append('/home/aqi/Documents/Projects/Insuarance_Churn_Prediction/Backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nyaradzo_backend.settings')

import django
django.setup()

from churn.models import Customer, Gender, Location, IncomeLevel, Policy, PolicyType, CustomerEngagement, ChurnPrediction
from django.db.models import Count, Avg, Q


def verify_import():
    """Verify and report on imported data."""
    print("=" * 60)
    print("NYARADZO CUSTOMER DATA IMPORT VERIFICATION")
    print("=" * 60)
    
    # Customer counts
    total_customers = Customer.objects.count()
    active_customers = Customer.objects.filter(is_active=True).count()
    
    print(f"\n📊 CUSTOMER OVERVIEW")
    print(f"Total customers: {total_customers}")
    print(f"Active customers: {active_customers}")
    print(f"Inactive customers: {total_customers - active_customers}")
    
    # Gender distribution
    print(f"\n👥 GENDER DISTRIBUTION")
    gender_stats = Customer.objects.values('gender__label').annotate(count=Count('id')).order_by('-count')
    for stat in gender_stats:
        percentage = (stat['count'] / total_customers) * 100
        print(f"{stat['gender__label']}: {stat['count']} ({percentage:.1f}%)")
    
    # Location distribution
    print(f"\n📍 LOCATION DISTRIBUTION")
    location_stats = Customer.objects.values('location__city').annotate(count=Count('id')).order_by('-count')[:10]
    for stat in location_stats:
        percentage = (stat['count'] / total_customers) * 100
        print(f"{stat['location__city']}: {stat['count']} ({percentage:.1f}%)")
    
    # Income level distribution
    print(f"\n💰 INCOME LEVEL DISTRIBUTION")
    income_stats = Customer.objects.values('income_level__label').annotate(count=Count('id')).order_by('-count')
    for stat in income_stats:
        percentage = (stat['count'] / total_customers) * 100
        print(f"{stat['income_level__label']}: {stat['count']} ({percentage:.1f}%)")
    
    # Policy overview
    total_policies = Policy.objects.count()
    print(f"\n📋 POLICY OVERVIEW")
    print(f"Total policies: {total_policies}")
    
    policy_type_stats = Policy.objects.values('policy_type__name').annotate(count=Count('id')).order_by('-count')
    for stat in policy_type_stats:
        percentage = (stat['count'] / total_policies) * 100
        print(f"{stat['policy_type__name']}: {stat['count']} ({percentage:.1f}%)")
    
    avg_premium = Policy.objects.aggregate(avg_premium=Avg('premium_amount'))['avg_premium']
    print(f"Average premium: ${avg_premium:.2f}" if avg_premium else "N/A")
    
    # Engagement metrics
    print(f"\n📈 ENGAGEMENT METRICS")
    engagement = CustomerEngagement.objects.aggregate(
        avg_tenure=Avg('customer_tenure_months'),
        avg_satisfaction=Avg('service_satisfaction_score'),
        total_dependents=Count('id'),
        avg_late_payments=Avg('late_payments_count'),
        avg_complaints=Avg('complaints_count')
    )
    
    print(f"Average customer tenure: {engagement['avg_tenure']:.1f} months")
    print(f"Average satisfaction score: {engagement['avg_satisfaction']:.1f}/5")
    print(f"Average late payments: {engagement['avg_late_payments']:.1f}")
    print(f"Average complaints: {engagement['avg_complaints']:.1f}")
    
    # Churn risk analysis
    print(f"\n⚠️  CHURN RISK ANALYSIS")
    churn_stats = ChurnPrediction.objects.values('risk_level').annotate(
        count=Count('id'),
        avg_churn=Avg('churn_percentage')
    ).order_by('-avg_churn')
    
    for stat in churn_stats:
        percentage = (stat['count'] / total_customers) * 100
        print(f"{stat['risk_level']} Risk: {stat['count']} customers ({percentage:.1f}%) - Avg churn: {stat['avg_churn']:.1f}%")
    
    # High-risk customers
    high_risk = ChurnPrediction.objects.filter(risk_level='HIGH').count()
    print(f"\n🚨 HIGH-RISK CUSTOMERS: {high_risk} ({(high_risk/total_customers)*100:.1f}%)")
    
    # Data quality checks
    print(f"\n✅ DATA QUALITY CHECKS")
    
    # Check for missing emails
    missing_email = Customer.objects.filter(email='').count()
    print(f"Customers with missing email: {missing_email}")
    
    # Check for missing phone numbers
    missing_phone = Customer.objects.filter(phone_primary='').count()
    print(f"Customers with missing phone: {missing_phone}")
    
    # Check duplicate national IDs
    duplicate_national_ids = Customer.objects.values('national_id').annotate(count=Count('id')).filter(count__gt=1).count()
    print(f"Duplicate national IDs: {duplicate_national_ids}")
    
    # Sample customer data
    print(f"\n👤 SAMPLE CUSTOMER DATA")
    sample_customers = Customer.objects.all()[:3]
    for customer in sample_customers:
        policy = Policy.objects.filter(customer=customer).first()
        engagement = CustomerEngagement.objects.filter(customer=customer).first()
        churn = ChurnPrediction.objects.filter(customer=customer).first()
        
        print(f"\n{customer.first_name} {customer.last_name} ({customer.customer_number})")
        print(f"  Email: {customer.email}")
        print(f"  Location: {customer.location.city}")
        print(f"  Policy: {policy.policy_type.name if policy else 'N/A'} - ${policy.premium_amount if policy else 'N/A'}")
        print(f"  Tenure: {engagement.customer_tenure_months if engagement else 'N/A'} months")
        print(f"  Churn Risk: {churn.risk_level} ({churn.churn_percentage}%)" if churn else "N/A")
    
    print(f"\n" + "=" * 60)
    print("✅ IMPORT VERIFICATION COMPLETE")
    print("=" * 60)


if __name__ == '__main__':
    try:
        verify_import()
    except Exception as e:
        print(f"❌ Verification failed: {str(e)}")
        sys.exit(1)
