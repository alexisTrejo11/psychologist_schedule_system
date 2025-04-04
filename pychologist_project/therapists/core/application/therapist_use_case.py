from core.exceptions.custom_exceptions import EntityNotFoundError
from ...core.application.domain.entities.home_data import HomeDataEntity

class GetTherapistHomeDataUseCase:
    def __init__(self, therapist_repository):
        self.therapist_repository = therapist_repository
    
    def execute(self, user_id):
        therapist = self.therapist_repository.get_by_user_id(user_id)
        if not therapist:
            raise EntityNotFoundError("Therapist", user_id)
        
        patient_count = self.therapist_repository.get_unique_patient_count(therapist.id)
        incoming_session_count = self.therapist_repository.get_incoming_session_count(therapist.id)
        
        return HomeDataEntity(
            patient_count=patient_count,
            incoming_session_count=incoming_session_count,
            therapist_name=therapist.name,
            profile_picture=None  #ADAPTER
        )
    
class CreateTherapistUseCase:
    def __init__(self, therapist_repository):
        self.therapist_repository = therapist_repository
    
    def execute(self, therapist_data):
        return self.therapist_repository.create(therapist_data)


class GetTherapistSessionsUseCase:
    def __init__(self, therapist_repository):
        self.therapist_repository = therapist_repository
    
    def execute(self, therapist_data):
        return self.therapist_repository.create(therapist_data)

class UpdateTherapistUseCase:
    def __init__(self, therapist_repository):
        self.therapist_repository = therapist_repository
    
    def execute(self, therapist, therapist_data):
        return self.therapist_repository.update(therapist_data, therapist)


class DeleteTherapistUseCase:
    def __init__(self, therapist_repository):
        self.therapist_repository = therapist_repository
    
    def execute(self, therapist_id):
        self.therapist_repository.delete(therapist_id)