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
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from core.api_response.response import ApiResponse
import logging

audit_logger = logging.getLogger('audit_logger')

class PatientViewSet(ModelViewSet):
    """
    ViewSet to manage patient data. Only therapists and admins can access these endpoints.
    """
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated, IsTherapistOrAdmin]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.patient_service = PatientService()

    @extend_schema(
        summary="Create a new patient",
        description="Creates a new patient record.",
        request=PatientSerializer,
        responses={
            201: PatientSerializer,
            400: OpenApiTypes.OBJECT,
        },
    )
    def create(self, request, *args, **kwargs):
        """
        Creates a new patient.
        """
        patient_data = request.data
        audit_logger.info(f"PatientViewSet: Creating new patient with data: {patient_data}, User: {request.user.id}")
        try:
            patient = self.patient_service.create_patient(patient_data)
            serializer = self.get_serializer(patient)
            formatted_response = ApiResponse.format_response(data=serializer.data, success=True, message="Patient created successfully.")
            audit_logger.info(f"PatientViewSet: Patient created successfully. ID: {patient.id}")
            return Response(formatted_response, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            audit_logger.error(f"PatientViewSet: ValidationError: {e}")
            formatted_response = ApiResponse.format_response(data=None, success=False, message=str(e))
            return Response(formatted_response, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Update an existing patient",
        description="Updates the information of an existing patient.",
        request=PatientSerializer,
        responses={
            200: PatientSerializer,
            400: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        parameters=[
            OpenApiParameter(
                name='pk',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='ID of the patient to update',
                required=True,
            ),
        ],
    )
    def update(self, request, *args, **kwargs):
        """
        Updates the information of an existing patient.
        """
        patient_id = kwargs.get('pk')
        patient_data = request.data
        audit_logger.info(f"PatientViewSet: Updating patient with ID: {patient_id}, data: {patient_data}, User: {request.user.id}")
        try:
            updated_patient = self.patient_service.update_patient(patient_id, patient_data)
            serializer = self.get_serializer(updated_patient)
            formatted_response = ApiResponse.format_response(data=serializer.data, success=True, message="Patient updated successfully.")
            audit_logger.info(f"PatientViewSet: Patient updated successfully. ID: {patient_id}")
            return Response(formatted_response, status=status.HTTP_200_OK)
        except ValidationError as e:
            audit_logger.error(f"PatientViewSet: ValidationError: {e}")
            formatted_response = ApiResponse.format_response(data=None, success=False, message=str(e))
            return Response(formatted_response, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            audit_logger.error(f"PatientViewSet: ValueError: {e}")
            formatted_response = ApiResponse.format_response(data=None, success=False, message=str(e))
            return Response(formatted_response, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        summary="Soft delete a patient",
        description="Logically deletes a patient by setting the deleted_at field.",
        responses={
            200: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        parameters=[
            OpenApiParameter(
                name='pk',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='ID of the patient to soft delete',
                required=True,
            ),
        ],
    )
    @action(detail=True, methods=['post'], url_path='soft-delete')
    def soft_delete(self, request, pk=None):
        """
        Performs a logical deletion of a patient.
        """
        audit_logger.info(f"PatientViewSet: Soft deleting patient with ID: {pk}, User: {request.user.id}")
        try:
            self.patient_service.soft_delete_patient_by_id(pk)
            formatted_response = ApiResponse.format_response(data={"message": "Patient soft deleted successfully."}, success=True, message="Patient soft deleted successfully.")
            audit_logger.info(f"PatientViewSet: Patient soft deleted successfully. ID: {pk}")
            return Response(formatted_response, status=status.HTTP_200_OK)
        except ValueError as e:
            audit_logger.error(f"PatientViewSet: ValueError: {e}")
            formatted_response = ApiResponse.format_response(data=None, success=False, message=str(e))
            return Response(formatted_response, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        summary="Get deleted patients",
        description="Retrieves a list of logically deleted patients.",
        responses={
            200: PatientSerializer(many=True),
            500: OpenApiTypes.OBJECT,
        },
    )
    @action(detail=False, methods=['get'], url_path='deleted')
    def get_deleted_patients(self, request):
        """
        Retrieves a list of logically deleted patients.
        """
        audit_logger.info(f"PatientViewSet: Retrieving deleted patients, User: {request.user.id}")
        try:
            deleted_patients = self.patient_service.get_deleted_patients()
            serializer = self.get_serializer(deleted_patients, many=True)
            formatted_response = ApiResponse.format_response(data=serializer.data, success=True, message="Deleted patients retrieved successfully.")
            audit_logger.info(f"PatientViewSet: Deleted patients retrieved. Count: {len(deleted_patients)}")
            return Response(formatted_response, status=status.HTTP_200_OK)
        except Exception as e:
            audit_logger.error(f"PatientViewSet: Exception: {e}")
            formatted_response = ApiResponse.format_response(data=None, success=False, message=str(e))
            return Response(formatted_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Search patients",
        description="Searches for patients based on provided filter parameters.",
        responses={
            200: PatientSerializer(many=True),
            400: OpenApiTypes.OBJECT,
        },
        parameters=[
            OpenApiParameter(
                name='name',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by patient name',
            ),
            OpenApiParameter(
                name='description',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by patient description',
            ),
        ],
    )
    @action(detail=False, methods=['get'], url_path='search')
    def search_patients(self, request):
        """
        Performs a dynamic search for patients based on filters.
        """
        filters = request.query_params.dict()
        audit_logger.info(f"PatientViewSet: Searching patients with filters: {filters}, User: {request.user.id}")
        try:
            patients = self.patient_service.search_patients(filters)
            serializer = self.get_serializer(patients, many=True)
            formatted_response = ApiResponse.format_response(data=serializer.data, success=True, message="Patients found successfully.")
            audit_logger.info(f"PatientViewSet: Patients found. Count: {len(patients)}")
            return Response(formatted_response, status=status.HTTP_200_OK)
        except ValueError as e:
            audit_logger.error(f"PatientViewSet: ValueError: {e}")
            formatted_response = ApiResponse.format_response(data=None, success=False, message=str(e))
            return Response(formatted_response, status=status.HTTP_400_BAD_REQUEST)