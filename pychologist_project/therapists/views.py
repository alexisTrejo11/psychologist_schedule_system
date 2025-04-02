from django.forms import ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .models import Therapist
from .serializers import TherapistSerializer
from .services import TherapistService
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from core.api_response.response import ApiResponse
import logging

audit_logger = logging.getLogger('audit_logger')

class TherapistViewSet(ModelViewSet):
    """
    ViewSet to manage therapist data. Only administrators can access these endpoints.
    """
    queryset = Therapist.objects.all()
    serializer_class = TherapistSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

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
        try:
            serializer = TherapistSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            therapist = TherapistService.create_therapist(serializer.validated_data)
            serializer = self.get_serializer(therapist)  # Use the serializer
            formatted_response = ApiResponse.format_response(data=serializer.data, success=True, message="Therapist created successfully.")
            audit_logger.info(f"TherapistViewSet: Therapist created successfully. ID: {therapist.id}")
            return Response(formatted_response, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            audit_logger.error(f"TherapistViewSet: ValidationError: {e}")
            formatted_response = ApiResponse.format_response(data=None, success=False, message=str(e))
            return Response(formatted_response, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            audit_logger.error(f"TherapistViewSet: Exception: {e}")
            formatted_response = ApiResponse.format_response(data=None, success=False, message=f"Internal server error: {e}")
            return Response(formatted_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        try:
            therapist = self.get_object()  # Use the default retrieve logic
            serializer = self.get_serializer(therapist)
            formatted_response = ApiResponse.format_response(data=serializer.data, success=True, message="Therapist retrieved successfully.")
            audit_logger.info(f"TherapistViewSet: Therapist retrieved successfully. ID: {therapist_id}")
            return Response(formatted_response, status=status.HTTP_200_OK)
        except Exception as e:
            audit_logger.error(f"TherapistViewSet: Exception: {e}")
            formatted_response = ApiResponse.format_response(data=None, success=False, message=f"Error retrieving therapist: {e}")
            return Response(formatted_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        try:
            instance = self.get_object()  # gets the therapist instance.
            serializer = TherapistSerializer(instance=instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            formatted_response = ApiResponse.format_response(data=serializer.data, success=True, message="Therapist updated successfully.")
            audit_logger.info(f"TherapistViewSet: Therapist updated successfully. ID: {therapist_id}")
            return Response(formatted_response, status=status.HTTP_200_OK)
        except ValidationError as e:
            audit_logger.error(f"TherapistViewSet: ValidationError: {e}")
            formatted_response = ApiResponse.format_response(data=None, success=False, message=str(e))
            return Response(formatted_response, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            audit_logger.error(f"TherapistViewSet: Exception: {e}")
            formatted_response = ApiResponse.format_response(data=None, success=False, message=f"Internal server error: {e}")
            return Response(formatted_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            formatted_response = ApiResponse.format_response(data=None, success=True, message="Therapist deleted successfully.")
            audit_logger.info(f"TherapistViewSet: Therapist deleted successfully. ID: {therapist_id}")
            return Response(formatted_response, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            audit_logger.error(f"TherapistViewSet: Exception: {e}")
            formatted_response = ApiResponse.format_response(data=None, success=False, message=f"Internal server error: {e}")
            return Response(formatted_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)