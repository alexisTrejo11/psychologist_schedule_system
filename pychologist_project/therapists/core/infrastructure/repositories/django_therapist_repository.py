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


    def get_by_id(self, therapist_id) -> TherapistEntity:
        therapist_cache_key = self.cache_manager.get_cache_key(therapist_id)

        therapist_cache = self.cache_manager.get(therapist_cache_key)
        if therapist_cache:
            return therapist_cache

        try:
            therapist = Therapist.objects.get(id=therapist_id)

            self.cache_manager.set(therapist_cache_key, therapist)
            
            return self._map_to_entity(therapist)
        except Therapist.DoesNotExist:
            raise EntityNotFoundError('Therapist')


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

    def create(self, new_therapist: TherapistEntity) -> TherapistEntity:
        """
        Creates a new therapist in the database and updates the provided TherapistEntity with database-generated fields.
        """
        therapist_model = Therapist.objects.create(
            user_id= new_therapist.user_id,
            name=new_therapist.name,
            license_number=new_therapist.license_number,
            specialization=new_therapist.specialization
        )

        new_therapist.id = therapist_model.id
        new_therapist.created_at = therapist_model.created_at
        new_therapist.updated_at = therapist_model.updated_at

        cache_key = self.cache_manager.get_cache_key(new_therapist.id)
        try:
            self.cache_manager.set(cache_key, new_therapist)
        except Exception as e:
            print(f"Cache set failed: {e}")

        return new_therapist

    def update(self, therapist_data: dict, existing_therapist: TherapistEntity) -> TherapistEntity:
        """
        Updates an existing therapist in the database and refreshes the cache.
        """
        if 'name' in therapist_data:
            existing_therapist.name = therapist_data['name']
        if 'license_number' in therapist_data:
            existing_therapist.license_number = therapist_data['license_number']
        if 'specialization' in therapist_data:
            existing_therapist.specialization = therapist_data['specialization']

        # Save the updated therapist to the database
        therapist_model = self._get_by_id(existing_therapist.id)
        therapist_model.name = existing_therapist.name
        therapist_model.license_number = existing_therapist.license_number
        therapist_model.specialization = existing_therapist.specialization
        therapist_model.save()

        updated_entity = self._map_to_entity(therapist_model)

        cache_key = self.cache_manager.get_cache_key(updated_entity.id)
        try:
            self.cache_manager.set(cache_key, updated_entity)
        except Exception as e:
            print(f"Cache set failed: {e}")

        return updated_entity

    def delete(self, therapist_id: int) -> None:
        """
        Deletes a therapist from the database and removes them from the cache.

        Args:
            therapist_id (int): The ID of the therapist to delete.

        Raises:
            EntityNotFoundError: If no therapist is found with the given ID.
        """
        therapist = self._get_by_id(therapist_id)

        therapist.delete()

        cache_key = self.cache_manager.get_cache_key(therapist_id)
        self.cache_manager.delete(cache_key)

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
    
    def _get_by_id(self, therapist_id):
        try:
            return Therapist.objects.get(id=therapist_id)
        except Therapist.DoesNotExist:
            raise EntityNotFoundError("Therapist", therapist_id)