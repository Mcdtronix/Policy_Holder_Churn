"""
Views for the Nyaradzo Assurance Management System
=================================================
Professional DRF views with proper separation of concerns,
permissions, pagination, and error handling.

Author: Nyaradzo Engineering Team
Version: 1.0.0
"""

from rest_framework import viewsets, status, permissions
from rest_framework import serializers as drf_serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction, models
from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
import logging

logger = logging.getLogger(__name__)

from . import models, serializers


# ─────────────────────────────────────────────
# BASE VIEWSET CLASS
# ─────────────────────────────────────────────

class BaseViewSet(viewsets.ModelViewSet):
    """Base viewset with common functionality."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return getattr(serializers, f'{self.serializer_class_prefix}ListSerializer')
        elif self.action in ['create', 'update', 'partial_update']:
            return getattr(serializers, f'{self.serializer_class_prefix}WriteSerializer')
        else:
            return getattr(serializers, f'{self.serializer_class_prefix}DetailSerializer')
    
    def get_serializer_context(self):
        """Add request to serializer context."""
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context


# ─────────────────────────────────────────────
# REFERENCE DATA VIEWS
# ─────────────────────────────────────────────

class PolicyTypeViewSet(BaseViewSet):
    """Policy type reference data viewset."""
    queryset = models.PolicyType.objects.all().order_by('name')
    serializer_class = serializers.PolicyTypeSerializer
    filterset_fields = ['is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['name']
    ordering = ['name']

    def get_serializer_class(self):
        return serializers.PolicyTypeSerializer


class GenderViewSet(BaseViewSet):
    """Gender reference data viewset."""
    queryset = models.Gender.objects.all().order_by('label')
    serializer_class = serializers.GenderSerializer
    ordering_fields = ['label', 'code']
    ordering = ['label']

    def get_serializer_class(self):
        return serializers.GenderSerializer


class LocationViewSet(BaseViewSet):
    """Location reference data viewset."""
    queryset = models.Location.objects.all().order_by('province', 'district', 'city')
    serializer_class = serializers.LocationSerializer
    ordering_fields = ['province', 'district', 'city']
    ordering = ['province', 'district', 'city']

    def get_serializer_class(self):
        return serializers.LocationSerializer


class IncomeLevelViewSet(BaseViewSet):
    """Income level reference data viewset."""
    queryset = models.IncomeLevel.objects.all().order_by('label')
    serializer_class = serializers.IncomeLevelSerializer
    ordering_fields = ['label', 'code', 'min_usd']
    ordering = ['label']

    def get_serializer_class(self):
        return serializers.IncomeLevelSerializer


# ─────────────────────────────────────────────
# USER MANAGEMENT VIEWS
# ─────────────────────────────────────────────

class UserViewSet(BaseViewSet):
    """User management viewset."""
    queryset = models.User.objects.all()
    serializer_class_prefix = 'User'
    filterset_fields = ['role', 'department', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.UserCreateSerializer
        return serializers.UserSerializer
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def me(self, request):
        """Get current user profile."""
        logger.info(f"👤 [BACKEND] User profile requested for user: {request.user}")
        logger.info(f"🔑 [BACKEND] Auth header: {request.META.get('HTTP_AUTHORIZATION', 'None')}")
        
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Bulk create users."""
        serializer = serializers.UserCreateSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ─────────────────────────────────────────────
# CUSTOMER VIEWS
# ─────────────────────────────────────────────

class CustomerViewSet(BaseViewSet):
    """Customer management viewset."""
    queryset = models.Customer.objects.select_related(
        'gender', 'location', 'income_level', 'registered_by'
    ).prefetch_related('policies', 'engagement')
    serializer_class_prefix = 'Customer'
    filterset_fields = ['gender', 'location', 'income_level', 'is_active', 'national_id', 'email']
    search_fields = ['first_name', 'last_name', 'email', 'customer_number']
    ordering_fields = ['last_name', 'first_name', 'created_at']
    
    def create(self, request, *args, **kwargs):
        """Create a new customer with comprehensive logging and duplicate safety recovery."""
        logger.info(f"👤 [CUSTOMER] Creating customer with data: {request.data}")
        try:
            response = super().create(request, *args, **kwargs)
            logger.info(f"✅ [CUSTOMER] Customer created successfully: {response.data.get('customer_number')}")
            return response
        except drf_serializers.ValidationError as exc:
            error_data = exc.detail
            national_id = request.data.get('national_id')
            email = request.data.get('email')

            # Only auto-fallback when unique constraint is the sole issue.
            constraints = []
            if isinstance(error_data, dict):
                for field in ['national_id', 'email']:
                    field_errors = error_data.get(field)
                    if field_errors and all(
                        (hasattr(e, 'code') and e.code == 'unique') or
                        ('already exists' in str(e).lower())
                        for e in field_errors
                    ):
                        constraints.append(field)

            if isinstance(error_data, dict) and set(error_data.keys()) <= set(constraints):
                if national_id:
                    existing = models.Customer.objects.filter(national_id=national_id).first()
                    if existing:
                        logger.warning(f"⚠️ [CUSTOMER] National ID exists; returning existing customer: {national_id}")
                        serializer = serializers.CustomerDetailSerializer(existing, context={'request': request})
                        return Response(serializer.data, status=status.HTTP_200_OK)
                if email:
                    existing = models.Customer.objects.filter(email=email).first()
                    if existing:
                        logger.warning(f"⚠️ [CUSTOMER] Email exists; returning existing customer: {email}")
                        serializer = serializers.CustomerDetailSerializer(existing, context={'request': request})
                        return Response(serializer.data, status=status.HTTP_200_OK)

            logger.error(f"❌ [CUSTOMER] Customer creation failed: {error_data}")
            raise
        except Exception as e:
            logger.error(f"❌ [CUSTOMER] Customer creation failed: {str(e)}")
            raise
    
    @action(detail=True, methods=['get'])
    def policies(self, request, pk=None):
        """Get customer policies."""
        customer = self.get_object()
        policies = customer.policies.select_related('policy_type', 'underwritten_by')
        serializer = serializers.PolicyListSerializer(policies, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def engagement(self, request, pk=None):
        """Get customer engagement metrics."""
        customer = self.get_object()
        try:
            engagement = customer.engagement
            serializer = serializers.CustomerEngagementSerializer(engagement)
            return Response(serializer.data)
        except models.CustomerEngagement.DoesNotExist:
            return Response({'detail': 'Engagement data not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def create_engagement(self, request, pk=None):
        """Create or update customer engagement."""
        customer = self.get_object()
        try:
            engagement = customer.engagement
            serializer = serializers.CustomerEngagementSerializer(
                engagement, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except models.CustomerEngagement.DoesNotExist:
            data = request.data.copy()
            data['customer'] = customer.id
            serializer = serializers.CustomerEngagementSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


# ─────────────────────────────────────────────
# POLICY VIEWS
# ─────────────────────────────────────────────

class PolicyViewSet(BaseViewSet):
    """Policy management viewset."""
    queryset = models.Policy.objects.select_related(
        'customer', 'policy_type', 'underwritten_by'
    ).prefetch_related('documents')
    serializer_class_prefix = 'Policy'
    filterset_fields = ['customer', 'policy_type', 'status']
    search_fields = ['policy_number', 'customer__first_name', 'customer__last_name']
    ordering_fields = ['created_at', 'start_date', 'policy_number']
    
    def create(self, request, *args, **kwargs):
        """Create a new policy with logging."""
        logger.info(f"📋 [POLICY] Creating policy with data: {request.data}")
        return super().create(request, *args, **kwargs)
    
    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        """Get policy documents."""
        policy = self.get_object()
        documents = policy.documents.select_related('uploaded_by')
        serializer = serializers.PolicyDocumentSerializer(documents, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def upload_document(self, request, pk=None):
        """Upload policy document."""
        policy = self.get_object()
        data = request.data.copy()
        data['policy'] = policy.id
        data['uploaded_by'] = request.user.id
        
        serializer = serializers.PolicyDocumentSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def generate_premium_schedule(self, request, pk=None):
        """Generate premium schedule for policy."""
        policy = self.get_object()
        
        # Clear existing schedule
        models.PremiumSchedule.objects.filter(policy=policy).delete()
        
        # Generate new schedule based on frequency
        schedules = []
        if policy.premium_frequency == 'MONTHLY':
            # Generate 12 months of premiums
            for i in range(12):
                due_date = policy.start_date.replace(day=1) + timezone.timedelta(days=30*i)
                schedules.append(models.PremiumSchedule(
                    policy=policy,
                    due_date=due_date,
                    amount_due=policy.premium_amount
                ))
        
        models.PremiumSchedule.objects.bulk_create(schedules)
        
        schedule = policy.premium_schedule.all().order_by('due_date')
        serializer = serializers.PremiumScheduleSerializer(schedule, many=True)
        return Response(serializer.data)


# ─────────────────────────────────────────────
# CLAIM VIEWS
# ─────────────────────────────────────────────

class ClaimViewSet(BaseViewSet):
    """Claim management viewset."""
    queryset = models.Claim.objects.select_related(
        'policy', 'assigned_officer'
    ).prefetch_related('documents', 'notes')
    serializer_class_prefix = 'Claim'
    filterset_fields = ['policy', 'claim_type', 'status', 'assigned_officer']
    search_fields = ['claim_number', 'policy__policy_number', 'policy__customer__first_name']
    ordering_fields = ['reported_date', 'event_date', 'claim_number']
    
    def perform_create(self, serializer):
        """Set reported date on creation."""
        serializer.save(reported_date=timezone.now().date())
    
    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        """Get claim documents."""
        claim = self.get_object()
        documents = claim.documents.select_related('uploaded_by')
        serializer = serializers.ClaimDocumentSerializer(documents, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def upload_document(self, request, pk=None):
        """Upload claim document."""
        claim = self.get_object()
        data = request.data.copy()
        data['claim'] = claim.id
        data['uploaded_by'] = request.user.id
        
        serializer = serializers.ClaimDocumentSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def add_note(self, request, pk=None):
        """Add note to claim."""
        claim = self.get_object()
        data = {
            'claim': claim.id,
            'author': request.user.id,
            'body': request.data.get('body')
        }
        
        serializer = serializers.ClaimNoteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve claim."""
        claim = self.get_object()
        if claim.status != models.Claim.Status.UNDER_REVIEW:
            return Response(
                {'detail': 'Only claims under review can be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        amount_approved = request.data.get('amount_approved')
        if not amount_approved:
            return Response(
                {'detail': 'Amount approved is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        claim.status = models.Claim.Status.APPROVED
        claim.amount_approved = amount_approved
        claim.save()
        
        serializer = serializers.ClaimDetailSerializer(claim)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def settle(self, request, pk=None):
        """Settle claim."""
        claim = self.get_object()
        if claim.status != models.Claim.Status.APPROVED:
            return Response(
                {'detail': 'Only approved claims can be settled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        amount_settled = request.data.get('amount_settled')
        if not amount_settled:
            return Response(
                {'detail': 'Amount settled is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            claim.status = models.Claim.Status.SETTLED
            claim.amount_settled = amount_settled
            claim.settled_at = timezone.now()
            claim.save()
            
            # Create claim payout payment record
            models.Payment.objects.create(
                policy=claim.policy,
                claim=claim,
                payment_method=models.PaymentMethod.objects.get(code='BANK_DEBIT'),
                category=models.Payment.PaymentCategory.CLAIM_PAYOUT,
                status=models.Payment.PaymentStatus.COMPLETED,
                amount=amount_settled,
                transaction_date=timezone.now(),
                processed_by=request.user
            )
        
        serializer = serializers.ClaimDetailSerializer(claim)
        return Response(serializer.data)


# ─────────────────────────────────────────────
# PAYMENT VIEWS
# ─────────────────────────────────────────────

class PaymentViewSet(BaseViewSet):
    """Payment management viewset."""
    queryset = models.Payment.objects.select_related(
        'policy', 'claim', 'payment_method', 'processed_by'
    ).prefetch_related('allocations__premium_schedule')
    serializer_class_prefix = 'Payment'
    filterset_fields = ['policy', 'payment_method', 'category', 'status']
    search_fields = ['payment_reference', 'policy__policy_number']
    ordering_fields = ['transaction_date', 'payment_reference']
    
    @action(detail=True, methods=['post'])
    def allocate(self, request, pk=None):
        """Allocate payment to premium schedules."""
        payment = self.get_object()
        
        if payment.status != models.Payment.PaymentStatus.COMPLETED:
            return Response(
                {'detail': 'Only completed payments can be allocated'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        allocations_data = request.data.get('allocations', [])
        
        with transaction.atomic():
            for alloc_data in allocations_data:
                schedule_id = alloc_data.get('premium_schedule')
                amount = alloc_data.get('amount_allocated')
                
                try:
                    schedule = models.PremiumSchedule.objects.get(
                        id=schedule_id, policy=payment.policy
                    )
                    
                    models.PaymentAllocation.objects.update_or_create(
                        payment=payment,
                        premium_schedule=schedule,
                        defaults={'amount_allocated': amount}
                    )
                    
                    # Mark schedule as paid if fully allocated
                    total_allocated = models.PaymentAllocation.objects.filter(
                        premium_schedule=schedule
                    ).aggregate(total=models.Sum('amount_allocated'))['total'] or 0
                    
                    if total_allocated >= schedule.amount_due:
                        schedule.is_paid = True
                        schedule.save()
                        
                except models.PremiumSchedule.DoesNotExist:
                    continue
        
        serializer = serializers.PaymentDetailSerializer(payment)
        return Response(serializer.data)


# ─────────────────────────────────────────────
# CHURN PREDICTION VIEWS
# ─────────────────────────────────────────────

class ChurnBatchJobViewSet(BaseViewSet):
    """Churn batch job management viewset."""
    queryset = models.ChurnBatchJob.objects.select_related('triggered_by')
    serializer_class_prefix = 'ChurnBatchJob'
    filterset_fields = ['status', 'model_version']
    ordering_fields = ['started_at', 'created_at']
    
    @action(detail=True, methods=['get'])
    def predictions(self, request, pk=None):
        """Get predictions for batch job."""
        batch_job = self.get_object()
        predictions = batch_job.predictions.select_related(
            'customer', 'risk_level'
        ).order_by('-predicted_at')
        serializer = serializers.ChurnPredictionListSerializer(predictions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def run_batch_prediction(self, request):
        """Run batch churn prediction."""
        from ml_engine.predictor import predictor
        
        # Create batch job
        batch_job = models.ChurnBatchJob.objects.create(
            model_version='1.0.0',
            status=models.ChurnBatchJob.JobStatus.QUEUED,
            triggered_by=request.user
        )
        
        try:
            # Update status to running
            batch_job.status = models.ChurnBatchJob.JobStatus.RUNNING
            batch_job.started_at = timezone.now()
            batch_job.save()
            
            # Get all customers
            customers = models.Customer.objects.filter(is_active=True)
            batch_job.total_customers = customers.count()
            batch_job.save()
            
            # Run predictions
            results = predictor.predict_batch(customers)
            
            # Create prediction records
            predictions = []
            for customer, result in zip(customers, results):
                risk_level = models.RiskLevel.objects.filter(
                    min_threshold__lte=result['churn_percentage'],
                    max_threshold__gt=result['churn_percentage']
                ).first()
                
                prediction = models.ChurnPrediction.objects.create(
                    customer=customer,
                    batch_job=batch_job,
                    risk_level=risk_level,
                    churn_percentage=result['churn_percentage'],
                    is_churned=result['churn_percentage'] >= 70,
                    model_version='1.0.0'
                )
                
                # Create feature records
                for feature_name, feature_value in result.get('features', {}).items():
                    models.ChurnPredictionFeature.objects.create(
                        prediction=prediction,
                        feature_name=feature_name,
                        feature_value=str(feature_value),
                        feature_type='NUMERIC' if isinstance(feature_value, (int, float)) else 'CATEGORICAL'
                    )
                
                predictions.append(prediction)
            
            # Update batch job completion
            batch_job.status = models.ChurnBatchJob.JobStatus.COMPLETED
            batch_job.completed_at = timezone.now()
            batch_job.processed = len(predictions)
            batch_job.save()
            
            serializer = serializers.ChurnBatchJobDetailSerializer(batch_job)
            return Response(serializer.data)
            
        except Exception as e:
            batch_job.status = models.ChurnBatchJob.JobStatus.FAILED
            batch_job.error_log = str(e)
            batch_job.completed_at = timezone.now()
            batch_job.save()
            
            return Response(
                {'detail': f'Batch prediction failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ChurnPredictionViewSet(BaseViewSet):
    """Churn prediction viewset."""
    queryset = models.ChurnPrediction.objects.select_related(
        'customer', 'batch_job', 'risk_level'
    ).prefetch_related('features')
    serializer_class_prefix = 'ChurnPrediction'
    filterset_fields = ['customer', 'risk_level', 'is_churned']
    search_fields = ['customer__first_name', 'customer__last_name', 'customer__customer_number']
    ordering_fields = ['predicted_at', 'churn_percentage']
    
    @action(detail=False, methods=['post'])
    def predict_single(self, request):
        """Predict churn for single customer."""
        from ml_engine.predictor import predictor
        
        customer_id = request.data.get('customer_id')
        if not customer_id:
            return Response(
                {'detail': 'customer_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            customer = models.Customer.objects.get(id=customer_id, is_active=True)
        except models.Customer.DoesNotExist:
            return Response(
                {'detail': 'Customer not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Run prediction
        result = predictor.predict(customer)
        
        # Create prediction record
        risk_level = models.RiskLevel.objects.filter(
            min_threshold__lte=result['churn_percentage'],
            max_threshold__gt=result['churn_percentage']
        ).first()
        
        prediction = models.ChurnPrediction.objects.create(
            customer=customer,
            risk_level=risk_level,
            churn_percentage=result['churn_percentage'],
            is_churned=result['churn_percentage'] >= 70,
            model_version='1.0.0'
        )
        
        # Create feature records
        for feature_name, feature_value in result.get('features', {}).items():
            models.ChurnPredictionFeature.objects.create(
                prediction=prediction,
                feature_name=feature_name,
                feature_value=str(feature_value),
                feature_type='NUMERIC' if isinstance(feature_value, (int, float)) else 'CATEGORICAL'
            )
        
        serializer = serializers.ChurnPredictionDetailSerializer(prediction)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ─────────────────────────────────────────────
# DASHBOARD VIEW
# ─────────────────────────────────────────────

class DashboardViewSet(viewsets.GenericViewSet):
    """Dashboard statistics viewset."""
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        """Get dashboard statistics."""
        from django.db.models import Count, Sum, Avg
        from django.db.models.functions import TruncMonth
        
        # Customer stats
        total_customers = models.Customer.objects.count()
        active_customers = models.Customer.objects.filter(is_active=True).count()
        
        # Policy stats
        active_policies = models.Policy.objects.filter(
            status=models.Policy.Status.ACTIVE
        ).count()
        total_policies = models.Policy.objects.count()
        
        # Claim stats
        pending_claims = models.Claim.objects.filter(
            status=models.Claim.Status.UNDER_REVIEW
        ).count()
        claims_processed = models.Claim.objects.filter(
            status__in=[models.Claim.Status.APPROVED, models.Claim.Status.SETTLED]
        ).count()
        
        # Payment stats
        total_payments = models.Payment.objects.filter(
            status=models.Payment.PaymentStatus.COMPLETED
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Monthly stats (current month)
        current_month = timezone.now().replace(day=1)
        next_month = (current_month + timezone.timedelta(days=32)).replace(day=1)
        
        new_policies_month = models.Policy.objects.filter(
            created_at__gte=current_month,
            created_at__lt=next_month
        ).count()
        
        # Matured policies (policies that have ended)
        matured_policies = models.Policy.objects.filter(
            end_date__lte=timezone.now().date(),
            status=models.Policy.Status.MATURED
        ).count()
        
        # Churn risk stats
        high_risk_customers = models.ChurnPrediction.objects.filter(
            risk_level__label='High Risk',
            risk_level__isnull=False,
            predicted_at__gte=timezone.now() - timezone.timedelta(days=30)
        ).values('customer').distinct().count()
        
        # Average churn rate
        avg_churn_rate = models.ChurnPrediction.objects.filter(
            predicted_at__gte=timezone.now() - timezone.timedelta(days=30)
        ).aggregate(avg=Avg('churn_percentage'))['avg'] or 0
        
        # Recent predictions
        recent_predictions = models.ChurnPrediction.objects.select_related(
            'customer', 'risk_level'
        ).filter(
            customer__isnull=False,
            risk_level__isnull=False
        ).order_by('-predicted_at')[:10]
        
        # Top claims by amount
        top_claims = models.Claim.objects.select_related(
            'policy__customer'
        ).filter(
            policy__isnull=False,
            policy__customer__isnull=False
        ).order_by('-amount_claimed')[:10]
        
        data = {
            'totalCustomers': total_customers,
            'totalPolicies': total_policies,
            'activePolicies': active_policies,
            'pendingClaims': pending_claims,
            'totalPremiumRevenue': float(total_payments),
            'avgChurnRate': float(avg_churn_rate),
            'newPoliciesThisMonth': new_policies_month,
            'claimsProcessed': claims_processed,
            'maturedPolicies': matured_policies,
            'highRiskCustomers': high_risk_customers,
            'recent_predictions': serializers.ChurnPredictionListSerializer(
                recent_predictions, many=True
            ).data,
            'top_claims': serializers.ClaimListSerializer(
                top_claims, many=True
            ).data
        }
        
        serializer = serializers.DashboardStatsSerializer(data)
        return Response(serializer.data)


# ─────────────────────────────────────────────
# ANALYTICS VIEWS
# ─────────────────────────────────────────────

class AnalyticsViewSet(viewsets.GenericViewSet):
    """Analytics and reporting viewset."""
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def monthly_trends(self, request):
        """Get monthly trends for dashboard charts."""
        from django.db.models import Count, Sum
        from django.db.models.functions import TruncMonth
        
        # Get last 3 months plus current month to show recent data
        end_date = timezone.now()
        start_date = end_date - timezone.timedelta(days=90)  # ~3 months
        
        # Monthly new policies
        monthly_policies = models.Policy.objects.filter(
            created_at__gte=start_date
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')
        
        # Monthly claims
        monthly_claims = models.Claim.objects.filter(
            created_at__gte=start_date
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')
        
        # Monthly revenue (completed payments)
        monthly_revenue = models.Payment.objects.filter(
            status=models.Payment.PaymentStatus.COMPLETED,
            transaction_date__gte=start_date
        ).annotate(
            month=TruncMonth('transaction_date')
        ).values('month').annotate(
            total=Sum('amount')
        ).order_by('month')
        
        # Monthly churn rate (from predictions)
        monthly_churn = models.ChurnPrediction.objects.filter(
            predicted_at__gte=start_date
        ).annotate(
            month=TruncMonth('predicted_at')
        ).values('month').annotate(
            avg_churn=Sum('churn_percentage') / Count('id')
        ).order_by('month')
        
        # Build response data - get unique months from all datasets
        all_months = set()
        for item in monthly_policies:
            all_months.add((item['month'].year, item['month'].month))
        for item in monthly_claims:
            all_months.add((item['month'].year, item['month'].month))
        for item in monthly_revenue:
            all_months.add((item['month'].year, item['month'].month))
        for item in monthly_churn:
            all_months.add((item['month'].year, item['month'].month))
        
        # Sort months and build data
        data = []
        for year, month in sorted(all_months):
            month_str = timezone.datetime(year, month, 1).strftime('%b')
            
            # Find data for this month
            policy_count = next((item['count'] for item in monthly_policies if item['month'].year == year and item['month'].month == month), 0)
            claim_count = next((item['count'] for item in monthly_claims if item['month'].year == year and item['month'].month == month), 0)
            revenue = next((item['total'] for item in monthly_revenue if item['month'].year == year and item['month'].month == month), 0) or 0
            churn_rate = next((item['avg_churn'] for item in monthly_churn if item['month'].year == year and item['month'].month == month), 0) or 0
            
            data.append({
                'month': month_str,
                'newPolicies': policy_count,
                'claims': claim_count,
                'revenue': float(revenue),
                'churnRate': float(churn_rate)
            })
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def churn_by_location(self, request):
        """Get churn rates by location."""
        from django.db.models import Avg, Count
        
        churn_by_loc = models.ChurnPrediction.objects.select_related(
            'customer__location'
        ).filter(
            customer__isnull=False,
            customer__location__isnull=False,
            customer__location__city__isnull=False
        ).values(
            'customer__location__city'
        ).annotate(
            churn_rate=Avg('churn_percentage'),
            policy_count=Count('customer', distinct=True)
        ).order_by('-churn_rate')
        
        data = [
            {
                'location': item['customer__location__city'],
                'churnRate': float(item['churn_rate']),
                'policyCount': item['policy_count']
            }
            for item in churn_by_loc
        ]
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def churn_by_age(self, request):
        """Get churn rates by age groups."""
        from django.db.models import Avg, Count, Case, When, CharField, Value
        from django.db.models.functions import ExtractYear
        
        # Calculate age groups
        current_year = timezone.now().year
        churn_by_age = models.ChurnPrediction.objects.select_related(
            'customer'
        ).filter(
            customer__isnull=False,
            customer__date_of_birth__isnull=False
        ).annotate(
            age=current_year - ExtractYear('customer__date_of_birth')
        ).annotate(
            age_group=Case(
                When(age__lt=26, then=Value('18-25')),
                When(age__range=(26, 35), then=Value('26-35')),
                When(age__range=(36, 45), then=Value('36-45')),
                When(age__range=(46, 55), then=Value('46-55')),
                When(age__range=(56, 65), then=Value('56-65')),
                When(age__gte=66, then=Value('65+')),
                default=Value('Unknown'),
                output_field=CharField()
            )
        ).values('age_group').annotate(
            churn_rate=Avg('churn_percentage'),
            count=Count('customer', distinct=True)
        ).order_by('age_group')
        
        # Map to expected format
        age_groups = ['18-25', '26-35', '36-45', '46-55', '56-65', '65+']
        data = []
        for group in age_groups:
            item = next((x for x in churn_by_age if x['age_group'] == group), None)
            if item:
                data.append({
                    'group': group,
                    'churnRate': float(item['churn_rate']),
                    'count': item['count']
                })
            else:
                data.append({
                    'group': group,
                    'churnRate': 0,
                    'count': 0
                })
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def churn_by_income(self, request):
        """Get churn rates by income level."""
        from django.db.models import Avg, Count
        
        churn_by_income = models.ChurnPrediction.objects.select_related(
            'customer__income_level'
        ).filter(
            customer__isnull=False,
            customer__income_level__isnull=False,
            customer__income_level__label__isnull=False
        ).values(
            'customer__income_level__label'
        ).annotate(
            churn_rate=Avg('churn_percentage'),
            count=Count('customer', distinct=True)
        ).order_by('customer__income_level__label')
        
        income_order = ['Low Income', 'Medium Income', 'High Income']
        data = []
        
        for income in income_order:
            item = next((x for x in churn_by_income if x['customer__income_level__label'] == income), None)
            if item:
                data.append({
                    'incomeLevel': income,
                    'churnRate': float(item['churn_rate']),
                    'count': item['count']
                })
            else:
                data.append({
                    'incomeLevel': income,
                    'churnRate': 0,
                    'count': 0
                })
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def recent_activities(self, request):
        """Get recent system activities."""
        activities = []
        
        # Recent claims
        recent_claims = models.Claim.objects.select_related(
            'policy__customer'
        ).order_by('-created_at')[:3]
        
        for claim in recent_claims:
            activities.append({
                'id': f"claim-{claim.id}",
                'type': 'claim',
                'description': f"Claim #{claim.claim_number} submitted by {claim.policy.customer.full_name}",
                'time': claim.created_at.isoformat(),
                'status': claim.status.lower()
            })
        
        # Recent policies
        recent_policies = models.Policy.objects.select_related(
            'customer'
        ).order_by('-created_at')[:3]
        
        for policy in recent_policies:
            activities.append({
                'id': f"policy-{policy.id}",
                'type': 'policy',
                'description': f"New {policy.policy_type.name} policy registered - {policy.customer.full_name}",
                'time': policy.created_at.isoformat(),
                'status': 'active'
            })
        
        # Recent payments
        recent_payments = models.Payment.objects.select_related(
            'policy__customer'
        ).filter(
            status=models.Payment.PaymentStatus.COMPLETED
        ).order_by('-transaction_date')[:3]
        
        for payment in recent_payments:
            activities.append({
                'id': f"payment-{payment.id}",
                'type': 'payment',
                'description': f"Premium payment received - ${payment.amount} from {payment.policy.customer.full_name}",
                'time': payment.transaction_date.isoformat(),
                'status': 'completed'
            })
        
        # Recent high-risk predictions
        recent_risks = models.ChurnPrediction.objects.select_related(
            'customer', 'risk_level'
        ).filter(
            risk_level__label='High Risk'
        ).order_by('-predicted_at')[:2]
        
        for risk in recent_risks:
            activities.append({
                'id': f"churn-{risk.id}",
                'type': 'churn',
                'description': f"High churn risk alert - {risk.customer.full_name} ({risk.churn_percentage:.1f}%)",
                'time': risk.predicted_at.isoformat(),
                'status': 'alert'
            })
        
        # Sort by time and take top 6
        activities.sort(key=lambda x: x['time'], reverse=True)
        activities = activities[:6]
        
        return Response(activities)


# ─────────────────────────────────────────────
# HEALTH CHECK VIEW
# ─────────────────────────────────────────────

class HealthViewSet(viewsets.GenericViewSet):
    """Health check endpoint."""
    permission_classes = [permissions.AllowAny]
    
    def list(self, request):
        """System health check."""
        from ml_engine.predictor import predictor
        
        return Response({
            'status': 'healthy',
            'service': 'Nyaradzo Assurance Management System',
            'version': '1.0.0',
            'model_mode': predictor._mode,
            'model_version': '1.0.0',
            'timestamp': timezone.now().isoformat()
        })


# ─────────────────────────────────────────────
# CUSTOMER CHURN CALCULATION VIEWSET
# ─────────────────────────────────────────────

class CustomerChurnCalculationViewSet(viewsets.GenericViewSet):
    """
    Professional customer churn calculation viewset.
    
    Provides endpoints for:
    - Customer search and selection
    - Pre-filled customer details
    - Churn prediction calculation
    - Results storage and retrieval
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def customer_search(self, request):
        """
        Search customers for churn calculation.
        
        Query Parameters:
        - q: Search query (customer name, number, email)
        - limit: Maximum results (default: 20)
        """
        search_query = request.GET.get('q', '').strip()
        limit = min(int(request.GET.get('limit', 20)), 100)
        
        if not search_query:
            return Response({
                'success': False,
                'message': 'Search query is required',
                'customers': []
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Professional customer search with multiple fields
        customers = models.Customer.objects.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(customer_number__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone_primary__icontains=search_query)
        ).select_related('gender', 'location', 'income_level').order_by('last_name', 'first_name')[:limit]
        
        # Serialize customer data for selection
        customer_data = []
        for customer in customers:
            customer_data.append({
                'id': str(customer.id),
                'customer_number': customer.customer_number,
                'full_name': customer.full_name,
                'email': customer.email,
                'phone_primary': customer.phone_primary,
                'age': customer.age,
                'gender': {
                    'code': customer.gender.code,
                    'label': customer.gender.label
                } if customer.gender else None,
                'location': {
                    'city': customer.location.city,
                    'district': customer.location.district,
                    'province': customer.location.province,
                    'label': str(customer.location)
                } if customer.location else None,
                'income_level': {
                    'code': customer.income_level.code,
                    'label': customer.income_level.label
                } if customer.income_level else None,
                'has_policy': customer.policies.exists(),
                'policy_count': customer.policies.count(),
                'last_engagement': self._get_last_engagement(customer)
            })
        
        return Response({
            'success': True,
            'message': f'Found {len(customer_data)} customers',
            'customers': customer_data,
            'search_query': search_query,
            'total_available': models.Customer.objects.filter(
                models.Q(first_name__icontains=search_query) |
                models.Q(last_name__icontains=search_query) |
                models.Q(customer_number__icontains=search_query) |
                models.Q(email__icontains=search_query) |
                models.Q(phone_primary__icontains=search_query)
            ).count()
        })
    
    @action(detail=False, methods=['get'])
    def customer_details(self, request):
        """
        Get detailed customer information for churn calculation form.
        
        Query Parameters:
        - customer_id: Customer UUID
        """
        customer_id = request.GET.get('customer_id')
        if not customer_id:
            return Response({
                'success': False,
                'message': 'Customer ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            customer = models.Customer.objects.get(id=customer_id)
        except models.Customer.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Customer not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get comprehensive customer details
        policies = customer.policies.select_related('policy_type').prefetch_related('documents')

        # Engagement is a OneToOne snapshot (not a queryset), so read values safely
        customer_engagement = None
        if hasattr(customer, 'engagement') and customer.engagement is not None:
            customer_engagement = customer.engagement

        # Calculate customer metrics
        total_premium = sum(policy.premium_amount for policy in policies)
        avg_premium = total_premium / len(policies) if policies else 0
        policy_tenure = self._calculate_average_tenure(policies)

        interaction_count = 0
        last_interaction = None
        interaction_types = []
        recent_engagements = []

        if customer_engagement:
            interaction_count = (customer_engagement.number_of_complaints or 0) + (customer_engagement.claims_filed or 0)
            last_interaction = customer_engagement.last_interaction_at
            # Legacy support fields; this serializer may not maintain per-event types in one-to-one model.
            interaction_types = []
            recent_engagements = [
                {
                    'interaction_type': 'Aggregate',
                    'last_interaction_at': customer_engagement.last_interaction_at,
                    'notes': None
                }
            ]

        customer_details = {
            'customer_info': {
                'id': str(customer.id),
                'customer_number': customer.customer_number,
                'full_name': customer.full_name,
                'email': customer.email,
                'phone_primary': customer.phone_primary,
                'phone_secondary': customer.phone_secondary,
                'date_of_birth': customer.date_of_birth,
                'age': customer.age,
                'gender': {
                    'code': customer.gender.code,
                    'label': customer.gender.label
                } if customer.gender else None,
                'location': {
                    'city': customer.location.city,
                    'district': customer.location.district,
                    'province': customer.location.province,
                    'label': str(customer.location)
                } if customer.location else None,
                'income_level': {
                    'code': customer.income_level.code,
                    'label': customer.income_level.label
                } if customer.income_level else None,
                'address_line1': customer.address_line1,
                'address_line2': customer.address_line2,
                'registered_at': customer.created_at
            },
            'policy_summary': {
                'total_policies': len(policies),
                'active_policies': len([p for p in policies if p.status == 'ACTIVE']),
                'total_premium': float(total_premium),
                'average_premium': float(avg_premium),
                'average_tenure_months': policy_tenure,
                'policy_types': list(set([p.policy_type.name for p in policies]))
            },
            'policies': [
                {
                    'id': str(policy.id),
                    'policy_number': policy.policy_number,
                    'policy_type': policy.policy_type.name,
                    'status': policy.status,
                    'premium_amount': float(policy.premium_amount),
                    'sum_assured': float(policy.sum_assured),
                    'start_date': policy.start_date,
                    'end_date': policy.end_date,
                    'dependents': policy.dependents
                }
                for policy in policies
            ],
            'engagement_metrics': {
                'total_interactions': interaction_count,
                'last_interaction': last_interaction,
                'interaction_types': interaction_types,
                'recent_engagements': recent_engagements
            },
            'churn_history': self._get_churn_history(customer)
        }
        
        return Response({
            'success': True,
            'message': 'Customer details retrieved successfully',
            'customer_details': customer_details
        })
    
    @action(detail=False, methods=['post'])
    def calculate_churn(self, request):
        """
        Calculate churn level for selected customer or free-form input.
        Uses trained ML model for predictions.

        Request Body:
        - customer_id: Customer UUID (optional)
        - calculation_context: Additional context for calculation
        - age, gender, location, income_level, policy_count, average_premium,
          payment_method, dependents, late_payments, missed_payments,
          number_of_complaints, claims_filed, customer_tenure,
          service_satisfaction (required when customer_id is not provided)
        """
        from ml_engine.predictor import ChurnPredictor
        
        customer_id = request.data.get('customer_id')
        calculation_context = request.data.get('calculation_context', {})

        if customer_id:
            try:
                customer = models.Customer.objects.get(id=customer_id)
            except models.Customer.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'Customer not found'
                }, status=status.HTTP_404_NOT_FOUND)

            # Use trained ML model for prediction
            try:
                predictor = ChurnPredictor()
                ml_result = predictor.predict(customer)
                churn_result = self._format_ml_result(customer, ml_result)
            except Exception as e:
                logger.error(f"ML model prediction failed: {e}. Falling back to rule-based scoring.")
                churn_result = self._calculate_churn_score(customer, calculation_context)
            churn_entry = models.ChurnPrediction.objects.create(
                customer=customer,
                risk_level=churn_result['risk_level'],
                churn_percentage=churn_result['churn_percentage'],
                is_churned=churn_result['is_churned'],
                model_version=churn_result.get('model_version', '1.0.0'),
                predicted_at=timezone.now()
            )

            payload = {
                'prediction_id': str(churn_entry.id),
                'customer_id': str(customer.id),
                'customer_name': customer.full_name,
                'churn_percentage': churn_result['churn_percentage'],
                'risk_level': {
                    'code': churn_result['risk_level'].code,
                    'label': churn_result['risk_level'].label,
                    'color_hex': churn_result['risk_level'].color_hex
                },
                'is_churned': churn_result['is_churned'],
                'model_version': '2.1',
                'predicted_at': churn_entry.predicted_at,
                'confidence_score': churn_result['confidence_score'],
                'key_factors': churn_result['key_factors'],
                'recommendations': churn_result['recommendations']
            }

        else:
            required_fields = [
                'age', 'gender', 'location', 'income_level', 'policy_count',
                'average_premium', 'payment_method', 'dependents', 'late_payments',
                'missed_payments', 'number_of_complaints', 'claims_filed',
                'customer_tenure', 'service_satisfaction'
            ]
            missing = [field for field in required_fields if field not in request.data or request.data.get(field) in [None, '']]
            if missing:
                return Response({
                    'success': False,
                    'message': f'Missing fields for manual churn calculation: {", ".join(missing)}'
                }, status=status.HTTP_400_BAD_REQUEST)

            manual_context = {
                'age': float(request.data['age']),
                'gender': request.data['gender'],
                'location': request.data['location'],
                'income_level': request.data['income_level'],
                'policy_count': int(request.data['policy_count']),
                'average_premium': float(request.data['average_premium']),
                'payment_method': request.data['payment_method'],
                'dependents': int(request.data['dependents']),
                'late_payments': int(request.data['late_payments']),
                'missed_payments': int(request.data['missed_payments']),
                'number_of_complaints': int(request.data['number_of_complaints']),
                'claims_filed': int(request.data['claims_filed']),
                'customer_tenure': int(request.data['customer_tenure']),
                'service_satisfaction': float(request.data['service_satisfaction'])
            }

            churn_result = self._calculate_churn_score_from_manual_data(manual_context)

            payload = {
                'prediction_id': None,
                'customer_id': None,
                'customer_name': request.data.get('customer_name', 'Manual Entry'),
                'churn_percentage': churn_result['churn_percentage'],
                'risk_level': {
                    'code': churn_result['risk_level'].code,
                    'label': churn_result['risk_level'].label,
                    'color_hex': churn_result['risk_level'].color_hex
                },
                'is_churned': churn_result['is_churned'],
                'model_version': '2.1',
                'predicted_at': timezone.now(),
                'confidence_score': churn_result['confidence_score'],
                'key_factors': churn_result['key_factors'],
                'recommendations': churn_result['recommendations']
            }

        return Response({
            'success': True,
            'message': 'Churn calculation completed successfully',
            'churn_prediction': payload,
            'calculation_metadata': {
                'calculation_time': timezone.now().isoformat(),
                'data_points_used': churn_result['data_points_used'],
                'model_confidence': churn_result['confidence_score'],
                'calculation_context': calculation_context
            }
        })

    def _calculate_churn_score_from_manual_data(self, data):
        """
        Calculate churn prediction using ML model for manually entered data.
        
        This method constructs feature vectors from user-provided data and uses
        the trained machine learning model to predict churn risk with high accuracy.
        
        Args:
            data (dict): Manual input data containing customer features
            
        Returns:
            dict: ML model churn prediction result with risk assessment
        """
        from ml_engine.predictor import ChurnPredictor
        import numpy as np
        
        try:
            predictor = ChurnPredictor()
            
            # Encoding maps (must match training)
            gender_map = {"Male": 1, "Female": 0}
            location_map = {
                "Bindura": 0, "Bulawayo": 1, "Chegutu": 2, "Chitungwiza": 3,
                "Gweru": 4, "Harare": 5, "Hwange": 6, "Kadoma": 7, "Kariba": 8,
                "Kwekwe": 9, "Marondera": 10, "Masvingo": 11, "Mutare": 12,
                "Norton": 13, "Victoria Falls": 14,
            }
            income_map = {"High Income": 0, "Low Income": 1, "Medium Income": 2}
            payment_map = {"Bank Debit": 0, "Cash": 1, "Ecocash": 2, "Mobile Money": 3}
            policy_map = {"Family": 0, "Individual": 1, "Basic": 1}
            
            # Encode categorical features
            gender_encoded = gender_map.get(str(data.get('gender', 'Male')), 1)
            location_encoded = location_map.get(str(data.get('location', 'Harare')), 5)
            income_encoded = income_map.get(str(data.get('income_level', 'Medium Income')), 2)
            payment_encoded = payment_map.get(str(data.get('payment_method', 'Mobile Money')), 3)
            policy_encoded = 1  # Default for manual entry
            
            # Construct 19-feature vector (matching FEATURE_ORDER in predictor.py)
            features = np.array([
                float(data.get('age', 30)),                    # Age
                gender_encoded,                                 # Gender (encoded)
                location_encoded,                               # Location (encoded)
                income_encoded,                                 # Income Level (encoded)
                policy_encoded,                                 # Policy Type (encoded)
                float(data.get('average_premium', 50)),        # Premium Amount
                float(data.get('dependents', 0)),              # Dependents
                payment_encoded,                                # Payment Method (encoded)
                float(data.get('late_payments', 0)),           # Late Payments
                float(data.get('missed_payments', 0)),         # Missed Payments
                float(data.get('number_of_complaints', 0)),    # Number of Complaints
                float(data.get('claims_filed', 0)),            # Claims Filed
                float(data.get('customer_tenure', 12)),        # Customer Tenure
                float(data.get('service_satisfaction', 7)),    # Service Satisfaction
                # Engineered features
                float(data.get('late_payments', 0)) + (float(data.get('missed_payments', 0)) * 2) + float(data.get('number_of_complaints', 0)),  # Risk Score
                float(data.get('number_of_complaints', 0)) + float(data.get('claims_filed', 0)),  # Engagement Score
                float(data.get('average_premium', 50)) / max(1, float(data.get('dependents', 1))),  # Premium per Dependent
                1.0 if float(data.get('number_of_complaints', 0)) > 0 else 0.0,  # Has Complaint
                1.0 if float(data.get('claims_filed', 0)) > 0 else 0.0,  # Has Claim
            ]).reshape(1, -1)
            
            # Scale features using the model's scaler
            scaled_features = predictor._scaler.transform(features)
            
            # Get prediction from model
            churn_prob = predictor._model.predict_proba(scaled_features)[0][1]
            churn_percentage = round(churn_prob * 100, 2)
            
            # Determine risk level
            high_risk = models.RiskLevel.objects.filter(code='HIGH').first()
            medium_risk = models.RiskLevel.objects.filter(code='MEDIUM').first()
            low_risk = models.RiskLevel.objects.filter(code='LOW').first()
            
            if churn_percentage >= 70:
                risk_level = high_risk
            elif churn_percentage >= 50:
                risk_level = medium_risk
            else:
                risk_level = low_risk
            
            # Extract key factors
            key_factors = []
            late_pay = int(data.get('late_payments', 0))
            missed_pay = int(data.get('missed_payments', 0))
            complaints = int(data.get('number_of_complaints', 0))
            satisfaction = float(data.get('service_satisfaction', 7))
            
            if late_pay > 0 or missed_pay > 0:
                key_factors.append(f"Payment issues: {late_pay} late, {missed_pay} missed")
            if complaints > 0:
                key_factors.append(f"Customer complaints: {complaints}")
            if satisfaction < 5:
                key_factors.append(f"Low satisfaction: {satisfaction}/10")
            if int(data.get('policy_count', 1)) < 2:
                key_factors.append("Limited policy portfolio")
            if float(data.get('average_premium', 50)) < 50:
                key_factors.append("Lower premium amount")
            
            if not key_factors:
                key_factors = ["Stable customer profile"]
            
            # Generate recommendations
            recommendations = []
            if churn_percentage >= 70:
                recommendations.append("🔴 HIGH RISK - Urgent retention action needed")
                recommendations.append("Schedule immediate customer contact")
                recommendations.append("Offer retention incentives or policy review")
                if late_pay > 0 or missed_pay > 0:
                    recommendations.append("Review payment arrangements and alternatives")
                if satisfaction < 5:
                    recommendations.append("Investigate service dissatisfaction")
            elif churn_percentage >= 50:
                recommendations.append("🟡 MEDIUM RISK - Active monitoring required")
                recommendations.append("Plan quarterly customer engagement")
                recommendations.append("Address identified concerns proactively")
                if complaints > 0:
                    recommendations.append("Follow up on customer complaints")
            else:
                recommendations.append("✅ LOW RISK - Customer appears stable")
                recommendations.append("Continue routine engagement")
                recommendations.append("Monitor for behavioral changes")
            
            # Prepare feature snapshot
            feature_snapshot = {
                'age': float(data.get('age', 30)),
                'gender': data.get('gender', 'Male'),
                'location': data.get('location', 'Harare'),
                'income_level': data.get('income_level', 'Medium Income'),
                'policy_count': int(data.get('policy_count', 1)),
                'average_premium': float(data.get('average_premium', 50)),
                'payment_method': data.get('payment_method', 'Mobile Money'),
                'dependents': int(data.get('dependents', 0)),
                'late_payments': late_pay,
                'missed_payments': missed_pay,
                'number_of_complaints': complaints,
                'claims_filed': int(data.get('claims_filed', 0)),
                'customer_tenure': int(data.get('customer_tenure', 12)),
                'service_satisfaction': satisfaction
            }
            
            return {
                'risk_level': risk_level,
                'churn_percentage': churn_percentage,
                'is_churned': churn_percentage >= 70,
                'confidence_score': 0.95,  # ML model confidence
                'key_factors': key_factors,
                'recommendations': recommendations,
                'model_version': '1.0.0',
                'feature_snapshot': feature_snapshot,
                'data_points_used': 19,
                'source': 'ml_model_manual_entry'
            }
            
        except Exception as e:
            logger.error(f"Manual ML prediction failed: {e}. Using fallback rule-based scoring.", extra={'error': str(e)})
            # Fallback to safe default if ML model fails
            return self._fallback_rule_based_churn(data)
    
    def _fallback_rule_based_churn(self, data):
        """
        Fallback rule-based churn calculation for manual entries.
        Used only when ML model prediction fails.
        
        This implements weighted scoring across multiple churn risk factors.
        """
        from .models import RiskLevel
        
        high_risk = RiskLevel.objects.filter(code='HIGH').first()
        medium_risk = RiskLevel.objects.filter(code='MEDIUM').first()
        low_risk = RiskLevel.objects.filter(code='LOW').first()
        
        churn_factors = {
            'demographic': 0,
            'policy': 0,
            'engagement': 0,
            'payment': 0,
            'claims': 0
        }
        
        # Demographic factors
        age = float(data.get('age', 30))
        if age < 25:
            churn_factors['demographic'] = 25
        elif age < 35:
            churn_factors['demographic'] = 20
        elif age < 45:
            churn_factors['demographic'] = 15
        elif age < 55:
            churn_factors['demographic'] = 10
        else:
            churn_factors['demographic'] = 18
        
        inc_label = str(data.get('income_level', 'Medium Income')).lower()
        if 'low' in inc_label:
            churn_factors['demographic'] += 15
        elif 'medium' in inc_label:
            churn_factors['demographic'] += 8
        else:
            churn_factors['demographic'] += 3
        
        # Policy factors
        policies = int(data.get('policy_count', 1))
        avg_premium = float(data.get('average_premium', 50))
        
        if policies == 0:
            churn_factors['policy'] = 40
        elif policies == 1:
            churn_factors['policy'] = 20
        elif policies == 2:
            churn_factors['policy'] = 10
        else:
            churn_factors['policy'] = 5
        
        if avg_premium < 50:
            churn_factors['policy'] += 15
        elif avg_premium < 80:
            churn_factors['policy'] += 8
        else:
            churn_factors['policy'] += 3
        
        # Engagement factors
        sat = float(data.get('service_satisfaction', 7))
        if sat <= 3:
            churn_factors['engagement'] = 30
        elif sat <= 6:
            churn_factors['engagement'] = 18
        elif sat <= 8:
            churn_factors['engagement'] = 10
        else:
            churn_factors['engagement'] = 5
        
        complaints = int(data.get('number_of_complaints', 0))
        if complaints < 2:
            churn_factors['engagement'] += 0
        elif complaints < 4:
            churn_factors['engagement'] += 5
        else:
            churn_factors['engagement'] += 10
        
        # Payment factors
        late = int(data.get('late_payments', 0))
        missed = int(data.get('missed_payments', 0))
        total = max(1, late + missed + 1)
        late_ratio = late / total
        
        if late_ratio > 0.3:
            churn_factors['payment'] = 20
        elif late_ratio > 0.1:
            churn_factors['payment'] = 12
        else:
            churn_factors['payment'] = 5
        
        # Claims factors
        claims = int(data.get('claims_filed', 0))
        if claims > 2:
            churn_factors['claims'] = 15
        elif claims > 0:
            churn_factors['claims'] = 8
        else:
            churn_factors['claims'] = 2
        
        # Calculate weighted score
        weights = {
            'demographic': 0.30,
            'policy': 0.25,
            'engagement': 0.20,
            'payment': 0.15,
            'claims': 0.10
        }
        
        churn_score = sum(churn_factors[f] * weights[f] for f in churn_factors)
        churn_score = min(max(churn_score, 0), 100)
        
        # Assign risk level
        if churn_score >= 75:
            risk_level = high_risk
        elif churn_score >= 50:
            risk_level = medium_risk
        else:
            risk_level = low_risk
        
        # Generate factors and recommendations
        key_factors = []
        if churn_factors['demographic'] > 20:
            key_factors.append('Demographic pressure')
        if churn_factors['policy'] > 20:
            key_factors.append('Policy risk')
        if churn_factors['engagement'] > 20:
            key_factors.append('Low engagement')
        if churn_factors['payment'] > 15:
            key_factors.append('Payment irregularities')
        if churn_factors['claims'] > 10:
            key_factors.append('Claims frequency')
        
        recommendations = []
        if churn_score >= 70:
            recommendations.append("Review retention strategy")
        if complaints > 0:
            recommendations.append("Address customer complaints")
        if late > 0 or missed > 0:
            recommendations.append("Monitor payment patterns")
        
        return {
            'risk_level': risk_level,
            'churn_percentage': round(churn_score, 2),
            'is_churned': churn_score >= 70,
            'confidence_score': 0.80,  # Lower confidence for fallback
            'key_factors': key_factors if key_factors else ["Standard profile"],
            'recommendations': recommendations if recommendations else ["Continue monitoring"],
            'model_version': '1.0.0-fallback',
            'feature_snapshot': data,
            'data_points_used': len(data),
            'source': 'fallback_rule_based'
        }
    
    def _get_last_engagement(self, customer):
        """Get last engagement date for customer."""
        last_engagement = customer.engagement.order_by('-last_interaction_at').first()
        return last_engagement.last_interaction_at if last_engagement else None
    
    def _calculate_average_tenure(self, policies):
        """Calculate average policy tenure in months."""
        if not policies:
            return 0
        
        total_tenure = 0
        for policy in policies:
            tenure = policy.tenure_months
            total_tenure += tenure
        
        return total_tenure / len(policies)
    
    def _get_churn_history(self, customer):
        """Get customer's churn prediction history."""
        predictions = customer.churn_predictions.select_related('risk_level').order_by('-predicted_at')[:5]
        
        return [
            {
                'prediction_date': pred.predicted_at,
                'churn_percentage': pred.churn_percentage,
                'risk_level': pred.risk_level.label if pred.risk_level else None,
                'model_version': pred.model_version
            }
            for pred in predictions
        ]
    
    def _format_ml_result(self, customer, ml_result):
        """
        Convert ML predictor result to the format expected by calculate_churn endpoint.
        
        ML Result Format:
        {
            "churn_percentage": float (0-100),
            "is_churned": bool (>= 70%),
            "feature_snapshot": dict,
            "model_version": str
        }
        """
        churn_pct = ml_result['churn_percentage']
        
        # Determine risk level based on churn percentage
        high_risk = models.RiskLevel.objects.get(code='HIGH')
        medium_risk = models.RiskLevel.objects.get(code='MEDIUM')
        low_risk = models.RiskLevel.objects.get(code='LOW')
        
        if churn_pct >= 70:
            risk_level = high_risk
        elif churn_pct >= 50:
            risk_level = medium_risk
        else:
            risk_level = low_risk
        
        # Extract key factors from feature snapshot
        snapshot = ml_result.get('feature_snapshot', {})
        key_factors = []
        
        if snapshot.get('late_payments', 0) > 0:
            key_factors.append(f"Late payments: {snapshot['late_payments']}")
        if snapshot.get('missed_payments', 0) > 0:
            key_factors.append(f"Missed payments: {snapshot['missed_payments']}")
        if snapshot.get('number_of_complaints', 0) > 0:
            key_factors.append(f"Complaints: {snapshot['number_of_complaints']}")
        if snapshot.get('claims_filed', 0) > 0:
            key_factors.append(f"Claims filed: {snapshot['claims_filed']}")
        if snapshot.get('service_satisfaction', 5) < 5:
            key_factors.append(f"Low satisfaction: {snapshot['service_satisfaction']}/10")
        
        # Generate recommendations
        recommendations = []
        if churn_pct >= 70:
            recommendations.append("⚠️ HIGH RISK - Immediate retention action recommended")
            recommendations.append("Contact customer within 24 hours")
            recommendations.append("Offer personalized incentives or policy review")
        elif churn_pct >= 50:
            recommendations.append("⚠️ MEDIUM RISK - Monitor customer closely")
            recommendations.append("Schedule quarterly check-ins")
            recommendations.append("Address identified concerns proactively")
        else:
            recommendations.append("✅ LOW RISK - Customer appears satisfied")
            recommendations.append("Continue regular engagement")
        
        return {
            'churn_percentage': churn_pct,
            'is_churned': churn_pct >= 70,
            'risk_level': risk_level,
            'confidence_score': 0.95,  # ML models have high confidence
            'key_factors': key_factors if key_factors else ["Stable profile"],
            'recommendations': recommendations,
            'model_version': ml_result.get('model_version', '1.0.0'),
            'feature_snapshot': snapshot,
            'data_points_used': 19  # ML model uses 19 features
        }
    
    def _calculate_churn_score(self, customer, context):
        """
        Professional churn calculation using multiple factors.
        
        This is a sophisticated churn prediction model that considers:
        - Customer demographics
        - Policy behavior
        - Engagement patterns
        - Payment history
        - Claims history
        """
        # Get risk levels
        high_risk = models.RiskLevel.objects.get(code='HIGH')
        medium_risk = models.RiskLevel.objects.get(code='MEDIUM')
        low_risk = models.RiskLevel.objects.get(code='LOW')
        
        # Initialize churn factors
        churn_factors = {
            'demographic': 0,
            'policy': 0,
            'engagement': 0,
            'payment': 0,
            'claims': 0
        }
        
        # 1. Demographic factors (30% weight)
        age = customer.age
        if age < 25:
            churn_factors['demographic'] = 25
        elif age < 35:
            churn_factors['demographic'] = 20
        elif age < 45:
            churn_factors['demographic'] = 15
        elif age < 55:
            churn_factors['demographic'] = 10
        else:
            churn_factors['demographic'] = 18
        
        # Income level factor
        if customer.income_level:
            if customer.income_level.label == 'Low Income':
                churn_factors['demographic'] += 15
            elif customer.income_level.label == 'Medium Income':
                churn_factors['demographic'] += 8
            else:
                churn_factors['demographic'] += 3
        
        # 2. Policy behavior factors (25% weight)
        policies = customer.policies.all()
        if not policies:
            churn_factors['policy'] = 40
        else:
            # Policy count factor
            if len(policies) == 1:
                churn_factors['policy'] = 20
            elif len(policies) == 2:
                churn_factors['policy'] = 10
            else:
                churn_factors['policy'] = 5
            
            # Premium amount factor
            avg_premium = sum(p.premium_amount for p in policies) / len(policies)
            if avg_premium < 50:
                churn_factors['policy'] += 15
            elif avg_premium < 80:
                churn_factors['policy'] += 8
            else:
                churn_factors['policy'] += 3
        
        # 3. Engagement factors (20% weight)
        customer_engagement = getattr(customer, 'engagement', None)
        if not customer_engagement:
            churn_factors['engagement'] = 30
        else:
            last_interaction_at = customer_engagement.last_interaction_at
            if not last_interaction_at:
                churn_factors['engagement'] = 30
            else:
                days_since_engagement = (timezone.now().date() - last_interaction_at.date()).days

                if days_since_engagement > 90:
                    churn_factors['engagement'] = 25
                elif days_since_engagement > 60:
                    churn_factors['engagement'] = 18
                elif days_since_engagement > 30:
                    churn_factors['engagement'] = 10
                else:
                    churn_factors['engagement'] = 5

            # Frequency factor is approximated by the number of known events (complaints+claims)
            engage_count = (customer_engagement.number_of_complaints or 0) + (customer_engagement.claims_filed or 0)
            if engage_count < 3:
                churn_factors['engagement'] += 10
            elif engage_count < 6:
                churn_factors['engagement'] += 5
            else:
                churn_factors['engagement'] += 0
        
        # 4. Payment factors (15% weight)
        payments = models.Payment.objects.filter(policy__customer=customer)
        if not payments.exists():
            churn_factors['payment'] = 25
        else:
            # Late payment factor (penalty category used as proxy for late payment)
            late_payments = payments.filter(category=models.Payment.PaymentCategory.PENALTY).count()
            total_payments = payments.count()
            late_payment_ratio = late_payments / total_payments if total_payments > 0 else 0

            if late_payment_ratio > 0.3:
                churn_factors['payment'] = 20
            elif late_payment_ratio > 0.1:
                churn_factors['payment'] = 12
            else:
                churn_factors['payment'] = 5

            # Missed payments are determined from unfufilled premium schedules
            missed_schedules = models.PremiumSchedule.objects.filter(
                policy__customer=customer,
                is_paid=False,
                due_date__lt=timezone.now().date()
            ).count()

            if missed_schedules > 5:
                churn_factors['payment'] += 10
            elif missed_schedules > 2:
                churn_factors['payment'] += 5
        
        # 5. Claims factors (10% weight)
        claims = models.Claim.objects.filter(policy__customer=customer)
        if claims:
            # Recent claims factor
            recent_claims = claims.filter(event_date__gte=timezone.now() - timezone.timedelta(days=180)).count()
            if recent_claims > 2:
                churn_factors['claims'] = 15
            elif recent_claims > 0:
                churn_factors['claims'] = 8
            else:
                churn_factors['claims'] = 3
        else:
            churn_factors['claims'] = 2
        
        # Calculate weighted churn score
        weights = {
            'demographic': 0.30,
            'policy': 0.25,
            'engagement': 0.20,
            'payment': 0.15,
            'claims': 0.10
        }
        
        churn_score = sum(
            churn_factors[factor] * weights[factor]
            for factor in churn_factors
        )
        
        # Determine risk level and percentage
        if churn_score >= 75:
            risk_level = high_risk
            churn_percentage = min(95, int(churn_score * 1.2))
            is_churned = False
        elif churn_score >= 50:
            risk_level = medium_risk
            churn_percentage = int(churn_score * 1.1)
            is_churned = False
        else:
            risk_level = low_risk
            churn_percentage = int(churn_score * 0.9)
            is_churned = False
        
        # Generate key factors and recommendations
        key_factors = []
        recommendations = []
        
        if churn_factors['demographic'] > 20:
            key_factors.append("Demographic risk factors")
            recommendations.append("Consider targeted retention programs for this demographic segment")
        
        if churn_factors['policy'] > 20:
            key_factors.append("Limited policy portfolio")
            recommendations.append("Upsell additional policies to increase customer stickiness")
        
        if churn_factors['engagement'] > 20:
            key_factors.append("Low customer engagement")
            recommendations.append("Increase customer touchpoints and engagement initiatives")
        
        if churn_factors['payment'] > 15:
            key_factors.append("Payment behavior concerns")
            recommendations.append("Offer flexible payment options and financial assistance")
        
        if churn_factors['claims'] > 10:
            key_factors.append("Recent claims activity")
            recommendations.append("Provide claims support and service improvements")
        
        return {
            'risk_level': risk_level,
            'churn_percentage': churn_percentage,
            'is_churned': is_churned,
            'confidence_score': min(95, 70 + (len(policies) * 2)),
            'key_factors': key_factors,
            'recommendations': recommendations,
            'data_points_used': {
                'demographic': True,
                'policies': len(policies),
                'engagements': 1 if customer_engagement else 0,
                'payments': payments.count(),
                'claims': claims.count()
            }
        }
