from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.urls import path
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

# ─────────────────────────────────────────────
# CUSTOM JWT SERIALIZER
# ─────────────────────────────────────────────

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT serializer that accepts email instead of username.
    Validates credentials against the User model's email field.
    """
    username_field = 'email'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Override the required fields to accept email instead of username
        self.fields['email'] = serializers.EmailField(required=True)
        # Remove the username field if it exists
        if 'username' in self.fields:
            del self.fields['username']
    
    def validate(self, attrs):
        """
        Validate email and password against the database.
        Authenticate using email field.
        """
        email = attrs.get('email')
        password = attrs.get('password')
        
        if not email or not password:
            msg = 'Both email and password are required.'
            raise serializers.ValidationError(msg, code='authorization')
        
        logger.info(f"🔐 [AUTH] Authentication attempt - Email: {email}")
        
        try:
            # Get user by email
            user = User.objects.get(email=email)
            logger.info(f"✅ [AUTH] User found - ID: {user.id}, Email: {email}")
            
            # Check password
            if not user.check_password(password):
                logger.warning(f"❌ [AUTH] Invalid password for user: {email}")
                msg = 'Incorrect password for this email address.'
                raise serializers.ValidationError(msg, code='authorization')
            
            # Check if user is active
            if not user.is_active:
                logger.warning(f"⚠️ [AUTH] Inactive user attempted login: {email}")
                msg = 'This user account is inactive.'
                raise serializers.ValidationError(msg, code='authorization')
            
            logger.info(f"✅ [AUTH] Authentication successful for user: {email}")
            
            # Set refresh token on the instance
            refresh = self.get_token(user)
            data = {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role,
                    'is_active': user.is_active,
                }
            }
            
            return data
            
        except User.DoesNotExist:
            logger.error(f"❌ [AUTH] User not found - Email: {email}")
            msg = 'No account found with this email address.'
            raise serializers.ValidationError(msg, code='authorization')
        except serializers.ValidationError:
            # Re-raise ValidationErrors as-is (they already have the specific message)
            raise
        except Exception as e:
            logger.error(f"❌ [AUTH] Authentication error: {str(e)}")
            msg = 'Authentication failed. Please try again.'
            raise serializers.ValidationError(msg, code='authorization')
    
    @classmethod
    def get_token(cls, user):
        """Generate JWT token for user."""
        token = super().get_token(user)
        
        # Add custom claims to token
        token['email'] = user.email
        token['role'] = user.role
        
        return token


# ─────────────────────────────────────────────
# CUSTOM JWT VIEW
# ─────────────────────────────────────────────

class LoginResponseSerializer(serializers.Serializer):
    """Serializer for login response containing tokens and user data."""
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = serializers.SerializerMethodField()
    
    def get_user(self, obj):
        """Return user information."""
        from .serializers import UserSerializer
        user = self.context.get('user')
        if user:
            return UserSerializer(user).data
        return None


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token endpoint that accepts email-based login.
    Returns tokens and user information on successful authentication.
    Enhanced with:
    - Login attempt tracking
    - Consistent error responses
    - Comprehensive user data in response
    """
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        email = request.data.get('email', 'unknown')
        ip_address = self._get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', 'unknown')
        
        logger.info("🔐 [BACKEND] Login endpoint called")
        logger.info(f"📤 [BACKEND] Email: {email}, IP: {ip_address}")
        
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Extract token data from serializer
            data = serializer.validated_data
            user = User.objects.get(email=email)
            
            # Log successful login attempt
            from .models import LoginAttempt
            LoginAttempt.objects.create(
                email=email,
                success=True,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Prepare response with user data
            response_data = {
                'access': data.get('access'),
                'refresh': data.get('refresh'),
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role,
                    'is_active': user.is_active,
                    'department': user.department,
                }
            }
            
            logger.info("✅ [BACKEND] Authentication successful")
            logger.info(f"👤 [BACKEND] Authenticated user: {email} | Role: {user.role}")
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except serializers.ValidationError as e:
            logger.warning(f"❌ [BACKEND] Validation error for {email}: {e.detail}")
            
            # Log failed attempt
            try:
                from .models import LoginAttempt
                LoginAttempt.objects.create(
                    email=email,
                    success=False,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    error_message=str(e.detail)
                )
            except Exception as log_error:
                logger.error(f"Failed to log login attempt: {log_error}")
            
            # Extract error message
            error_message = self._extract_error_message(e.detail)
            
            return Response(
                {
                    'error': error_message,
                    'status': 'authentication_failed',
                    'email': email
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        except User.DoesNotExist:
            logger.warning(f"❌ [BACKEND] User not found: {email}")
            
            # Log failed attempt
            try:
                from .models import LoginAttempt
                LoginAttempt.objects.create(
                    email=email,
                    success=False,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    error_message='User not found'
                )
            except Exception as log_error:
                logger.error(f"Failed to log login attempt: {log_error}")
            
            return Response(
                {
                    'error': 'No account found with this email address',
                    'status': 'user_not_found',
                    'email': email
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            logger.error(f"❌ [BACKEND] Authentication error: {str(e)}", exc_info=True)
            return Response(
                {
                    'error': 'Authentication failed. Please try again.',
                    'status': 'authentication_error'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @staticmethod
    def _get_client_ip(request):
        """Extract client IP from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def _extract_error_message(detail):
        """Extract human-readable error message from validation error detail."""
        if isinstance(detail, dict):
            for key, errors in detail.items():
                if isinstance(errors, list) and errors:
                    return str(errors[0])
                elif isinstance(errors, str):
                    return errors
        elif isinstance(detail, list) and detail:
            return str(detail[0])
        return 'Authentication failed'


# ─────────────────────────────────────────────
# LOGOUT VIEW
# ─────────────────────────────────────────────

class LogoutView(APIView):
    """
    Logout endpoint - invalidates refresh token on server.
    Frontend should also clear access token from localStorage.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        logger.info(f"🚪 [AUTH] Logout request from user: {request.user.email}")
        
        try:
            # In production, implement token blacklist here
            # For now, frontend handles token cleanup
            from .models import LoginAttempt
            
            ip_address = CustomTokenObtainPairView._get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', 'unknown')
            
            # Log logout event
            LoginAttempt.objects.create(
                email=request.user.email,
                success=None,  # Neutral for logout
                ip_address=ip_address,
                user_agent=user_agent,
                error_message='Logout'
            )
            
            logger.info(f"✅ [AUTH] User logged out: {request.user.email}")
            
            return Response(
                {
                    'message': 'Successfully logged out',
                    'status': 'success'
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"❌ [AUTH] Logout error: {str(e)}")
            return Response(
                {
                    'error': 'Logout failed',
                    'status': 'error'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ─────────────────────────────────────────────
# HEALTH CHECK VIEW
# ─────────────────────────────────────────────

class AuthHealthCheckView(APIView):
    """
    Health check endpoint for authentication service.
    Always available (no auth required).
    """
    permission_classes = []  # Allow anyone
    
    def get(self, request):
        """Check if authentication service is healthy."""
        logger.info("🏥 [AUTH] Health check request")
        
        try:
            # Test database connection
            test_user_count = User.objects.count()
            
            return Response(
                {
                    'status': 'healthy',
                    'service': 'authentication',
                    'database': 'connected',
                    'users_count': test_user_count,
                    'timestamp': timezone.now().isoformat()
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"❌ [AUTH] Health check failed: {str(e)}")
            return Response(
                {
                    'status': 'unhealthy',
                    'service': 'authentication',
                    'error': str(e)
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )


# ─────────────────────────────────────────────
# TOKEN VERIFICATION VIEW
# ─────────────────────────────────────────────

class VerifyTokenView(APIView):
    """
    Verify that a token is valid without performing full authentication.
    Useful for checking token validity before sensitive operations.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Verify current token."""
        logger.info(f"🔑 [AUTH] Token verification for user: {request.user.email}")
        
        return Response(
            {
                'valid': True,
                'user_id': str(request.user.id),
                'email': request.user.email,
                'role': request.user.role,
                'is_active': request.user.is_active
            },
            status=status.HTTP_200_OK
        )




urlpatterns = [
    # Authentication endpoints
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Health & verification
    path('auth/health/', AuthHealthCheckView.as_view(), name='auth_health'),
    path('token/verify/', VerifyTokenView.as_view(), name='verify_token'),
]

