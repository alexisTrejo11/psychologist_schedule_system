from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .....models import User
from ..serializers.serializers import UserSerializer

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging
from core.api_response.response import ApiResponse

audit_logger = logging.getLogger('audit_logger')

class UserViewSet(ModelViewSet):
    """
    ViewSet to manage user data.  Accessible to authenticated users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Create a new user",
        operation_description="Creates a new user record.",
        request_body=UserSerializer,
        responses={
            201: openapi.Response(
                description="User created successfully.",
                schema=UserSerializer,
            ),
            400: openapi.Response(
                description="Invalid input data.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(type=openapi.TYPE_STRING, description="Error message."),
                    },
                ),
            ),
            500: openapi.Response(
                description="Internal server error.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(type=openapi.TYPE_STRING, description="Error message."),
                    },
                ),
            ),
        },
        security=[{"Bearer": []}],
    )
    def create(self, request, *args, **kwargs):
        """
        Creates a new user.
        """
        from ....domain.usecase.user_user_case import CreateUserUseCase
        from ....data.repositories.django_user_repository import DjangoUserRepository
        
        user_repository = DjangoUserRepository()
        user_use_case = CreateUserUseCase(user_repository)
        
        audit_logger.info(f"UserViewSet: Creating new user with data: {request.data}, User: {request.user.id}")
        
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = user_use_case.execute(serializer.validated_data)
        
        audit_logger.info(f"UserViewSet: User created successfully. ID: {user.id}")
        
        formatted_response = ApiResponse.format_response(data=self.get_serializer(user).data, success=True, message="User created successfully.")
        return Response(formatted_response, status=status.HTTP_201_CREATED)


    @swagger_auto_schema(
        operation_summary="Retrieve a user",
        operation_description="Retrieves a single user by ID.",
        responses={
            200: openapi.Response(
                description="User retrieved successfully.",
                schema=UserSerializer,
            ),
            404: openapi.Response(
                description="User not found.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(type=openapi.TYPE_STRING, description="Error message."),
                    },
                ),
            ),
            500: openapi.Response(
                description="Internal server error.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(type=openapi.TYPE_STRING, description="Error message."),
                    },
                ),
            ),
        },
        security=[{"Bearer": []}],
        manual_parameters=[
            openapi.Parameter(
                name='pk',
                in_=openapi.IN_PATH,
                type=openapi.TYPE_INTEGER,
                required=True,
                description='ID of the user to retrieve'
            ),
        ]
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a user by ID.
        """
        user_id = kwargs.get('pk')
        audit_logger.info(f"UserViewSet: Retrieving user with ID: {user_id}, User: {request.user.id}")
        
        user = self.get_object()
        
        audit_logger.info(f"UserViewSet: User retrieved successfully. ID: {user_id}")
        
        formatted_response = ApiResponse.format_response(data=self.get_serializer(user).data, success=True, message="User retrieved successfully.")
        return Response(formatted_response, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Update a user",
        operation_description="Updates an existing user record.",
        request_body=UserSerializer,
        responses={
            200: openapi.Response(
                description="User updated successfully.",
                schema=UserSerializer,
            ),
            400: openapi.Response(
                description="Invalid input data.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(type=openapi.TYPE_STRING, description="Error message."),
                    },
                ),
            ),
            404: openapi.Response(
                description="User not found.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(type=openapi.TYPE_STRING, description="Error message."),
                    },
                ),
            ),
            500: openapi.Response(
                description="Internal server error.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(type=openapi.TYPE_STRING, description="Error message."),
                    },
                ),
            ),
        },
        security=[{"Bearer": []}],
        manual_parameters=[
            openapi.Parameter(
                name='pk',
                in_=openapi.IN_PATH,
                type=openapi.TYPE_INTEGER,
                required=True,
                description='ID of the user to update'
            ),
        ]
    )
    def update(self, request, *args, **kwargs):
        """
        Updates an existing user.
        """
        from ....domain.usecase.user_user_case import UpdateUserUseCase
        from ....data.repositories.django_user_repository import DjangoUserRepository
        
        user_repository = DjangoUserRepository()
        update_use_case = UpdateUserUseCase(user_repository)
        

        user_id = kwargs.get('pk')
        audit_logger.info(f"UserViewSet: Updating user with ID: {user_id}, data: {request.data}, User: {request.user.id}")
        instance = self.get_object()
        
        serializer = UserSerializer(instance=instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        user = update_use_case.execute(serializer.validated_data)
        
        audit_logger.info(f"UserViewSet: User updated successfully. ID: {user_id}")
        
        formatted_response = ApiResponse.format_response(data=user, success=True, message="User updated successfully.")
        return Response(formatted_response, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Delete a user",
        operation_description="Deletes a user.",
        responses={
            204: openapi.Response(
                description="User deleted successfully.",
            ),
            404: openapi.Response(
                description="User not found.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(type=openapi.TYPE_STRING, description="Error message."),
                    },
                ),
            ),
            500: openapi.Response(
                description="Internal server error.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(type=openapi.TYPE_STRING, description="Error message."),
                    },
                ),
            ),
        },
        security=[{"Bearer": []}],
        manual_parameters=[
            openapi.Parameter(
                name='pk',
                in_=openapi.IN_PATH,
                type=openapi.TYPE_INTEGER,
                required=True,
                description='ID of the user to delete'
            ),
        ]
    )
    def destroy(self, request, *args, **kwargs):
        """
        Deletes a user.
        """
        user_id = kwargs.get('pk')
        audit_logger.info(f"UserViewSet: Deleting user with ID: {user_id}, User: {request.user.id}")
        
        from ....domain.usecase.user_user_case import DeleteUserUseCase
        from ....data.repositories.django_user_repository import DjangoUserRepository
        
        user_repository = DjangoUserRepository()
        delete_use_case = DeleteUserUseCase(user_repository)

        delete_use_case.execute(user_id)

        audit_logger.info(f"UserViewSet: User deleted successfully. ID: {user_id}")
        
        formatted_response = ApiResponse.format_response(data=None, success=True, message="User deleted successfully.")
        return Response(formatted_response, status=status.HTTP_204_NO_CONTENT)


