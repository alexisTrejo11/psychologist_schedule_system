from typing import Dict, List, Optional, Any
from datetime import datetime
from ..domain.entities.patient_entitiy import Patient
from ..domain.repository.patient_repository import PatientRepository

class CreatePatientUseCase:
    """Caso de uso para crear un nuevo paciente."""
    
    def __init__(self, patient_repository: PatientRepository):
        self.patient_repository = patient_repository
    
    def execute(self, data: Dict[str, Any]) -> Patient:
        patient = Patient(
            id=None,
            name=data.get('name', ''),
            description=data.get('description', ''),
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        return self.patient_repository.create(patient)


class UpdatePatientUseCase:
    """Caso de uso para actualizar un paciente existente."""
    def __init__(self, patient_repository: PatientRepository):
        self.patient_repository = patient_repository
    
    def execute(self, patient_id: int, data: Dict[str, Any]) -> Patient:
        patient = self.patient_repository.get_by_id(patient_id)
        
        patient.name = data.get('name', patient.name)
        patient.description = data.get('description', patient.description)
        patient.updated_at = datetime.now()
        
        if 'first_therapy' in data:
            patient.first_therapy = data.get('first_therapy')
        if 'last_therapy' in data:
            patient.last_therapy = data.get('last_therapy')
        
        return self.patient_repository.update(patient)


class GetPatientUseCase:
    """Caso de uso para obtener un paciente por su ID."""
    
    def __init__(self, patient_repository: PatientRepository):
        self.patient_repository = patient_repository
    
    def execute(self, patient_id: int) -> Patient:
        return self.patient_repository.get_by_id(patient_id)


class SearchPatientsUseCase:
    """Caso de uso para buscar pacientes con filtros."""
    
    def __init__(self, patient_repository: PatientRepository):
        self.patient_repository = patient_repository
    
    def execute(self, filters: Optional[Dict[str, Any]] = None) -> List[Patient]:
        return self.patient_repository.search(filters)


class DeletePatientUseCase:
    """Caso de uso para eliminar lógicamente un paciente."""
    
    def __init__(self, patient_repository: PatientRepository):
        self.patient_repository = patient_repository
    
    def execute(self, patient_id: int) -> None:
        self.patient_repository.delete(patient_id)


class DeactivatePatientUseCase:
    """Caso de uso para desactivar un paciente."""
    
    def __init__(self, patient_repository: PatientRepository):
        self.patient_repository = patient_repository
    
    def execute(self, patient_id: int) -> None:
        self.patient_repository.deactivate(patient_id)


class ActivatePatientUseCase:
    """Caso de uso para activar un paciente."""
    
    def __init__(self, patient_repository: PatientRepository):
        self.patient_repository = patient_repository
    
    def execute(self, patient_id: int) -> None:
        self.patient_repository.activate(patient_id)


class GetDeletedPatientsUseCase:
    """Caso de uso para obtener pacientes eliminados."""
    
    def __init__(self, patient_repository: PatientRepository):
        self.patient_repository = patient_repository
    
    def execute(self) -> List[Patient]:
        return self.patient_repository.get_deleted()
