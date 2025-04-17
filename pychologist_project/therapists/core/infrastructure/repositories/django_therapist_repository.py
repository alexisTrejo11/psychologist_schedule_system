from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from ...application.domain.entities.therapist import TherapistEntity
from therapists.models import Therapist
from therapy.models import TherapySession
from ...application.domain.repositories.therapist_repository import TherapistRepository
from core.exceptions.custom_exceptions import EntityNotFoundError
from core.cache.cache_manager import CacheManager

CACHE_PREFIX = "therapist_"
CACHE_TTL = 3600

class DjangoTherapistRepository(TherapistRepository):
    def __init__(self, cache_manager: CacheManager = None):
        self.cache_manager = cache_manager or CacheManager(CACHE_PREFIX)
        self.cache_ttl = CACHE_TTL

    def get_by_id(self, therapist_id: int) -> TherapistEntity:
        cache_key = f"{CACHE_PREFIX}id_{therapist_id}"
        if cached := self.cache_manager.get(cache_key):
            return cached
            
        therapist = Therapist.objects.get(id=therapist_id)
        entity = self._map_to_entity(therapist)
        self.cache_manager.set(cache_key, entity, self.cache_ttl)
        return entity

    def get_by_user_id(self, user_id: int) -> TherapistEntity:
        cache_key = f"{CACHE_PREFIX}user_{user_id}"
        if cached := self.cache_manager.get(cache_key):
            return cached
            
        therapist = Therapist.objects.get(user_id=user_id)
        entity = self._map_to_entity(therapist)
        self.cache_manager.set_multi({
            f"{CACHE_PREFIX}id_{therapist.id}": entity,
            cache_key: entity
        }, self.cache_ttl)
        return entity

    def save(self, therapist: TherapistEntity) -> TherapistEntity:
        if therapist.id:
            return self._update(therapist)
        return self._create(therapist)

    def _create(self, therapist: TherapistEntity) -> TherapistEntity:
        therapist_model = Therapist.objects.create(
            user_id=therapist.user_id,
            name=therapist.name,
            license_number=therapist.license_number,
            specialization=therapist.specialization
        )
        entity = self._map_to_entity(therapist_model)
        self._update_cache(entity)
        return entity

    def _update(self, therapist: TherapistEntity) -> TherapistEntity:
        therapist_model = Therapist.objects.get(id=therapist.id)
        therapist_model.name = therapist.name
        therapist_model.license_number = therapist.license_number
        therapist_model.specialization = therapist.specialization
        therapist_model.save()
        entity = self._map_to_entity(therapist_model)
        self._update_cache(entity)
        return entity

    def get_unique_patient_count(self, therapist_id: int) -> int:
        cache_key = f"unique_patients_{therapist_id}"
        if count := self.cache_manager.get(cache_key):
            return count
            
        count = TherapySession.objects.filter(
            therapist_id=therapist_id
        ).values('patient_id').distinct().count()
        self.cache_manager.set(cache_key, count, self.cache_ttl)
        return count

    def get_incoming_session_count(self, therapist_id: int) -> int:
        cache_key = f"incoming_sessions_{therapist_id}"
        if count := self.cache_manager.get(cache_key):
            return count
            
        count = TherapySession.objects.filter(
            therapist_id=therapist_id,
            status='SCHEDULED',
            start_date__gte=timezone.now()
        ).count()
        self.cache_manager.set(cache_key, count, self.cache_ttl)
        return count

    def delete(self, therapist_id: int) -> None:
        therapist = Therapist.objects.get(id=therapist_id)
        user_id = therapist.user_id
        therapist.delete()
        self.cache_manager.delete_multi([
            f"{CACHE_PREFIX}id_{therapist_id}",
            f"{CACHE_PREFIX}user_{user_id}"
        ])

    def _map_to_entity(self, model: Therapist) -> TherapistEntity:
        return TherapistEntity(
            id=model.id,
            user_id=model.user_id,
            name=model.name,
            license_number=model.license_number,
            specialization=model.specialization,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def _update_cache(self, entity: TherapistEntity) -> None:
        self.cache_manager.set_multi({
            f"{CACHE_PREFIX}id_{entity.id}": entity,
            f"{CACHE_PREFIX}user_{entity.user_id}": entity
        }, self.cache_ttl)