from django.forms import ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from ..serializers import SignupSerializer, LoginSerializer
from ..services.auth_services import AuthService
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

class SignupView(APIView):
    permission_classes = [AllowAny]  

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            auth_service = AuthService()
            auth_service.validate_singup_credentials(serializer.validated_data)
            session = auth_service.process_signup(serializer.validated_data)
            return Response(session, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]  

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            auth_service = AuthService()

            user = auth_service.validate_login_credentials(serializer.validated_data)
            session = auth_service.process_login(user)
            
            return Response(session, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated] 

    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            auth_service = AuthService()
            auth_service.logout(refresh_token)
            return Response({"message": "Session successfully logged out"}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RefreshSessionView(APIView):
    permission_classes = [IsAuthenticated] 

    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            auth_service = AuthService()
            session_refreshed = auth_service.refresh_session(refresh_token)
            return Response(session_refreshed, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
