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
            therapist_data = request.data
            therapist = TherapistService.create_therapist(therapist_data)
            serializer = self.get_serializer(therapist)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"error": e.message}, status=status.HTTP_400_BAD_REQUEST)
