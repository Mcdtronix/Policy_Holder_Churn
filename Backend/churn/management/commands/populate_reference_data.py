"""
Management command to populate reference data tables
====================================================
Creates initial data for Gender, Location, IncomeLevel, and PolicyType models.

Usage:
    python manage.py populate_reference_data
"""

from django.core.management.base import BaseCommand
from churn import models


class Command(BaseCommand):
    help = 'Populate reference data tables with initial data'

    def handle(self, *args, **options):
        self.stdout.write('Populating reference data...')

        # Create genders
        genders = [
            {'code': 'M', 'label': 'Male'},
            {'code': 'F', 'label': 'Female'},
        ]
        for gender_data in genders:
            models.Gender.objects.get_or_create(
                code=gender_data['code'],
                defaults={'label': gender_data['label']}
            )
        self.stdout.write('✓ Created genders')

        # Create locations
        locations = [
            {'province': 'Harare', 'district': 'Harare', 'city': 'Harare'},
            {'province': 'Bulawayo', 'district': 'Bulawayo', 'city': 'Bulawayo'},
            {'province': 'Manicaland', 'district': 'Mutare', 'city': 'Mutare'},
            {'province': 'Mashonaland East', 'district': 'Marondera', 'city': 'Marondera'},
            {'province': 'Mashonaland West', 'district': 'Chinhoyi', 'city': 'Chinhoyi'},
        ]
        for location_data in locations:
            models.Location.objects.get_or_create(
                province=location_data['province'],
                district=location_data['district'],
                city=location_data['city']
            )
        self.stdout.write('✓ Created locations')

        # Create income levels
        income_levels = [
            {'code': 'LOW', 'label': 'Low', 'min_usd': 0, 'max_usd': 500},
            {'code': 'MED', 'label': 'Medium', 'min_usd': 501, 'max_usd': 2000},
            {'code': 'HIGH', 'label': 'High', 'min_usd': 2001, 'max_usd': None},
        ]
        for income_data in income_levels:
            models.IncomeLevel.objects.get_or_create(
                code=income_data['code'],
                defaults={
                    'label': income_data['label'],
                    'min_usd': income_data['min_usd'],
                    'max_usd': income_data['max_usd']
                }
            )
        self.stdout.write('✓ Created income levels')

        # Create policy types
        policy_types = [
            {'code': 'IND', 'name': 'Individual', 'description': 'Single person policy'},
            {'code': 'FAM', 'name': 'Family', 'description': 'Family coverage policy'},
        ]
        for policy_data in policy_types:
            models.PolicyType.objects.get_or_create(
                code=policy_data['code'],
                defaults={
                    'name': policy_data['name'],
                    'description': policy_data['description']
                }
            )
        self.stdout.write('✓ Created policy types')

        self.stdout.write(self.style.SUCCESS('Reference data populated successfully!'))