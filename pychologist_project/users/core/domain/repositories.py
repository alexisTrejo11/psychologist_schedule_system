from abc import ABC, abstractmethod

class UserRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id):
        pass
    
    @abstractmethod
    def get_by_email(self, email):
        pass

    @abstractmethod
    def create(self, user_entity, password):
        pass
    
    @abstractmethod
    def update(self, user_entity):
        pass
    
    @abstractmethod
    def exists_by_email(self, email):
        pass
    
    @abstractmethod
    def exists_by_phone(self, phone):
        pass
