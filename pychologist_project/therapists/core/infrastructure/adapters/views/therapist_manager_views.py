from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from core.api_response.response import DjangoResponseWrapper as ResponseWrapper
from .....models import Therapist
from ..serializers.serializers import TherapistSerializer
from ....application.therapist_use_case import CreateTherapistUseCase, UpdateTherapistUseCase, DeleteTherapistUseCase
from ...repositories.django_therapist_repository import DjangoTherapistRepository
import logging

audit_logger = logging.getLogger('audit_logger')

class TherapistViewSet(ModelViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        repository = DjangoTherapistRepository()
        self.create_therapist_use_case = CreateTherapistUseCase(repository)
        self.update_therapist_use_case = UpdateTherapistUseCase(repository)
        self.delete_therapist_use_case = DeleteTherapistUseCase(repository)

    """
    ViewSet to manage therapist data. Only administrators can access these endpoints.
    """
    queryset = Therapist.objects.all()
    serializer_class = TherapistSerializer
    

    @extend_schema(
        summary="Retrieve a therapist",
        description="Retrieves a single therapist by ID.",
        responses={
            200: TherapistSerializer,
            404: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
        parameters=[
            OpenApiParameter(
                name='pk',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='ID of the therapist to retrieve',
                required=True,
            ),
        ],
    )
    def retrieve(self, request, *args, **kwargs):
        therapist_id = kwargs.get('pk')
        audit_logger.info(f"TherapistViewSet: Retrieving therapist with ID: {therapist_id}, User: {request.user.id}")
        
        therapist = self.get_object() 
        
        audit_logger.info(f"TherapistViewSet: Therapist retrieved successfully. ID: {therapist_id}")
        
        return ResponseWrapper.found(
            data=self.get_serializer(therapist).data, 
            entity='therapist'
        )


    @extend_schema(
        summary="List all therapists",
        description="Retrieves a list of all therapists.",
        responses={
            200: TherapistSerializer(many=True),
            500: OpenApiTypes.OBJECT,
        },
    )
    def list(self, request, *args, **kwargs):
        """
        Retrieves a list of all therapists.
        """
        audit_logger.info(f"TherapistViewSet: Retrieving all therapists. User: {request.user.id}")
        
        therapists = self.get_queryset()
        
        audit_logger.info("TherapistViewSet: All therapists retrieved successfully.")
    
        return ResponseWrapper.found(
            data=self.get_serializer(therapists, many=True).data,
            entity='therapists'
        )

    @extend_schema(
        summary="Create a new therapist",
        description="Creates a new therapist record.",
        request=TherapistSerializer,
        responses={
            201: TherapistSerializer,
            400: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
    )
    def create(self, request, *args, **kwargs):
        audit_logger.info(f"TherapistViewSet: Creating new therapist with data: {request.data}, User: {request.user.id}")
        
        serializer = TherapistSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        therapist = self.create_therapist_use_case.execute(serializer.validated_data)

        audit_logger.info(f"TherapistViewSet: Therapist created successfully. ID: {therapist.id}")
        
        return ResponseWrapper.created(data=self.get_serializer(therapist).data, entity='therapist')
        
    @extend_schema(
        summary="Update a therapist",
        description="Updates an existing therapist record.",
        request=TherapistSerializer,
        responses={
            200: TherapistSerializer,
            400: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
        parameters=[
            OpenApiParameter(
                name='pk',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='ID of the therapist to update',
                required=True,
            ),
        ],
    )
    def update(self, request, *args, **kwargs):
        therapist_id = kwargs.get('pk')
        audit_logger.info(f"TherapistViewSet: Updating therapist with ID: {therapist_id}, data: {request.data}, User: {request.user.id}")
        
        instance = self.get_object() 
        
        serializer = TherapistSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        therapist = self.update_therapist_use_case.execute(instance, serializer.validated_data)
        
        audit_logger.info(f"TherapistViewSet: Therapist updated successfully. ID: {therapist_id}")
        
        return ResponseWrapper.updated(
            data=self.get_serializer(therapist).data, 
            entity='therapist'
        )

    @extend_schema(
        summary="Delete a therapist",
        description="Deletes a therapist.",
        responses={
            204: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
        parameters=[
            OpenApiParameter(
                name='pk',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='ID of the therapist to delete',
                required=True,
            ),
        ],
    )
    def destroy(self, request, *args, **kwargs):
        therapist_id = kwargs.get('pk')
        audit_logger.info(f"TherapistViewSet: Deleting therapist with ID: {therapist_id}, User: {request.user.id}")
        
        delete_use_case = self.delete_therapist_use_case(self.repository)
        delete_use_case.execute(therapist_id)

        audit_logger.info(f"TherapistViewSet: Therapist deleted successfully. ID: {therapist_id}")
        
        return ResponseWrapper.no_content(message="Therapist deleted successfully.")
