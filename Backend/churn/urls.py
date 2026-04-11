"""
URL Configuration for Nyaradzo Assurance Management System
=======================================================
Professional URL routing with proper versioning and
RESTful endpoints structure.

Author: Nyaradzo Engineering Team
Version: 1.0.0
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

# ─────────────────────────────────────────────
# API ROUTER CONFIGURATION
# ─────────────────────────────────────────────

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'policy-types', views.PolicyTypeViewSet, basename='policy-type')
router.register(r'genders', views.GenderViewSet, basename='gender')
router.register(r'locations', views.LocationViewSet, basename='location')
router.register(r'income-levels', views.IncomeLevelViewSet, basename='income-level')
router.register(r'customers', views.CustomerViewSet, basename='customer')
router.register(r'policies', views.PolicyViewSet, basename='policy')
router.register(r'claims', views.ClaimViewSet, basename='claim')
router.register(r'payments', views.PaymentViewSet, basename='payment')
router.register(r'batch-jobs', views.ChurnBatchJobViewSet, basename='batch-job')
router.register(r'predictions', views.ChurnPredictionViewSet, basename='prediction')
router.register(r'dashboard', views.DashboardViewSet, basename='dashboard')
router.register(r'analytics', views.AnalyticsViewSet, basename='analytics')
router.register(r'churn-calculation', views.CustomerChurnCalculationViewSet, basename='churn-calculation')
router.register(r'health', views.HealthViewSet, basename='health')

# ─────────────────────────────────────────────
# URL PATTERNS
# ─────────────────────────────────────────────

app_name = 'churn'

urlpatterns = [
    # API v1 endpoints
    path('api/v1/', include(router.urls)),
    
    # Legacy endpoints for backward compatibility
    path('', include(router.urls)),
    
    # Health check endpoint (always available)
    path('health/', views.HealthViewSet.as_view({'get': 'list'}), name='health-check'),
]

# ─────────────────────────────────────────────
# ENDPOINT DOCUMENTATION
# ─────────────────────────────────────────────
"""
API ENDPOINTS
=============

Users:
- GET    /api/v1/users/                    - List all users
- POST   /api/v1/users/                    - Create new user
- GET    /api/v1/users/{id}/               - Get user details
- PUT    /api/v1/users/{id}/               - Update user
- DELETE /api/v1/users/{id}/               - Delete user
- POST   /api/v1/users/bulk_create/        - Bulk create users

Customers:
- GET    /api/v1/customers/               - List all customers
- POST   /api/v1/customers/               - Create new customer
- GET    /api/v1/customers/{id}/          - Get customer details
- PUT    /api/v1/customers/{id}/          - Update customer
- DELETE /api/v1/customers/{id}/          - Delete customer
- GET    /api/v1/customers/{id}/policies/ - Get customer policies
- GET    /api/v1/customers/{id}/engagement/ - Get customer engagement
- POST   /api/v1/customers/{id}/create_engagement/ - Create/update engagement

Policies:
- GET    /api/v1/policies/                - List all policies
- POST   /api/v1/policies/                - Create new policy
- GET    /api/v1/policies/{id}/           - Get policy details
- PUT    /api/v1/policies/{id}/           - Update policy
- DELETE /api/v1/policies/{id}/           - Delete policy
- GET    /api/v1/policies/{id}/documents/ - Get policy documents
- POST   /api/v1/policies/{id}/upload_document/ - Upload document
- POST   /api/v1/policies/{id}/generate_premium_schedule/ - Generate premium schedule

Claims:
- GET    /api/v1/claims/                   - List all claims
- POST   /api/v1/claims/                   - Create new claim
- GET    /api/v1/claims/{id}/              - Get claim details
- PUT    /api/v1/claims/{id}/              - Update claim
- DELETE /api/v1/claims/{id}/              - Delete claim
- GET    /api/v1/claims/{id}/documents/    - Get claim documents
- POST   /api/v1/claims/{id}/upload_document/ - Upload document
- POST   /api/v1/claims/{id}/add_note/      - Add note to claim
- POST   /api/v1/claims/{id}/approve/       - Approve claim
- POST   /api/v1/claims/{id}/settle/       - Settle claim

Payments:
- GET    /api/v1/payments/                 - List all payments
- POST   /api/v1/payments/                 - Create new payment
- GET    /api/v1/payments/{id}/            - Get payment details
- PUT    /api/v1/payments/{id}/            - Update payment
- DELETE /api/v1/payments/{id}/            - Delete payment
- POST   /api/v1/payments/{id}/allocate/    - Allocate payment to premiums

Churn Predictions:
- GET    /api/v1/predictions/              - List all predictions
- POST   /api/v1/predictions/predict_single/ - Predict single customer
- GET    /api/v1/predictions/{id}/         - Get prediction details

Batch Jobs:
- GET    /api/v1/batch-jobs/              - List all batch jobs
- POST   /api/v1/batch-jobs/              - Create new batch job
- GET    /api/v1/batch-jobs/{id}/         - Get batch job details
- GET    /api/v1/batch-jobs/{id}/predictions/ - Get job predictions
- POST   /api/v1/batch-jobs/run_batch_prediction/ - Run batch prediction

Dashboard:
- GET    /api/v1/dashboard/               - Get dashboard statistics

Health Check:
- GET    /health/                          - System health check
- GET    /api/v1/health/                 - System health check (versioned)

Authentication:
All endpoints require JWT authentication except:
- GET /health/
- POST /api/v1/users/ (for login/registration)

Pagination:
All list endpoints support page and page_size query parameters:
- /api/v1/customers/?page=2&page_size=20

Filtering:
Endpoints support filtering via query parameters:
- /api/v1/customers/?gender=1&location=2
- /api/v1/policies/?status=ACTIVE

Searching:
Endpoints support search via q parameter:
- /api/v1/customers/?search=john doe
- /api/v1/policies/?search=POL-123456

Sorting:
Endpoints support ordering via ordering parameter:
- /api/v1/customers/?ordering=last_name
- /api/v1/customers/?ordering=-created_at
"""
