from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from core.api_response.response import DjangoResponseWrapper as ResponseWrapper
from rest_framework import status
from therapists.core.infrastructure.adapters.serializers.serializers import HomeDataSerializer
from ....data.repositories.django_user_repository import DjangoUserRepository
from ....domain.usecase.user_user_case import GetUserHomeDataUseCase
from ..serializers.serializers import UserSerializer, UserProfileSerializer
from ....domain.usecase.user_user_case import UpdateProfileUseCase

class HomeView(APIView):
    def __init__(self, **kwargs):
        self.user_repository = DjangoUserRepository()
        self.home_use_case = GetUserHomeDataUseCase(self.user_repository)
        super().__init__(**kwargs)

    permission_classes = [IsAuthenticated]


    def get(self, request):
        user = request.get_user()
                        
        home_data = self.home_use_case.execute(user)

        return ResponseWrapper(HomeDataSerializer(home_data).data, status=status.HTTP_200_OK)
    
class ProfileView(APIView):
    def __init__(self, **kwargs):
        self.user_repository = DjangoUserRepository()
        self.use_case = UpdateProfileUseCase(self.user_repository)
        super().__init__(**kwargs)
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
    
        return ResponseWrapper.found(data=UserSerializer(user).data, entity='User Profile')
    
    def patch(self, request):
        user = request.user

        
        serializer = UserProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        self.use_case.execute(serializer.validated_data, user)
        
        return ResponseWrapper.updated(entity='User Profile')
