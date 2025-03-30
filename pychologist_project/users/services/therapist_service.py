from ..models import Patient, Therapist
from ..models import Therapist
from .user_services import UserService


class TherapistService:
    @staticmethod
    def create_therapist(data):
        """
        Crea un nuevo terapeuta asociado a un usuario.
        """
        user_data = data.pop('user', None)
        if not user_data:
            raise ValueError("Los datos del usuario son obligatorios")

        user_service = UserService()
        user = user_service.create_user(user_data)

        therapist = Therapist.objects.create(
            user=user,
            license_number=data.get('license_number'),
            specialization=data.get('specialization')
        )
        return therapist