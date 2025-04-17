from core.exceptions.custom_exceptions import EntityNotFoundError
from ...core.application.domain.entities.home_data import HomeDataEntity
from ...core.application.domain.entities.therapist import TherapistEntity
from ..application.domain.repositories.therapist_repository import TherapistRepository
from ...models import Therapist
from core.mappers.therapist.therapist_mappers import TherapistMapper

class GetTherapistHomeDataUseCase:
    def __init__(self, therapist_repository : TherapistRepository):
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
    def __init__(self, therapist_repository : TherapistRepository):
        self.therapist_repository = therapist_repository
    
    def execute(self, therapist_data) -> Therapist:
        user = therapist_data.get('user')
        user_id = user.id if user and hasattr(user, 'id') else None

        entity = TherapistEntity(
            user_id=user_id,
            name=therapist_data.get('name'),
            specialization=therapist_data.get('specialization'),
            license_number=therapist_data.get('license_number'),
        )

        created_entity = self.therapist_repository.save(entity)

        return TherapistMapper.to_model(created_entity)


class GetTherapistSessionsUseCase:
    def __init__(self, therapist_repository : TherapistRepository):
        self.therapist_repository = therapist_repository
    
    def execute(self, id)  -> Therapist:
        therapist_entity = self.therapist_repository.get_by_id(id)
        return TherapistMapper.to_model(therapist_entity)


class UpdateTherapistUseCase:
    def __init__(self, therapist_repository : TherapistRepository):
        self.therapist_repository = therapist_repository

    def execute(self, therapist_object, validated_data) -> Therapist:
            for field, value in validated_data.items():
                if hasattr(therapist_object, field):
                    setattr(therapist_object, field, value)
                else:
                    raise ValueError(f"Campo inválido para terapeuta: {field}")
            updated_therapist = self.therapist_repository.update(therapist_object, validated_data)
            return TherapistMapper.to_model(updated_therapist)


class DeleteTherapistUseCase:
    def __init__(self, therapist_repository : TherapistRepository):
        self.therapist_repository = therapist_repository
    
    def execute(self, therapist_id) -> None:
        self.therapist_repository.delete(therapist_id)