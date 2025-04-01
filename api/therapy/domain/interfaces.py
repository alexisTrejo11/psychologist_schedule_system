from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from .entities import TherapySession

class ISessionRepository(ABC):
    @abstractmethod
    def get_by_id(self, session_id: int) -> Optional[TherapySession]:
        pass

    @abstractmethod
    def search(self, filters: Dict) -> List[TherapySession]:
        pass

    @abstractmethod
    def create(self, session: TherapySession) -> TherapySession:
        pass

    @abstractmethod
    def update(self, session: TherapySession) -> TherapySession:
        pass

    @abstractmethod
    def delete(self, session_id: int) -> None:
        pass