from django.forms import ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from core.permissions import IsTherapistOrAdmin
from ..models import Patient
from ..serializers import PatientSerializer
from rest_framework.permissions import IsAuthenticated
from ..services.patient_service import PatientService

class PatientViewSet(ModelViewSet):
    queryset = Patient.objects.all()
    patient_service = PatientService()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated, IsTherapistOrAdmin]

    def create(self, request, *args, **kwargs):
        """
        Crea un nuevo paciente.
        """
        try:
            patient_data = request.data
            patient = self.patient_service.create_patient(patient_data)
            serializer = self.get_serializer(patient)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """
        Actualiza la información de un paciente existente.
        """
        try:
            patient_id = kwargs.get('pk')
            patient_data = request.data
            updated_patient = self.patient_service.update_patient(patient_id, patient_data)
            serializer = self.get_serializer(updated_patient)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], url_path='soft-delete')
    def soft_delete(self, request, pk=None):
        """
        Realiza una eliminación lógica de un paciente.
        """
        try:
            PatientService().soft_delete_patient_by_id(pk)
            return Response({"message": "Paciente eliminado lógicamente."}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], url_path='deleted')
    def get_deleted_patients(self, request):
        """
        Obtiene una lista de pacientes eliminados lógicamente.
        """
        try:
            deleted_patients = self.patient_service.get_deleted_patients()
            serializer = self.get_serializer(deleted_patients, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='search')
    def search_patients(self, request):
        """
        Realiza una búsqueda dinámica de pacientes basada en filtros.
        """
        try:
            filters = request.query_params.dict()  
            patients = self.patient_service.search_patients(filters)
            serializer = self.get_serializer(patients, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)