from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from ....application.use_cases.patient_use_cases import (
    CreatePatientUseCase,
    UpdatePatientUseCase,
    GetPatientUseCase,
    SearchPatientsUseCase,
    DeletePatientUseCase,
    DeactivatePatientUseCase,
    ActivatePatientUseCase,
    GetDeletedPatientsUseCase
)
from ..serializers.serializers import PatientSerializer
from ....infrastructure.repositories.django_patient_repository import DjangoPatientRepository
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

class PatientViewSet(viewsets.ViewSet):
    """API para la gestión de pacientes."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repository = DjangoPatientRepository()
        self.create_patient_use_case = CreatePatientUseCase(self.repository)
        self.update_patient_use_case = UpdatePatientUseCase(self.repository)
        self.get_patient_use_case = GetPatientUseCase(self.repository)
        self.search_patients_use_case = SearchPatientsUseCase(self.repository)
        self.delete_patient_use_case = DeletePatientUseCase(self.repository)
        self.deactivate_patient_use_case = DeactivatePatientUseCase(self.repository)
        self.activate_patient_use_case = ActivatePatientUseCase(self.repository)
        self.get_deleted_patients_use_case = GetDeletedPatientsUseCase(self.repository)
    

    @extend_schema(
        summary="Create a new patient",
        description="Creates a new patient record.",
        request=PatientSerializer,
        responses={
            201: PatientSerializer,
            400: OpenApiTypes.OBJECT,
        },
    )
    def create(self, request):
        """Crea un nuevo paciente."""
        serializer = PatientSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        patient = self.create_patient_use_case.execute(serializer.validated_data)
        
        return Response(self._entity_to_dict(patient), status=status.HTTP_201_CREATED)

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
    def update(self, request, pk=None):
        """Actualiza un paciente existente."""
        serializer = PatientSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        patient = self.update_patient_use_case.execute(int(pk), serializer.validated_data)
        
        return Response(self._entity_to_dict(patient))

    
    @extend_schema(
        summary="Retrieve a patient",
        description="Gets a patient by their ID.",
        responses={
            200: PatientSerializer,
            404: OpenApiTypes.OBJECT,
        },
        parameters=[
            OpenApiParameter(
                name='pk',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='ID of the patient to retrieve',
                required=True,
            ),
        ],
    )
    def retrieve(self, request, pk=None):
        """Obtiene un paciente por su ID."""
        patient = self.get_patient_use_case.execute(int(pk))
        return Response(self._entity_to_dict(patient))

    
    @extend_schema(
        summary="List patients",
        description="Lists all patients with optional filters applied via query parameters.",
        responses={
            200: PatientSerializer(many=True),
        },
        parameters=[
            OpenApiParameter(
                name='name',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter patients by name (partial match)',
                required=False,
            ),
            OpenApiParameter(
                name='is_active',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Filter patients by active status',
                required=False,
            ),
            # ADD THE PARAMS
        ],
    )
    def list(self, request):
        """Lista todos los pacientes con filtros opcionales."""
        filters = request.query_params.dict()
        patients = self.search_patients_use_case.execute(filters)
        return Response([self._entity_to_dict(patient) for patient in patients])
    
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
    @action(detail=True, methods=['post'])
    def delete(self, request, pk=None):
        """Elimina lógicamente un paciente."""
        self.delete_patient_use_case.execute(int(pk))
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
    @extend_schema(
        summary="Deactivate a patient",
        description="Deactivates the specified patient.",
        responses={
            204: None,
            404: OpenApiTypes.OBJECT,
        },
        parameters=[
            OpenApiParameter(
                name='pk',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='ID of the patient to deactivate',
                required=True,
            ),
        ],
    )
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Desactiva un paciente."""
        self.deactivate_patient_use_case.execute(int(pk))
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @extend_schema(
        summary="Activate a patient",
        description="Activates the specified patient.",
        responses={
            204: None,
            404: OpenApiTypes.OBJECT,
        },
        parameters=[
            OpenApiParameter(
                name='pk',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='ID of the patient to activate',
                required=True,
            ),
        ],
    )    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activa un paciente."""
        self.activate_patient_use_case.execute(int(pk))
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @extend_schema(
        summary="List deleted patients",
        description="Lists all patients that have been logically deleted.",
        responses={
            200: PatientSerializer(many=True),
        },
    )
    @action(detail=False, methods=['get'])
    def deleted(self, request):
        """Obtiene los pacientes eliminados lógicamente."""
        patients = self.get_deleted_patients_use_case.execute()
        return Response([self._entity_to_dict(patient) for patient in patients])
    

    def _entity_to_dict(self, patient):
        """Convierte una entidad de paciente a un diccionario."""
        return {
            'id': patient.id,
            'name': patient.name,
            'description': patient.description,
            'first_therapy': patient.first_therapy,
            'last_therapy': patient.last_therapy,
            'is_active': patient.is_active,
            'created_at': patient.created_at,
            'updated_at': patient.updated_at,
            'deleted_at': patient.deleted_at,
            'user_id': patient.user_id
        }

