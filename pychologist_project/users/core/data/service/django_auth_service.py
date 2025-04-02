from django.contrib.auth import authenticate

class DjangoAuthService:
    def authenticate(self, email, password):
        """
        Autentica a un usuario usando Django
        """
        user = authenticate(email=email, password=password)
        
        if not user:
            return None
        
        from ...domain.entities import UserEntity
        return UserEntity(
            id=user.id,
            email=user.email,
            phone=user.phone,
            role=user.role,
            is_active=user.is_active,
            profile_picture=user.profile_picture,
            name=getattr(user, 'name', None)
        )