"""
Management command: import_customers
======================================
Bulk-imports the Nyaradzo dataset CSV into the Customer table.

Usage
-----
  python manage.py import_customers path/to/nyaradzo_churn_dataset_5000_customers.csv

Options
-------
  --clear     Deletes all existing customer records before import (use with caution)
  --batch     Number of records per bulk_create batch (default: 500)
"""

import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from churn.models import Customer


class Command(BaseCommand):
    help = "Import customer records from the Nyaradzo dataset CSV file."

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str, help="Path to the CSV file.")
        parser.add_argument(
            "--clear",
            action="store_true",
            default=False,
            help="Clear existing customers before importing.",
        )
        parser.add_argument(
            "--batch",
            type=int,
            default=500,
            help="Bulk insert batch size (default: 500).",
        )

    def handle(self, *args, **options):
        csv_path = Path(options["csv_path"])

        if not csv_path.exists():
            raise CommandError(f"File not found: {csv_path}")

        if options["clear"]:
            count = Customer.objects.count()
            Customer.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Cleared {count} existing customer records."))

        batch_size  = options["batch"]
        records     = []
        total       = 0
        skipped     = 0

        self.stdout.write(f"Reading {csv_path.name} ...")

        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                try:
                    records.append(
                        Customer(
                            name_and_surname    = row["Name_and_Surname"].strip(),
                            age                 = int(row["Age"]),
                            gender              = row["Gender"].strip(),
                            location            = row["Location"].strip(),
                            income_level        = row["Income_Level"].strip(),
                            policy_type         = row["Policy_Type"].strip(),
                            premium_amount      = int(row["Premium_Amount"]),
                            dependents          = int(row["Dependents"]),
                            payment_method      = row["Payment_Method"].strip(),
                            late_payments       = int(row["Late_Payments"]),
                            missed_payments     = int(row["Missed_Payments"]),
                            number_of_complaints= int(row["Number_of_Complaints"]),
                            claims_filed        = int(row["Claims_Filed"]),
                            customer_tenure     = int(row["Customer_Tenure"]),
                            service_satisfaction= int(row["Service_Satisfaction"]),
                        )
                    )
                    total += 1

                except (KeyError, ValueError) as exc:
                    skipped += 1
                    self.stderr.write(f"  Skipped row {total + skipped}: {exc}")

        if not records:
            raise CommandError("No valid records found in the CSV file.")

        self.stdout.write(f"Inserting {total:,} records in batches of {batch_size} ...")

        with transaction.atomic():
            Customer.objects.bulk_create(records, batch_size=batch_size)

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Import complete: {total:,} customers imported, {skipped} skipped."
            )
        )
