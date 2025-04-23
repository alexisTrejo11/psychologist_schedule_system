from django.forms import ValidationError
from core.api_response.response import DjangoResponseWrapper as ResponseWrapper
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiTypes
from rest_framework import status
from .....core.presentation.api.serializers.serializers import SignupSerializer, LoginSerializer
from core.api_response.response import ApiResponse
import logging

audit_logger = logging.getLogger('audit_logger')

class SignupView(APIView):
    """
    View for user registration.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Register a new user",
        description="Registers a new user with the provided information. Handles validation and user creation.",
        request=SignupSerializer,
        responses={
            201: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
        },
    )
    def post(self, request):
        """
        Handles the registration of a new user.
        """
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            audit_logger.warning(f"SignupView: Invalid input data: {serializer.errors}")
            formatted_response = ApiResponse.format_response(data=serializer.errors, success=False, message="Invalid input data.")
           
            return Response(formatted_response, status=status.HTTP_400_BAD_REQUEST)
        try:
            from .....core.data.repositories.django_user_repository import DjangoUserRepository
            from .....core.data.service.token_service import TokenService
            from .....core.domain.usecase.auth_use_case import SignupUseCase
            from therapists.services import TherapistService
            from patients.core.infrastructure.repositories.django_patient_repository import DjangoPatientRepository

            user_repository = DjangoUserRepository()
            token_service = TokenService()
            therapist_repository = TherapistService()
            patient_repository = DjangoPatientRepository()
            signup_use_case = SignupUseCase(
                user_repository=user_repository,
                therapist_repository=therapist_repository,
                patient_repository=patient_repository,  
                token_service=token_service
            )

            session = SignupUseCase.execute(signup_use_case, serializer.validated_data)

            audit_logger.info(f"SignupView: User successfully registered.")
            
            formatted_response = ApiResponse.format_response(data=session, success=True, message="User successfully registered.")
            return Response(formatted_response, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            audit_logger.error(f"SignupView: ValidationError: {e}")
            
            formatted_response = ApiResponse.format_response(data=None, success=False, message=str(e))
            return Response(formatted_response, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    View for user login.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Authenticate and log in a user",
        description="Authenticates a user and returns a session token upon successful login.",
        request=LoginSerializer,
        responses={
            200: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
        },
    )
    def post(self, request):
        """
        Handles user login.
        """
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            audit_logger.warning(f"LoginView: Invalid input data: {serializer.errors}")
            
            formatted_response = ApiResponse.format_response(data=serializer.errors, success=False, message="Invalid input data.")
            return Response(formatted_response, status=status.HTTP_400_BAD_REQUEST)
        
        from .....core.domain.usecase.auth_use_case import LoginUseCase
        from .....core.data.service.token_service import TokenService
        from .....core.data.service.django_auth_service import DjangoAuthService
        from .....core.data.repositories.django_user_repository import DjangoUserRepository

        user_repository = DjangoUserRepository()
        auth_service = DjangoAuthService()
        token_service = TokenService()
        
        login_use_case = LoginUseCase(
            user_repository=user_repository,
            auth_service = auth_service,
            token_service = token_service
        )
        
        session = login_use_case.execute(serializer.validated_data)
        
        audit_logger.info(f"LoginView: User successfully logged in.")
        
        formatted_response = ApiResponse.format_response(data=session, success=True, message="User successfully logged in.")
        return Response(formatted_response, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    View for user logout.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Log out a user",
        description="Invalidates the user's session using the refresh token.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "refresh_token": {"type": "string", "description": "Refresh token to invalidate."},
                },
                "required": ["refresh_token"],
            },
        },
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
        },
    )
    def post(self, request):
        """
        Handles user logout.
        """
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            audit_logger.warning(f"LogoutView: Refresh token is required.")
            
            return ResponseWrapper.failure(message="Refresh token is required.")
        
        from .....core.data.service.token_service import TokenService
        from .....core.domain.usecase.auth_use_case import LogoutUseCase

        token_service = TokenService()
        
        logout_use_case = LogoutUseCase(token_service)
        logout_use_case.execute(refresh_token)
        
        audit_logger.info(f"LogoutView:Session successfully logged out.")
        
        return ResponseWrapper.success(message="Session successfully logged out.")
        

class RefreshSessionView(APIView):
    """
    View for refreshing user session.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Refresh user session",
        description="Refreshes the user's session and returns new tokens.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "refresh_token": {"type": "string", "description": "Refresh token to refresh."},
                },
                "required": ["refresh_token"],
            },
        },
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
        },
    )
    def post(self, request):
        """
        Handles session refresh using a refresh token.
        """
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            audit_logger.warning(f"RefreshSessionView: Refresh token is required.")
            
            return ResponseWrapper.failure(message="Refresh token is required.", status=status.HTTP_400_BAD_REQUEST)

        from .....core.domain.usecase.auth_use_case import RefreshTokenUseCase
        from .....core.data.service.token_service import TokenService
        from .....core.data.repositories.django_user_repository import DjangoUserRepository

        user_repository = DjangoUserRepository()
        token_service = TokenService()
        
        refresh_token_use_case = RefreshTokenUseCase(token_service=token_service, user_repository=user_repository)
        
        session_refreshed = refresh_token_use_case.execute(refresh_token)
        
        audit_logger.info(f"RefreshSessionView: Session successfully refreshed.")
        
        return ResponseWrapper.success(session_refreshed, message="Session successfully refreshed")


