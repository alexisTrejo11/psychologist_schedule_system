from django.db.models import Q
from datetime import datetime
from django.utils import timezone
from django.forms import ValidationError
from .models import TherapySession, TherapyParticipant

class SessionService:

    def get_session_by_id(self, session_id):
        try:
            return TherapySession.objects.get(id=session_id)
        except TherapySession.DoesNotExist:
            raise ValueError("Session Not Found")

    def search_session(self, filters=None):
        """
        Realiza una búsqueda dinámica de sesiones basada en los filtros proporcionados.
        
        :param filters: Diccionario con los criterios de búsqueda (opcional).
                        Ejemplo: {
                            'status': 'PENDING',
                            'patient_ids': [1, 2, 3],
                            'start_time_after': '2023-01-01T00:00:00',
                            'end_time_before': '2023-12-31T23:59:59'
                        }
        :return: Queryset de sesiones filtradas.
        """
        queryset = TherapySession.objects.all()

        if not filters:
            return queryset

        if 'status' in filters:
            status_filter = filters['status']
            queryset = queryset.filter(status=status_filter)

        if 'patient_ids' in filters:
            patient_ids = filters['patient_ids']
            if isinstance(patient_ids, list) and all(isinstance(pid, int) for pid in patient_ids):
                queryset = queryset.filter(patients__id__in=patient_ids)
            else:
                raise ValueError("'patient_ids' debe ser una lista de IDs de pacientes.")

        if 'start_time_after' in filters:
            try:
                start_time_after = datetime.fromisoformat(filters['start_time_after'])
                queryset = queryset.filter(start_time__gte=start_time_after)
            except ValueError:
                raise ValueError("El formato de 'start_time_after' debe ser ISO 8601 (YYYY-MM-DDTHH:MM:SS).")

        if 'start_time_before' in filters:
            try:
                start_time_before = datetime.fromisoformat(filters['start_time_before'])
                queryset = queryset.filter(start_time__lte=start_time_before)
            except ValueError:
                raise ValueError("El formato de 'start_time_before' debe ser ISO 8601 (YYYY-MM-DDTHH:MM:SS).")

        if 'end_time_after' in filters:
            try:
                end_time_after = datetime.fromisoformat(filters['end_time_after'])
                queryset = queryset.filter(end_time__gte=end_time_after)
            except ValueError:
                raise ValueError("El formato de 'end_time_after' debe ser ISO 8601 (YYYY-MM-DDTHH:MM:SS).")

        if 'end_time_before' in filters:
            try:
                end_time_before = datetime.fromisoformat(filters['end_time_before'])
                queryset = queryset.filter(end_time__lte=end_time_before)
            except ValueError:
                raise ValueError("El formato de 'end_time_before' debe ser ISO 8601 (YYYY-MM-DDTHH:MM:SS).")


        if 'created_at_after' in filters:
            try:
                created_at_after = datetime.fromisoformat(filters['created_at_after'])
                queryset = queryset.filter(created_at__gte=created_at_after)
            except ValueError:
                raise ValueError("El formato de 'created_at_after' debe ser ISO 8601 (YYYY-MM-DDTHH:MM:SS).")

        if 'created_at_before' in filters:
            try:
                created_at_before = datetime.fromisoformat(filters['created_at_before'])
                queryset = queryset.filter(created_at__lte=created_at_before)
            except ValueError:
                raise ValueError("El formato de 'created_at_before' debe ser ISO 8601 (YYYY-MM-DDTHH:MM:SS).")


        if 'search_term' in filters:
            search_term = filters['search_term']
            queryset = queryset.filter(
                Q(notes__icontains=search_term) |
                Q(status__icontains=search_term)
            )

        return queryset
    
    def schedule_session(self, data):
        self.__validate_schedule(data)
        self.__validate_not_patient_conflict(data)

        session = TherapySession.objects.create(
                therapist=data.get('therapist'),
                start_time=data.get('start_time'),
                end_time=data.get('end_time'),
                status=data.get('status', 'PENDING'), 
                notes=data.get('notes', ''),  
            )
        
        patients = data.get('patients', [])
        session.patients.set(patients) 

        return session
    
    def update_status(self, id, status):
        session = self.get_session_by_id(id)
        
        self.__validate_status_update(status)
        if status == 'CANCELLED':
            session.cancelled_at = timezone.now()
        self.status = status

        session.save()

        return session
    
    def update_schedule(self, id, data):
        session = self.get_session_by_id(id)
        self.__validate_schedule(data)

        session.start_time = data.get('start_time')
        session.end_time = data.get('end_time')

        session.save()

        return session
    
    def update_patients(self, id, data):
        session = self.get_session_by_id(id)
        
        self.__validate_not_patient_conflict(data)
        
        session.patients = data.get('patients')
        session.save()

        return session
    
    def soft_delete(self, id):
        session = self.get_session_by_id(id)
        
        session.soft_delete()
        session.save()
    
    def __validate_schedule(schedule, data):
        start_time = data.get('start_time')
        end_time = data.get('end_time')
       
        filtered_sessions = TherapySession.objects.filter(
            start_time__lte=start_time,
            end_time__lte=end_time
        ).exclude(status="RESCHEDULED")

        if filtered_sessions:
            raise ValueError('Schdule conflict: A Session Already Schdule in the requested time range')
        
    def __validate_not_patient_conflict(self, data):
        patients = data.get('patients', [])
        
        if len(patients) > 5:
            raise ValueError('Schdule conflict: Patient limit reached, max capacity per session is 5')

        for patient in patients:
            if TherapyParticipant.objects.filter(patient=patient).exists():
                raise ValueError(f'Schdule conflict: Patient:{patient.name}')

    def __validate_status_update(self, new_status):
        """
        Actualiza el estado de la sesión validando las transiciones permitidas.
        
        :param new_status: Nuevo estado a asignar.
        :raises ValidationError: Si el nuevo estado no es válido o no se permite la transición.
        """
        valid_statuses = [choice[0] for choice in TherapySession.STATUS_CHOICES]

        if new_status not in valid_statuses:
            raise ValidationError(f"Estado inválido: '{new_status}'. Los estados válidos son: {valid_statuses}.")

        match self.status:
            case 'PENDING':
                if new_status not in ['SCHEDULED', 'CANCELLED']:
                    raise ValidationError("Una sesión pendiente solo puede ser agendada o cancelada.")
            
            case 'SCHEDULED':
                if new_status not in ['COMPLETED', 'CANCELLED', 'RESCHEDULED']:
                    raise ValidationError("Una sesión agendada solo puede ser completada, cancelada o reagendada.")
            
            case 'CANCELLED':
                if new_status not in ['RESCHEDULED']:
                    raise ValidationError("Una sesión cancelada solo puede ser reagendada.")
                
            case 'COMPLETED':
                raise ValidationError("No se puede cambiar el estado de una sesión completada.")
            
            case 'RESCHEDULED':
                if new_status not in ['SCHEDULED', 'COMPLETED']:
                    raise ValidationError("Una sesión reagendada solo puede ser agendada nuevamente o completada.")
        