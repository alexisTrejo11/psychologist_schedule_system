from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from core.api_response.response import DjangoResponseWrapper as ResponseWrapper
from core.api_response.response import ApiResponse
from ..serializers.serializers import UserSerializer
from .....models import User
from ....domain.usecase.user_user_case import CreateUserUseCase
from ....data.repositories.django_user_repository import DjangoUserRepository
from ....domain.usecase.user_user_case import UpdateUserUseCase
from ....domain.usecase.user_user_case import DeleteUserUseCase

import logging

audit_logger = logging.getLogger('audit_logger')

class UserViewSet(ModelViewSet):
    """
    ViewSet to manage user data. Accessible to authenticated users with Admin role.
    """
    def __init__(self, **kwargs):
        self.user_repository = DjangoUserRepository()
        self.create_user_use_case = CreateUserUseCase(self.user_repository)
        self.update_user_use_case = UpdateUserUseCase(self.user_repository)
        self.user_delete_use_case = DeleteUserUseCase(self.user_repository)
        super().__init__(**kwargs)

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
        audit_logger.info(f"UserViewSet: Creating new user with data: {request.data}, User: {request.user.id}")
        
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = self.create_user_use_case.execute(serializer.validated_data)
        
        audit_logger.info(f"UserViewSet: User created successfully. ID: {user.id}")
        
        return ResponseWrapper.created(data=self.get_serializer(user).data, entity='User')


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
        user_id = kwargs.get('pk')
        audit_logger.info(f"UserViewSet: Retrieving user with ID: {user_id}, User: {request.user.id}")
        
        user = self.get_object()
        
        audit_logger.info(f"UserViewSet: User retrieved successfully. ID: {user_id}")
        
        return ResponseWrapper.found(
            data=self.get_serializer(user).data,
            entity='User', 
            param='ID',
            value=user_id,
        )

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
        user_id = kwargs.get('pk')
        audit_logger.info(f"UserViewSet: Updating user with ID: {user_id}, data: {request.data}, User: {request.user.id}")
        instance = self.get_object()
        
        serializer = UserSerializer(instance=instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        user = self.update_user_use_case.execute(serializer.validated_data)
        
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
        user_id = kwargs.get('pk')
        audit_logger.info(f"UserViewSet: Deleting user with ID: {user_id}, User: {request.user.id}")
                
        self.user_delete_use_case.execute(user_id)

        audit_logger.info(f"UserViewSet: User deleted successfully. ID: {user_id}")
        
        return ResponseWrapper.no_content(message="User deleted successfully.")

