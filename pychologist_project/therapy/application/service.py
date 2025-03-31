from datetime import datetime
from typing import Dict, List, Optional
from ..domain.entities import TherapySession
from ..domain.interfaces import ISessionRepository
from .validators import SessionValidator

class SessionService:
    def __init__(self, repository: ISessionRepository):
        self.repository = repository
        self.validator = SessionValidator()

    def get_session(self, session_id: int) -> TherapySession:
        session = self.repository.get_by_id(session_id)
        if not session:
            raise ValueError("Sesión no encontrada")
        return session

    def search_sessions(self, filters: Dict) -> List[TherapySession]:
        self.validator.validate_search_filters(filters)
        return self.repository.search(filters)

    def schedule_session(self, data: Dict) -> TherapySession:
        self.validator.validate_schedule(data)
        session = TherapySession(
            therapist_id=data['therapist_id'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            status=data.get('status', 'PENDING'),
            notes=data.get('notes', ''),
            patient_ids=data.get('patient_ids', [])
        )
        return self.repository.create(session)

    def update_status(self, session_id: int, new_status: str) -> TherapySession:
        session = self.get_session(session_id)
        self.validator.validate_status_transition(session.status, new_status)
        session.status = new_status
        return self.repository.update(session)

    def update_schedule(self, session_id: int, data: Dict) -> TherapySession:
        session = self.get_session(session_id)
        self.validator.validate_schedule(data)
        session.start_time = data['start_time']
        session.end_time = data['end_time']
        return self.repository.update(session)

    def update_patients(self, session_id: int, patient_ids: List[int]) -> TherapySession:
        session = self.get_session(session_id)
        self.validator.validate_patient_limit(patient_ids)
        session.patient_ids = patient_ids
        return self.repository.update(session)