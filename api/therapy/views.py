from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from .application.service import SessionService
from .models import TherapySession
from .serializers import TherapySessionSerializer
from .infrastructure.repositories import DjangoSessionRepository as sessionRepository
from core.api_response.response import ApiResponse
import logging
from core.swagger.schemas import TherapySessionResponseSchema

audit_logger = logging.getLogger('audit_logger')

class TherapySessionViewSet(ModelViewSet):
    """
    ViewSet to manage therapy sessions.
    """
    serializer_class = TherapySessionSerializer
    queryset = TherapySession.objects.all()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = SessionService(sessionRepository())

    @extend_schema(
        summary="Retrieves a therapy session by ID",
        description="Fetches a single therapy session based on its unique identifier.",
        responses={
            200: TherapySessionResponseSchema,
            404: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
        parameters=[
            OpenApiParameter(
                name='pk',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='ID of the therapy session to retrieve',
                required=True,
            ),
        ],
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Override the `retrieve` method to handle GET requests by ID.
        """
        session_id = kwargs.get('pk')
        user = request.user if request.user.is_authenticated else None
        ip_address = request.META.get('REMOTE_ADDR')
        audit_logger.info(f"GET request for session ID: {session_id}, User: {user}, IP: {ip_address}")
        try:
            session = self.service.get_session(int(session_id))
            audit_logger.info(f"Session successfully retrieved with ID: {session_id}")
            formatted_response = ApiResponse.format_response(self.get_serializer(session).data, success=True)
            return Response(formatted_response)
        except Exception as e:
            formatted_response = ApiResponse.format_response(None, success=False, message=str(e))
            return Response(formatted_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Creates a new therapy session",
        description="Creates a new therapy session with the provided data.",
        request=TherapySessionSerializer,
        responses={
            201: TherapySessionSerializer,
            400: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
    )
    def create(self, request, *args, **kwargs):
        """
        Creates a new therapy session.
        """
        user = request.user if request.user.is_authenticated else None
        ip_address = request.META.get('REMOTE_ADDR')
        audit_logger.info(f"POST request to create a new session, User: {user}, IP: {ip_address}")
        serializer = TherapySessionSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            session = self.service.schedule_session(serializer.validated_data)
            audit_logger.info(f"New session created successfully with ID: {session.id}, User: {user}, IP: {ip_address}")
            formatted_response = ApiResponse.format_response(self.get_serializer(session).data, success=True)
            return Response(formatted_response, status=status.HTTP_201_CREATED)
        except Exception as e:
            formatted_response = ApiResponse.format_response(None, success=False, message=str(e))
            return Response(formatted_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Updates an existing therapy session",
        description="Updates an existing therapy session with the provided data.",
        request=TherapySessionSerializer,
        responses={
            200: TherapySessionSerializer,
            400: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
        parameters=[
            OpenApiParameter(
                name='pk',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='ID of the therapy session to update',
                required=True,
            ),
        ],
    )
    def update(self, request, *args, **kwargs):
        """
        Updates an existing therapy session.
        """
        session_id = kwargs.get('pk')
        user = request.user if request.user.is_authenticated else None
        ip_address = request.META.get('REMOTE_ADDR')
        audit_logger.info(f"PUT request to update session ID: {session_id}, User: {user}, IP: {ip_address}")
        instance = self.get_object()
        serializer = TherapySessionSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            audit_logger.info(serializer.validated_data)
            session_updated = self.service.update(instance, serializer.validated_data)
            audit_logger.info(f"Session updated successfully with ID: {session_id}, User: {user}, IP: {ip_address}")
            formatted_response = ApiResponse.format_response(self.get_serializer(session_updated).data, success=True)
            return Response(formatted_response, status=status.HTTP_200_OK)
        except Exception as e:
            formatted_response = ApiResponse.format_response(None, success=False, message=str(e))
            return Response(formatted_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Soft deletes a therapy session",
        description="Logically deletes a therapy session, marking it as deleted without removing it from the database.",
        responses={
            200: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
        parameters=[
            OpenApiParameter(
                name='pk',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='ID of the therapy session to soft delete',
                required=True,
            ),
        ],
    )
    @action(detail=True, methods=['post'], url_path='soft-delete')
    def soft_delete(self, request, pk=None):
        """
        Performs a logical deletion of a therapy session.
        """
        user = request.user if request.user.is_authenticated else None
        ip_address = request.META.get('REMOTE_ADDR')
        audit_logger.info(f"POST request to soft delete session ID: {pk}, User: {user}, IP: {ip_address}")
        try:
            self.service.soft_delete(pk)
            audit_logger.info(f"Session soft deleted successfully with ID: {pk}, User: {user}, IP: {ip_address}")
            formatted_response = ApiResponse.format_response({"message": "Session logically deleted."}, success=True)
            return Response(formatted_response, status=status.HTTP_200_OK)
        except Exception as e:
            formatted_response = ApiResponse.format_response(None, success=False, message=str(e))
            return Response(formatted_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Searches therapy sessions",
        description="Searches therapy sessions based on various filter criteria.",
        responses={
            200: TherapySessionSerializer(many=True),
            400: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
        parameters=[
            OpenApiParameter(
                name='status',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter sessions by status',
            ),
            OpenApiParameter(
                name='patient_ids',
                type={'type': 'array', 'items': {'type': 'integer'}},
                location=OpenApiParameter.QUERY,
                description='Filter sessions by patient IDs (list of integers)',
            ),
            OpenApiParameter(
                name='start_time_after',
                type=OpenApiTypes.DATETIME,
                location=OpenApiParameter.QUERY,
                description='Filter sessions by start time after this datetime (ISO 8601)',
            ),
            OpenApiParameter(
                name='start_time_before',
                type=OpenApiTypes.DATETIME,
                location=OpenApiParameter.QUERY,
                description='Filter sessions by start time before this datetime (ISO 8601)',
            ),
            OpenApiParameter(
                name='end_time_after',
                type=OpenApiTypes.DATETIME,
                location=OpenApiParameter.QUERY,
                description='Filter sessions by end time after this datetime (ISO 8601)',
            ),
            OpenApiParameter(
                name='end_time_before',
                type=OpenApiTypes.DATETIME,
                location=OpenApiParameter.QUERY,
                description='Filter sessions by end time before this datetime (ISO 8601)',
            ),
            OpenApiParameter(
                name='created_at_after',
                type=OpenApiTypes.DATETIME,
                location=OpenApiParameter.QUERY,
                description='Filter sessions by creation time after this datetime (ISO 8601)',
            ),
            OpenApiParameter(
                name='created_at_before',
                type=OpenApiTypes.DATETIME,
                location=OpenApiParameter.QUERY,
                description='Filter sessions by creation time before this datetime (ISO 8601)',
            ),
            OpenApiParameter(
                name='search_term',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search sessions by notes or status',
            ),
        ],
    )
    @action(detail=False, methods=['get'], url_path='search')
    def search_sessions(self, request):
        """
        Searches therapy sessions based on dynamic filters.
        """
        user = request.user if request.user.is_authenticated else None
        ip_address = request.META.get('REMOTE_ADDR')
        audit_logger.info(f"GET request to search sessions, Filters: {request.query_params.dict()}, User: {user}, IP: {ip_address}")
        try:
            filters = request.query_params.dict()
            sessions = self.service.search_sessions(filters)
            audit_logger.info(f"Search successful, Results count: {len(sessions)}, User: {user}, IP: {ip_address}")
            formatted_response = ApiResponse.format_response(self.get_serializer(sessions, many=True).data, success=True)
            return Response(formatted_response, status=status.HTTP_200_OK)
        except Exception as e:
            formatted_response = ApiResponse.format_response(None, success=False, message=str(e))
            return Response(formatted_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)