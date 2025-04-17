from datetime import datetime
from typing import Optional
from therapists.models import Therapist
from therapists.core.application.domain.entities.therapist import TherapistEntity

class TherapistMapper:
    @staticmethod
    def to_entity(therapist_model: Therapist) -> TherapistEntity :
        """
        Convierte un objeto Therapist (modelo de Django) en un objeto TherapistEntity.
        """
        return TherapistEntity(
            id=therapist_model.id,
            user_id=therapist_model.user.id if therapist_model.user else None,
            name=therapist_model.name,
            license_number=therapist_model.license_number,
            specialization=therapist_model.specialization,
            created_at=therapist_model.created_at,
            updated_at=therapist_model.updated_at
        )

    @staticmethod
    def to_model(therapist_entity: TherapistEntity ) -> 'Therapist':
        """
        Convierte un objeto TherapistEntity en un objeto Therapist (modelo de Django).
        """
        therapist_model = Therapist(
            id=therapist_entity._id,
            user_id=therapist_entity._user_id,
            name=therapist_entity._name,
            license_number=therapist_entity._license_number,
            specialization=therapist_entity._specialization,
            created_at=therapist_entity._created_at or datetime.now(),
            updated_at=therapist_entity._updated_at or datetime.now()
        )
        return therapist_model