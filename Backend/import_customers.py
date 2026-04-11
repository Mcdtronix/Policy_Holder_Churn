#!/usr/bin/env python3
"""
Nyaradzo Customer Data Import Script
=====================================
Professional data import utility for churn dataset.

Features:
- Data validation and cleansing
- Duplicate detection and handling
- Progress tracking and error reporting
- Transactional integrity
- Comprehensive logging

Usage:
    python manage.py import_customers nyaradzo_churn_dataset_5000_customers.csv

Author: Nyaradzo Engineering Team
"""

import os
import sys
import csv
import logging
from datetime import datetime, date
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from churn.models import Customer, Gender, Location, IncomeLevel, Policy, CustomerEngagement, ChurnPrediction

# Configure professional logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('customer_import.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class CustomerImportCommand(BaseCommand):
    """
    Django management command for importing customer data from CSV.
    
    Handles data mapping, validation, and error reporting with professional
    logging and transaction management.
    """
    
    help = 'Import customers from CSV file with comprehensive validation'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to the CSV file containing customer data'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Validate data without importing to database'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Number of records to process in each transaction (default: 1000)'
        )
    
    def handle(self, *args, **options):
        """Main command execution handler."""
        csv_file = options['csv_file']
        dry_run = options['dry_run']
        batch_size = options['batch_size']
        
        logger.info("=" * 60)
        logger.info("NYARADZO CUSTOMER DATA IMPORT")
        logger.info("=" * 60)
        logger.info(f"Source file: {csv_file}")
        logger.info(f"Dry run mode: {dry_run}")
        logger.info(f"Batch size: {batch_size}")
        logger.info(f"Started at: {timezone.now()}")
        
        # Validate file existence
        if not os.path.exists(csv_file):
            logger.error(f"CSV file not found: {csv_file}")
            sys.exit(1)
        
        # Initialize reference data
        self._initialize_reference_data()
        
        # Process the import
        try:
            stats = self._process_import(csv_file, dry_run, batch_size)
            self._log_final_statistics(stats, dry_run)
            
        except Exception as e:
            logger.error(f"Import failed: {str(e)}")
            logger.exception("Full error traceback:")
            sys.exit(1)
    
    def _initialize_reference_data(self):
        """Initialize or create reference data required for import."""
        logger.info("Initializing reference data...")
        
        # Create gender records
        genders = [
            ('M', 'Male'),
            ('F', 'Female'),
            ('O', 'Other')
        ]
        for code, label in genders:
            Gender.objects.get_or_create(code=code, defaults={'label': label})
        
        # Create income level records
        income_levels = [
            ('LOW', 'Low Income', Decimal('0'), Decimal('500')),
            ('MEDIUM', 'Medium Income', Decimal('500'), Decimal('2000')),
            ('HIGH', 'High Income', Decimal('2000'), Decimal('999999'))
        ]
        for code, label, min_usd, max_usd in income_levels:
            IncomeLevel.objects.get_or_create(
                code=code,
                defaults={
                    'label': label,
                    'min_usd': min_usd,
                    'max_usd': max_usd
                }
            )
        
        # Create location records from CSV data
        locations = set()
        with open('nyaradzo_churn_dataset_5000_customers.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                location = row['Location'].strip()
                if location:
                    locations.add(location)
        
        for location in locations:
            Location.objects.get_or_create(
                province=location,
                district=location,
                city=location,
                defaults={'city': location}
            )
        
        logger.info(f"Created {Gender.objects.count()} gender records")
        logger.info(f"Created {IncomeLevel.objects.count()} income level records")
        logger.info(f"Created {Location.objects.count()} location records")
    
    def _process_import(self, csv_file, dry_run, batch_size):
        """Process the CSV file and import customer data."""
        stats = {
            'total_records': 0,
            'processed_records': 0,
            'failed_records': 0,
            'skipped_records': 0,
            'created_customers': 0,
            'created_policies': 0,
            'created_engagement': 0,
            'created_predictions': 0,
            'errors': []
        }
        
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            total_rows = sum(1 for row in reader) - 1  # Subtract header
            f.seek(0)
            reader = csv.DictReader(f)
            
            stats['total_records'] = total_rows
            logger.info(f"Found {total_rows} records to process")
            
            batch_data = []
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    # Process individual record
                    processed_data = self._process_record(row, row_num)
                    
                    if processed_data:
                        batch_data.append(processed_data)
                        
                        # Process batch when full
                        if len(batch_data) >= batch_size:
                            batch_stats = self._process_batch(batch_data, dry_run)
                            self._update_stats(stats, batch_stats)
                            batch_data = []
                            
                            # Progress logging
                            progress = (row_num - 1) / total_rows * 100
                            logger.info(f"Progress: {progress:.1f}% ({row_num-1}/{total_rows})")
                    
                    stats['processed_records'] += 1
                    
                except Exception as e:
                    error_msg = f"Row {row_num}: {str(e)}"
                    stats['errors'].append(error_msg)
                    stats['failed_records'] += 1
                    logger.error(error_msg)
            
            # Process remaining batch
            if batch_data:
                batch_stats = self._process_batch(batch_data, dry_run)
                self._update_stats(stats, batch_stats)
        
        return stats
    
    def _process_record(self, row, row_num):
        """Process individual CSV record and map to Django models."""
        try:
            # Extract and validate data
            customer_id = int(row['Customer_ID'])
            name_parts = row['Name_and_Surname'].strip().split(' ', 1)
            first_name = name_parts[0] if len(name_parts) > 0 else ''
            last_name = name_parts[1] if len(name_parts) > 1 else ''
            
            # Calculate birth year from age (assuming current year)
            current_year = datetime.now().year
            birth_year = current_year - int(row['Age'])
            birth_date = date(birth_year, 1, 1)  # Default to January 1st
            
            # Map reference data
            gender_code = row['Gender'].strip().upper()[0]  # M/F from Male/Female
            income_code = row['Income_Level'].strip().upper()
            location_name = row['Location'].strip()
            
            # Get reference objects
            gender = Gender.objects.get(code=gender_code)
            income_level = IncomeLevel.objects.get(code=income_code)
            location = Location.objects.get(city=location_name)
            
            # Generate unique identifiers
            customer_number = f"NYC-{customer_id:06d}"
            national_id = f"{birth_year % 100:02d}-{customer_id:06d}A{customer_id % 100:02d}"
            email = f"customer{customer_id}@nyaradzo.co.zw"
            
            # Build customer data
            customer_data = {
                'customer_number': customer_number,
                'first_name': first_name,
                'last_name': last_name,
                'date_of_birth': birth_date,
                'national_id': national_id,
                'gender': gender,
                'location': location,
                'income_level': income_level,
                'email': email,
                'phone_primary': f"263{customer_id:09d}",  # Generate phone number
                'address_line1': f"{location_name}, Zimbabwe",
                'is_active': True,
                'created_at': timezone.now(),
                'updated_at': timezone.now()
            }
            
            # Policy data
            policy_data = {
                'policy_number': f"POL-{customer_id:06d}",
                'policy_type': row['Policy_Type'].strip(),
                'premium_amount': Decimal(row['Premium_Amount']),
                'start_date': timezone.now().date(),
                'status': 'ACTIVE',
                'created_at': timezone.now(),
                'updated_at': timezone.now()
            }
            
            # Engagement data
            engagement_data = {
                'dependents_count': int(row['Dependents']),
                'late_payments_count': int(row['Late_Payments']),
                'missed_payments_count': int(row['Missed_Payments']),
                'complaints_count': int(row['Number_of_Complaints']),
                'claims_filed_count': int(row['Claims_Filed']),
                'customer_tenure_months': int(row['Customer_Tenure']),
                'service_satisfaction_score': int(row['Service_Satisfaction']),
                'last_interaction_date': timezone.now().date(),
                'created_at': timezone.now(),
                'updated_at': timezone.now()
            }
            
            # Churn prediction data
            prediction_data = {
                'churn_percentage': Decimal(row['Churn_Percentage']),
                'risk_level': self._calculate_risk_level(Decimal(row['Churn_Percentage'])),
                'prediction_date': timezone.now().date(),
                'model_version': '1.0',
                'confidence_score': Decimal('0.85'),
                'created_at': timezone.now(),
                'updated_at': timezone.now()
            }
            
            return {
                'customer': customer_data,
                'policy': policy_data,
                'engagement': engagement_data,
                'prediction': prediction_data,
                'row_num': row_num
            }
            
        except Exception as e:
            raise Exception(f"Data processing failed: {str(e)}")
    
    def _calculate_risk_level(self, churn_percentage):
        """Calculate risk level based on churn percentage."""
        if churn_percentage >= 80:
            return 'HIGH'
        elif churn_percentage >= 50:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _process_batch(self, batch_data, dry_run):
        """Process a batch of records in a single transaction."""
        batch_stats = {
            'created_customers': 0,
            'created_policies': 0,
            'created_engagement': 0,
            'created_predictions': 0,
            'skipped_records': 0
        }
        
        if dry_run:
            logger.info(f"DRY RUN: Would process {len(batch_data)} records")
            batch_stats.update({
                'created_customers': len(batch_data),
                'created_policies': len(batch_data),
                'created_engagement': len(batch_data),
                'created_predictions': len(batch_data)
            })
            return batch_stats
        
        try:
            with transaction.atomic():
                for record in batch_data:
                    # Check for existing customer
                    customer_number = record['customer']['customer_number']
                    if Customer.objects.filter(customer_number=customer_number).exists():
                        batch_stats['skipped_records'] += 1
                        continue
                    
                    # Create customer
                    customer = Customer.objects.create(**record['customer'])
                    batch_stats['created_customers'] += 1
                    
                    # Create policy
                    policy_data = record['policy'].copy()
                    policy_data['customer'] = customer
                    Policy.objects.create(**policy_data)
                    batch_stats['created_policies'] += 1
                    
                    # Create engagement
                    engagement_data = record['engagement'].copy()
                    engagement_data['customer'] = customer
                    CustomerEngagement.objects.create(**engagement_data)
                    batch_stats['created_engagement'] += 1
                    
                    # Create churn prediction
                    prediction_data = record['prediction'].copy()
                    prediction_data['customer'] = customer
                    ChurnPrediction.objects.create(**prediction_data)
                    batch_stats['created_predictions'] += 1
                    
        except Exception as e:
            logger.error(f"Batch transaction failed: {str(e)}")
            raise
        
        return batch_stats
    
    def _update_stats(self, stats, batch_stats):
        """Update cumulative statistics."""
        for key in batch_stats:
            stats[key] += batch_stats[key]
    
    def _log_final_statistics(self, stats, dry_run):
        """Log comprehensive import statistics."""
        logger.info("=" * 60)
        logger.info("IMPORT SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Mode: {'DRY RUN' if dry_run else 'LIVE IMPORT'}")
        logger.info(f"Total records in file: {stats['total_records']}")
        logger.info(f"Records processed: {stats['processed_records']}")
        logger.info(f"Records failed: {stats['failed_records']}")
        logger.info(f"Records skipped (duplicates): {stats['skipped_records']}")
        
        if not dry_run:
            logger.info(f"Customers created: {stats['created_customers']}")
            logger.info(f"Policies created: {stats['created_policies']}")
            logger.info(f"Engagement records created: {stats['created_engagement']}")
            logger.info(f"Churn predictions created: {stats['created_predictions']}")
        
        if stats['errors']:
            logger.warning(f"Errors encountered: {len(stats['errors'])}")
            logger.warning("First 10 errors:")
            for error in stats['errors'][:10]:
                logger.warning(f"  - {error}")
        
        success_rate = (stats['processed_records'] - stats['failed_records']) / stats['total_records'] * 100
        logger.info(f"Success rate: {success_rate:.2f}%")
        logger.info(f"Completed at: {timezone.now()}")
        logger.info("=" * 60)


if __name__ == '__main__':
    # Allow running as standalone script
    from django.core.management import execute_from_command_line
    
    execute_from_command_line(['manage.py', 'import_customers'] + sys.argv[1:])
