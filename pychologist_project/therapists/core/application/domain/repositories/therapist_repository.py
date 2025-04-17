from abc import ABC, abstractmethod
from ....application.domain.entities.therapist import TherapistEntity

class TherapistRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id : int) -> TherapistEntity:
        pass

    @abstractmethod
    def get_by_user_id(self, user_id : int) -> TherapistEntity:
        pass
    
    @abstractmethod
    def save(self, therapist : TherapistEntity) -> TherapistEntity:
        pass
    
    @abstractmethod
    def get_unique_patient_count(self, therapist_id: int) -> int:
        pass
    
    @abstractmethod
    def get_incoming_session_count(self, therapist_id : int) -> int:
        pass

    @abstractmethod
    def delete(self, therapist_id : int) -> None:
        pass