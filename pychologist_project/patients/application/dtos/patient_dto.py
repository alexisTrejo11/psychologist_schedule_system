from dataclasses import dataclass

@dataclass
class PatientDTO:
    id: int
    name: str
    description: str
    is_active: bool
    created_at: str