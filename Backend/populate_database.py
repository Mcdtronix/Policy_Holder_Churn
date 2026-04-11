#!/usr/bin/env python3
"""
Complete Database Population Script
=================================
Populates entire database with comprehensive data from CSV
and generates realistic related data for all tables.

Features:
- Complete customer data import
- Policy generation with realistic details
- Customer engagement metrics
- Churn predictions with ML-like scoring
- Payment history
- Claims data
- Document records
- Batch jobs and predictions

Usage:
    python populate_database.py
"""

import os
import sys
import csv
import random
from datetime import datetime, date, timedelta
from decimal import Decimal

# Add Django project path
sys.path.append('/home/aqi/Documents/Projects/Insuarance_Churn_Prediction/Backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nyaradzo_backend.settings')

import django
django.setup()

from churn.models import (
    Customer, Gender, Location, IncomeLevel, PolicyType, Policy,
    CustomerEngagement, ChurnPrediction, Payment, PaymentMethod, PremiumSchedule,
    Claim, ClaimDocument, PolicyDocument, ChurnBatchJob, RiskLevel
)
from django.db import transaction
from django.db.models import Avg, Sum
from django.utils import timezone


class DatabasePopulator:
    """Complete database population utility."""
    
    def __init__(self):
        self.csv_file = '/home/aqi/Documents/Projects/Insuarance_Churn_Prediction/nyaradzo_churn_dataset_5000_customers.csv'
        self.customers_data = []
        
    def populate_all(self):
        """Populate entire database with comprehensive data."""
        print("=" * 60)
        print("COMPLETE DATABASE POPULATION")
        print("=" * 60)
        
        with transaction.atomic():
            # Step 1: Create reference data
            self.create_reference_data()
            
            # Step 2: Load and parse CSV data
            self.load_csv_data()
            
            # Step 3: Import customers
            self.import_customers()
            
            # Step 4: Create policies for all customers
            self.create_policies()
            
            # Step 5: Generate engagement data
            self.create_engagement_data()
            
            # Step 6: Create churn predictions
            self.create_churn_predictions()
            
            # Step 7: Generate payment history
            self.create_payment_history()
            
            # Step 8: Create claims data
            self.create_claims_data()
            
            # Step 9: Generate documents
            self.create_documents()
            
            # Step 10: Create batch jobs
            self.create_batch_jobs()
        
        self.print_final_summary()
    
    def create_reference_data(self):
        """Create all required reference data."""
        print("\n📋 Creating reference data...")
        
        # Clear existing reference data
        Gender.objects.all().delete()
        Location.objects.all().delete()
        IncomeLevel.objects.all().delete()
        PolicyType.objects.all().delete()
        
        # Genders
        genders = [
            ('M', 'Male'),
            ('F', 'Female'),
            ('O', 'Other')
        ]
        for code, label in genders:
            Gender.objects.create(code=code, label=label)
        
        # Income Levels
        income_levels = [
            ('LOW', 'Low Income', Decimal('0'), Decimal('500')),
            ('MEDIUM', 'Medium Income', Decimal('500'), Decimal('2000')),
            ('HIGH', 'High Income', Decimal('2000'), Decimal('999999'))
        ]
        for code, label, min_usd, max_usd in income_levels:
            IncomeLevel.objects.create(
                code=code,
                label=label,
                min_usd=min_usd,
                max_usd=max_usd
            )
        
        # Policy Types
        policy_types = [
            ('FAMILY', 'Family Policy', 'Comprehensive family coverage with multiple beneficiaries'),
            ('INDIVIDUAL', 'Individual Policy', 'Personal insurance coverage for individuals'),
            ('BUSINESS', 'Business Policy', 'Commercial insurance for businesses'),
            ('SPECIAL', 'Special Policy', 'Specialized insurance products')
        ]
        for code, name, description in policy_types:
            PolicyType.objects.create(
                code=code,
                name=name,
                description=description
            )
        
        # Risk Levels
        risk_levels = [
            ('LOW', 'Low Risk', Decimal('0'), Decimal('49')),
            ('MEDIUM', 'Medium Risk', Decimal('50'), Decimal('79')),
            ('HIGH', 'High Risk', Decimal('80'), Decimal('100'))
        ]
        for code, label, min_threshold, max_threshold in risk_levels:
            RiskLevel.objects.create(
                code=code,
                label=label,
                min_threshold=min_threshold,
                max_threshold=max_threshold
            )
        
        # Payment Methods
        payment_methods = [
            ('MOBILE_MONEY', 'Mobile Money'),
            ('ECOCASH', 'Ecocash'),
            ('CASH', 'Cash'),
            ('BANK_DEBIT', 'Bank Debit')
        ]
        for code, label in payment_methods:
            PaymentMethod.objects.create(code=code, label=label)
        
        # Extract unique locations from CSV
        locations = set()
        with open(self.csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                locations.add(row['Location'].strip())
        
        for location in sorted(locations):
            Location.objects.create(
                province=location,
                district=location,
                city=location
            )
        
        print(f"✅ Created {Gender.objects.count()} genders")
        print(f"✅ Created {IncomeLevel.objects.count()} income levels")
        print(f"✅ Created {PolicyType.objects.count()} policy types")
        print(f"✅ Created {RiskLevel.objects.count()} risk levels")
        print(f"✅ Created {PaymentMethod.objects.count()} payment methods")
        print(f"✅ Created {Location.objects.count()} locations")
    
    def load_csv_data(self):
        """Load and parse CSV customer data."""
        print(f"\n📊 Loading CSV data from {self.csv_file}...")
        
        with open(self.csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, start=2):
                try:
                    # Parse and validate data
                    customer_id = int(row['Customer_ID'])
                    name_parts = row['Name_and_Surname'].strip().split(' ', 1)
                    first_name = name_parts[0] if len(name_parts) > 0 else 'Unknown'
                    last_name = name_parts[1] if len(name_parts) > 1 else 'Customer'
                    
                    # Calculate birth date
                    current_year = datetime.now().year
                    birth_year = current_year - int(row['Age'])
                    birth_date = date(birth_year, random.randint(1, 12), random.randint(1, 28))
                    
                    # Map reference data
                    gender_code = row['Gender'].strip().upper()[0]
                    income_code = row['Income_Level'].strip().upper()
                    location_name = row['Location'].strip()
                    policy_type_name = row['Policy_Type'].strip().upper()
                    
                    self.customers_data.append({
                        'customer_id': customer_id,
                        'first_name': first_name,
                        'last_name': last_name,
                        'date_of_birth': birth_date,
                        'gender_code': gender_code,
                        'income_code': income_code,
                        'location_name': location_name,
                        'policy_type_name': policy_type_name,
                        'premium_amount': Decimal(row['Premium_Amount']),
                        'dependents': int(row['Dependents']),
                        'payment_method': row['Payment_Method'].strip(),
                        'late_payments': int(row['Late_Payments']),
                        'missed_payments': int(row['Missed_Payments']),
                        'complaints': int(row['Number_of_Complaints']),
                        'claims_filed': int(row['Claims_Filed']),
                        'tenure': int(row['Customer_Tenure']),
                        'satisfaction': int(row['Service_Satisfaction']),
                        'churn_percentage': Decimal(row['Churn_Percentage'])
                    })
                    
                except Exception as e:
                    print(f"⚠️  Error parsing row {row_num}: {str(e)}")
                    continue
        
        print(f"✅ Loaded {len(self.customers_data)} customer records")
    
    def import_customers(self):
        """Import all customers from parsed data."""
        print(f"\n👥 Importing {len(self.customers_data)} customers...")
        
        for data in self.customers_data:
            # Get reference objects
            gender = Gender.objects.get(code=data['gender_code'])
            income_level = IncomeLevel.objects.get(code=data['income_code'])
            location = Location.objects.get(city=data['location_name'])
            
            # Generate identifiers
            customer_number = f"NYC-{data['customer_id']:06d}"
            national_id = f"{data['date_of_birth'].year % 100:02d}-{data['customer_id']:06d}A{data['customer_id'] % 100:02d}"
            email = f"customer{data['customer_id']}@nyaradzo.co.zw"
            
            # Create customer
            Customer.objects.create(
                customer_number=customer_number,
                first_name=data['first_name'],
                last_name=data['last_name'],
                date_of_birth=data['date_of_birth'],
                national_id=national_id,
                gender=gender,
                location=location,
                income_level=income_level,
                email=email,
                phone_primary=f"263{data['customer_id']:09d}",
                phone_secondary=f"263{random.randint(100000000, 999999999)}",
                address_line1=f"{data['location_name']}, Zimbabwe",
                address_line2=f"Plot {random.randint(1, 9999)} {data['location_name']} Road",
                is_active=True
            )
        
        print(f"✅ Created {Customer.objects.count()} customers")
    
    def create_policies(self):
        """Create policies for all customers."""
        print(f"\n📋 Creating policies for all customers...")
        
        customers = Customer.objects.all()
        policy_type_map = {
            'FAMILY': PolicyType.objects.get(code='FAMILY'),
            'INDIVIDUAL': PolicyType.objects.get(code='INDIVIDUAL'),
            'BUSINESS': PolicyType.objects.get(code='BUSINESS'),
            'SPECIAL': PolicyType.objects.get(code='SPECIAL')
        }
        
        for customer in customers:
            # Find corresponding customer data
            customer_data = next((c for c in self.customers_data if c['customer_id'] == int(customer.customer_number.split('-')[1])), None)
            
            if customer_data:
                policy_type = policy_type_map.get(customer_data['policy_type_name'], policy_type_map['INDIVIDUAL'])
                
                # Create policy
                start_date = timezone.now().date() - timedelta(days=random.randint(30, 365))
                end_date = start_date + timedelta(days=365)
                
                Policy.objects.create(
                    customer=customer,
                    policy_number=f"POL-{customer.customer_number.split('-')[1]}",
                    policy_type=policy_type,
                    premium_amount=customer_data['premium_amount'],
                    start_date=start_date,
                    end_date=end_date,
                    status='ACTIVE',
                    sum_assured=customer_data['premium_amount'] * Decimal(random.randint(50, 200)),
                    dependents=customer_data['dependents'],
                    created_at=timezone.now() - timedelta(days=random.randint(1, 365))
                )
        
        print(f"✅ Created {Policy.objects.count()} policies")
    
    def create_engagement_data(self):
        """Create customer engagement data."""
        print(f"\n📈 Creating engagement data...")
        
        customers = Customer.objects.all()
        
        for customer in customers:
            # Find corresponding customer data
            customer_data = next((c for c in self.customers_data if c['customer_id'] == int(customer.customer_number.split('-')[1])), None)
            
            if customer_data:
                CustomerEngagement.objects.create(
                    customer=customer,
                    number_of_complaints=customer_data['complaints'],
                    claims_filed=customer_data['claims_filed'],
                    service_satisfaction=Decimal(customer_data['satisfaction']),
                    last_interaction_at=timezone.now() - timedelta(days=random.randint(1, 30))
                )
        
        print(f"✅ Created {CustomerEngagement.objects.count()} engagement records")
    
    def create_churn_predictions(self):
        """Create churn predictions for all customers."""
        print(f"\n⚠️  Creating churn predictions...")
        
        customers = Customer.objects.all()
        
        for customer in customers:
            # Find corresponding customer data
            customer_data = next((c for c in self.customers_data if c['customer_id'] == int(customer.customer_number.split('-')[1])), None)
            
            if customer_data:
                churn_percentage = customer_data['churn_percentage']
                
                # Calculate risk level
                if churn_percentage >= 80:
                    risk_level_code = 'HIGH'
                elif churn_percentage >= 50:
                    risk_level_code = 'MEDIUM'
                else:
                    risk_level_code = 'LOW'
                
                risk_level = RiskLevel.objects.get(code=risk_level_code)
                
                ChurnPrediction.objects.create(
                    customer=customer,
                    risk_level=risk_level,
                    churn_percentage=churn_percentage,
                    model_version='2.1',
                    predicted_at=timezone.now() - timedelta(hours=random.randint(1, 24))
                )
        
        print(f"✅ Created {ChurnPrediction.objects.count()} churn predictions")
    
    def create_payment_history(self):
        """Create payment history for policies."""
        print(f"\n💰 Creating payment history...")
        
        policies = Policy.objects.all()
        payment_count = 0
        
        for policy in policies:
            # Generate 6-12 months of payment history
            months = random.randint(6, 12)
            for i in range(months):
                payment_date = timezone.now() - timedelta(days=i*30)
                
                # 80% on-time payments, 20% late
                is_late = random.random() < 0.2
                
                payment_method_code = random.choice(['MOBILE_MONEY', 'ECOCASH', 'CASH', 'BANK_DEBIT'])
                payment_method = PaymentMethod.objects.get(code=payment_method_code)
                
                Payment.objects.create(
                    policy=policy,
                    payment_reference=f"PAY-{policy.policy_number}-{i+1:03d}",
                    amount=policy.premium_amount,
                    transaction_date=payment_date,
                    payment_method=payment_method,
                    status='COMPLETED',
                    category='PREMIUM',
                    created_at=payment_date
                )
                payment_count += 1
        
        print(f"✅ Created {payment_count} payment records")
    
    def create_claims_data(self):
        """Create claims data for customers with filed claims."""
        print(f"\n📄 Creating claims data...")
        
        customers_with_claims = [c for c in self.customers_data if c['claims_filed'] > 0]
        claim_count = 0
        
        for customer_data in customers_with_claims:
            customer = Customer.objects.get(customer_number=f"NYC-{customer_data['customer_id']:06d}")
            policy = Policy.objects.get(customer=customer)
            
            # Create claims for this customer
            for i in range(customer_data['claims_filed']):
                claim_date = timezone.now() - timedelta(days=random.randint(1, 180))
                
                # Random claim amounts
                claim_amount = policy.premium_amount * Decimal(random.randint(5, 50))
                
                Claim.objects.create(
                    policy=policy,
                    claim_number=f"CLM-{policy.policy_number}-{i+1:02d}",
                    claim_type=random.choice(['DEATH', 'DISABILITY', 'MEDICAL', 'MATURITY']),
                    description=f"Claim {i+1} for {customer.first_name} {customer.last_name}",
                    amount_claimed=claim_amount,
                    amount_approved=claim_amount * Decimal(random.uniform(0.6, 1.0)),
                    status=random.choice(['APPROVED', 'PENDING', 'REJECTED']),
                    event_date=claim_date.date(),
                    reported_date=claim_date.date(),
                    created_at=claim_date
                )
                claim_count += 1
        
        print(f"✅ Created {claim_count} claim records")
    
    def create_documents(self):
        """Create document records for policies and claims."""
        print(f"\n📎 Creating document records...")
        
        policy_doc_count = 0
        claim_doc_count = 0
        
        # Policy documents
        for policy in Policy.objects.all()[:100]:  # Limit to first 100 policies
            for doc_type in ['PROPOSAL', 'MEDICAL_REPORT', 'ID_COPY']:
                PolicyDocument.objects.create(
                    policy=policy,
                    doc_type=doc_type,
                    title=f"{doc_type} for {policy.policy_number}",
                    uploaded_at=timezone.now() - timedelta(days=random.randint(1, 365))
                )
                policy_doc_count += 1
        
        # Claim documents
        for claim in Claim.objects.all()[:50]:  # Limit to first 50 claims
            for doc_type in ['MEDICAL_REPORT', 'PHOTOGRAPH', 'POLICE_REPORT']:
                ClaimDocument.objects.create(
                    claim=claim,
                    doc_type=doc_type,
                    title=f"{doc_type} for {claim.claim_number}",
                    uploaded_at=timezone.now() - timedelta(days=random.randint(1, 30))
                )
                claim_doc_count += 1
        
        print(f"✅ Created {policy_doc_count} policy documents")
        print(f"✅ Created {claim_doc_count} claim documents")
    
    def create_batch_jobs(self):
        """Create batch job records."""
        print(f"\n🔄 Creating batch jobs...")
        
        # Create different types of batch jobs
        job_types = [
            ('CHURN_PREDICTION', 'Monthly Churn Prediction'),
            ('DATA_SYNC', 'Customer Data Synchronization'),
            ('REPORT_GENERATION', 'Monthly Report Generation'),
            ('CLEANUP', 'Data Cleanup Task')
        ]
        
        for job_code, job_name in job_types:
            # Create multiple instances of each job type
            for i in range(3):
                started_at = timezone.now() - timedelta(days=i*30)
                duration = timedelta(hours=random.randint(1, 6))
                
                ChurnBatchJob.objects.create(
                    model_version=job_code,
                    status=random.choice(['COMPLETED', 'RUNNING', 'FAILED']),
                    started_at=started_at,
                    completed_at=started_at + duration,
                    total_customers=random.randint(1000, 5000),
                    processed=random.randint(1000, 5000)
                )
        
        print(f"✅ Created {ChurnBatchJob.objects.count()} batch jobs")
    
    def print_final_summary(self):
        """Print comprehensive database population summary."""
        print("\n" + "=" * 60)
        print("DATABASE POPULATION COMPLETE")
        print("=" * 60)
        
        print(f"\n📊 FINAL DATABASE STATE:")
        print(f"  Customers: {Customer.objects.count()}")
        print(f"  Policies: {Policy.objects.count()}")
        print(f"  CustomerEngagement: {CustomerEngagement.objects.count()}")
        print(f"  ChurnPredictions: {ChurnPrediction.objects.count()}")
        print(f"  Payments: {Payment.objects.count()}")
        print(f"  Claims: {Claim.objects.count()}")
        print(f"  PolicyDocuments: {PolicyDocument.objects.count()}")
        print(f"  ClaimDocuments: {ClaimDocument.objects.count()}")
        print(f"  ChurnBatchJobs: {ChurnBatchJob.objects.count()}")
        
        print(f"\n📋 REFERENCE DATA:")
        print(f"  Genders: {Gender.objects.count()}")
        print(f"  Locations: {Location.objects.count()}")
        print(f"  IncomeLevels: {IncomeLevel.objects.count()}")
        print(f"  PolicyTypes: {PolicyType.objects.count()}")
        print(f"  RiskLevels: {RiskLevel.objects.count()}")
        
        # Sample statistics
        if Policy.objects.exists():
            avg_premium = Policy.objects.aggregate(avg_premium=Avg('premium_amount'))['avg_premium']
            print(f"\n💰 POLICY STATISTICS:")
            print(f"  Average Premium: ${avg_premium:.2f}")
            print(f"  Total Premium Sum: ${Policy.objects.aggregate(total=Sum('premium_amount'))['total']:.2f}")
        
        if ChurnPrediction.objects.exists():
            high_risk = ChurnPrediction.objects.filter(risk_level='HIGH').count()
            total_customers = Customer.objects.count()
            print(f"\n⚠️  CHURN ANALYSIS:")
            print(f"  High Risk Customers: {high_risk} ({(high_risk/total_customers)*100:.1f}%)")
        
        print(f"\n✅ Database population completed successfully!")
        print("=" * 60)


if __name__ == '__main__':
    try:
        populator = DatabasePopulator()
        populator.populate_all()
    except Exception as e:
        print(f"❌ Database population failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
