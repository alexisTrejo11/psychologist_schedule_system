from ....core.domain.entities import UserEntity
from core.exceptions.custom_exceptions import BusinessLogicError

class SignupUseCase:
    def __init__(self, user_repository, therapist_repository, patient_repository, token_service):
        self.user_repository = user_repository
        self.therapist_repository = therapist_repository
        self.patient_repository = patient_repository
        self.token_service = token_service
    
    def execute(self, data):
        if self.user_repository.exists_by_email(data.get('email')):
            raise BusinessLogicError("El email ya está registrado")
        
        if 'phone' in data and self.user_repository.exists_by_phone(data.get('phone')):
            raise BusinessLogicError("El teléfono ya está registrado")
        
        self._validate_password(data.get('password'))
        
        user_role = data.get('user_role')
        user = None
        
        if user_role == 'admin':
            self._create_user(data, 'ADMIN')
        elif user_role == 'therapist':
            user = self._create_user(data, 'ADMIN')
            # TODO: link user to therapist
            self.therapist_repository.create_therapist(data)

        elif user_role == 'patient':
            # TODO: link user to therapist
            user = self._create_user(data, 'ADMIN')
            self.patient_repository.create(data)
        else:
            raise BusinessLogicError("Invalid User Role")
        
        return self.token_service.create_tokens(user)
    
    def _create_user(self, data, role) -> UserEntity:
        return self.user_repository.create(
            UserEntity(email=data.get('email'), phone=data.get('phone'), role='ADMIN'),
            data.get('password')
        )

    def _validate_password(self, password):
        import re
        password_regex = r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$"
        if not re.match(password_regex, password):
            raise BusinessLogicError(
                "La contraseña debe tener al menos 8 caracteres, incluir al menos una letra y un número."
            )

class LoginUseCase:
    def __init__(self, user_repository, auth_service, token_service):
        self.user_repository = user_repository
        self.auth_service = auth_service
        self.token_service = token_service
    
    def execute(self, data):
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            raise BusinessLogicError("Se requieren email y contraseña.")
        
        user = self.auth_service.authenticate(email, password)
        if not user:
            raise BusinessLogicError("Credenciales inválidas.")
        
        if not user.is_active:
            raise BusinessLogicError("El usuario está inactivo.")
        
        # Actualizar último login
        self.user_repository.update_last_login(user)
        
        # Crear tokens de sesión
        return self.token_service.create_tokens(user)

class LogoutUseCase:
    def __init__(self, token_service):
        self.token_service = token_service
    
    def execute(self, refresh_token):
        try:
            self.token_service.invalidate_token(refresh_token)
        except Exception as e:
            raise BusinessLogicError(f"Error al cerrar sesión: {str(e)}")

class RefreshTokenUseCase:
    def __init__(self, token_service, user_repository):
        self.token_service = token_service
        self.user_repository = user_repository
    
    def execute(self, refresh_token):
        try:
            return self.token_service.refresh_token(refresh_token, self.user_repository)
        except Exception as e:
            raise BusinessLogicError(f"Error al refrescar la sesión: {str(e)}")