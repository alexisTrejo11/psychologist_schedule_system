from users.models import User
from .models import Therapist
from therapy.models import TherapySession
from core.exceptions.custom_exceptions import EntityNotFoundError
from django.utils import timezone
from users.core.presentation.api.serializers.serializers import HomeData

class TherapistService:
    @staticmethod
    def get_unique_patient_count(therapist):
        """Obtiene el conteo de pacientes únicos para un terapeuta."""
        return TherapySession.objects.filter(
            therapist=therapist
        ).values('patients__id').distinct().count()

    @staticmethod
    def get_incoming_session_count(therapist):
        """Obtiene el conteo de sesiones entrantes para un terapeuta."""
        return TherapySession.objects.filter(
            therapist=therapist,
            status='SCHEDULED',
            start_date__lte=timezone.now()
        ).count()

    @staticmethod
    def get_therapist_home_data(user : User):
        therapist = TherapistService.get_therapist_by_user(user)

        try:
            therapist_patient_count = TherapistService.get_unique_patient_count(therapist)
            incoming_session_count = TherapistService.get_incoming_session_count(therapist)
        except Exception as e:
            raise RuntimeError(f"Error al obtener datos del terapeuta: {str(e)}")

        return {
            HomeData(therapist_patient_count, incoming_session_count, therapist.name, therapist.user.profile_picture)
        }


    @staticmethod
    def get_therapist_by_user(user):
        try:
            return Therapist.objects.get(user=user)
        except Therapist.DoesNotExist:
            raise EntityNotFoundError("User", user)

    @staticmethod
    def create_therapist(data):
        """
        Crea un nuevo terapeuta asociado a un usuario.
        """
        therapist = Therapist.objects.create(
            license_number=data.get('license_number'),
            name = data.get('name'),
            specialization=data.get('specialization')
        )

        return therapist