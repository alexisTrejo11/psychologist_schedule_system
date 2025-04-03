from abc import ABC, abstractmethod

class TherapistRepository(ABC):
    @abstractmethod
    def get_by_user_id(self, user_id):
        pass
    
    @abstractmethod
    def create(self, therapist_data):
        pass
    
    @abstractmethod
    def get_unique_patient_count(self, therapist_id):
        pass
    
    @abstractmethod
    def get_incoming_session_count(self, therapist_id):
        pass

    @abstractmethod
    def update(self, therapist_data, therapist_id):
        pass

    @abstractmethod
    def delete(self, therapist_id):
        pass