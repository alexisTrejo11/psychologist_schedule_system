from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from ..core.application.domain.entities.patient_entitiy import Patient as PatientEntity
from ..core.infrastructure.repositories.django_patient_repository import DjangoPatientRepository
from ..models import Patient

class PatientRepositoryTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Configuración inicial para todas las pruebas."""
        cls.User = get_user_model()
        cls.repository = DjangoPatientRepository()

    def create_user(self, username):
        """Helper para crear usuarios únicos."""
        return self.User.objects.create_user(username=username, password="password")

    def test_create_patient(self):
        """Prueba la creación de un paciente."""
        user = self.create_user("testuser_unique")
        patient_data = PatientEntity(
            name="John Doe",
            description="Test patient",
            first_therapy=timezone.now(),
            last_therapy=timezone.now(),
            is_active=True,
            user_id=user.id
        )
        created_patient = self.repository.create(patient_data)
        model = self.repository.get_by_id(created_patient.id)
        self.assertEqual(model.name, "John Doe")
        self.assertEqual(created_patient.user_id, user.id)

    def test_update_patient(self):
        """Prueba la actualización de un paciente."""
        user = self.create_user("update_user_unique")
        patient = PatientEntity(name="Original", description="Original desc", user_id=user.id)
        created = self.repository.create(patient)

        created.name = "Updated"
        updated_patient = self.repository.update(created)

        model = self.repository.get_by_id(created.id)
        self.assertEqual(model.name, "Updated")
        self.assertEqual(updated_patient.description, "Original desc")

    def test_get_by_id_existing(self):
        """Prueba la obtención de un paciente existente por ID."""
        user = self.create_user("get_by_id_user_unique")
        patient = PatientEntity(name="Test", user_id=user.id)
        created = self.repository.create(patient)

        retrieved = self.repository.get_by_id(created.id)
        self.assertEqual(retrieved.id, created.id)

    def test_get_by_id_not_found(self):
        """Prueba la obtención de un paciente inexistente por ID."""
        with self.assertRaises(ValueError, msg="Patient with ID 999 not found."):
            self.repository.get_by_id(999)

    def test_search_by_name(self):
        """Prueba la búsqueda de pacientes por nombre."""
        user1 = self.create_user("user1_unique")
        user2 = self.create_user("user2_unique")

        patient1 = PatientEntity(name="John Doe", user_id=user1.id)
        patient2 = PatientEntity(name="Jane Smith", user_id=user2.id)
        self.repository.create(patient1)
        self.repository.create(patient2)

        results = self.repository.search({"name": "John"})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "John Doe")

    def test_search_by_is_active(self):
        """Prueba la búsqueda de pacientes por estado activo."""
        user1 = self.create_user("user3_unique")
        user2 = self.create_user("user4_unique")

        patient1 = PatientEntity(name="Active", is_active=True, user_id=user1.id)
        patient2 = PatientEntity(name="Inactive", is_active=False, user_id=user2.id)
        self.repository.create(patient1)
        self.repository.create(patient2)

        results = self.repository.search({"is_active": True})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Active")

    def test_search_term(self):
        """Prueba la búsqueda de pacientes por término."""
        user1 = self.create_user("user7_unique")
        user2 = self.create_user("user8_unique")

        patient1 = PatientEntity(name="John", description="Doe", user_id=user1.id)
        patient2 = PatientEntity(name="Jane", description="John", user_id=user2.id)
        self.repository.create(patient1)
        self.repository.create(patient2)

        results = self.repository.search({"search_term": "John"})
        self.assertEqual(len(results), 2)

    def test_get_deleted(self):
        """Prueba la obtención de pacientes eliminados."""
        user = self.create_user("delete_user_unique")
        patient = PatientEntity(name="Delete Me", user_id=user.id)
        created = self.repository.create(patient)
        self.repository.delete(created.id)

        deleted_patients = self.repository.get_deleted()
        self.assertEqual(len(deleted_patients), 1)
        self.assertEqual(deleted_patients[0].id, created.id)

    def test_delete(self):
        """Prueba la eliminación de un paciente."""
        user = self.create_user("delete_test_user_unique")
        patient = PatientEntity(name="Delete Me", user_id=user.id)
        created = self.repository.create(patient)
        self.repository.delete(created.id)

        with self.assertRaises(ValueError):
            self.repository.get_by_id(created.id)

        model = Patient.objects.get(id=created.id)
        self.assertIsNotNone(model.deleted_at)

    def test_deactivate_activate(self):
        """Prueba la desactivación y activación de un paciente."""
        user = self.create_user("deactivate_user_unique")

        patient = PatientEntity(name="Toggle", is_active=True, user_id=user.id)
        created = self.repository.create(patient)

        self.repository.deactivate(created.id)
        deactivated = self.repository.get_by_id(created.id)
        self.assertFalse(deactivated.is_active)

        self.repository.activate(created.id)
        activated = self.repository.get_by_id(created.id)
        self.assertTrue(activated.is_active)