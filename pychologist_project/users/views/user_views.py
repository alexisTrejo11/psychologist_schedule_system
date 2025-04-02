from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from ..services.user_services import UserService
from ..core.presentation.api.serializers.serializers import UserSerializer, UserProfileSerializer
from therapists.serializers import TherapistHomeDataSerializer
from core.api_response.response import ApiResponse
from rest_framework.response import Response
from rest_framework import status

class HomeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        self.user_service = UserService()
        home_data = self.user_service.get_user_home_data(user)

        formatted_response = ApiResponse.format_response(
            data=TherapistHomeDataSerializer(home_data).data,
            success=True,
            message="User Home Data Successfully Retrieved"
        )

        return Response(formatted_response, status=status.HTTP_200_OK)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
    
        formatted_response = ApiResponse.format_response(
            data=UserSerializer(user).data,
            success=True,
            message="User Profile Successfully Retrieved"
        )

        return Response(formatted_response, status=status.HTTP_200_OK)
    
    def patch(self, request):
        user = request.user
        self.user_service = UserService()
        
        serializer = UserProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        self.user_service.update_profile(serializer.validated_data, user)
        
        formatted_response = ApiResponse.format_response(
            data=None,
            success=True,
            message="User Profile Successfully Updated"
        )

        return Response(formatted_response, status=status.HTTP_200_OK)