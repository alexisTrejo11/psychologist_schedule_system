from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict

@dataclass
class Person:
    id: int
    name: str

@dataclass
class Patient(Person):
    pass

@dataclass
class Therapist(Person):
    pass


@dataclass
class TherapySession:
    therapist_id: int
    start_time: datetime
    end_time: datetime
    status: str
    notes: str
    patients: List[Patient] 
    id: int = None

    @property
    def patient_ids(self):
        """Devuelve una lista de IDs de pacientes."""
        if not self.patients:
            return [] 
        try:
            return [patient['id'] for patient in self.patients]
        except (TypeError, KeyError) as e:
            raise ValueError("Los datos de 'patients' no tienen el formato esperado.") from e