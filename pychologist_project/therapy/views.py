from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from django.forms import ValidationError
from .service import SessionService
from .models import TherapySession
from .serializers import TherapySessionSerializer

class TherapySessionViewSet(ModelViewSet):
    """
    ViewSet para gestionar sesiones de terapia.
    """
    serializer_class = TherapySessionSerializer
    queryset = TherapySession.objects.all()
    service = SessionService()

    def create(self, request, *args, **kwargs):
        """
        Crear una nueva sesión de terapia.
        """
        try:
            data = request.data
            session = self.service.schedule_session(data)
            serializer = self.get_serializer(session)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """
        Actualizar una sesión de terapia existente.
        """
        try:
            instance = self.get_object()
            data = request.data

            if 'start_time' in data or 'end_time' in data:
                self.service.update_schedule(instance.id, data)
            if 'patients' in data:
                self.service.update_patients(instance.id, data)

            instance.refresh_from_db()
            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='update-status')
    def update_status(self, request, pk=None):
        """
        Actualizar el estado de una sesión de terapia.
        """
        try:
            new_status = request.data.get('status')
            if not new_status:
                return Response({"error": "El campo 'status' es obligatorio."}, status=status.HTTP_400_BAD_REQUEST)

            session = self.service.update_status(pk, new_status)
            serializer = self.get_serializer(session)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='soft-delete')
    def soft_delete(self, request, pk=None):
        """
        Realizar una eliminación lógica de una sesión de terapia.
        """
        try:
            self.service.soft_delete(pk)
            return Response({"message": "Sesión eliminada lógicamente."}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], url_path='search')
    def search_sessions(self, request):
        """
        Buscar sesiones de terapia basadas en filtros dinámicos.
        """
        try:
            filters = request.query_params.dict()
            sessions = self.service.search_session(filters)
            serializer = self.get_serializer(sessions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)