from django.core.exceptions import ValidationError
from ..models import User
from therapists.services import TherapistService
from django.utils import timezone
import re
from ..core.presentation.api.serializers.serializers import HomeData
from core.exceptions.custom_exceptions import InvalidOperationError

class UserService:
    def __init__(self):
        self.user_model = User

    def get_user_by_id(self, user_id):
        user = self.user_model.objects.filter(id=user_id).first()

        return user
    
    def get_user_home_data(self, user: User):
        if user.role == 'ADMIN':
            return HomeData(0, 0, "ADMIN", "")
        elif user.role == 'THERAPIST':
            return TherapistService.get_therapist_home_data(user)
        else:
            raise ValueError('Not Supported Yet')
        
    def update_profile(self, data, user : User) -> None:
        email = data.get('email')
        if email:
            self.__validate_unique_email(email)
            user.email = email

        phone = data.get('phone')
        if phone:
            self.__validate_unique_phone(phone)
            user.phone = phone

        name = data.get('name')
        if name:
            user.set_name(name)

        profile_picture = data.get('profile_picture')
        if profile_picture:
            user.profile_picture = profile_picture

        user.save()

        
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

    def __validate_unique_phone(self, phone):
        """
        Validar que el numero telefonico no esté siendo usado por otro usuario.
        """
        if User.objects.filter(phone=phone).exists():
            raise InvalidOperationError("Este telefono ya está en uso.")
        
    def __validate_unique_email(self, email):
        """
        Validar que el numero telefonico no esté siendo usado por otro usuario.
        """
        if User.objects.filter(email=email).exists():
            raise InvalidOperationError("Este email ya está en uso.")

    def __validate_password(self, password):
        password_regex = r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$"
        if not re.match(password_regex, password):
            raise ValueError(
                "La contraseña debe tener al menos 8 caracteres, incluir al menos una letra y un número."
            )
