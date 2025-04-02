from django.forms import ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiTypes
from ..serializers import SignupSerializer, LoginSerializer
from ..services.auth_services import AuthService
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
            auth_service = AuthService()
            auth_service.validate_singup_credentials(serializer.validated_data)
            session = auth_service.process_signup(serializer.validated_data)
            audit_logger.info(f"SignupView: User successfully registered. Session data: {session}")
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
        try:
            auth_service = AuthService()
            user = auth_service.validate_login_credentials(serializer.validated_data)
            session = auth_service.process_login(user)
            audit_logger.info(f"LoginView: User successfully logged in. Session data: {session}")
            formatted_response = ApiResponse.format_response(data=session, success=True, message="User successfully logged in.")
            return Response(formatted_response, status=status.HTTP_200_OK)
        except ValueError as e:
            audit_logger.error(f"LoginView: Authentication error: {e}")
            formatted_response = ApiResponse.format_response(data=None, success=False, message=str(e))
            return Response(formatted_response, status=status.HTTP_401_UNAUTHORIZED)

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
            formatted_response = ApiResponse.format_response(data=None, success=False, message="Refresh token is required")
            return Response(formatted_response, status=status.HTTP_400_BAD_REQUEST)
        try:
            auth_service = AuthService()
            auth_service.logout(refresh_token)
            audit_logger.info(f"LogoutView: User successfully logged out.")
            formatted_response = ApiResponse.format_response(data={"message": "Session successfully logged out"}, success=True, message="User successfully logged out.")
            return Response(formatted_response, status=status.HTTP_200_OK)
        except ValueError as e:
            audit_logger.error(f"LogoutView: ValueError: {e}")
            formatted_response = ApiResponse.format_response(data=None, success=False, message=str(e))
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

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
            formatted_response = ApiResponse.format_response(data=None, success=False, message="Refresh token is required.")
            return Response(formatted_response, status=status.HTTP_400_BAD_REQUEST)
        try:
            auth_service = AuthService()
            session_refreshed = auth_service.refresh_session(refresh_token)
            audit_logger.info(f"RefreshSessionView: Session successfully refreshed.")
            formatted_response = ApiResponse.format_response(data=session_refreshed, success=True, message="Session successfully refreshed.")
            return Response(formatted_response, status=status.HTTP_200_OK)
        except ValueError as e:
            audit_logger.error(f"RefreshSessionView: ValueError: {e}")
            formatted_response = ApiResponse.format_response(data=None, success=False, message=str(e))
            return Response(formatted_response, status=status.HTTP_400_BAD_REQUEST)

