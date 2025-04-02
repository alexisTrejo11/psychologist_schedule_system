from django.utils import timezone
from ....core.domain.repositories import UserRepository
from ....core.domain.entities import UserEntity
from users.models import User

class DjangoUserRepository(UserRepository):
    def get_by_id(self, user_id):
        user = User.objects.filter(id=user_id).first()
        if not user:
            return None
        
        return self._map_to_entity(user)
    
    def get_by_email(self, email):
        user = User.objects.filter(email=email).first()
        if not user:
            return None
        
        return self._map_to_entity(user)
    
    def create(self, user_entity, password):
        user = User.objects.create_user(
            email=user_entity.email,
            role=user_entity.role,
            phone=user_entity.phone or ''
        )
        
        user.set_password(password)
        user.save()
        
        return self._map_to_entity(user)
    
    def update(self, user_entity):
        user = User.objects.get(id=user_entity.id)
        
        if user_entity.email:
            user.email = user_entity.email
        
        if user_entity.phone:
            user.phone = user_entity.phone
        
        if user_entity.name:
            user.set_name(user_entity.name)
        
        if user_entity.profile_picture:
            user.profile_picture = user_entity.profile_picture
        
        if user_entity.is_active is not None:
            user.is_active = user_entity.is_active
        
        user.save()
        
        return self._map_to_entity(user)
    
    def update_last_login(self, user_entity):
        user = User.objects.get(id=user_entity.id)
        user.last_login = timezone.now()
        user.is_active = True
        user.save(update_fields=['last_login', 'is_active'])
    
    def exists_by_email(self, email):
        return User.objects.filter(email=email).exists()
    
    def exists_by_phone(self, phone):
        return User.objects.filter(phone=phone).exists()
    
    def _map_to_entity(self, user_model):
        return UserEntity(
            id=user_model.id,
            email=user_model.email,
            phone=user_model.phone,
            role=user_model.role,
            is_active=user_model.is_active,
            profile_picture=user_model.profile_picture,
            name=getattr(user_model, 'name', None)
        )

# core/data/services/token_service.py
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

class TokenService:
    def create_tokens(self, user_entity):
        """
        Crea tokens JWT para un usuario
        """
        user_model = self._get_user_model(user_entity.id)
        
        refresh_token = RefreshToken.for_user(user_model)
        access_token = AccessToken.for_user(user_model)
        
        # Añadir claims personalizados
        access_token['user_id'] = user_entity.id
        access_token['email'] = user_entity.email
        access_token['role'] = user_entity.role
        
        return {
            'refresh_token': str(refresh_token),
            'access_token': str(access_token),
        }
    
    def invalidate_token(self, refresh_token_str):
        """
        Invalida un token de refresco
        """
        token = RefreshToken(refresh_token_str)
        token.blacklist()
    
    def refresh_token(self, refresh_token_str, user_repository):
        """
        Refresca un token de acceso
        """
        refresh = RefreshToken(refresh_token_str)
        new_access_token = refresh.access_token
        
        user_id = refresh.payload.get('user_id')
        user = user_repository.get_by_id(user_id)
        
        new_access_token['user_id'] = user.id
        new_access_token['email'] = user.email
        new_access_token['role'] = user.role
        
        return {
            'refresh_token': refresh_token_str,
            'access_token': str(new_access_token),
        }
    
    def _get_user_model(self, user_id):
        """
        Obtiene el modelo de usuario de Django a partir de un ID
        """
        from users.models import User
        return User.objects.get(id=user_id)

