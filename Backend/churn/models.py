"""
Nyaradzo Assurance Management System
=====================================
Django ORM models — PostgreSQL backend
Covers: Customer Registration, Policy Management,
        Claims Processing, Payments & Premiums,
        and Churn Prediction (ML-ready)

Author : Nyaradzo Engineering Team
Version: 1.0.0
"""

import uuid
from decimal import Decimal
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.db import models
from django.utils import timezone


# ─────────────────────────────────────────────
# 0.  CUSTOM USER  (registered via Django Admin)
# ─────────────────────────────────────────────

class User(AbstractUser):
    """
    Extended user model.  Superusers register staff accounts
    through Django Admin panel.
    Roles drive permission granularity throughout system.
    """

    class Role(models.TextChoices):
        SUPERUSER       = "SUPERUSER",       "Superuser"
        ADMIN           = "ADMIN",           "Administrator"
        UNDERWRITER     = "UNDERWRITER",     "Underwriter"
        CLAIMS_OFFICER  = "CLAIMS_OFFICER",  "Claims Officer"
        FINANCE_OFFICER = "FINANCE_OFFICER", "Finance Officer"
        AGENT           = "AGENT",           "Sales Agent"
        READ_ONLY       = "READ_ONLY",       "Read-Only Viewer"

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email       = models.EmailField(unique=True, blank=False, null=False)
    role        = models.CharField(max_length=20, choices=Role.choices, default=Role.READ_ONLY)
    phone       = models.CharField(max_length=20, blank=True)
    department  = models.CharField(max_length=100, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        db_table    = "auth_user"
        verbose_name        = "System User"
        verbose_name_plural = "System Users"
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"


# ─────────────────────────────────────────────
# 1.  REFERENCE / LOOKUP  TABLES
# ─────────────────────────────────────────────

class Gender(models.Model):
    code  = models.CharField(max_length=10, unique=True)
    label = models.CharField(max_length=50)

    class Meta:
        db_table = "ref_genders"
        ordering = ["label"]

    def __str__(self):
        return self.label


class Location(models.Model):
    province = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    city     = models.CharField(max_length=100)

    class Meta:
        db_table = "ref_locations"
        unique_together = ("province", "district", "city")
        ordering = ["province", "district", "city"]

    def __str__(self):
        return f"{self.city}, {self.district}"


class IncomeLevel(models.Model):
    code          = models.CharField(max_length=20, unique=True)
    label         = models.CharField(max_length=100)
    min_usd       = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    max_usd       = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = "ref_income_levels"
        ordering = ["label"]

    def __str__(self):
        return self.label


class PolicyType(models.Model):
    code        = models.CharField(max_length=30, unique=True)
    name        = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    is_active   = models.BooleanField(default=True)

    class Meta:
        db_table = "ref_policy_types"
        ordering = ["name"]

    def __str__(self):
        return self.name


class PaymentMethod(models.Model):
    code  = models.CharField(max_length=30, unique=True)
    label = models.CharField(max_length=100)

    class Meta:
        db_table = "ref_payment_methods"

    def __str__(self):
        return self.label


class RiskLevel(models.Model):
    code          = models.CharField(max_length=20, unique=True)
    label         = models.CharField(max_length=50)
    min_threshold = models.DecimalField(max_digits=5, decimal_places=2)
    max_threshold = models.DecimalField(max_digits=5, decimal_places=2)
    color_hex     = models.CharField(max_length=7, default="#000000",
                                     help_text="Hex colour for UI badges e.g. #FF0000")

    class Meta:
        db_table = "ref_risk_levels"
        ordering = ["min_threshold"]

    def __str__(self):
        return self.label


# ─────────────────────────────────────────────
# 2.  CUSTOMER  (Core Identity)
# ─────────────────────────────────────────────

class Customer(models.Model):
    """
    Core policyholder entity.
    Demographic and contact information only —
    financial, policy, and engagement details
    are each held in their own dedicated tables (2NF/3NF).
    """

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_number = models.CharField(
        max_length=20, unique=True, editable=False, null=True,
        help_text="Auto-generated human-readable reference e.g. NYC-000123"
    )

    # ── Identity
    first_name      = models.CharField(max_length=100)
    last_name       = models.CharField(max_length=100)
    date_of_birth   = models.DateField()
    national_id     = models.CharField(
        max_length=30, unique=True,
        validators=[RegexValidator(r"^\d{2}-\d{6,7}[A-Z]\d{2}$",
                                   "Enter a valid Zimbabwean National ID e.g. 63-123456A75")]
    )
    gender          = models.ForeignKey(Gender, on_delete=models.PROTECT, related_name="customers")
    location        = models.ForeignKey(Location, on_delete=models.PROTECT, related_name="customers")
    income_level    = models.ForeignKey(IncomeLevel, on_delete=models.PROTECT, related_name="customers")

    # ── Contact
    email           = models.EmailField(unique=True)
    phone_primary   = models.CharField(max_length=20)
    phone_secondary = models.CharField(max_length=20, blank=True)
    address_line1   = models.CharField(max_length=255)
    address_line2   = models.CharField(max_length=255, blank=True)

    # ── Status
    is_active       = models.BooleanField(default=True)
    registered_by   = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="registered_customers"
    )

    # ── Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "customers"
        indexes  = [
            models.Index(fields=["last_name", "first_name"]),
            models.Index(fields=["national_id"]),
            models.Index(fields=["customer_number"]),
        ]
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.customer_number} — {self.last_name}, {self.first_name}"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new and not self.customer_number:
            self.customer_number = f"NYC-{self.pk.int % 1000000:06d}"
            self.save(update_fields=['customer_number'])

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        today = timezone.now().date()
        dob   = self.date_of_birth
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    # ── ML Feature Properties ──────────────────────────────────────────────────

    @property
    def primary_policy(self):
        """Get the first active policy for this customer."""
        return self.policies.filter(status=Policy.Status.ACTIVE).first() or self.policies.first()

    @property
    def premium_amount(self):
        """Premium amount from the primary active policy."""
        policy = self.primary_policy
        return float(policy.premium_amount) if policy else 0.0

    @property
    def policy_type(self):
        """Policy type from the primary active policy."""
        policy = self.primary_policy
        return policy.policy_type.name if policy else "Unknown"

    @property
    def dependents(self):
        """Number of dependents from the primary active policy."""
        policy = self.primary_policy
        return policy.dependents if policy else 0

    @property
    def payment_method(self):
        """Payment method from latest payment, or default."""
        from churn.models import Payment
        latest_payment = Payment.objects.filter(policy__customer=self).order_by('-transaction_date').first()
        return latest_payment.payment_method.label if latest_payment else "Bank Debit"

    @property
    def late_payments(self):
        """Count of late premium payments."""
        from churn.models import PremiumSchedule
        return PremiumSchedule.objects.filter(
            policy__customer=self, is_late=True
        ).count()

    @property
    def missed_payments(self):
        """Count of missed/unpaid premium schedules."""
        from churn.models import PremiumSchedule
        return PremiumSchedule.objects.filter(
            policy__customer=self, is_paid=False
        ).exclude(policy__status=Policy.Status.PENDING).count()

    @property
    def customer_tenure(self):
        """Months since first policy was created."""
        from dateutil.relativedelta import relativedelta
        earliest_policy = self.policies.order_by('start_date').first()
        if earliest_policy:
            today = timezone.now().date()
            delta = relativedelta(today, earliest_policy.start_date)
            return delta.years * 12 + delta.months
        return 0

    @property
    def number_of_complaints(self):
        """Number of complaints from engagement record."""
        try:
            return self.engagement.number_of_complaints
        except:
            return 0

    @property
    def claims_filed(self):
        """Number of claims filed by this customer."""
        try:
            return self.engagement.claims_filed
        except:
            return 0

    @property
    def service_satisfaction(self):
        """Service satisfaction score (0-10)."""
        try:
            return float(self.engagement.service_satisfaction) if self.engagement.service_satisfaction else 5.0
        except:
            return 5.0

    @property
    def risk_score(self):
        """Calculated risk score combining payment and complaint history."""
        return (
            self.late_payments 
            + (self.missed_payments * 2) 
            + self.number_of_complaints
        )

    @property
    def engagement_score(self):
        """Engagement score combining tenure and satisfaction."""
        return self.service_satisfaction * max(1, self.customer_tenure)

    @property
    def premium_per_dependent(self):
        """Premium amount per dependent (or per 1 if no dependents)."""
        return self.premium_amount / (self.dependents + 1)


# ─────────────────────────────────────────────
# 3.  POLICY  MANAGEMENT
# ─────────────────────────────────────────────

class Policy(models.Model):
    """
    Insurance policy issued to a customer.
    One customer may hold multiple policies.
    """

    class Status(models.TextChoices):
        PENDING    = "PENDING",    "Pending Approval"
        ACTIVE     = "ACTIVE",     "Active"
        LAPSED     = "LAPSED",     "Lapsed"
        SUSPENDED  = "SUSPENDED",  "Suspended"
        TERMINATED = "TERMINATED", "Terminated"
        MATURED    = "MATURED",    "Matured"

    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    policy_number  = models.CharField(max_length=30, unique=True, editable=False)
    customer       = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="policies")
    policy_type    = models.ForeignKey(PolicyType, on_delete=models.PROTECT, related_name="policies")
    underwritten_by= models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="underwritten_policies"
    )

    # ── Terms
    start_date     = models.DateField()
    end_date       = models.DateField(null=True, blank=True)
    sum_assured    = models.DecimalField(max_digits=14, decimal_places=2,
                                         validators=[MinValueValidator(Decimal("0.01"))])
    premium_amount = models.DecimalField(max_digits=12, decimal_places=2,
                                         validators=[MinValueValidator(Decimal("0.01"))])
    premium_frequency = models.CharField(
        max_length=20,
        choices=[("MONTHLY","Monthly"),("QUARTERLY","Quarterly"),
                 ("SEMI_ANNUAL","Semi-Annual"),("ANNUAL","Annual")],
        default="MONTHLY"
    )
    dependents     = models.PositiveSmallIntegerField(default=0)
    status         = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    notes          = models.TextField(blank=True)

    # ── Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "policies"
        indexes  = [
            models.Index(fields=["customer", "status"]),
            models.Index(fields=["policy_number"]),
            models.Index(fields=["start_date", "end_date"]),
        ]
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.policy_number:
            count = Policy.objects.count() + 1
            self.policy_number = f"POL-{count:08d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.policy_number} ({self.policy_type})"

    @property
    def is_active(self):
        return self.status == self.Status.ACTIVE

    @property
    def tenure_months(self):
        today = timezone.now().date()
        delta = today - self.start_date
        return delta.days // 30


class PolicyBeneficiary(models.Model):
    """
    Policy beneficiaries allow the system to register multiple persons who can receive
    benefit payouts. Supports primary vs dependents and share allocation.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    policy = models.ForeignKey(
        Policy,
        on_delete=models.CASCADE,
        related_name='beneficiaries'
    )
    full_name = models.CharField(max_length=200)
    relationship = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    is_primary = models.BooleanField(default=False)
    share_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'policy_beneficiaries'
        ordering = ['-is_primary', 'full_name']

    def __str__(self):
        return f"{self.full_name} ({'primary' if self.is_primary else 'secondary'})"


class PolicyDocument(models.Model):
    """
    Supporting documents attached to a policy
    (e.g. signed proposal form, medical report).
    """

    class DocType(models.TextChoices):
        PROPOSAL        = "PROPOSAL",       "Proposal Form"
        MEDICAL_REPORT  = "MEDICAL_REPORT", "Medical Report"
        ID_COPY         = "ID_COPY",        "ID / Passport Copy"
        ENDORSEMENT     = "ENDORSEMENT",    "Endorsement"
        OTHER           = "OTHER",          "Other"

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    policy      = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name="documents")
    doc_type    = models.CharField(max_length=30, choices=DocType.choices)
    title       = models.CharField(max_length=200)
    file        = models.FileField(upload_to="policy_docs/%Y/%m/")
    uploaded_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "policy_documents"

    def __str__(self):
        return f"{self.doc_type} — {self.policy.policy_number}"


# ─────────────────────────────────────────────
# 4.  CLAIMS  PROCESSING
# ─────────────────────────────────────────────

class Claim(models.Model):
    """
    Insurance claim lodged against a policy.
    Tracks the full lifecycle from submission
    through investigation to settlement.
    """

    class Status(models.TextChoices):
        SUBMITTED   = "SUBMITTED",   "Submitted"
        UNDER_REVIEW= "UNDER_REVIEW","Under Review"
        APPROVED    = "APPROVED",    "Approved"
        REJECTED    = "REJECTED",    "Rejected"
        SETTLED     = "SETTLED",     "Settled"
        WITHDRAWN   = "WITHDRAWN",   "Withdrawn"

    class ClaimType(models.TextChoices):
        DEATH        = "DEATH",       "Death Benefit"
        DISABILITY   = "DISABILITY",  "Disability"
        MEDICAL      = "MEDICAL",     "Medical"
        MATURITY     = "MATURITY",    "Maturity"
        SURRENDER    = "SURRENDER",   "Surrender"
        REPATRIATION = "REPATRIATION","Repatriation"

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    claim_number    = models.CharField(max_length=30, unique=True, editable=False)
    policy          = models.ForeignKey(Policy, on_delete=models.PROTECT, related_name="claims")
    claim_type      = models.CharField(max_length=20, choices=ClaimType.choices)
    status          = models.CharField(max_length=20, choices=Status.choices, default=Status.SUBMITTED)

    # ── Event details
    event_date      = models.DateField(help_text="Date the insured event occurred")
    reported_date   = models.DateField(default=timezone.now)
    description     = models.TextField()

    # ── Financials
    amount_claimed  = models.DecimalField(max_digits=14, decimal_places=2,
                                           validators=[MinValueValidator(Decimal("0.01"))])
    amount_approved = models.DecimalField(max_digits=14, decimal_places=2,
                                           null=True, blank=True)
    amount_settled  = models.DecimalField(max_digits=14, decimal_places=2,
                                           null=True, blank=True)

    # ── Ownership
    assigned_officer= models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="assigned_claims"
    )
    rejection_reason= models.TextField(blank=True)
    settled_at      = models.DateTimeField(null=True, blank=True)

    # ── Claimant Information
    claimant_name   = models.CharField(max_length=150, null=True, blank=True)
    claimant_relation = models.CharField(max_length=100, null=True, blank=True, help_text="Relationship to deceased (e.g., Spouse, Child)")
    claimant_phone  = models.CharField(max_length=20, null=True, blank=True)
    claimant_email  = models.EmailField(null=True, blank=True)

    # ── Deceased Information
    deceased_name   = models.CharField(max_length=150, null=True, blank=True, help_text="Full name of deceased")
    date_of_death   = models.DateField(null=True, blank=True)
    cause_of_death  = models.CharField(max_length=200, null=True, blank=True)
    place_of_death  = models.CharField(max_length=200, null=True, blank=True)
    burial_date     = models.DateField(null=True, blank=True)
    burial_place    = models.CharField(max_length=200, blank=True)

    # ── Banking Details for Payout
    bank_name       = models.CharField(max_length=150, null=True, blank=True)
    account_number  = models.CharField(max_length=30, null=True, blank=True)
    branch_code     = models.CharField(max_length=20, null=True, blank=True)

    # ── Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "claims"
        indexes  = [
            models.Index(fields=["policy", "status"]),
            models.Index(fields=["claim_number"]),
            models.Index(fields=["event_date"]),
        ]
        ordering = ["-reported_date"]

    def save(self, *args, **kwargs):
        if not self.claim_number:
            count = Claim.objects.count() + 1
            self.claim_number = f"CLM-{count:08d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.claim_number} — {self.claim_type} ({self.status})"


class ClaimDocument(models.Model):
    """Evidence and supporting documents for a claim."""

    class DocType(models.TextChoices):
        DEATH_CERT   = "DEATH_CERT",   "Death Certificate"
        POLICE_REPORT= "POLICE_REPORT","Police Report"
        MEDICAL_CERT = "MEDICAL_CERT", "Medical Certificate"
        AFFIDAVIT    = "AFFIDAVIT",    "Affidavit"
        INVOICE      = "INVOICE",      "Invoice / Receipt"
        OTHER        = "OTHER",        "Other"

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    claim       = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name="documents")
    doc_type    = models.CharField(max_length=30, choices=DocType.choices)
    title       = models.CharField(max_length=200)
    file        = models.FileField(upload_to="claim_docs/%Y/%m/")
    uploaded_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "claim_documents"

    def __str__(self):
        return f"{self.doc_type} — {self.claim.claim_number}"


class ClaimNote(models.Model):
    """
    Timestamped audit trail of officer notes
    and status changes on a claim.
    """

    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    claim      = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name="notes")
    author     = models.ForeignKey(User, on_delete=models.PROTECT)
    body       = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "claim_notes"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Note on {self.claim.claim_number} by {self.author}"


# ─────────────────────────────────────────────
# 5.  PAYMENTS  &  PREMIUMS
# ─────────────────────────────────────────────

class PremiumSchedule(models.Model):
    """
    Expected premium due dates generated when
    a policy is activated.  One row per due date.
    """

    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    policy       = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name="premium_schedule")
    due_date     = models.DateField()
    amount_due   = models.DecimalField(max_digits=12, decimal_places=2)
    is_paid      = models.BooleanField(default=False)
    is_late      = models.BooleanField(default=False)

    class Meta:
        db_table = "premium_schedules"
        unique_together = ("policy", "due_date")
        ordering = ["due_date"]
        indexes  = [models.Index(fields=["policy", "is_paid", "due_date"])]

    def __str__(self):
        status = "Paid" if self.is_paid else "Due"
        return f"{self.policy.policy_number} — {self.due_date} [{status}]"


class Payment(models.Model):
    """
    Actual payment record — could satisfy one or
    more premium schedule entries.
    """

    class PaymentStatus(models.TextChoices):
        PENDING   = "PENDING",   "Pending"
        COMPLETED = "COMPLETED", "Completed"
        FAILED    = "FAILED",    "Failed"
        REVERSED  = "REVERSED",  "Reversed"

    class PaymentCategory(models.TextChoices):
        PREMIUM      = "PREMIUM",      "Premium"
        CLAIM_PAYOUT = "CLAIM_PAYOUT", "Claim Payout"
        REFUND       = "REFUND",       "Refund"
        PENALTY      = "PENALTY",      "Late Payment Penalty"

    id               = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment_reference= models.CharField(max_length=50, unique=True, editable=False)
    policy           = models.ForeignKey(Policy, on_delete=models.PROTECT, related_name="payments")
    claim            = models.ForeignKey(
        Claim, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="payouts",
        help_text="Populated only for claim payout transactions"
    )
    payment_method   = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT)
    category         = models.CharField(max_length=20, choices=PaymentCategory.choices, default=PaymentCategory.PREMIUM)
    status           = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)

    amount           = models.DecimalField(max_digits=14, decimal_places=2,
                                            validators=[MinValueValidator(Decimal("0.01"))])
    currency         = models.CharField(max_length=5, default="USD")
    transaction_date = models.DateTimeField(default=timezone.now)
    external_ref     = models.CharField(max_length=100, blank=True,
                                         help_text="EcoCash / bank transaction reference")
    notes            = models.TextField(blank=True)

    processed_by     = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="processed_payments"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payments"
        indexes  = [
            models.Index(fields=["policy", "status"]),
            models.Index(fields=["transaction_date"]),
            models.Index(fields=["payment_reference"]),
        ]
        ordering = ["-transaction_date"]

    def save(self, *args, **kwargs):
        if not self.payment_reference:
            count = Payment.objects.count() + 1
            self.payment_reference = f"PAY-{count:010d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.payment_reference} — {self.amount} {self.currency}"


class PaymentAllocation(models.Model):
    """
    Links a payment to the specific premium schedule
    entries it covers.  Supports partial allocations.
    """

    id               = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment          = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name="allocations")
    premium_schedule = models.ForeignKey(PremiumSchedule, on_delete=models.PROTECT, related_name="allocations")
    amount_allocated = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = "payment_allocations"
        unique_together = ("payment", "premium_schedule")

    def __str__(self):
        return f"{self.payment.payment_reference} → {self.premium_schedule}"


# ─────────────────────────────────────────────
# 6.  CUSTOMER  ENGAGEMENT  SNAPSHOT
# ─────────────────────────────────────────────

class CustomerEngagement(models.Model):
    """
    Running tallies of service interactions for
    a customer.  Updated on every relevant event.
    Kept separate from Customer to satisfy 2NF.
    """

    customer             = models.OneToOneField(
        Customer, on_delete=models.CASCADE, primary_key=True,
        related_name="engagement"
    )
    number_of_complaints = models.PositiveIntegerField(default=0)
    claims_filed         = models.PositiveIntegerField(default=0)
    service_satisfaction = models.DecimalField(
        max_digits=3, decimal_places=1, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="CSAT score 0–10"
    )
    last_interaction_at  = models.DateTimeField(null=True, blank=True)
    updated_at           = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "customer_engagement"

    def __str__(self):
        return f"Engagement — {self.customer.customer_number}"


# ─────────────────────────────────────────────
# 7.  CHURN  PREDICTION  (ML Pipeline)
# ─────────────────────────────────────────────

class ChurnBatchJob(models.Model):
    """
    Represents a single ML model inference run
    across a batch of customers.
    """

    class JobStatus(models.TextChoices):
        QUEUED    = "QUEUED",    "Queued"
        RUNNING   = "RUNNING",   "Running"
        COMPLETED = "COMPLETED", "Completed"
        FAILED    = "FAILED",    "Failed"

    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model_version  = models.CharField(max_length=50)
    status         = models.CharField(max_length=20, choices=JobStatus.choices, default=JobStatus.QUEUED)
    total_customers= models.PositiveIntegerField(default=0)
    processed      = models.PositiveIntegerField(default=0)
    started_at     = models.DateTimeField(null=True, blank=True)
    completed_at   = models.DateTimeField(null=True, blank=True)
    triggered_by   = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL
    )
    error_log      = models.TextField(blank=True)

    class Meta:
        db_table = "churn_batch_jobs"
        ordering = ["-started_at"]

    def __str__(self):
        return f"Batch {self.id} [{self.model_version}] — {self.status}"


class ChurnPrediction(models.Model):
    """
    Per-customer churn prediction result.
    feature_snapshot is replaced by a normalised
    child table (ChurnPredictionFeature) to satisfy 1NF.
    The JSON field is retained as a lightweight cache
    for the ML pipeline but is NOT the source of truth.
    """

    id               = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer         = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="churn_predictions")
    batch_job        = models.ForeignKey(
        ChurnBatchJob, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="predictions"
    )
    risk_level       = models.ForeignKey(RiskLevel, on_delete=models.PROTECT, related_name="predictions")
    churn_percentage = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    is_churned       = models.BooleanField(default=False,
                                            help_text="Set True when customer actually churns — used for model retraining")
    model_version    = models.CharField(max_length=50)
    predicted_at     = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "churn_predictions"
        indexes  = [
            models.Index(fields=["customer", "predicted_at"]),
            models.Index(fields=["risk_level"]),
            models.Index(fields=["is_churned"]),
        ]
        ordering = ["-predicted_at"]

    def __str__(self):
        return (f"{self.customer.customer_number} — "
                f"{self.churn_percentage}% churn [{self.risk_level}]")


class ChurnPredictionFeature(models.Model):
    """
    Normalised feature snapshot (replaces JSON blob).
    One row per feature per prediction.
    """

    class FeatureType(models.TextChoices):
        NUMERIC     = "NUMERIC",     "Numeric"
        CATEGORICAL = "CATEGORICAL", "Categorical"
        BOOLEAN     = "BOOLEAN",     "Boolean"

    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prediction    = models.ForeignKey(ChurnPrediction, on_delete=models.CASCADE, related_name="features")
    feature_name  = models.CharField(max_length=100)
    feature_value = models.CharField(max_length=255)
    feature_type  = models.CharField(max_length=20, choices=FeatureType.choices)

    class Meta:
        db_table        = "churn_prediction_features"
        unique_together = ("prediction", "feature_name")

    def __str__(self):
        return f"{self.feature_name} = {self.feature_value}"


# ─────────────────────────────────────────────
# 9. AUDIT & SECURITY MODELS
# ─────────────────────────────────────────────

class LoginAttempt(models.Model):
    """
    Audit trail for all login attempts (successful and failed).
    Used for:
    - Security auditing
    - Brute force attack detection
    - User activity tracking
    - Failed login analysis
    """
    
    email           = models.EmailField(db_index=True)
    success         = models.BooleanField(null=True)  # None = logout, True = success, False = failure
    ip_address      = models.GenericIPAddressField()
    user_agent      = models.TextField(blank=True)
    timestamp       = models.DateTimeField(auto_now_add=True, db_index=True)
    error_message   = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = "audit_login_attempts"
        indexes = [
            models.Index(fields=["email", "-timestamp"]),
            models.Index(fields=["ip_address", "-timestamp"]),
            models.Index(fields=["success", "-timestamp"]),
            models.Index(fields=["-timestamp"]),
        ]
        ordering = ["-timestamp"]
    
    def __str__(self):
        status = "✓ Success" if self.success is True else ("✗ Failed" if self.success is False else "⊘ Logout")
        return f"{self.email} {status} from {self.ip_address} at {self.timestamp}"
    
    @classmethod
    def get_failed_attempts(cls, email: str, minutes: int = 30) -> int:
        """
        Get number of failed login attempts for an email in the last N minutes.
        Used for brute force detection.
        """
        from django.utils import timezone
        from datetime import timedelta
        
        time_threshold = timezone.now() - timedelta(minutes=minutes)
        return cls.objects.filter(
            email=email,
            success=False,
            timestamp__gte=time_threshold
        ).count()
    
    @classmethod
    def get_failed_attempts_by_ip(cls, ip_address: str, minutes: int = 30) -> int:
        """
        Get number of failed login attempts from an IP in the last N minutes.
        Used for distributed brute force detection.
        """
        from django.utils import timezone
        from datetime import timedelta
        
        time_threshold = timezone.now() - timedelta(minutes=minutes)
        return cls.objects.filter(
            ip_address=ip_address,
            success=False,
            timestamp__gte=time_threshold
        ).count()
