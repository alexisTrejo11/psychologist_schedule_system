from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from ..serializers.serializers import TherapySessionSerializer
from therapy.serializers import TherapySessionSerializer
from core.api_response.response import ApiResponse
from ....application.therapist_session_case import (
    GetTherapistIncomingSessionsUseCase,
    GetTherapistSessionListUseCase,
    CreateTherapistSessionUseCase,
    UpdateTherapistSessionUseCase,
)
from therapy.infrastructure.django_session_repository import DjangoSessionRepository
from therapy.application.service import SessionService

class TherapistSession(APIView):
    """
    API endpoints for managing therapist sessions.
    """
    permission_classes = [IsAuthenticated]
    session_service = SessionService()
    session_repository = DjangoSessionRepository()

    @extend_schema(
        summary="List Therapist Sessions",
        description="Retrieves a list of all therapy sessions associated with the authenticated therapist.",
        responses={
            200: TherapySessionSerializer(many=True),
            401: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
    )
    def get(self, request):
        """
        Retrieve a list of all therapy sessions for the authenticated therapist.
        """
        user = request.user

        session_use_case = GetTherapistSessionListUseCase(self.session_service)
        sessions = session_use_case.execute(user)

        formatted_response = ApiResponse.format_response(
            data=TherapySessionSerializer(sessions, many=True).data,
            success=True,
            message="Therapist sessions retrieved successfully."
        )
        return Response(formatted_response, status=status.HTTP_200_OK)

    @extend_schema(
        summary="List Incoming Therapist Sessions",
        description="Retrieves a list of upcoming/incoming therapy sessions for the authenticated therapist.",
        responses={
            200: TherapySessionSerializer(many=True),
            401: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
    )
    def list_incoming_sessions(self, request):
        """
        Retrieve a list of upcoming/incoming therapy sessions for the authenticated therapist.
        """
        user = request.user

        session_use_case = GetTherapistIncomingSessionsUseCase(self.session_service)
        sessions = session_use_case.execute(user)

        formatted_response = ApiResponse.format_response(
            data=TherapySessionSerializer(sessions, many=True).data,
            success=True,
            message="Incoming therapist sessions retrieved successfully."
        )
        return Response(formatted_response, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Create a New Therapy Session",
        description="Creates a new therapy session for the authenticated therapist.",
        request=TherapySessionSerializer,
        responses={
            201: TherapySessionSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
    )
    def post(self, request):
        """
        Create a new therapy session for the authenticated therapist.
        """
        serializer = TherapySessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session_use_case = CreateTherapistSessionUseCase(self.session_service)
        session = session_use_case.execute(serializer.validated_data)

        formatted_response = ApiResponse.format_response(
            data=TherapySessionSerializer(session).data,
            success=True,
            message="Therapy session created successfully."
        )
        return Response(formatted_response, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Update an Existing Therapy Session",
        description="Updates an existing therapy session for the authenticated therapist.",
        request=TherapySessionSerializer,
        responses={
            200: TherapySessionSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
    )
    def patch(self, request):
        """
        Update an existing therapy session for the authenticated therapist.
        """
        serializer = TherapySessionSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        session_use_case = UpdateTherapistSessionUseCase(self.session_service)
        session = session_use_case.execute(serializer.validated_data)

        formatted_response = ApiResponse.format_response(
            data=TherapySessionSerializer(session).data,
            success=True,
            message="Therapy session updated successfully."
        )
        return Response(formatted_response, status=status.HTTP_200_OK)