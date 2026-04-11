#!/usr/bin/env python3
"""
Quick Customer Data Import Utility
==================================
Simplified import script for immediate data loading.

Usage:
    python quick_import.py
"""

import os
import sys
import csv
from datetime import datetime, date
from decimal import Decimal

# Add Django project path
sys.path.append('/home/aqi/Documents/Projects/Insuarance_Churn_Prediction/Backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nyaradzo_backend.settings')

import django
django.setup()

from churn.models import Customer, Gender, Location, IncomeLevel, Policy, PolicyType, CustomerEngagement, ChurnPrediction


def create_reference_data():
    """Create required reference data."""
    print("Creating reference data...")
    
    # Genders
    genders = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    for code, label in genders:
        Gender.objects.get_or_create(code=code, defaults={'label': label})
    
    # Income Levels
    income_levels = [
        ('LOW', 'Low Income', Decimal('0'), Decimal('500')),
        ('MEDIUM', 'Medium Income', Decimal('500'), Decimal('2000')),
        ('HIGH', 'High Income', Decimal('2000'), Decimal('999999'))
    ]
    for code, label, min_usd, max_usd in income_levels:
        IncomeLevel.objects.get_or_create(
            code=code,
            defaults={'label': label, 'min_usd': min_usd, 'max_usd': max_usd}
        )
    
    # Policy Types
    policy_types = [
        ('FAMILY', 'Family Policy', 'Comprehensive family coverage'),
        ('INDIVIDUAL', 'Individual Policy', 'Personal insurance coverage')
    ]
    for code, name, description in policy_types:
        PolicyType.objects.get_or_create(
            code=code,
            defaults={'name': name, 'description': description}
        )
    
    # Locations from CSV - clean duplicates first
    print("Clearing duplicate locations...")
    Location.objects.all().delete()
    
    locations = set()
    with open('/home/aqi/Documents/Projects/Insuarance_Churn_Prediction/nyaradzo_churn_dataset_5000_customers.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            locations.add(row['Location'].strip())
    
    for location in locations:
        Location.objects.create(
            province=location,
            district=location, 
            city=location
        )
    
    print(f"Created {Gender.objects.count()} genders")
    print(f"Created {IncomeLevel.objects.count()} income levels")
    print(f"Created {PolicyType.objects.count()} policy types")
    print(f"Created {Location.objects.count()} locations")


def import_customers():
    """Import customers from CSV file."""
    csv_file = '/home/aqi/Documents/Projects/Insuarance_Churn_Prediction/nyaradzo_churn_dataset_5000_customers.csv'
    
    print(f"Importing customers from {csv_file}...")
    
    created_count = 0
    skipped_count = 0
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        
        for row_num, row in enumerate(reader, start=2):
            try:
                # Extract data
                customer_id = int(row['Customer_ID'])
                name_parts = row['Name_and_Surname'].strip().split(' ', 1)
                first_name = name_parts[0] if len(name_parts) > 0 else 'Unknown'
                last_name = name_parts[1] if len(name_parts) > 1 else 'Customer'
                
                # Calculate birth date
                current_year = datetime.now().year
                birth_year = current_year - int(row['Age'])
                birth_date = date(birth_year, 1, 1)
                
                # Map references
                gender_code = row['Gender'].strip().upper()[0]
                income_code = row['Income_Level'].strip().upper()
                location_name = row['Location'].strip()
                policy_type_name = row['Policy_Type'].strip().upper()
                
                gender = Gender.objects.get(code=gender_code)
                income_level = IncomeLevel.objects.get(code=income_code)
                location = Location.objects.get(city=location_name)
                policy_type = PolicyType.objects.get(code=policy_type_name)
                
                # Generate identifiers
                customer_number = f"NYC-{customer_id:06d}"
                national_id = f"{birth_year % 100:02d}-{customer_id:06d}A{customer_id % 100:02d}"
                email = f"customer{customer_id}@nyaradzo.co.zw"
                
                # Check if exists
                if Customer.objects.filter(customer_number=customer_number).exists():
                    skipped_count += 1
                    continue
                
                # Create customer
                customer = Customer.objects.create(
                    customer_number=customer_number,
                    first_name=first_name,
                    last_name=last_name,
                    date_of_birth=birth_date,
                    national_id=national_id,
                    gender=gender,
                    location=location,
                    income_level=income_level,
                    email=email,
                    phone_primary=f"263{customer_id:09d}",
                    address_line1=f"{location_name}, Zimbabwe",
                    is_active=True
                )
                
                # Create policy
                Policy.objects.create(
                    customer=customer,
                    policy_number=f"POL-{customer_id:06d}",
                    policy_type=policy_type,
                    premium_amount=Decimal(row['Premium_Amount']),
                    start_date=datetime.now().date(),
                    status='ACTIVE'
                )
                
                # Create engagement
                CustomerEngagement.objects.create(
                    customer=customer,
                    dependents_count=int(row['Dependents']),
                    late_payments_count=int(row['Late_Payments']),
                    missed_payments_count=int(row['Missed_Payments']),
                    complaints_count=int(row['Number_of_Complaints']),
                    claims_filed_count=int(row['Claims_Filed']),
                    customer_tenure_months=int(row['Customer_Tenure']),
                    service_satisfaction_score=int(row['Service_Satisfaction']),
                    last_interaction_date=datetime.now().date()
                )
                
                # Create churn prediction
                churn_percentage = Decimal(row['Churn_Percentage'])
                risk_level = 'HIGH' if churn_percentage >= 80 else 'MEDIUM' if churn_percentage >= 50 else 'LOW'
                
                ChurnPrediction.objects.create(
                    customer=customer,
                    churn_percentage=churn_percentage,
                    risk_level=risk_level,
                    prediction_date=datetime.now().date(),
                    model_version='1.0',
                    confidence_score=Decimal('0.85')
                )
                
                created_count += 1
                
                # Progress indicator
                if created_count % 100 == 0:
                    print(f"Created {created_count} customers...")
                    
            except Exception as e:
                print(f"Error processing row {row_num}: {str(e)}")
                continue
    
    print(f"\nImport completed!")
    print(f"Customers created: {created_count}")
    print(f"Customers skipped (duplicates): {skipped_count}")
    print(f"Total customers in database: {Customer.objects.count()}")


if __name__ == '__main__':
    print("Nyaradzo Customer Data Import")
    print("=" * 40)
    
    try:
        create_reference_data()
        import_customers()
        print("\n✅ Import successful!")
    except Exception as e:
        print(f"\n❌ Import failed: {str(e)}")
        sys.exit(1)
