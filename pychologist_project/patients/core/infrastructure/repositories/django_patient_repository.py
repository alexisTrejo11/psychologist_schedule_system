from typing import List, Dict, Optional, Any
from datetime import datetime
from django.db.models import Q
from ...application.domain.entities.patient_entitiy import Patient as PatientEntity
from ...application.domain.repository.patient_repository import PatientRepository
from ....models import Patient as PatientModel
from core.cache.cache_manager import CacheManager

CACHE_PREFIX = 'patient_'

class DjangoPatientRepository(PatientRepository):
    """Patient repository implementation using Django ORM."""
    def __init__(self):
        self.cache_manager = CacheManager(CACHE_PREFIX)
        super().__init__()

    def get_by_id(self, patient_id: int) -> PatientEntity:
        cache_key = self.cache_manager.get_cache_key(patient_id)

        cached_patient = self.cache_manager.get(cache_key)
        if cached_patient:
            return cached_patient

        try:
            patient_model = PatientModel.objects.get(id=patient_id, deleted_at__isnull=True)
            patient_entity = self._to_entity(patient_model)

            self.cache_manager.set(cache_key, patient_entity)
            return patient_entity
        except PatientModel.DoesNotExist:
            raise ValueError(f"Patient with ID {patient_id} not found.")

    def search(self, filters: Optional[Dict[str, Any]] = None) -> List[PatientEntity]:
        cache_key = self.cache_manager.generate_search_key(filters)

        cached_patients = self.cache_manager.get(cache_key)
        if cached_patients:
            return cached_patients

        queryset = PatientModel.objects.filter(deleted_at__isnull=True)

        if not filters:
            patients = [self._to_entity(model) for model in queryset]
            self.cache_manager.set(cache_key, patients)
            return patients

        if 'name' in filters:
            queryset = queryset.filter(name__icontains=filters['name'])

        if 'description' in filters:
            queryset = queryset.filter(description__icontains=filters['description'])

        if 'is_active' in filters:
            queryset = queryset.filter(is_active=filters['is_active'])

        if 'created_after' in filters:
            try:
                created_after = datetime.strptime(filters['created_after'], '%Y-%m-%d')
                queryset = queryset.filter(created_at__gte=created_after)
            except ValueError:
                raise ValueError("The format of 'created_after' must be 'YYYY-MM-DD'.")

        if 'created_before' in filters:
            try:
                created_before = datetime.strptime(filters['created_before'], '%Y-%m-%d')
                queryset = queryset.filter(created_at__lte=created_before)
            except ValueError:
                raise ValueError("The format of 'created_before' must be 'YYYY-MM-DD'.")

        if 'first_therapy_after' in filters:
            try:
                first_therapy_after = datetime.strptime(filters['first_therapy_after'], '%Y-%m-%d')
                queryset = queryset.filter(first_therapy__gte=first_therapy_after)
            except ValueError:
                raise ValueError("The format of 'first_therapy_after' must be 'YYYY-MM-DD'.")

        if 'last_therapy_before' in filters:
            try:
                last_therapy_before = datetime.strptime(filters['last_therapy_before'], '%Y-%m-%d')
                queryset = queryset.filter(last_therapy__lte=last_therapy_before)
            except ValueError:
                raise ValueError("The format of 'last_therapy_before' must be 'YYYY-MM-DD'.")

        if 'search_term' in filters:
            search_term = filters['search_term']
            queryset = queryset.filter(
                Q(name__icontains=search_term) |
                Q(description__icontains=search_term)
            )

        patients = [self._to_entity(model) for model in queryset]

        self.cache_manager.set(cache_key, patients)
        return patients

    def create(self, patient: PatientEntity) -> PatientEntity:
        model = self._to_model(patient)
        model.save()

        entity = self._to_entity(model)

        cache_key = self.cache_manager.get_cache_key(entity.id)
        self.cache_manager.set(cache_key, entity)

        return entity

    def update(self, patient: PatientEntity) -> PatientEntity:
        model = self._to_model(patient)
        model.save()

        entity = self._to_entity(model)

        cache_key = self.cache_manager.get_cache_key(entity.id)
        self.cache_manager.set(cache_key, entity)

        return entity

    def delete(self, patient_id: int) -> None:
        patient = self.get_by_id(patient_id)
        patient.set_as_deleted()
        self.update(patient)

        cache_key = self.cache_manager.get_cache_key(patient_id)
        self.cache_manager.delete(cache_key)

    def deactivate(self, patient_id: int) -> None:
        patient = self.get_by_id(patient_id)
        patient.set_as_inactive()
        self.update(patient)

    def activate(self, patient_id: int) -> None:
        patient = self.get_by_id(patient_id)
        patient.activate()
        self.update(patient)

    def _to_entity(self, model: PatientModel) -> PatientEntity:
        """Converts a Django model to a domain entity."""
        return PatientEntity(
            id=model.id,
            name=model.name,
            description=model.description,
            first_therapy=model.first_therapy,
            last_therapy=model.last_therapy,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
            user_id=model.user_id if hasattr(model, 'user_id') else None
        )

    def _to_model(self, entity: PatientEntity) -> PatientModel:
        """Converts a domain entity to a Django model."""
        if entity.id:
            try:
                model = PatientModel.objects.get(id=entity.id)
                model.name = entity.name
                model.description = entity.description
                model.first_therapy = entity.first_therapy
                model.last_therapy = entity.last_therapy
                model.is_active = entity.is_active
                model.deleted_at = entity.deleted_at
                return model
            except PatientModel.DoesNotExist:
                pass

        return PatientModel(
            name=entity.name,
            description=entity.description,
            first_therapy=entity.first_therapy,
            last_therapy=entity.last_therapy,
            is_active=entity.is_active,
            deleted_at=entity.deleted_at,
            user_id=entity.user_id
        )