from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from ..entities.patient_entitiy import Patient

class PatientRepository(ABC):
    """Interfaz para el repositorio de pacientes."""
    
    @abstractmethod
    def create(self, patient: Patient) -> Patient:
        """Crea un nuevo paciente."""
        pass
    
    @abstractmethod
    def update(self, patient: Patient) -> Patient:
        """Actualiza un paciente existente."""
        pass
    
    @abstractmethod
    def get_by_id(self, patient_id: int) -> Patient:
        """Obtiene un paciente por su ID."""
        pass
    
    @abstractmethod
    def search(self, filters: Optional[Dict[str, Any]] = None) -> List[Patient]:
        """Busca pacientes según filtros especificados."""
        pass
    
    @abstractmethod
    def get_deleted(self) -> List[Patient]:
        """Obtiene pacientes eliminados lógicamente."""
        pass
    
    @abstractmethod
    def delete(self, patient_id: int) -> None:
        """Elimina lógicamente un paciente."""
        pass
    
    @abstractmethod
    def deactivate(self, patient_id: int) -> None:
        """Desactiva un paciente."""
        pass
    
    @abstractmethod
    def activate(self, patient_id: int) -> None:
        """Activa un paciente."""
        pass