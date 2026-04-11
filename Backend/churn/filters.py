"""
filters.py — Customer QuerySet Filters
========================================
Enables fine-grained filtering on the /customers/ list endpoint
via URL query parameters using django-filter.

Example usage:
  GET /api/v1/customers/?gender=Female&income_level=Low&policy_type=Family
  GET /api/v1/customers/?age_min=30&age_max=50&missed_payments_min=3
  GET /api/v1/customers/?location=Harare&payment_method=Ecocash
"""

import django_filters
from .models import Customer, Gender, IncomeLevel, PolicyType, PaymentMethod, Location


class CustomerFilter(django_filters.FilterSet):
    """
    Comprehensive filter set for the Customer model.
    Supports exact matches on categorical fields and range filters
    on numerical fields.
    """

    # ── Exact filters ──────────────────────────────────────────────────────────
    gender         = django_filters.ChoiceFilter(choices=Gender.choices)
    location       = django_filters.ChoiceFilter(choices=Location.choices)
    income_level   = django_filters.ChoiceFilter(choices=IncomeLevel.choices)
    policy_type    = django_filters.ChoiceFilter(choices=PolicyType.choices)
    payment_method = django_filters.ChoiceFilter(choices=PaymentMethod.choices)

    # ── Range filters ──────────────────────────────────────────────────────────
    age_min = django_filters.NumberFilter(field_name="age", lookup_expr="gte", label="Minimum Age")
    age_max = django_filters.NumberFilter(field_name="age", lookup_expr="lte", label="Maximum Age")

    tenure_min = django_filters.NumberFilter(field_name="customer_tenure", lookup_expr="gte", label="Min Tenure (years)")
    tenure_max = django_filters.NumberFilter(field_name="customer_tenure", lookup_expr="lte", label="Max Tenure (years)")

    premium_min = django_filters.NumberFilter(field_name="premium_amount", lookup_expr="gte", label="Min Premium")
    premium_max = django_filters.NumberFilter(field_name="premium_amount", lookup_expr="lte", label="Max Premium")

    missed_payments_min = django_filters.NumberFilter(field_name="missed_payments", lookup_expr="gte")
    late_payments_min   = django_filters.NumberFilter(field_name="late_payments",   lookup_expr="gte")
    complaints_min      = django_filters.NumberFilter(field_name="number_of_complaints", lookup_expr="gte")

    satisfaction_min = django_filters.NumberFilter(field_name="service_satisfaction", lookup_expr="gte")
    satisfaction_max = django_filters.NumberFilter(field_name="service_satisfaction", lookup_expr="lte")

    class Meta:
        model  = Customer
        fields = [
            "gender", "location", "income_level", "policy_type", "payment_method",
            "age_min", "age_max",
            "tenure_min", "tenure_max",
            "premium_min", "premium_max",
            "missed_payments_min", "late_payments_min", "complaints_min",
            "satisfaction_min", "satisfaction_max",
        ]
