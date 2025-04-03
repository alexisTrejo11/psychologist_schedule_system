from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from core.api_response.response import ApiResponse
from rest_framework.response import Response
from rest_framework import status

class HomeView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.get_user()
        
        from therapists.serializers import HomeDataSerializer
        from ....data.repositories.django_user_repository import DjangoUserRepository
        from ....domain.usecase.user_user_case import GetUserHomeDataUseCase
        
        user_repository = DjangoUserRepository()
        home_use_case = GetUserHomeDataUseCase(user_repository)
        home_data = home_use_case.execute(user)

        formatted_response = ApiResponse.format_response(
                    data=HomeDataSerializer(home_data).data,
                    success=True,
                    message="User Home Data Successfully Retrieved"
                )

        return Response(formatted_response, status=status.HTTP_200_OK)