from typing import List, Dict, Optional, Any
from datetime import datetime
from django.db.models import Q
from ...application.domain.entities.patient_entitiy import Patient as PatientEntity
from ...application.domain.repository.patient_repository import PatientRepository
from ....models import Patient as PatientModel

class DjangoPatientRepository(PatientRepository):
    """Implementación del repositorio de pacientes usando Django ORM."""
    
    def _to_entity(self, model: PatientModel) -> PatientEntity:
        """Convierte un modelo de Django a una entidad de dominio."""
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
        """Convierte una entidad de dominio a un modelo de Django."""
        if entity.id:
            try:
                model = PatientModel.objects.get(id=entity.id)
                model.name = entity.name
                model.description = entity.description
                model.first_therapy = entity.first_therapy
                model.last_therapy = entity.last_therapy
                model.is_active = entity.is_active
                model.deleted_at = entity.deleted_at
                # No actualizamos created_at ya que es auto_now_add
                # updated_at se actualiza automáticamente con auto_now
                return model
            except PatientModel.DoesNotExist:
                pass
        
        # Si no existe o no tiene ID, crear nuevo modelo
        return PatientModel(
            name=entity.name,
            description=entity.description,
            first_therapy=entity.first_therapy,
            last_therapy=entity.last_therapy,
            is_active=entity.is_active,
            deleted_at=entity.deleted_at,
            user_id=entity.user_id
        )
    
    def create(self, patient: PatientEntity) -> PatientEntity:
        model = self._to_model(patient)
        model.save()
        return self._to_entity(model)
    
    def update(self, patient: PatientEntity) -> PatientEntity:
        model = self._to_model(patient)
        model.save()
        return self._to_entity(model)
    
    def get_by_id(self, patient_id: int) -> PatientEntity:
        try:
            model = PatientModel.objects.get(id=patient_id, deleted_at__isnull=True)
            return self._to_entity(model)
        except PatientModel.DoesNotExist:
            raise ValueError("Paciente no encontrado")
    
    def search(self, filters: Optional[Dict[str, Any]] = None) -> List[PatientEntity]:
        queryset = PatientModel.objects.filter(deleted_at__isnull=True)
        
        if not filters:
            return [self._to_entity(model) for model in queryset]
        
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
                raise ValueError("El formato de 'created_after' debe ser 'YYYY-MM-DD'.")
        
        if 'created_before' in filters:
            try:
                created_before = datetime.strptime(filters['created_before'], '%Y-%m-%d')
                queryset = queryset.filter(created_at__lte=created_before)
            except ValueError:
                raise ValueError("El formato de 'created_before' debe ser 'YYYY-MM-DD'.")
        
        if 'first_therapy_after' in filters:
            try:
                first_therapy_after = datetime.strptime(filters['first_therapy_after'], '%Y-%m-%d')
                queryset = queryset.filter(first_therapy__gte=first_therapy_after)
            except ValueError:
                raise ValueError("El formato de 'first_therapy_after' debe ser 'YYYY-MM-DD'.")
        
        if 'last_therapy_before' in filters:
            try:
                last_therapy_before = datetime.strptime(filters['last_therapy_before'], '%Y-%m-%d')
                queryset = queryset.filter(last_therapy__lte=last_therapy_before)
            except ValueError:
                raise ValueError("El formato de 'last_therapy_before' debe ser 'YYYY-MM-DD'.")
        
        if 'search_term' in filters:
            search_term = filters['search_term']
            queryset = queryset.filter(
                Q(name__icontains=search_term) |
                Q(description__icontains=search_term)
            )
        
        return [self._to_entity(model) for model in queryset]
    
    def get_deleted(self) -> List[PatientEntity]:
        queryset = PatientModel.objects.filter(deleted_at__isnull=False)
        return [self._to_entity(model) for model in queryset]
    
    def delete(self, patient_id: int) -> None:
        patient = self.get_by_id(patient_id)
        patient.set_as_deleted()
        self.update(patient)
    
    def deactivate(self, patient_id: int) -> None:
        patient = self.get_by_id(patient_id)
        patient.set_as_inactive()
        self.update(patient)
    
    def activate(self, patient_id: int) -> None:
        patient = self.get_by_id(patient_id)
        patient.activate()
        self.update(patient)