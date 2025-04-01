from ..models import Patient, Therapist
from ..models import Therapist
from .user_services import UserService


class TherapistService:
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

        user_data = data.pop('user', None)
        if user_data:
            user_service = UserService()
            user = user_service.create_user(user_data)
            therapist.user = user
        return therapist