from django.db.models import Q
from ..models import TherapySession as DjangoTherapySession
from ..domain.interfaces import ISessionRepository
from ..domain.entities import TherapySession
from typing import Optional, Dict, List
from datetime import datetime
from django.utils import timezone
from core.cache.cache_manager import CacheManager
from core.exceptions.custom_exceptions import EntityNotFoundError, InvalidOperationError

CACHE_PREFIX = "therapy_session_"

class DjangoSessionRepository(ISessionRepository):
    def __init__(self):
        self.cache_manager = CacheManager(CACHE_PREFIX)
        super().__init__()

    def get_by_id(self, session_id: int) -> Optional[TherapySession]:
        cache_key = self.cache_manager.get_cache_key(session_id)
        
        cached_session = self.cache_manager.get(cache_key)
        if cached_session is not None:
            return cached_session
        
        try:
            session = DjangoTherapySession.objects.get(id=session_id)
            entity = self._convert_to_entity(session)
            
            self.cache_manager.set(cache_key, entity)
            return entity
        except DjangoTherapySession.DoesNotExist:
            raise EntityNotFoundError('therapy session', session_id)

    def get_sessions_by_therapist(self, therapist, incoming=False):
        filter_key = f"therapist_{therapist.id}_incoming_{incoming}"
        cache_key = self.cache_manager.generate_search_key({'filter': filter_key})
        
        cached_sessions = self.cache_manager.get(cache_key)
        if cached_sessions is not None:
            return cached_sessions
        
        if incoming:
            queryset = DjangoTherapySession.objects.filter(
                therapist=therapist,
                status='SCHEDULED',
                start_time__gte=timezone.now()
            )
        else:
            queryset = DjangoTherapySession.objects.filter(therapist=therapist).order_by('start_time')
        
        sessions = [self._convert_to_entity(s) for s in queryset]
        
        self.cache_manager.set(cache_key, sessions)
        return sessions

    def search(self, filters: Dict) -> List[TherapySession]:
        cache_key = self.cache_manager.generate_search_key(filters)
        
        cached_sessions = self.cache_manager.get(cache_key)
        if cached_sessions is not None:
            return cached_sessions
        
        queryset = DjangoTherapySession.objects.all()

        if filters.get('status'):
            queryset = queryset.filter(status=filters['status'])

        if filters.get('patient_ids'):
            queryset = queryset.filter(patients__id__in=filters['patient_ids'])

        if filters.get('start_time_after'):
            queryset = queryset.filter(start_time__gte=filters['start_time_after'])

        if 'start_time_before' in filters:
            try:
                start_time_before = datetime.fromisoformat(filters['start_time_before'])
                queryset = queryset.filter(start_time__lte=start_time_before)
            except InvalidOperationError:
                raise InvalidOperationError("El formato de 'start_time_before' debe ser ISO 8601 (YYYY-MM-DDTHH:MM:SS).")

        if 'end_time_after' in filters:
            try:
                end_time_after = datetime.fromisoformat(filters['end_time_after'])
                queryset = queryset.filter(end_time__gte=end_time_after)
            except InvalidOperationError:
                raise InvalidOperationError("El formato de 'end_time_after' debe ser ISO 8601 (YYYY-MM-DDTHH:MM:SS).")

        if 'end_time_before' in filters:
            try:
                end_time_before = datetime.fromisoformat(filters['end_time_before'])
                queryset = queryset.filter(end_time__lte=end_time_before)
            except InvalidOperationError:
                raise InvalidOperationError("El formato de 'end_time_before' debe ser ISO 8601 (YYYY-MM-DDTHH:MM:SS).")

        if 'created_at_after' in filters:
            try:
                created_at_after = datetime.fromisoformat(filters['created_at_after'])
                queryset = queryset.filter(created_at__gte=created_at_after)
            except InvalidOperationError:
                raise InvalidOperationError("El formato de 'created_at_after' debe ser ISO 8601 (YYYY-MM-DDTHH:MM:SS).")

        if 'created_at_before' in filters:
            try:
                created_at_before = datetime.fromisoformat(filters['created_at_before'])
                queryset = queryset.filter(created_at__lte=created_at_before)
            except InvalidOperationError:
                raise InvalidOperationError("El formato de 'created_at_before' debe ser ISO 8601 (YYYY-MM-DDTHH:MM:SS).")

        if 'search_term' in filters:
            search_term = filters['search_term']
            queryset = queryset.filter(
                Q(notes__icontains=search_term) |
                Q(status__icontains=search_term)
            )

        sessions = [self._convert_to_entity(s) for s in queryset]
        
        self.cache_manager.set(cache_key, sessions)
        return sessions

    def create(self, session: TherapySession) -> TherapySession:
        django_session = DjangoTherapySession(
            therapist_id=session.therapist_id,
            start_time=session.start_time,
            end_time=session.end_time,
            status=session.status,
            notes=session.notes
        )
        django_session.save()
        django_session.patients.set(session.patient_ids)
        
        entity = self._convert_to_entity(django_session)
        
        cache_key = self.cache_manager.get_cache_key(entity.id)
        self.cache_manager.set(cache_key, entity)
        
        return entity

    def update(self, session: TherapySession) -> TherapySession:
        django_session = DjangoTherapySession.objects.get(id=session.id)
        django_session.start_time = session.start_time
        django_session.end_time = session.end_time
        django_session.status = session.status
        django_session.notes = session.notes
        django_session.save()
        
        if hasattr(session, 'patients') and session.patients is not None:
            if hasattr(session.patients, 'values_list'):
                patient_ids = list(session.patients.values_list('id', flat=True))
            else:
                patient_ids = session.patients

            django_session.patients.set(patient_ids)
        
        entity = self._convert_to_entity(django_session)
        
        cache_key = self.cache_manager.get_cache_key(entity.id)
        self.cache_manager.set(cache_key, entity)
        
        return entity

    def delete(self, session_id: int) -> None:
        DjangoTherapySession.objects.filter(id=session_id).delete()
        
        cache_key = self.cache_manager.get_cache_key(session_id)
        self.cache_manager.delete(cache_key)

    def _convert_to_entity(self, django_session: DjangoTherapySession) -> TherapySession:
        return TherapySession(
            id=django_session.id,
            therapist_id=django_session.therapist.id,
            start_time=django_session.start_time,
            end_time=django_session.end_time,
            status=django_session.status,
            notes=django_session.notes,
            patients=list(django_session.patients.values_list('id', flat=True))
        )