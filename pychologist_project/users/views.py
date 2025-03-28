from django.forms import ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import User, Patient, Therapist
from .serializers import UserSerializer, PatientSerializer, TherapistSerializer, SignupSerializer, LoginSerializer
from .services.services import UserService, PatientService, TherapistService
from .services.auth_services import AuthService
from rest_framework.views import APIView

class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        self.auth_service = AuthService()

        self.auth_service.validate_singup_credentials(serializer.validated_data)
        
        session = self.auth_service.procces_signup(serializer.validated_data)
        return Response(session, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        self.auth_service = AuthService()

        user = self.auth_service.validate_login_credentials(serializer.validated_data)
        session = self.auth_service.procces_login(user)
        
        return Response(session, status=status.HTTP_201_CREATED)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            user_data = request.data
            user = UserService.create_user(user_data) 
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PatientViewSet(ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            patient_data = request.data
            patient = PatientService.create_patient(patient_data)
            serializer = self.get_serializer(patient)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"error": e.message}, status=status.HTTP_400_BAD_REQUEST)

class TherapistViewSet(ModelViewSet):
    queryset = Therapist.objects.all()
    serializer_class = TherapistSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            therapist_data = request.data
            therapist = TherapistService.create_therapist(therapist_data)  # Servicio personalizado
            serializer = self.get_serializer(therapist)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"error": e.message}, status=status.HTTP_400_BAD_REQUEST)
