from datetime import datetime
from typing import List
from typing import Dict

class SessionValidator:
    def validate_search_filters(self, filters: Dict):
        if 'start_time_after' in filters and not isinstance(filters['start_time_after'], datetime):
            raise ValueError("'start_time_after' debe ser una fecha/hora válida")

        # ... (otras validaciones de formato)

    def validate_schedule(self, data: Dict):
        required_fields = ['therapist_id', 'start_time', 'end_time']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Falta campo obligatorio: {field}")

        if data['start_time'] >= data['end_time']:
            raise ValueError("La fecha de inicio debe ser anterior a la fecha de fin")

        # Validar conflictos de horario
        # (Puedes usar el repositorio para verificar disponibilidad)

    def validate_status_transition(self, current_status: str, new_status: str):
        valid_transitions = {
            'PENDING': ['SCHEDULED', 'CANCELLED'],
            'SCHEDULED': ['COMPLETED', 'CANCELLED', 'RESCHEDULED'],
            'CANCELLED': ['RESCHEDULED'],
            'COMPLETED': [],
            'RESCHEDULED': ['SCHEDULED', 'COMPLETED']
        }

        if new_status not in valid_transitions.get(current_status, []):
            raise ValueError(f"Transición de estado inválida: {current_status} → {new_status}")

    def validate_patient_limit(self, patient_ids: List[int]):
        if len(patient_ids) > 5:
            raise ValueError("Límite máximo de pacientes por sesión: 5")