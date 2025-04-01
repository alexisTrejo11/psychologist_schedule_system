from datetime import datetime
from typing import Dict, List
from ..domain.entities import TherapySession
from ..domain.interfaces import ISessionRepository
from .validators import SessionValidator
from core.exceptions.custom_exceptions import EntityNotFoundError
import logging
from ..models import TherapySession as DjangoTherapySession

class SessionService:
    def __init__(self, repository: ISessionRepository):
        self.repository = repository
        self.validator = SessionValidator()

    def get_session(self, session_id: int) -> DjangoTherapySession:
        """
        Obtiene una sesión por ID y la convierte a un modelo Django.
        """
        session = self.repository.get_by_id(session_id)
        if not session:
            raise EntityNotFoundError("Sesión no encontrada")
        
        return self._convert_to_model(session)

    def search_sessions(self, filters: Dict) -> List[DjangoTherapySession]:
        """
        Busca sesiones según filtros y las convierte a modelos Django.
        """
        self.validator.validate_search_filters(filters)
        domain_sessions = self.repository.search(filters)
        return [self._convert_to_model(session) for session in domain_sessions]

    def schedule_session(self, data: Dict) -> DjangoTherapySession:
        """
        Programa una nueva sesión y la convierte a un modelo Django.
        """
        self.validator.validate_schedule(data, 'create')
        
        session = TherapySession(
            therapist_id=data['therapist'].id,
            start_time=data['start_time'],
            end_time=data['end_time'],
            status=data.get('status', 'PENDING'),
            notes=data.get('notes', ''),
            patients=data.get('patient_ids', [])
        )
        
        created_session = self.repository.create(session)
        return self._convert_to_model(created_session)

    def update(self, session, data: Dict) -> DjangoTherapySession:
        """
        Actualiza una sesión existente y la convierte a un modelo Django.
        """
        self.__update_schedule(session, data)

        if session.status != data['status']:
            self.__update_status(session, data['status'])

        self.__update_patients(session, data.get('patients'))

        session.notes = data['notes']

        updated_session = self.repository.update(session)
        
        return self._convert_to_model(updated_session)

    def __update_status(self, session, new_status: str):
        self.validator.validate_status_transition(session.status, new_status)
        session.status = new_status

    def __update_schedule(self, session, data: Dict):
        self.validator.validate_schedule(data, 'update', session.id)
        session.start_time = data['start_time']
        session.end_time = data['end_time']

    def __update_patients(self, session, patients):
        """
        Actualiza los pacientes asociados a una sesión.
        """
        self.validator.validate_patient_limit(patients)

        if patients is not None:
            session.patients.set(patients)


    def _convert_to_entity(self, django_session: DjangoTherapySession) -> TherapySession:
        """
        Convierte un modelo Django a una entidad de dominio.
        """
        return TherapySession(
            id=django_session.id,
            therapist_id=django_session.therapist.id,
            start_time=django_session.start_time,
            end_time=django_session.end_time,
            status=django_session.status,
            notes=django_session.notes,
            patients=list(django_session.patients.values_list('id', flat=True))
        )

    def _convert_to_model(self, session: TherapySession) -> DjangoTherapySession:
        """
        Convierte una entidad de dominio a un modelo Django.
        """
        django_session = DjangoTherapySession.objects.get(id=session.id)
        django_session.start_time = session.start_time
        django_session.end_time = session.end_time
        django_session.status = session.status
        django_session.notes = session.notes
        django_session.therapist_id = session.therapist_id
        django_session.patients.set(session.patients)
        return django_session