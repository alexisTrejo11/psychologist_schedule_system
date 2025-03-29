from django.core.exceptions import ValidationError
from ..models import User, Patient, Therapist
from ..models import Therapist
from django.utils import timezone
import re

class UserService:
    def __init__(self):
        self.user_model = User

    def get_user_by_id(self, user_id):
        user = self.user_model.objects.filter(id=user_id).first()

        return user

    def create_user(self, data):
        """
        Crea un nuevo usuario después de validar los datos.
        """
        self.__validate_password(data.get('password'))
        user = self.__generate_user(data)
        user.save()

        return user
    
    def update_last_login(self, user: User):
        user.last_login = timezone.now()  
        user.is_active = True
        user.save(update_fields=['last_login', 'is_active'])


    def validate_unique_user_credentials(self, data):
        """
        Valida que el email y el teléfono sean únicos.
        """
        if self.user_model.objects.filter(email=data['email']).exists():
            raise ValidationError("El email ya está registrado")
        
        if 'phone' in data and self.user_model.objects.filter(phone=data['phone']).exists():
            raise ValidationError("El teléfono ya está registrado")

    def __generate_user(self, data):
        """
        Genera una instancia de User con los datos proporcionados.
        """
        user = self.user_model.objects.create_user(
            email=data['email'],
            role=data.get('role', 'PATIENT'),
            phone=data.get('phone', '')
        )

        user.set_password(data['password'])
        return user


    def __validate_password(self, password):
        password_regex = r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$"
        if not re.match(password_regex, password):
            raise ValueError(
                "La contraseña debe tener al menos 8 caracteres, incluir al menos una letra y un número."
            )
    
class PatientService:
    @staticmethod
    def create_patient(data):
        """
        Crea un nuevo paciente asociado a un usuario.
        """
        user_data = data.pop('user', None)
        if not user_data:
            raise ValueError("Los datos del usuario son obligatorios")

        user_service = UserService()
        user = user_service.create_user(user_data)

        patient = Patient.objects.create(
            user=user,
            name=data.get('name', ''),
            description=data.get('description', '')
        )
        return patient


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