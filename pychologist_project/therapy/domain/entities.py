from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass
class TherapySession:
    id: int
    therapist_id: int
    start_time: datetime
    end_time: datetime
    status: str
    notes: str
    patient_ids: List[int]