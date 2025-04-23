from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import asdict
from ...core.domain.entities.patient_entitiy import Patient
from ...core.domain.repository.patient_repository import PatientRepository
from ...core.mappers.payment_mappers import PatientMapper
from ...application.dtos.patient_dto import PatientDTO
from core.exceptions.custom_exceptions import EntityNotFoundError

class CreatePatientUseCase:    
    def __init__(self, patient_repository: PatientRepository):
        self.patient_repository = patient_repository
    
    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        patient = PatientMapper.dict_to_domain(data)

        patient_entity = self.patient_repository.create(patient)
        
        return asdict(PatientMapper.to_dto(patient_entity))

class UpdatePatientUseCase:
    def __init__(self, patient_repository: PatientRepository):
        self.patient_repository = patient_repository
    
    def execute(self, patient_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        patient = self.patient_repository.get_by_id(patient_id)
        if not patient:
            raise EntityNotFoundError('Patient', patient_id)
        
        patient.name = data.get('name', patient.name)
        patient.description = data.get('description', patient.description)
        patient.updated_at = datetime.now()
        
        if 'first_therapy' in data:
            patient.first_therapy = data.get('first_therapy')
        if 'last_therapy' in data:
            patient.last_therapy = data.get('last_therapy')
        
        patient_entity = self.patient_repository.update(patient)
        
        return asdict(PatientMapper.to_dto(patient_entity))


class GetPatientUseCase:    
    def __init__(self, patient_repository: PatientRepository):
        self.patient_repository = patient_repository
    
    def execute(self, patient_id: int) -> Dict[str, Any]:
        patient_entity = self.patient_repository.get_by_id(patient_id)
        
        return asdict(PatientMapper.to_dto(patient_entity))


class SearchPatientsUseCase:    
    def __init__(self, patient_repository: PatientRepository):
        self.patient_repository = patient_repository
    
    def execute(self, filters: Optional[Dict[str, Any]] = None) -> List[Patient]:
        return self.patient_repository.search(filters)


class DeletePatientUseCase:    
    def __init__(self, patient_repository: PatientRepository):
        self.patient_repository = patient_repository
    
    def execute(self, patient_id: int) -> None:
        self.patient_repository.get_by_id(patient_id)
        
        self.patient_repository.delete(patient_id)


class DeactivatePatientUseCase:    
    def __init__(self, patient_repository: PatientRepository):
        self.patient_repository = patient_repository
    
    def execute(self, patient_id: int) -> None:
        self.patient_repository.get_by_id(patient_id)

        self.patient_repository.deactivate(patient_id)


class ActivatePatientUseCase:    
    def __init__(self, patient_repository: PatientRepository):
        self.patient_repository = patient_repository
    
    def execute(self, patient_id: int) -> None:
        self.patient_repository.get_by_id(patient_id)

        self.patient_repository.activate(patient_id)


class GetDeletedPatientsUseCase:    
    def __init__(self, patient_repository: PatientRepository):
        self.patient_repository = patient_repository
    
    def execute(self) -> List[Patient]:
        return self.patient_repository.get_deleted()

