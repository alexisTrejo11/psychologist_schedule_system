from django.forms import ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from ..models import Therapist
from ..serializers import TherapistSerializer
from ..services.therapist_service import TherapistService
from rest_framework.permissions import IsAuthenticated


class TherapistViewSet(ModelViewSet):
    queryset = Therapist.objects.all()
    serializer_class = TherapistSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def create(self, request, *args, **kwargs):
        try:
            serializer = TherapistSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            therapist = TherapistService.create_therapist(serializer.validated_data)
            therapist_output = self.get_serializer(therapist).data
            return Response(therapist_output, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"error": e.message}, status=status.HTTP_400_BAD_REQUEST)
