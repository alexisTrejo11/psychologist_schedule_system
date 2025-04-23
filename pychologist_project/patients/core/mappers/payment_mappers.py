from typing import Optional
from datetime import datetime
from patients.core.domain.entities.patient_entitiy import Patient
from patients.models import Patient as PatientModel 
from patients.application.dtos.patient_dto import PatientDTO

class PatientMapper:
    """Mapper para convertir entre entidades de dominio y modelos de Django."""
    
    @staticmethod
    def model_to_entity(patient_model: PatientModel) -> Patient:
        """Convierte un modelo de Django en una entidad de dominio."""
        return Patient(
            id=patient_model.id,
            name=patient_model.name,
            description=patient_model.description,
            first_therapy=patient_model.first_therapy,
            last_therapy=patient_model.last_therapy,
            is_active=patient_model.is_active,
            created_at=patient_model.created_at,
            updated_at=patient_model.updated_at,
            deleted_at=patient_model.deleted_at,
            user_id=patient_model.user_id if patient_model.user else None
        )
    
    @staticmethod
    def domain_to_model(patient_entity: Patient) -> PatientModel:
        """Convierte una entidad de dominio en un modelo de Django."""
        return PatientModel(
            id=patient_entity.id,
            name=patient_entity.name,
            description=patient_entity.description,
            first_therapy=patient_entity.first_therapy,
            last_therapy=patient_entity.last_therapy,
            is_active=patient_entity.is_active,
            created_at=patient_entity.created_at,
            updated_at=patient_entity.updated_at,
            deleted_at=patient_entity.deleted_at,
            user_id=patient_entity.user_id
        )
    

    @staticmethod
    def dict_to_domain(data: dict) -> Patient:
        """Convierte un diccionario en una entidad de dominio."""
        return Patient(
            id=data.get('id'),
            name=data['name'],
            description=data.get('description', ''),
            first_therapy=datetime.fromisoformat(data['first_therapy']) if data.get('first_therapy') else None,
            last_therapy=datetime.fromisoformat(data['last_therapy']) if data.get('last_therapy') else None,
            is_active=data.get('is_active', True),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None,
            deleted_at=datetime.fromisoformat(data['deleted_at']) if data.get('deleted_at') else None,
            user_id=data.get('user_id')
        )
    

    @staticmethod
    def entity(patient_entity: Patient) -> PatientDTO :
        return PatientDTO(
            id=patient_entity.id,
            name=patient_entity.name,
            description=patient_entity.description,
            is_active=patient_entity.is_active,
            created_at=patient_entity.created_at.isoformat(),
        )