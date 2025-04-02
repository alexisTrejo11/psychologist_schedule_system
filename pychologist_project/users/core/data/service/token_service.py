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