from django.utils import timezone
from ...application.domain.entities.therapist import TherapistEntity
from users.models import User
from therapists.models import Therapist
from therapy.models import TherapySession
from ...application.domain.repositories.therapist_repository import TherapistRepository
from core.exceptions.custom_exceptions import EntityNotFoundError
from core.cache.cache_manager import CacheManager

CACHE_PREFIX = "therapist_"

class DjangoTherapistRepository(TherapistRepository):
    """
    Repository implementation for managing Therapist entities using Django ORM.
    This repository handles CRUD operations for therapists and integrates caching 
    to optimize performance.
    """
    def __init__(self):
        """
        Initializes the repository with a CacheManager instance.
        """
        self.cache_manager = CacheManager(CACHE_PREFIX)
        super().__init__()

    def get_by_user_id(self, user_id: int) -> TherapistEntity:
        """
        Retrieves a therapist by their associated user ID.
        If the therapist exists in the cache, it is returned directly.
        Otherwise, the therapist is fetched from the database and cached.

        Args:
            user_id (int): The ID of the user associated with the therapist.

        Returns:
            TherapistEntity: The therapist entity.

        Raises:
            EntityNotFoundError: If no therapist is found for the given user ID.
        """
        cache_key = self.cache_manager.get_cache_key(user_id)

        cached_therapist = self.cache_manager.get(cache_key)
        if cached_therapist:
            return cached_therapist

        try:

            therapist_model = Therapist.objects.get(user_id=user_id)
            therapist_entity = self._map_to_entity(therapist_model)


            self.cache_manager.set(cache_key, therapist_entity)
            return therapist_entity
        except Therapist.DoesNotExist:
            raise EntityNotFoundError("Therapist", user_id)

    def get_unique_patient_count(self, therapist_id: int) -> int:
        """
        Retrieves the count of unique patients associated with a therapist.

        Args:
            therapist_id (int): The ID of the therapist.

        Returns:
            int: The count of unique patients.
        """
        cache_key = f"unique_patient_count_{therapist_id}"

        cached_count = self.cache_manager.get(cache_key)
        if cached_count is not None:
            return cached_count

        count = TherapySession.objects.filter(
            therapist_id=therapist_id
        ).values('patients__id').distinct().count()

        self.cache_manager.set(cache_key, count)
        return count

    def get_incoming_session_count(self, therapist_id: int) -> int:
        """
        Retrieves the count of incoming sessions for a therapist.

        Args:
            therapist_id (int): The ID of the therapist.

        Returns:
            int: The count of incoming sessions.
        """
        cache_key = f"incoming_session_count_{therapist_id}"

        cached_count = self.cache_manager.get(cache_key)
        if cached_count is not None:
            return cached_count

        count = TherapySession.objects.filter(
            therapist_id=therapist_id,
            status='SCHEDULED',
            start_date__lte=timezone.now()
        ).count()

        self.cache_manager.set(cache_key, count)
        return count

    def create(self, therapist_data: dict) -> TherapistEntity:
        """
        Creates a new therapist in the database and caches the result.

        Args:
            therapist_data (dict): A dictionary containing therapist data:
                - user_id (int): The ID of the associated user.
                - name (str): The therapist's name.
                - license_number (str): The therapist's license number.
                - specialization (str): The therapist's specialization.

        Returns:
            TherapistEntity: The newly created therapist entity.
        """
        therapist_model = Therapist.objects.create(
            user_id=therapist_data.get('user_id'),
            name=therapist_data.get('name', ''),
            license_number=therapist_data.get('license_number'),
            specialization=therapist_data.get('specialization')
        )

        therapist_entity = self._map_to_entity(therapist_model)

        cache_key = self.cache_manager.get_cache_key(therapist_entity.id)
        self.cache_manager.set(cache_key, therapist_entity)

        return therapist_entity

    def update(self, therapist_data: dict, therapist: Therapist) -> TherapistEntity:
        """
        Updates an existing therapist in the database and refreshes the cache.

        Args:
            therapist_data (dict): A dictionary containing updated therapist data:
                - name (str, optional): The updated name.
                - license_number (str, optional): The updated license number.
                - specialization (str, optional): The updated specialization.
            therapist (Therapist): The therapist model instance to update.

        Returns:
            TherapistEntity: The updated therapist entity.
        """
        if 'name' in therapist_data:
            therapist.name = therapist_data['name']
        if 'license_number' in therapist_data:
            therapist.license_number = therapist_data['license_number']
        if 'specialization' in therapist_data:
            therapist.specialization = therapist_data['specialization']

        therapist.save()

        therapist_entity = self._map_to_entity(therapist)

        cache_key = self.cache_manager.get_cache_key(therapist_entity.id)
        self.cache_manager.set(cache_key, therapist_entity)

        return therapist_entity

    def delete(self, therapist_id: int) -> None:
        """
        Deletes a therapist from the database and removes them from the cache.

        Args:
            therapist_id (int): The ID of the therapist to delete.

        Raises:
            EntityNotFoundError: If no therapist is found with the given ID.
        """
        try:

            therapist = Therapist.objects.get(id=therapist_id)

            therapist.delete()

            cache_key = self.cache_manager.get_cache_key(therapist_id)
            self.cache_manager.delete(cache_key)
        except Therapist.DoesNotExist:
            raise EntityNotFoundError("Therapist", therapist_id)

    def _map_to_entity(self, model: Therapist) -> TherapistEntity:
        """
        Maps a Therapist model instance to a TherapistEntity.

        Args:
            model (Therapist): The Therapist model instance.

        Returns:
            TherapistEntity: The mapped therapist entity.
        """
        return TherapistEntity(
            id=model.id,
            user_id=model.user_id,
            name=model.name,
            license_number=model.license_number,
            specialization=model.specialization,
            created_at=model.created_at,
            updated_at=model.updated_at
        )