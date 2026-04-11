"""
Serializers for the Nyaradzo Assurance Management System
==================================================
DRF serializers for all models with proper validation,
nested relationships, and read/write separation.

Author: Nyaradzo Engineering Team
Version: 1.0.0
"""

from decimal import Decimal
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
import logging
from . import models

User = get_user_model()
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# REFERENCE TABLE SERIALIZERS
# ─────────────────────────────────────────────

class GenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Gender
        fields = ['id', 'code', 'label']


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Location
        fields = ['id', 'province', 'district', 'city']


class IncomeLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.IncomeLevel
        fields = ['id', 'code', 'label', 'min_usd', 'max_usd']


class PolicyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PolicyType
        fields = ['id', 'code', 'name', 'description', 'is_active']


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PaymentMethod
        fields = ['id', 'code', 'label']


class RiskLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RiskLevel
        fields = ['id', 'code', 'label', 'min_threshold', 'max_threshold', 'color_hex']


# ─────────────────────────────────────────────
# USER MANAGEMENT SERIALIZERS
# ─────────────────────────────────────────────

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'phone', 'department', 'is_active', 'date_joined', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'date_joined', 'created_at', 'updated_at']
    
    def get_full_name(self, obj):
        """Return the full name of the user."""
        return obj.get_full_name() if obj else None


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 'password',
            'password_confirm', 'role', 'phone', 'department'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


# ─────────────────────────────────────────────
# CUSTOMER SERIALIZERS
# ─────────────────────────────────────────────

class CustomerListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views with engagement and policy data."""
    age = serializers.ReadOnlyField()
    full_name = serializers.ReadOnlyField()
    date_of_birth = serializers.DateField()
    gender = GenderSerializer(read_only=True)
    location = LocationSerializer(read_only=True)
    income_level = IncomeLevelSerializer(read_only=True)
    latest_policy = serializers.SerializerMethodField()
    engagement = serializers.SerializerMethodField()
    
    class Meta:
        model = models.Customer
        fields = [
            'id', 'customer_number', 'first_name', 'last_name', 'full_name',
            'date_of_birth', 'age', 'gender', 'location', 'income_level', 'email',
            'phone_primary', 'is_active', 'latest_policy', 'engagement', 'created_at'
        ]
    
    def get_latest_policy(self, obj):
        """Get the most recent policy for the customer."""
        latest = obj.policies.order_by('-created_at').first()
        if latest:
            return {
                'id': latest.id,
                'policy_number': latest.policy_number,
                'policy_type': latest.policy_type.name,
                'status': latest.status,
                'premium_amount': str(latest.premium_amount),
                'created_at': latest.created_at.isoformat()
            }
        return None
    
    def get_engagement(self, obj):
        """Get customer engagement metrics with fallback for missing relationship."""
        try:
            engagement = obj.engagement
            return {
                'service_satisfaction': float(engagement.service_satisfaction),
                'number_of_complaints': engagement.number_of_complaints,
                'claims_filed': engagement.claims_filed
            }
        except Exception:
            # Return default values if engagement relationship doesn't exist
            return {
                'service_satisfaction': 0,
                'number_of_complaints': 0,
                'claims_filed': 0
            }


class CustomerDetailSerializer(serializers.ModelSerializer):
    """Full serializer for detail views with comprehensive data."""
    age = serializers.ReadOnlyField()
    full_name = serializers.ReadOnlyField()
    gender = GenderSerializer(read_only=True)
    location = LocationSerializer(read_only=True)
    income_level = IncomeLevelSerializer(read_only=True)
    registered_by = UserSerializer(read_only=True)
    policies_count = serializers.SerializerMethodField()
    latest_policy = serializers.SerializerMethodField()
    engagement = serializers.SerializerMethodField()
    
    class Meta:
        model = models.Customer
        fields = [
            'id', 'customer_number', 'first_name', 'last_name', 'full_name',
            'date_of_birth', 'age', 'national_id', 'gender', 'location',
            'income_level', 'email', 'phone_primary', 'phone_secondary',
            'address_line1', 'address_line2', 'is_active', 'registered_by',
            'policies_count', 'latest_policy', 'engagement', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'customer_number', 'created_at', 'updated_at']
    
    def get_policies_count(self, obj):
        return obj.policies.count()
    
    def get_latest_policy(self, obj):
        """Get the most recent policy with complete details."""
        latest = obj.policies.order_by('-created_at').first()
        if latest:
            return {
                'id': latest.id,
                'policy_number': latest.policy_number,
                'policy_type': latest.policy_type.name,
                'status': latest.status,
                'premium_amount': str(latest.premium_amount),
                'created_at': latest.created_at.isoformat()
            }
        return None
    
    def get_engagement(self, obj):
        """Get comprehensive customer engagement metrics with fallback for missing relationship."""
        try:
            engagement = obj.engagement
            return {
                'service_satisfaction': float(engagement.service_satisfaction),
                'number_of_complaints': engagement.number_of_complaints,
                'claims_filed': engagement.claims_filed,
                'missed_payments': engagement.missed_payments,
                'late_payments': engagement.late_payments
            }
        except Exception:
            # Return default values if engagement relationship doesn't exist
            return {
                'service_satisfaction': 0,
                'number_of_complaints': 0,
                'claims_filed': 0,
                'missed_payments': 0,
                'late_payments': 0
            }


class FlexibleSlugRelatedField(serializers.SlugRelatedField):
    """Custom slug field to support code aliases and alternate labels."""

    def to_internal_value(self, data):
        try:
            return super().to_internal_value(data)
        except serializers.ValidationError:
            if self.slug_field == 'label' and self.queryset is not None:
                alias_map = {
                    'Low': 'Low Income',
                    'Medium': 'Medium Income',
                    'High': 'High Income',
                    'low': 'Low Income',
                    'medium': 'Medium Income',
                    'high': 'High Income',
                }
                normalized = alias_map.get(str(data).strip())
                if normalized:
                    obj = self.queryset.filter(label__iexact=normalized).first()
                    if obj:
                        return obj
                obj = self.queryset.filter(code__iexact=str(data).strip()).first()
                if obj:
                    return obj
            raise


class CustomerWriteSerializer(serializers.ModelSerializer):
    """Serializer for create/update operations."""
    gender = FlexibleSlugRelatedField(slug_field='label', queryset=models.Gender.objects.all())
    location = serializers.CharField(write_only=True, required=True, allow_blank=False)
    income_level = FlexibleSlugRelatedField(slug_field='label', queryset=models.IncomeLevel.objects.all())
    registered_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False, allow_null=True
    )
    
    class Meta:
        model = models.Customer
        fields = [
            'id', 'first_name', 'last_name', 'date_of_birth', 'national_id',
            'gender', 'location', 'income_level', 'email', 'phone_primary',
            'phone_secondary', 'address_line1', 'address_line2',
            'is_active', 'registered_by'
        ]
        read_only_fields = ['id']
    
    def validate(self, attrs):
        """Comprehensive validation for customer data."""
        logger.info(f"🔍 [CUSTOMER_SERIALIZER] Validating customer data: {attrs}")
        
        # Handle location: accept city name string and auto-create/fetch Location object
        location_city = attrs.get('location')
        if location_city:
            try:
                # Try to find existing location by city name
                location_obj = models.Location.objects.filter(city__iexact=location_city).first()
                if not location_obj:
                    # Auto-create location if it doesn't exist
                    location_obj, created = models.Location.objects.get_or_create(
                        city=location_city.strip(),
                        defaults={
                            'province': location_city.strip(),  # Use city name as default province
                            'district': location_city.strip()   # Use city name as default district
                        }
                    )
                    action = "created" if created else "retrieved"
                    logger.info(f"📍 [CUSTOMER_SERIALIZER] Location {action}: {location_obj} (city: {location_city})")
                attrs['location'] = location_obj
            except Exception as e:
                logger.error(f"❌ [CUSTOMER_SERIALIZER] Error processing location '{location_city}': {str(e)}")
                raise serializers.ValidationError({
                    'location': f"Unable to process location: {location_city}"
                })
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'date_of_birth', 'national_id', 
                          'gender', 'location', 'income_level', 'email', 'phone_primary']
        
        missing_fields = [field for field in required_fields if field not in attrs or attrs[field] is None]
        if missing_fields:
            logger.error(f"❌ [CUSTOMER_SERIALIZER] Missing required fields: {missing_fields}")
            raise serializers.ValidationError({
                field: f"This field is required." for field in missing_fields
            })
        
        # Validate national ID format
        national_id = attrs.get('national_id')
        if national_id and not self._validate_national_id(national_id):
            logger.error(f"❌ [CUSTOMER_SERIALIZER] Invalid national ID format: {national_id}")
            raise serializers.ValidationError({
                'national_id': 'Invalid Zimbabwean National ID format. Expected: XX-XXXXXXXAXX'
            })
        
        # Validate email uniqueness
        email = attrs.get('email')
        if email:
            existing = models.Customer.objects.filter(email=email)
            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                logger.error(f"❌ [CUSTOMER_SERIALIZER] Email already exists: {email}")
                raise serializers.ValidationError({
                    'email': 'A customer with this email already exists'
                })
        
        # Validate national ID uniqueness
        if national_id:
            existing = models.Customer.objects.filter(national_id=national_id)
            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                logger.error(f"❌ [CUSTOMER_SERIALIZER] National ID already exists: {national_id}")
                raise serializers.ValidationError({
                    'national_id': 'A customer with this national ID already exists'
                })
        
        # Validate date of birth (must be in past, reasonable age)
        dob = attrs.get('date_of_birth')
        if dob:
            today = timezone.now().date()
            if dob >= today:
                logger.error(f"❌ [CUSTOMER_SERIALIZER] Invalid date of birth: {dob} (must be in past)")
                raise serializers.ValidationError({
                    'date_of_birth': 'Date of birth must be in the past'
                })
            
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            if age < 18 or age > 120:
                logger.error(f"❌ [CUSTOMER_SERIALIZER] Invalid age: {age} (must be 18-120)")
                raise serializers.ValidationError({
                    'date_of_birth': 'Customer must be between 18 and 120 years old'
                })
        
        logger.info(f"✅ [CUSTOMER_SERIALIZER] Validation passed for customer: {attrs.get('first_name')} {attrs.get('last_name')}")
        return attrs
    
    def _validate_national_id(self, national_id):
        """Validate Zimbabwean National ID format."""
        import re
        pattern = r'^\d{2}-\d{6,7}[A-Z]\d{2}$'
        return bool(re.match(pattern, national_id))
    
    def create(self, validated_data):
        """Create customer with automatic registered_by assignment."""
        # Auto-assign registered_by if not provided
        if 'registered_by' not in validated_data or validated_data['registered_by'] is None:
            request = self.context.get('request')
            if request and hasattr(request, 'user') and request.user.is_authenticated:
                validated_data['registered_by'] = request.user
                logger.info(f"📝 [CUSTOMER_SERIALIZER] Auto-assigned registered_by: {request.user}")
        
        # Ensure is_active defaults to True
        if 'is_active' not in validated_data:
            validated_data['is_active'] = True
        
        customer = super().create(validated_data)
        logger.info(f"✅ [CUSTOMER_SERIALIZER] Customer created successfully: {customer.customer_number} - {customer.full_name}")
        return customer


# ─────────────────────────────────────────────
# POLICY SERIALIZERS
# ─────────────────────────────────────────────

class PolicyDocumentSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = models.PolicyDocument
        fields = [
            'id', 'policy', 'doc_type', 'title', 'file', 'file_url',
            'uploaded_by', 'uploaded_at'
        ]
        read_only_fields = ['id', 'uploaded_by', 'uploaded_at']
    
    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class PolicyListSerializer(serializers.ModelSerializer):
    """Lightweight policy serializer for lists."""
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    policy_type = PolicyTypeSerializer(read_only=True)
    underwritten_by = UserSerializer(read_only=True)
    is_active = serializers.ReadOnlyField()
    tenure_months = serializers.ReadOnlyField()
    
    class Meta:
        model = models.Policy
        fields = [
            'id', 'policy_number', 'customer', 'customer_name',
            'policy_type', 'status', 'is_active', 'premium_amount',
            'start_date', 'tenure_months', 'underwritten_by', 'created_at'
        ]


class PolicyBeneficiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PolicyBeneficiary
        fields = ['id', 'full_name', 'relationship', 'phone', 'is_primary', 'share_percent']


class PolicyBeneficiaryWriteSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=200)
    relationship = serializers.CharField(max_length=50, allow_blank=True, required=False)
    phone = serializers.CharField(max_length=20, allow_blank=True, required=False)
    is_primary = serializers.BooleanField(default=False)
    share_percent = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)


class PolicyDetailSerializer(serializers.ModelSerializer):
    """Full policy serializer with nested relationships."""
    customer = CustomerDetailSerializer(read_only=True)
    policy_type = PolicyTypeSerializer(read_only=True)
    underwritten_by = UserSerializer(read_only=True)
    documents = PolicyDocumentSerializer(many=True, read_only=True)
    beneficiaries = PolicyBeneficiarySerializer(many=True, read_only=True)
    is_active = serializers.ReadOnlyField()
    tenure_months = serializers.ReadOnlyField()
    
    class Meta:
        model = models.Policy
        fields = [
            'id', 'policy_number', 'customer', 'policy_type', 'underwritten_by',
            'start_date', 'end_date', 'sum_assured', 'premium_amount',
            'premium_frequency', 'dependents', 'status', 'is_active',
            'tenure_months', 'notes', 'documents', 'beneficiaries', 'created_at', 'updated_at'
        ]


class PolicyWriteSerializer(serializers.ModelSerializer):
    """Serializer for policy create/update."""
    customer = serializers.PrimaryKeyRelatedField(queryset=models.Customer.objects.all())
    policy_type = serializers.PrimaryKeyRelatedField(queryset=models.PolicyType.objects.all())
    underwritten_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False, allow_null=True
    )
    sum_assured = serializers.DecimalField(max_digits=14, decimal_places=2, coerce_to_string=False)
    premium_amount = serializers.DecimalField(max_digits=12, decimal_places=2, coerce_to_string=False)
    dependents = serializers.IntegerField(required=False, default=0, min_value=0)
    beneficiaries = PolicyBeneficiaryWriteSerializer(many=True, required=False)
    
    class Meta:
        model = models.Policy
        fields = [
            'customer', 'policy_type', 'underwritten_by', 'start_date',
            'end_date', 'sum_assured', 'premium_amount', 'premium_frequency',
            'dependents', 'status', 'notes', 'beneficiaries'
        ]
    
    def validate(self, attrs):
        logger.info(f"🔍 [POLICY_SERIALIZER] Validating policy data: {attrs}")
        if attrs.get('end_date') and attrs.get('start_date'):
            if attrs['end_date'] <= attrs['start_date']:
                logger.error(f"❌ [POLICY_SERIALIZER] End date {attrs['end_date']} is not after start date {attrs['start_date']}")
                raise serializers.ValidationError({
                    'end_date': 'End date must be after start date'
                })

        policy_type = attrs.get('policy_type')
        dependents = attrs.get('dependents', 0)

        if policy_type and hasattr(policy_type, 'name'):
            policy_type_name = policy_type.name.lower()
            if policy_type_name == 'individual' and dependents > 0:
                logger.error(f"❌ [POLICY_SERIALIZER] Individual policies cannot have dependents: {dependents}")
                raise serializers.ValidationError({
                    'dependents': 'Individual policies cannot have dependents'
                })
            if policy_type_name == 'family' and dependents == 0:
                logger.error("❌ [POLICY_SERIALIZER] Family policy requires at least one dependent")
                raise serializers.ValidationError({
                    'dependents': 'Family policies require at least one dependent'
                })

        beneficiaries = attrs.get('beneficiaries', [])
        if not beneficiaries:
            logger.warning('⚠️ [POLICY_SERIALIZER] No beneficiaries supplied; will default to policyholder')
        else:
            if len(beneficiaries) > 0:
                for idx, ben in enumerate(beneficiaries):
                    if not ben.get('full_name'):
                        raise serializers.ValidationError({'beneficiaries': 'Each beneficiary must include full name'})
                    if not ben.get('relationship'):
                        raise serializers.ValidationError({'beneficiaries': 'Each beneficiary must include relationship'})

        logger.info(f"✅ [POLICY_SERIALIZER] Validation passed")
        return attrs

    def create(self, validated_data):
        beneficiaries_data = validated_data.pop('beneficiaries', [])

        policy = models.Policy.objects.create(**validated_data)

        if not beneficiaries_data:
            # Default beneficiary is policyholder
            models.PolicyBeneficiary.objects.create(
                policy=policy,
                full_name=f"{policy.customer.full_name}",
                relationship='Self',
                phone=policy.customer.phone_primary,
                is_primary=True,
                share_percent=100.00
            )
        else:
            share = round(100.0 / len(beneficiaries_data), 2)
            for i, ben_data in enumerate(beneficiaries_data):
                if ben_data.get('share_percent') is not None:
                    share_percent = Decimal(str(ben_data.get('share_percent')))
                else:
                    share_percent = Decimal(str(share))

                models.PolicyBeneficiary.objects.create(
                    policy=policy,
                    full_name=ben_data.get('full_name'),
                    relationship=ben_data.get('relationship'),
                    phone=ben_data.get('phone', ''),
                    is_primary=ben_data.get('is_primary', False),
                    share_percent=share_percent
                )

        return policy


# ─────────────────────────────────────────────
# CLAIM SERIALIZERS
# ─────────────────────────────────────────────

class ClaimDocumentSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = models.ClaimDocument
        fields = [
            'id', 'claim', 'doc_type', 'title', 'file', 'file_url',
            'uploaded_by', 'uploaded_at'
        ]
        read_only_fields = ['id', 'uploaded_by', 'uploaded_at']
    
    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class ClaimNoteSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = models.ClaimNote
        fields = ['id', 'claim', 'author', 'body', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']


class ClaimListSerializer(serializers.ModelSerializer):
    """Lightweight claim serializer for lists."""
    policy_number = serializers.CharField(source='policy.policy_number', read_only=True)
    customer_name = serializers.CharField(source='policy.customer.full_name', read_only=True)
    assigned_officer = UserSerializer(read_only=True)
    
    class Meta:
        model = models.Claim
        fields = [
            'id', 'claim_number', 'policy_number', 'customer_name',
            'claim_type', 'status', 'event_date', 'amount_claimed',
            'assigned_officer', 'reported_date'
        ]


class ClaimDetailSerializer(serializers.ModelSerializer):
    """Full claim serializer with nested relationships."""
    policy = PolicyDetailSerializer(read_only=True)
    assigned_officer = UserSerializer(read_only=True)
    documents = ClaimDocumentSerializer(many=True, read_only=True)
    notes = ClaimNoteSerializer(many=True, read_only=True)
    
    class Meta:
        model = models.Claim
        fields = [
            'id', 'claim_number', 'policy', 'claim_type', 'status',
            'event_date', 'reported_date', 'description', 'amount_claimed',
            'amount_approved', 'amount_settled', 'claimant_name', 'claimant_relation',
            'claimant_phone', 'claimant_email', 'deceased_name', 'date_of_death',
            'cause_of_death', 'place_of_death', 'burial_date', 'burial_place',
            'bank_name', 'account_number', 'branch_code', 'assigned_officer',
            'rejection_reason', 'settled_at', 'documents', 'notes',
            'created_at', 'updated_at'
        ]


class ClaimWriteSerializer(serializers.ModelSerializer):
    """Serializer for claim create/update with policy lookup and file handling."""
    policy_number = serializers.CharField(write_only=True, required=True, allow_blank=False)
    claimant_name = serializers.CharField(required=True, allow_blank=False)
    claimant_relation = serializers.CharField(required=True, allow_blank=False)
    claimant_phone = serializers.CharField(required=True, allow_blank=False)
    claimant_email = serializers.EmailField(required=True)
    deceased_name = serializers.CharField(required=True, allow_blank=False)
    date_of_death = serializers.DateField(required=True)
    cause_of_death = serializers.CharField(required=True, allow_blank=False)
    place_of_death = serializers.CharField(required=True, allow_blank=False)
    burial_place = serializers.CharField(required=True, allow_blank=False)
    bank_name = serializers.CharField(required=True, allow_blank=False)
    account_number = serializers.CharField(required=True, allow_blank=False)
    branch_code = serializers.CharField(required=True, allow_blank=False)
    assigned_officer = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False, allow_null=True
    )
    
    class Meta:
        model = models.Claim
        fields = [
            'policy_number', 'claim_type', 'status', 'event_date', 'reported_date',
            'description', 'amount_claimed', 'amount_approved', 'amount_settled',
            'claimant_name', 'claimant_relation', 'claimant_phone', 'claimant_email',
            'deceased_name', 'date_of_death', 'cause_of_death', 'place_of_death',
            'burial_date', 'burial_place', 'bank_name', 'account_number', 'branch_code',
            'assigned_officer', 'rejection_reason', 'settled_at'
        ]
        read_only_fields = ['claim_number', 'reported_date']
    
    def validate(self, attrs):
        """Validate claim data and lookup policy by number."""
        # Lookup policy by policy_number
        policy_number = attrs.get('policy_number')
        if policy_number:
            try:
                policy = models.Policy.objects.get(policy_number=policy_number)
                attrs['policy'] = policy
                logger.info(f"✅ [CLAIM SERIALIZER] Policy found: {policy_number}")
            except models.Policy.DoesNotExist:
                logger.error(f"❌ [CLAIM SERIALIZER] Policy not found: {policy_number}")
                raise serializers.ValidationError({
                    'policy_number': f'No policy found with number {policy_number}'
                })
        
        # Remove temporary policy_number field for model saving
        attrs.pop('policy_number', None)
        
        # Validate settlement data
        if attrs.get('settled_at') and attrs.get('status') != 'SETTLED':
            raise serializers.ValidationError({
                'settled_at': 'Can only set settlement date for settled claims'
            })
        
        # Validate date of death is not in future
        dob = attrs.get('date_of_death')
        if dob and dob > timezone.now().date():
            logger.error(f"❌ [CLAIM SERIALIZER] Invalid date of death: {dob}")
            raise serializers.ValidationError({
                'date_of_death': 'Date of death cannot be in the future'
            })
        
        # Validate burial date is after date of death
        burial_date = attrs.get('burial_date')
        if burial_date and dob and burial_date < dob:
            logger.error(f"❌ [CLAIM SERIALIZER] Burial date before death date")
            raise serializers.ValidationError({
                'burial_date': 'Burial date must be on or after date of death'
            })
        
        logger.info(f"✅ [CLAIM SERIALIZER] Claim validation passed")
        return attrs
    
    def create(self, validated_data):
        """Create claim with comprehensive logging."""
        logger.info(f"📝 [CLAIM SERIALIZER] Creating claim: {validated_data.get('deceased_name')}")
        claim = super().create(validated_data)
        logger.info(f"✅ [CLAIM SERIALIZER] Claim created: {claim.claim_number}")
        return claim


# ─────────────────────────────────────────────
# PAYMENT SERIALIZERS
# ─────────────────────────────────────────────

class PaymentAllocationSerializer(serializers.ModelSerializer):
    premium_schedule_due_date = serializers.DateField(
        source='premium_schedule.due_date', read_only=True
    )
    
    class Meta:
        model = models.PaymentAllocation
        fields = [
            'id', 'payment', 'premium_schedule', 'amount_allocated',
            'premium_schedule_due_date'
        ]


class PremiumScheduleSerializer(serializers.ModelSerializer):
    """Serializer for premium schedules."""
    policy_number = serializers.CharField(source='policy.policy_number', read_only=True)
    
    class Meta:
        model = models.PremiumSchedule
        fields = [
            'id', 'policy', 'policy_number', 'due_date', 'amount_due',
            'is_paid', 'is_late'
        ]


class PaymentListSerializer(serializers.ModelSerializer):
    """Lightweight payment serializer for lists."""
    policy_number = serializers.CharField(source='policy.policy_number', read_only=True)
    customer_name = serializers.CharField(
        source='policy.customer.full_name', read_only=True
    )
    payment_method = PaymentMethodSerializer(read_only=True)
    processed_by = UserSerializer(read_only=True)
    
    class Meta:
        model = models.Payment
        fields = [
            'id', 'payment_reference', 'policy', 'policy_number',
            'customer_name', 'payment_method', 'category', 'status',
            'amount', 'currency', 'transaction_date', 'processed_by'
        ]


class PaymentDetailSerializer(serializers.ModelSerializer):
    """Full payment serializer with nested relationships."""
    policy = PolicyDetailSerializer(read_only=True)
    claim = ClaimDetailSerializer(read_only=True)
    payment_method = PaymentMethodSerializer(read_only=True)
    processed_by = UserSerializer(read_only=True)
    allocations = PaymentAllocationSerializer(many=True, read_only=True)
    
    class Meta:
        model = models.Payment
        fields = [
            'id', 'payment_reference', 'policy', 'claim', 'payment_method',
            'category', 'status', 'amount', 'currency', 'transaction_date',
            'external_ref', 'notes', 'processed_by', 'allocations',
            'created_at', 'updated_at'
        ]


class PaymentWriteSerializer(serializers.ModelSerializer):
    """Serializer for payment create/update."""
    policy = serializers.PrimaryKeyRelatedField(queryset=models.Policy.objects.all())
    claim = serializers.PrimaryKeyRelatedField(
        queryset=models.Claim.objects.all(), required=False, allow_null=True
    )
    payment_method = serializers.PrimaryKeyRelatedField(
        queryset=models.PaymentMethod.objects.all()
    )
    processed_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False, allow_null=True
    )
    
    class Meta:
        model = models.Payment
        fields = [
            'policy', 'claim', 'payment_method', 'category', 'status',
            'amount', 'currency', 'transaction_date', 'external_ref', 'notes',
            'processed_by'
        ]
    
    def validate(self, attrs):
        # Validate claim payout category
        if attrs.get('category') == 'CLAIM_PAYOUT' and not attrs.get('claim'):
            raise serializers.ValidationError({
                'claim': 'Claim is required for claim payout transactions'
            })
        
        # Validate premium category
        if attrs.get('category') == 'PREMIUM' and attrs.get('claim'):
            raise serializers.ValidationError({
                'claim': 'Claim should not be set for premium transactions'
            })
        return attrs


# ─────────────────────────────────────────────
# CUSTOMER ENGAGEMENT SERIALIZER
# ─────────────────────────────────────────────

class CustomerEngagementSerializer(serializers.ModelSerializer):
    customer = CustomerDetailSerializer(read_only=True)
    
    class Meta:
        model = models.CustomerEngagement
        fields = [
            'customer', 'number_of_complaints', 'claims_filed',
            'service_satisfaction', 'last_interaction_at', 'updated_at'
        ]


# ─────────────────────────────────────────────
# CHURN PREDICTION SERIALIZERS
# ─────────────────────────────────────────────

class ChurnPredictionFeatureSerializer(serializers.ModelSerializer):
    """Serializer for individual prediction features."""
    class Meta:
        model = models.ChurnPredictionFeature
        fields = ['id', 'prediction', 'feature_name', 'feature_value', 'feature_type']


class ChurnPredictionListSerializer(serializers.ModelSerializer):
    """Lightweight churn prediction serializer for lists."""
    customer_number = serializers.CharField(source='customer.customer_number', read_only=True)
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    risk_level = RiskLevelSerializer(read_only=True)
    
    class Meta:
        model = models.ChurnPrediction
        fields = [
            'id', 'customer_number', 'customer_name',
            'risk_level', 'churn_percentage', 'is_churned',
            'model_version', 'predicted_at'
        ]


class ChurnPredictionDetailSerializer(serializers.ModelSerializer):
    """Full churn prediction serializer with features."""
    customer = CustomerDetailSerializer(read_only=True)
    batch_job = serializers.StringRelatedField(read_only=True)
    risk_level = RiskLevelSerializer(read_only=True)
    features = ChurnPredictionFeatureSerializer(many=True, read_only=True)
    
    class Meta:
        model = models.ChurnPrediction
        fields = [
            'id', 'customer', 'batch_job', 'risk_level',
            'churn_percentage', 'is_churned', 'model_version',
            'predicted_at', 'features'
        ]


class ChurnBatchJobListSerializer(serializers.ModelSerializer):
    """Lightweight batch job serializer for lists."""
    triggered_by = UserSerializer(read_only=True)
    
    class Meta:
        model = models.ChurnBatchJob
        fields = [
            'id', 'model_version', 'status', 'total_customers',
            'processed', 'triggered_by', 'started_at', 'completed_at'
        ]


class ChurnBatchJobDetailSerializer(serializers.ModelSerializer):
    """Full batch job serializer with statistics."""
    triggered_by = UserSerializer(read_only=True)
    predictions = ChurnPredictionListSerializer(many=True, read_only=True)
    
    class Meta:
        model = models.ChurnBatchJob
        fields = [
            'id', 'model_version', 'status', 'total_customers', 'processed',
            'triggered_by', 'started_at', 'completed_at', 'error_log',
            'predictions'
        ]


# ─────────────────────────────────────────────
# DASHBOARD SERIALIZERS
# ─────────────────────────────────────────────

class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics."""
    totalCustomers = serializers.IntegerField()
    totalPolicies = serializers.IntegerField()
    activePolicies = serializers.IntegerField()
    pendingClaims = serializers.IntegerField()
    totalPremiumRevenue = serializers.DecimalField(max_digits=14, decimal_places=2)
    avgChurnRate = serializers.FloatField()
    newPoliciesThisMonth = serializers.IntegerField()
    claimsProcessed = serializers.IntegerField()
    maturedPolicies = serializers.IntegerField()
    highRiskCustomers = serializers.IntegerField()
    recent_predictions = ChurnPredictionListSerializer(many=True)
    top_claims = ClaimListSerializer(many=True)
