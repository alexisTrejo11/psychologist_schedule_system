from django.utils import timezone
from ...application.domain.entities.therapist import TherapistEntity
from users.models import User
from therapists.models import Therapist
from therapy.models import TherapySession
from ...application.domain.repositories.therapist_repository import TherapistRepository
from core.exceptions.custom_exceptions import EntityNotFoundError

class DjangoTherapistRepository(TherapistRepository):
    def get_by_user_id(self, user_id):
        try:
            therapist = Therapist.objects.get(user_id=user_id)
            return self._map_to_entity(therapist)
        except Therapist.DoesNotExist:
            return EntityNotFoundError("Therapist", user_id)
    
    def create(self, therapist_data):
        therapist = Therapist.objects.create(
            user_id=therapist_data.get('user_id'),
            name=therapist_data.get('name', ''),
            license_number=therapist_data.get('license_number'),
            specialization=therapist_data.get('specialization')
        )
        return self._map_to_entity(therapist)
    
    def get_unique_patient_count(self, therapist_id):
        return TherapySession.objects.filter(
            therapist_id=therapist_id
        ).values('patients__id').distinct().count()
    
    def get_incoming_session_count(self, therapist_id):
        return TherapySession.objects.filter(
            therapist_id=therapist_id,
            status='SCHEDULED',
            start_date__lte=timezone.now()
        ).count()
    
    def update(self, therapist_data, therapist):
        if 'name' in therapist_data:
            therapist.name = therapist_data['name']
        if 'license_number' in therapist_data:
            therapist.license_number = therapist_data['license_number']
        if 'specialization' in therapist_data:
            therapist.specialization = therapist_data['specialization']
        
        therapist.save()
        
        return self._map_to_entity(therapist)

    
    def delete(self, therapist_id):
        try:
            therapist = Therapist.objects.get(id=therapist_id)
            
            therapist.delete()

        except Therapist.DoesNotExist:
            return EntityNotFoundError("Therapist", therapist_id)
    
    def _map_to_entity(self, model):
        return TherapistEntity(
            id=model.id,
            user_id=model.user_id,
            name=model.name,
            license_number=model.license_number,
            specialization=model.specialization,
            created_at=model.created_at,
            updated_at=model.updated_at
        )