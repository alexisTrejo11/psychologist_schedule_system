from datetime import datetime
from typing import List
from typing import Dict
from core.exceptions.custom_exceptions import BusinessLogicError, InvalidOperationError
from django.db.models import Q
from ..models import TherapySession

class SessionValidator:
    def validate_search_filters(self, filters: Dict):
        if 'start_time_after' in filters and not isinstance(filters['start_time_after'], datetime):
            raise ValueError("'start_time_after' debe ser una fecha/hora válida")

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

    def validate_schedule(self, data: Dict, action : str, id : int = None):
        required_fields = ['therapist', 'start_time', 'end_time']
        for field in required_fields:
            if field not in data:
                raise InvalidOperationError(f"Falta campo obligatorio: {field}")

        if data['start_time'] >= data['end_time']:
            raise InvalidOperationError("La fecha de inicio debe ser anterior a la fecha de fin")

        filtered_session = TherapySession.objects.filter(
            start_time__lte=data['start_time'],
            end_time__lte=data['end_time']
        ).exclude(status="RESCHEDULED").first()

        #  Avoid conflict while updating
        if action == 'update' and id is not None:
            if id == filtered_session.id:
                return

        if filtered_session:
            raise InvalidOperationError('Schdule conflict: A Session Already Schdule in the requested time range')


    def validate_status_transition(self, current_status: str, new_status: str):
        valid_transitions = {
            'PENDING': ['SCHEDULED', 'CANCELLED'],
            'SCHEDULED': ['COMPLETED', 'CANCELLED', 'RESCHEDULED'],
            'CANCELLED': ['RESCHEDULED'],
            'COMPLETED': [],
            'RESCHEDULED': ['SCHEDULED', 'COMPLETED']
        }

        if new_status not in valid_transitions.get(current_status, []):
            raise BusinessLogicError(f"Transición de estado inválida: {current_status} → {new_status}")

        match current_status:
            case 'PENDING':
                if new_status not in ['SCHEDULED', 'CANCELLED']:
                    raise BusinessLogicError("Una sesión pendiente solo puede ser agendada o cancelada.")
            
            case 'SCHEDULED':
                if new_status not in ['COMPLETED', 'CANCELLED', 'RESCHEDULED']:
                    raise BusinessLogicError("Una sesión agendada solo puede ser completada, cancelada o reagendada.")
            
            case 'CANCELLED':
                if new_status not in ['RESCHEDULED']:
                    raise BusinessLogicError("Una sesión cancelada solo puede ser reagendada.")
                
            case 'COMPLETED':
                raise BusinessLogicError("No se puede cambiar el estado de una sesión completada.")
            
            case 'RESCHEDULED':
                if new_status not in ['SCHEDULED', 'COMPLETED']:
                    raise BusinessLogicError("Una sesión reagendada solo puede ser agendada nuevamente o completada.")
        
    def validate_patient_limit(self, patients: List):
        if len(patients) > 5:
            raise BusinessLogicError("Límite máximo de pacientes por sesión: 5")