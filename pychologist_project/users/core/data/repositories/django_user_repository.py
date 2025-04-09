from django.utils import timezone
from ....core.domain.repositories import UserRepository
from ....core.domain.entities import UserEntity
from users.models import User
from core.cache.cache_manager import CacheManager
from typing import Optional

CACHE_PREFIX = "user_"

class DjangoUserRepository(UserRepository):
    """
    Repository implementation for managing User entities using Django ORM.
    This repository handles CRUD operations for users and integrates caching 
    to optimize performance.
    """

    def __init__(self):
        """
        Initializes the repository with a CacheManager instance.
        """
        self.cache_manager = CacheManager(CACHE_PREFIX)

    def get_by_id(self, user_id: int) -> Optional[UserEntity]:
        """
        Retrieves a user by their ID.
        If the user exists in the cache, it is returned directly.
        Otherwise, the user is fetched from the database and cached.

        Args:
            user_id (int): The ID of the user.

        Returns:
            Optional[UserEntity]: The user entity if found, otherwise None.
        """
        cache_key = self.cache_manager.get_cache_key(user_id)

        cached_user = self.cache_manager.get(cache_key)
        if cached_user:
            return cached_user

        user = User.objects.filter(id=user_id).first()
        if not user:
            return None

        user_entity = self._map_to_entity(user)
        self.cache_manager.set(cache_key, user_entity)
        return user_entity

    def get_by_email(self, email: str) -> Optional[UserEntity]:
        """
        Retrieves a user by their email.
        If the user exists in the cache, it is returned directly.
        Otherwise, the user is fetched from the database and cached.

        Args:
            email (str): The email of the user.

        Returns:
            Optional[UserEntity]: The user entity if found, otherwise None.
        """
        cache_key = f"user_email_{email}"

        cached_user = self.cache_manager.get(cache_key)
        if cached_user:
            return cached_user

        user = User.objects.filter(email=email).first()
        if not user:
            return None

        user_entity = self._map_to_entity(user)
        self.cache_manager.set(cache_key, user_entity)
        return user_entity

    def create(self, user_entity: UserEntity, password: str) -> UserEntity:
        """
        Creates a new user in the database and caches the result.

        Args:
            user_entity (UserEntity): The user entity containing the user's data.
            password (str): The user's password.

        Returns:
            UserEntity: The newly created user entity.
        """
        user = User.objects.create_user(
            email=user_entity.email,
            role=user_entity.role,
            phone=user_entity.phone or ''
        )

        user.set_password(password)
        user.save()

        user_entity = self._map_to_entity(user)
        cache_key = self.cache_manager.get_cache_key(user_entity.id)
        self.cache_manager.set(cache_key, user_entity)

        return user_entity

    def update(self, user_entity: UserEntity) -> UserEntity:
        """
        Updates an existing user in the database and refreshes the cache.

        Args:
            user_entity (UserEntity): The updated user entity.

        Returns:
            UserEntity: The updated user entity.
        """
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

        user_entity = self._map_to_entity(user)
        cache_key = self.cache_manager.get_cache_key(user_entity.id)
        self.cache_manager.set(cache_key, user_entity)

        return user_entity

    def update_last_login(self, user_entity: UserEntity) -> None:
        """
        Updates the last login timestamp for a user.

        Args:
            user_entity (UserEntity): The user entity to update.
        """
        user = User.objects.get(id=user_entity.id)

        user.last_login = timezone.now()
        user.is_active = True
        user.save(update_fields=['last_login', 'is_active'])

        cache_key = self.cache_manager.get_cache_key(user_entity.id)
        self.cache_manager.delete(cache_key)

    def exists_by_email(self, email: str) -> bool:
        """
        Checks if a user with the given email exists.

        Args:
            email (str): The email to check.

        Returns:
            bool: True if a user with the given email exists, False otherwise.
        """
        return User.objects.filter(email=email).exists()

    def exists_by_phone(self, phone: str) -> bool:
        """
        Checks if a user with the given phone number exists.

        Args:
            phone (str): The phone number to check.

        Returns:
            bool: True if a user with the given phone number exists, False otherwise.
        """
        return User.objects.filter(phone=phone).exists()

    def _map_to_entity(self, user_model: User) -> UserEntity:
        """
        Maps a User model instance to a UserEntity.

        Args:
            user_model (User): The User model instance.

        Returns:
            UserEntity: The mapped user entity.
        """
        return UserEntity(
            id=user_model.id,
            email=user_model.email,
            phone=user_model.phone,
            role=user_model.role,
            is_active=user_model.is_active,
            profile_picture=user_model.profile_picture,
            name=getattr(user_model, 'name', None)
        )
