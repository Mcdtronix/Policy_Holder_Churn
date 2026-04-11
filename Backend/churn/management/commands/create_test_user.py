"""
Management command to create a test user
========================================
Creates a test user for development purposes.

Usage:
    python manage.py create_test_user
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from churn import models

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a test user for development'

    def handle(self, *args, **options):
        self.stdout.write('Creating test user...')

        # Create test user
        user, created = User.objects.get_or_create(
            email='admin@nyaradzo.co.zw',
            defaults={
                'username': 'admin',
                'first_name': 'Test',
                'last_name': 'Admin',
                'role': User.Role.ADMIN,
                'phone': '+263771234567',
                'department': 'IT'
            }
        )

        if created:
            user.set_password('admin123')
            user.save()
            self.stdout.write(self.style.SUCCESS('✓ Test user created:'))
            self.stdout.write('  Email: admin@nyaradzo.co.zw')
            self.stdout.write('  Password: admin123')
            self.stdout.write('  Role: Admin')
        else:
            self.stdout.write('✓ Test user already exists')

        self.stdout.write(self.style.SUCCESS('Test user setup complete!'))