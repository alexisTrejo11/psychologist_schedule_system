from core.exceptions.custom_exceptions import EntityNotFoundError
from ...core.application.domain.entities.home_data import HomeDataEntity
from ...core.application.domain.entities.therapist import TherapistEntity
from ...models import Therapist

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
    
    def execute(self, therapist_data) -> Therapist:
        user = therapist_data.get('user')
        user_id = user.id if user and hasattr(user, 'id') else None

        entity = TherapistEntity(
            user_id=user_id,
            name=therapist_data.get('name'),
            specialization=therapist_data.get('specialization'),
            license_number=therapist_data.get('license_number'),
        )

        created_entity = self.therapist_repository.create(entity)


        return Therapist(
            id=user_id,
            user_id=created_entity.user_id,
            name=created_entity.name,
            specialization=created_entity.specialization,
            license_number=created_entity.license_number,
            created_at=created_entity.created_at,
            updated_at=created_entity.updated_at
        )


class GetTherapistSessionsUseCase:
    def __init__(self, therapist_repository):
        self.therapist_repository = therapist_repository
    
    def execute(self, id):
        return self.therapist_repository.get_by_id(id)


class GetTherapistSessionsUseCase:
    def __init__(self, therapist_repository):
        self.therapist_repository = therapist_repository
    
    def execute(self, id):
        return self.therapist_repository.get_by_id(id)


class UpdateTherapistUseCase:
    def __init__(self, therapist_repository):
        self.therapist_repository = therapist_repository

    def execute(self, therapist_object, validated_data):
        """
        Actualiza un terapeuta con los datos validados.
        
        Args:
            therapist_object: Instancia del modelo Therapist a actualizar
            validated_data: Diccionario con los datos validados para actualizar
            
        Returns:
            Therapist: La instancia actualizada del terapeuta
            
        Raises:
            ValueError: Si los datos no son válidos
            RepositoryException: Si ocurre un error en el repositorio
        """
        try:
            for field, value in validated_data.items():
                if hasattr(therapist_object, field):
                    setattr(therapist_object, field, value)
                else:
                    raise ValueError(f"Campo inválido para terapeuta: {field}")
            updated_therapist = self.therapist_repository.update(therapist_object, validated_data)
            
            return updated_therapist
        except Exception as e:
            error_msg = f"Error actualizando terapeuta: {str(e)}"
            raise Exception(error_msg)

class DeleteTherapistUseCase:
    def __init__(self, therapist_repository):
        self.therapist_repository = therapist_repository
    
    def execute(self, therapist_id):
        self.therapist_repository.delete(therapist_id)