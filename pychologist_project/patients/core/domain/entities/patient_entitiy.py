from datetime import datetime
from dataclasses import dataclass
from typing import Optional

@dataclass
class Patient:
    """Entidad de dominio para representar un paciente."""
    name: str
    description: str = ''
    id: Optional[int] = None
    first_therapy: Optional[datetime] = None
    last_therapy: Optional[datetime] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    user_id: Optional[int] = None
    
    def set_as_deleted(self) -> None:
        """Marca el paciente como eliminado."""
        if self.deleted_at is not None:
            raise ValueError("Patient Already Deleted")
        
        self.deleted_at = datetime.now()
    
    def set_as_inactive(self) -> None:
        """Marca el paciente como inactivo."""
        if not self.is_active:
            raise ValueError("Patient Is Already Inactive")
        
        self.is_active = False
        self.updated_at = datetime.now()
    
    def activate(self) -> None:
        """Activa un paciente inactivo."""
        if self.is_active:
            raise ValueError("Patient Is Already Active")
        
        self.is_active = True
        self.updated_at = datetime.now()
