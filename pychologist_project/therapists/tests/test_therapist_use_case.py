from django.test import TestCase
from unittest.mock import MagicMock
from datetime import datetime
from ..core.application.domain.entities.therapist import TherapistEntity
from ..core.application.therapist_use_case import GetTherapistSessionsUseCase, CreateTherapistUseCase, UpdateTherapistUseCase ,DeleteTherapistUseCase
from core.exceptions.custom_exceptions import EntityNotFoundError

class TherapistUseCaseTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Configuración inicial para todos los tests
        cls.therapist_repository = MagicMock()

        cls.sample_therapist_data = {
            "name": "John Doe",
            "license_number": "123456789",
            "specialization": "Clinic",
            "user_id": 1,
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        cls.existing_therapist_entity = TherapistEntity(
            id=1,
            user_id=1,
            name="Original Name",
            license_number="123456789",
            specialization="Clinic",
        )


    @staticmethod
    def get_test_therapist():
        # Método para crear un TherapistEntity de prueba
        return TherapistEntity(
            id=1,
            user_id=1,
            name="John Doe",
            license_number="123456789",
            specialization="Clinic"
        )

    def test_create_therapist_usecase(self):
            expected_entity = self.get_test_therapist()            
            self.therapist_repository.create.return_value = expected_entity
            use_case = CreateTherapistUseCase(therapist_repository=self.therapist_repository)


            result = use_case.execute(self.sample_therapist_data)
            
            self.assertEqual(result.user_id, expected_entity.user_id)
            self.assertEqual(result.name, expected_entity.name)
            self.assertEqual(result.license_number, expected_entity.license_number)
            self.assertEqual(result.specialization, expected_entity.specialization)


    def test_get_therapist_use_case(self):
        # Arrange
        user_case = GetTherapistSessionsUseCase(therapist_repository=self.therapist_repository)
        self.therapist_repository.get_by_id.return_value= self.get_test_therapist()

        # Act 
        result = user_case.execute(1)

        # Assert
        expected_therapist = self.get_test_therapist()
        self.assertEqual(result.id, expected_therapist.id)
        self.therapist_repository.get_by_id.assert_called_once_with(1)

    def test_delete_therapist_use_case(self):
        # Arrange
        use_case = DeleteTherapistUseCase(therapist_repository=self.therapist_repository)
        self.therapist_repository.get_by_id.return_value = self.get_test_therapist()

        # Act
        use_case.execute(1)

        # Assert
        self.therapist_repository.delete.assert_called_once_with(1)

    def test_update_therapist_success(self):
        """
        Test that the therapist is updated successfully with all fields provided.
        """
        # Arrange
        use_case = UpdateTherapistUseCase(therapist_repository=self.therapist_repository)
        updated_therapist_entity = TherapistEntity(
            id=1,
            user_id=1,
            name="Updated Name",
            license_number="987654321",
            specialization="Pediatrics",
        )
        self.therapist_repository.update.return_value = updated_therapist_entity

        # Act
        result = use_case.execute(self.existing_therapist_entity, self.sample_therapist_data)

        # Assert
        self.assertEqual(result.id, updated_therapist_entity.id)
        self.assertEqual(result.name, updated_therapist_entity.name)
        self.assertEqual(result.license_number, updated_therapist_entity.license_number)
        self.assertEqual(result.specialization, updated_therapist_entity.specialization)
        self.therapist_repository.update.assert_called_once_with(
            self.sample_therapist_data,
            self.existing_therapist_entity,
        )

    def test_update_therapist_partial_fields(self):
        """
        Test that only the provided fields are updated, leaving others unchanged.
        """
        # Arrange
        use_case = UpdateTherapistUseCase(therapist_repository=self.therapist_repository)
        partial_data = {"name": "Updated Name"}
        updated_therapist_entity = TherapistEntity(
            id=1,
            user_id=1,
            name="Updated Name",
            license_number="123456789",  # Original value
            specialization="Clinic",    # Original value
        )
        self.therapist_repository.update.return_value = updated_therapist_entity

        # Act
        result = use_case.execute(self.existing_therapist_entity, partial_data)

        # Assert
        self.assertEqual(result.name, partial_data["name"])
        self.assertEqual(result.license_number, updated_therapist_entity.license_number)
        self.assertEqual(result.specialization, updated_therapist_entity.specialization)
        self.therapist_repository.update.assert_called_once_with(
            partial_data,
            self.existing_therapist_entity,
        )