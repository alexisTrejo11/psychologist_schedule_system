from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from core.api_response.response import ApiResponse
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
        """
        Retrieves a therapist by ID.
        """
        therapist_id = kwargs.get('pk')
        audit_logger.info(f"TherapistViewSet: Retrieving therapist with ID: {therapist_id}, User: {request.user.id}")
        
        therapist = self.get_object() 
        serializer = self.get_serializer(therapist)
        
        audit_logger.info(f"TherapistViewSet: Therapist retrieved successfully. ID: {therapist_id}")
        
        formatted_response = ApiResponse.format_response(data=serializer.data, success=True, message="Therapist retrieved successfully.")
        return Response(formatted_response, status=status.HTTP_200_OK)


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
        
        serializer = self.get_serializer(therapists, many=True)
        
        audit_logger.info("TherapistViewSet: All therapists retrieved successfully.")
        
        formatted_response = ApiResponse.format_response(
            data=serializer.data,
            success=True,
            message="All therapists retrieved successfully."
        )
        return Response(formatted_response, status=status.HTTP_200_OK)

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
        """
        Creates a new therapist.
        """
        audit_logger.info(f"TherapistViewSet: Creating new therapist with data: {request.data}, User: {request.user.id}")
        
        serializer = TherapistSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        therapist = self.create_therapist_use_case.execute(serializer.validated_data)

        audit_logger.info(f"TherapistViewSet: Therapist created successfully. ID: {therapist.id}")
        
        therapist_data = self.get_serializer(therapist).data
        formatted_response = ApiResponse.format_response(data=therapist_data, success=True, message="Therapist created successfully.")
        return Response(formatted_response, status=status.HTTP_201_CREATED)
        
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
        """
        Updates an existing therapist.
        """
        therapist_id = kwargs.get('pk')
        audit_logger.info(f"TherapistViewSet: Updating therapist with ID: {therapist_id}, data: {request.data}, User: {request.user.id}")
        
        instance = self.get_object() 
        
        serializer = TherapistSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        therapist = self.update_therapist_use_case.execute(instance, serializer.validated_data)
        
        audit_logger.info(f"TherapistViewSet: Therapist updated successfully. ID: {therapist_id}")
        
        therapist_data = self.get_serializer(therapist).data
        formatted_response = ApiResponse.format_response(therapist_data, success=True, message="Therapist updated successfully.")
        return Response(formatted_response, status=status.HTTP_200_OK)

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
        """
        Deletes a therapist.
        """
        therapist_id = kwargs.get('pk')
        audit_logger.info(f"TherapistViewSet: Deleting therapist with ID: {therapist_id}, User: {request.user.id}")
        
        delete_use_case = self.delete_therapist_use_case(self.repository)
        delete_use_case.execute(therapist_id)

        audit_logger.info(f"TherapistViewSet: Therapist deleted successfully. ID: {therapist_id}")
        
        formatted_response = ApiResponse.format_response(data=None, success=True, message="Therapist deleted successfully.")
        return Response(formatted_response, status=status.HTTP_204_NO_CONTENT)
