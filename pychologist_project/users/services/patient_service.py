from django.forms import ValidationError
from ..models import Patient
from datetime import datetime
from django.db.models import Q

class PatientService:

    def create_patient(self, data):
        """
        Crea un nuevo paciente asociado a un usuario.
        """
        patient = Patient.objects.create(
            name=data.get('name', ''),
            description=data.get('description', ''),
            is_active=True,
        )
        return patient
    
    def inactive_user(self, patient_id):
        exisitngPatient = self.get_patient_by_id(patient_id)
        
        exisitngPatient.set_as_inactive()
        exisitngPatient.save()

    def update_patient(self, patient_id, data) -> Patient:
        """
        Actualiza la información de un paciente.
        """
        exisitngPatient = self.get_patient_by_id(patient_id)

        exisitngPatient.name = data.get('name', exisitngPatient.name)
        exisitngPatient.description = data.get('description', exisitngPatient.description)
        exisitngPatient.save()
        
        return exisitngPatient

    def soft_delete_patient_by_id(self, patient_id):
        exisitngPatient = self.get_patient_by_id(patient_id)
        
        exisitngPatient.set_as_deleted()
        exisitngPatient.save()

    def get_patient_by_id(self, patient_id) -> Patient:
        try:
            patient = Patient.objects.get(id=patient_id, deleted_at__isnull=True)
            return patient
        except Patient.DoesNotExist:
            raise ValueError("Paciente no encontrado")
    
    def get_deleted_patients(self) -> Patient:
        patient = Patient.objects.filter(deleted_at__isnull=True)
        return patient

    def search_patients(self, filters=None):
        """
        Realiza una búsqueda dinámica de pacientes basada en los filtros proporcionados.
        
        :param filters: Diccionario con los criterios de búsqueda (opcional).
                        Ejemplo: {
                            'name': 'John',
                            'is_active': True,
                            'created_after': '2023-01-01',
                            'created_before': '2023-12-31'
                        }
        :return: Queryset de pacientes filtrados.
        """
        queryset = Patient.objects.all() 
        queryset = queryset.filter(deleted_at__isnull=True)

        if not filters:
            return queryset

        if 'name' in filters:
            queryset = queryset.filter(name__icontains=filters['name'])

        if 'description' in filters:
            queryset = queryset.filter(description__icontains=filters['description'])

        if 'is_active' in filters:
            queryset = queryset.filter(is_active=filters['is_active'])

        if 'created_after' in filters:
            try:
                created_after = datetime.strptime(filters['created_after'], '%Y-%m-%d')
                queryset = queryset.filter(created_at__gte=created_after)
            except ValueError:
                raise ValueError("El formato de 'created_after' debe ser 'YYYY-MM-DD'.")

        if 'created_before' in filters:
            try:
                created_before = datetime.strptime(filters['created_before'], '%Y-%m-%d')
                queryset = queryset.filter(created_at__lte=created_before)
            except ValueError:
                raise ValueError("El formato de 'created_before' debe ser 'YYYY-MM-DD'.")

        if 'first_therapy_after' in filters:
            try:
                first_therapy_after = datetime.strptime(filters['first_therapy_after'], '%Y-%m-%d')
                queryset = queryset.filter(first_therapy__gte=first_therapy_after)
            except ValueError:
                raise ValueError("El formato de 'first_therapy_after' debe ser 'YYYY-MM-DD'.")

        if 'last_therapy_before' in filters:
            try:
                last_therapy_before = datetime.strptime(filters['last_therapy_before'], '%Y-%m-%d')
                queryset = queryset.filter(last_therapy__lte=last_therapy_before)
            except ValueError:
                raise ValueError("El formato de 'last_therapy_before' debe ser 'YYYY-MM-DD'.")

        if 'search_term' in filters:
            search_term = filters['search_term']
            queryset = queryset.filter(
                Q(name__icontains=search_term) |
                Q(description__icontains=search_term)
            )

        return queryset
