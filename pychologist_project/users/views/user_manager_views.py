from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from ..models import User
from ..serializers import UserSerializer
from ..services.user_services import UserService
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
        audit_logger.info(f"UserViewSet: Creating new user with data: {request.data}, User: {request.user.id}")
        try:
            user_data = request.data
            user = UserService.create_user(user_data)
            serializer = self.get_serializer(user)
            formatted_response = ApiResponse.format_response(data=serializer.data, success=True, message="User created successfully.")
            audit_logger.info(f"UserViewSet: User created successfully. ID: {user.id}")
            return Response(formatted_response, status=status.HTTP_201_CREATED)
        except Exception as e:
            audit_logger.error(f"UserViewSet: Exception: {e}")
            formatted_response = ApiResponse.format_response(data=None, success=False, message=f"Error creating user: {e}")
            return Response(formatted_response, status=status.HTTP_400_BAD_REQUEST)

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
        try:
            user = self.get_object()
            serializer = self.get_serializer(user)
            formatted_response = ApiResponse.format_response(data=serializer.data, success=True, message="User retrieved successfully.")
            audit_logger.info(f"UserViewSet: User retrieved successfully. ID: {user_id}")
            return Response(formatted_response, status=status.HTTP_200_OK)
        except Exception as e:
            audit_logger.error(f"UserViewSet: Exception: {e}")
            formatted_response = ApiResponse.format_response(data=None, success=False, message=f"Error retrieving user: {e}")
            return Response(formatted_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        user_id = kwargs.get('pk')
        audit_logger.info(f"UserViewSet: Updating user with ID: {user_id}, data: {request.data}, User: {request.user.id}")
        try:
            instance = self.get_object() # gets the user instance.
            serializer = UserSerializer(instance=instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            formatted_response = ApiResponse.format_response(data=serializer.data, success=True, message="User updated successfully.")
            audit_logger.info(f"UserViewSet: User updated successfully. ID: {user_id}")
            return Response(formatted_response, status=status.HTTP_200_OK)
        except Exception as e:
            audit_logger.error(f"UserViewSet: Exception: {e}")
            formatted_response = ApiResponse.format_response(data=None, success=False, message=f"Internal server error: {e}")
            return Response(formatted_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            formatted_response = ApiResponse.format_response(data=None, success=True, message="User deleted successfully.")
            audit_logger.info(f"UserViewSet: User deleted successfully. ID: {user_id}")
            return Response(formatted_response, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            audit_logger.error(f"UserViewSet: Exception: {e}")
            formatted_response = ApiResponse.format_response(data=None, success=False, message=f"Internal server error: {e}")
            return Response(formatted_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



from rest_framework.views import APIView
class HomeView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.get_user()
        

