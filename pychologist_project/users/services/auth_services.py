from .user_services import UserService
from therapists.services import TherapistService
from patients.services import PatientService
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from django.contrib.auth import authenticate

class AuthService:
    def __init__(self):
        self.user_service = UserService()
        self.therapist_service = TherapistService()
        self.patient_service = PatientService()
        
    def validate_singup_credentials(self, data):
        self.user_service.validate_unique_user_credentials(data)

    def process_signup(self, data):
        user_role = data.get('user_role')
        user = None
        match user_role:
            case 'admin':
                user = self.user_service.create_user(data)
            case 'therapist':
                user = self.therapist_service.create_therapist(data)
            case 'patient':
                user = self.patient_service.create_patient(data)
            case _:
                raise ValueError("Invalid User Role")

        session = self.__create_session(user) 
        return session


    def validate_login_credentials(self, data):
        """
        Valida las credenciales del usuario.
        """
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            raise ValueError("Se requieren email y contraseña.")

        user = authenticate(email=email, password=password)
        if not user:
            raise ValueError("Credenciales inválidas.")

        if not user.is_active:
            raise ValueError("El usuario está inactivo.")

        return user
    

    def process_login(self, user):
        session = self.__create_session(user) 
        self.user_service.update_last_login(user)
        return session


    def logout(self, refresh_token):
        """
        Cierra la sesión invalidando el refresh token.
        """
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            raise ValueError(f"Error al cerrar sesión: {str(e)}")
        

    def refresh_session(self, refresh_token):
        """
        Refresca la sesión generando un nuevo access token.
        """
        try:
            refresh = RefreshToken(refresh_token)
            new_access_token = refresh.access_token

            user_id = refresh.payload.get('user_id')
            user = self.user_service.get_user_by_id(user_id)
            new_access_token['user_id'] = user.id
            new_access_token['email'] = user.email
            new_access_token['role'] = user.role

            return {
                'refresh_token' : refresh_token,
                'access_token': str(new_access_token),
            }
        except Exception as e:
            raise ValueError(f"Error al refrescar la sesión: {str(e)}")
    

    def __create_session(self, user) -> dict:
        refresh_token = RefreshToken.for_user(user)
        access_token = AccessToken.for_user(user)

        access_token['user_id'] = user.id
        access_token['email'] = user.email
        access_token['role'] = user.role

        return {
            'refresh_token': str(refresh_token),
            'access_token': str(access_token),
        }
    
