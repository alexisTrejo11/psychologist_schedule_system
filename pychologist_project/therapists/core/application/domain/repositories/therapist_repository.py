from abc import ABC, abstractmethod
from ....application.domain.entities.therapist import TherapistEntity

class TherapistRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id):
        pass

    @abstractmethod
    def get_by_user_id(self, user_id):
        pass
    
    @abstractmethod
    def create(self, therapist):
        pass
    
    @abstractmethod
    def get_unique_patient_count(self, therapist_id):
        pass
    
    @abstractmethod
    def get_incoming_session_count(self, therapist_id):
        pass

    @abstractmethod
    def update(self, therapist):
        pass

    @abstractmethod
    def delete(self, therapist_id):
        pass