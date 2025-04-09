from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from ....core.domain.entities import UserEntity

class TokenService:
    """
    Service for managing JWT tokens.
    This service provides methods for creating, refreshing, and invalidating tokens.
    """

    def create_tokens(self, user_entity: UserEntity) -> dict:
        """
        Creates access and refresh tokens for a user.

        Args:
            user_entity (UserEntity): The user entity for whom tokens are being created.

        Returns:
            dict: A dictionary containing the access token and refresh token.
        """
        user_model = self._get_user_model(user_entity.id)

        refresh_token = RefreshToken.for_user(user_model)
        access_token = AccessToken.for_user(user_model)

        access_token['user_id'] = user_entity.id
        access_token['email'] = user_entity.email
        access_token['role'] = user_entity.role

        return {
            'refresh_token': str(refresh_token),
            'access_token': str(access_token),
        }

    def invalidate_token(self, refresh_token_str: str) -> None:
        """
        Invalidates a refresh token by adding it to the blacklist.

        Args:
            refresh_token_str (str): The refresh token string to invalidate.
        """
        token = RefreshToken(refresh_token_str)
        token.blacklist()

    def refresh_token(self, refresh_token_str: str, user_repository) -> dict:
        """
        Refreshes an access token using a refresh token.

        Args:
            refresh_token_str (str): The refresh token string.
            user_repository (UserRepository): The user repository to fetch user details.

        Returns:
            dict: A dictionary containing the new access token and refresh token.
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

    def _get_user_model(self, user_id: int):
        """
        Retrieves the Django User model instance for a given user ID.

        Args:
            user_id (int): The ID of the user.

        Returns:
            User: The Django User model instance.
        """
        from users.models import User
        return User.objects.get(id=user_id)