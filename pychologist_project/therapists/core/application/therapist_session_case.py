from ...models import Therapist
from core.exceptions.custom_exceptions import EntityNotFoundError
from therapy.infrastructure.django_session_repository import DjangoSessionRepository

class GetTherapistIncomingSessionsUseCase:
    def __init__(self, sesion_repository):
        self.sesion_repository = sesion_repository
    
    
    def execute(self, user):
        patient = get_therapist_by_user(user)
        return self.sesion_repository.get_sessions_by_therapist(patient=patient, incoming=True)


class GetTherapistSessionListUseCase:
    def __init__(self, sesion_repository):
        self.sesion_repository = sesion_repository
    
    def execute(self, user):
        patient = get_therapist_by_user(user)
        return self.sesion_repository.get_sessions_by_therapist(patient=patient)


class CreateTherapistSessionUseCase:
    def __init__(self, session_service):
        self.session_service = session_service
    
    def execute(self, data):
        return self.session_service.schedule_session(data)


class UpdateTherapistSessionUseCase:
    def __init__(self, session_service):
        self.session_service = session_service
    
    def execute(self, data):
        return self.session_service.update(data)


def get_therapist_by_user(user):
    try:
        return Therapist.object.get(user=user)
    except Therapist.DoesNotExist:
        raise EntityNotFoundError("therapist", f"{user.id}")