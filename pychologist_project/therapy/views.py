from django.forms import ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from .application.service import SessionService
from .models import TherapySession
from .serializers import TherapySessionSerializer
from .infrastructure.repositories import DjangoSessionRepository as sessionRepository
import logging

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

    def retrieve(self, request, *args, **kwargs):
        """
        Override the `retrieve` method to handle GET requests by ID.
        """
        session_id = kwargs.get('pk')
        user = request.user if request.user.is_authenticated else None
        ip_address = request.META.get('REMOTE_ADDR')

        audit_logger.info(f"GET request for session ID: {session_id}, User: {user}, IP: {ip_address}")

        session = self.service.get_session(int(session_id))
        audit_logger.info(f"Session successfully retrieved with ID: {session_id}")
        return Response({"session": session.__dict__})

    def create(self, request, *args, **kwargs):
        """
        Create a new therapy session.
        """
        user = request.user if request.user.is_authenticated else None
        ip_address = request.META.get('REMOTE_ADDR')

        audit_logger.info(f"POST request to create a new session, User: {user}, IP: {ip_address}")

        data = request.data
        serializer = TherapySessionSerializer(data=data)
        session = self.service.schedule_session(serializer.validated_data)
        audit_logger.info(f"New session created successfully with ID: {session.id}, User: {user}, IP: {ip_address}")
        return Response(self.get_serializer(session).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        Update an existing therapy session.
        """
        session_id = kwargs.get('pk')
        user = request.user if request.user.is_authenticated else None
        ip_address = request.META.get('REMOTE_ADDR')

        audit_logger.info(f"PUT request to update session ID: {session_id}, User: {user}, IP: {ip_address}")

        instance = self.get_object()
        data = request.data

        if 'start_time' in data or 'end_time' in data:
            self.service.update_schedule(instance.id, data)
        if 'patients' in data:
            self.service.update_patients(instance.id, data)

        instance.refresh_from_db()
        audit_logger.info(f"Session updated successfully with ID: {session_id}, User: {user}, IP: {ip_address}")
        return Response(self.get_serializer(instance).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='update-status')
    def update_status(self, request, pk=None):
        """
        Update the status of a therapy session.
        """
        user = request.user if request.user.is_authenticated else None
        ip_address = request.META.get('REMOTE_ADDR')

        audit_logger.info(f"POST request to update status for session ID: {pk}, User: {user}, IP: {ip_address}")

        new_status = request.data.get('status')
        if not new_status:
            raise ValidationError("The 'status' field is required.")

        session = self.service.update_status(pk, new_status)
        audit_logger.info(f"Status updated successfully for session ID: {pk}, New Status: {new_status}, User: {user}, IP: {ip_address}")
        return Response(self.get_serializer(session).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='soft-delete')
    def soft_delete(self, request, pk=None):
        """
        Perform a logical deletion of a therapy session.
        """
        user = request.user if request.user.is_authenticated else None
        ip_address = request.META.get('REMOTE_ADDR')

        audit_logger.info(f"POST request to soft delete session ID: {pk}, User: {user}, IP: {ip_address}")

        self.service.soft_delete(pk)
        audit_logger.info(f"Session soft deleted successfully with ID: {pk}, User: {user}, IP: {ip_address}")
        return Response({"message": "Session logically deleted."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='search')
    def search_sessions(self, request):
        """
        Search therapy sessions based on dynamic filters.
        """
        user = request.user if request.user.is_authenticated else None
        ip_address = request.META.get('REMOTE_ADDR')

        audit_logger.info(f"GET request to search sessions, Filters: {request.query_params.dict()}, User: {user}, IP: {ip_address}")

        filters = request.query_params.dict()
        sessions = self.service.search_sessions(filters)
        audit_logger.info(f"Search successful, Results count: {len(sessions)}, User: {user}, IP: {ip_address}")
        return Response(self.get_serializer(sessions, many=True).data, status=status.HTTP_200_OK)