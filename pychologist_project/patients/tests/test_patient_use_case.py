from django.test import TestCase
from unittest.mock import MagicMock
from datetime import datetime
from ..core.application.domain.entities.patient_entitiy import Patient
from ..core.application.use_cases.patient_use_cases import (
    CreatePatientUseCase,
    UpdatePatientUseCase,
    GetPatientUseCase,
    SearchPatientsUseCase,
    DeletePatientUseCase,
    DeactivatePatientUseCase,
    ActivatePatientUseCase,
    GetDeletedPatientsUseCase,
)

class PatientUseCaseTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Set up data for all tests."""
        cls.mock_patient_repository = MagicMock()

        # Sample patient data
        cls.sample_patient_data = {
            "name": "John Doe",
            "description": "Test patient",
            "user_id": 1,
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

    def test_create_patient_use_case(self):
        """
        Test creating a patient using the CreatePatientUseCase.
        Ensures that the repository's create method is called and returns the correct result.
        """
        # Arrange
        use_case = CreatePatientUseCase(patient_repository=self.mock_patient_repository)
        self.mock_patient_repository.create.return_value = Patient(
            id=1,
            name=self.sample_patient_data["name"],
            description=self.sample_patient_data["description"],
            user_id=self.sample_patient_data["user_id"],
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # Act
        result = use_case.execute(self.sample_patient_data)

        # Assert
        self.assertEqual(result.id, 1)
        self.assertEqual(result.name, self.sample_patient_data["name"])
        self.mock_patient_repository.create.assert_called_once()

    def test_update_patient_use_case(self):
        """
        Test updating a patient using the UpdatePatientUseCase.
        Ensures that the repository's update method is called and returns the correct result.
        """
        # Arrange
        patient_id = 1
        update_data = {"name": "Updated Name", "description": "Updated description"}
        existing_patient = Patient(
            id=patient_id,
            name=self.sample_patient_data["name"],
            description=self.sample_patient_data["description"],
            user_id=self.sample_patient_data["user_id"],
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.mock_patient_repository.get_by_id.return_value = existing_patient

        # Mock the update method to return an updated Patient object
        updated_patient = Patient(
            id=patient_id,
            name=update_data["name"],
            description=update_data["description"],
            user_id=self.sample_patient_data["user_id"],
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.mock_patient_repository.update.return_value = updated_patient

        use_case = UpdatePatientUseCase(patient_repository=self.mock_patient_repository)

        # Act
        result = use_case.execute(patient_id, update_data)

        # Assert
        self.assertEqual(result.name, update_data["name"])
        self.assertEqual(result.description, update_data["description"])
        self.mock_patient_repository.get_by_id.assert_called_once_with(patient_id)
        self.mock_patient_repository.update.assert_called_once()

    def test_get_patient_use_case(self):
        """
        Test retrieving a patient by ID using the GetPatientUseCase.
        Ensures that the repository's get_by_id method is called and returns the correct result.
        """
        # Arrange
        patient_id = 1
        patient_entity = Patient(
            id=patient_id,
            name=self.sample_patient_data["name"],
            description=self.sample_patient_data["description"],
            user_id=self.sample_patient_data["user_id"],
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.mock_patient_repository.get_by_id.return_value = patient_entity

        use_case = GetPatientUseCase(patient_repository=self.mock_patient_repository)

        # Act
        result = use_case.execute(patient_id)

        # Assert
        self.assertEqual(result.id, patient_id)
        self.assertEqual(result.name, self.sample_patient_data["name"])
        self.mock_patient_repository.get_by_id.assert_called_once_with(patient_id)

    def test_search_patients_use_case(self):
        """
        Test searching for patients using the SearchPatientsUseCase.
        Ensures that the repository's search method is called and returns the correct result.
        """
        # Arrange
        filters = {"name": "John"}
        patient_entity = Patient(
            id=1,
            name=self.sample_patient_data["name"],
            description=self.sample_patient_data["description"],
            user_id=self.sample_patient_data["user_id"],
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.mock_patient_repository.search.return_value = [patient_entity]

        use_case = SearchPatientsUseCase(patient_repository=self.mock_patient_repository)

        # Act
        result = use_case.execute(filters)

        # Assert
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, self.sample_patient_data["name"])
        self.mock_patient_repository.search.assert_called_once_with(filters)

    def test_delete_patient_use_case(self):
        """
        Test deleting a patient using the DeletePatientUseCase.
        Ensures that the repository's delete method is called with the correct patient ID.
        """
        # Arrange
        patient_id = 1
        use_case = DeletePatientUseCase(patient_repository=self.mock_patient_repository)

        # Act
        use_case.execute(patient_id)

        # Assert
        self.mock_patient_repository.delete.assert_called_once_with(patient_id)

    def test_deactivate_patient_use_case(self):
        """
        Test deactivating a patient using the DeactivatePatientUseCase.
        Ensures that the repository's deactivate method is called with the correct patient ID.
        """
        # Arrange
        patient_id = 1
        use_case = DeactivatePatientUseCase(patient_repository=self.mock_patient_repository)

        # Act
        use_case.execute(patient_id)

        # Assert
        self.mock_patient_repository.deactivate.assert_called_once_with(patient_id)

    def test_activate_patient_use_case(self):
        """
        Test activating a patient using the ActivatePatientUseCase.
        Ensures that the repository's activate method is called with the correct patient ID.
        """
        # Arrange
        patient_id = 1
        use_case = ActivatePatientUseCase(patient_repository=self.mock_patient_repository)

        # Act
        use_case.execute(patient_id)

        # Assert
        self.mock_patient_repository.activate.assert_called_once_with(patient_id)

    def test_get_deleted_patients_use_case(self):
        """
        Test retrieving deleted patients using the GetDeletedPatientsUseCase.
        Ensures that the repository's get_deleted method is called and returns the correct result.
        """
        # Arrange
        patient_entity = Patient(
            id=1,
            name=self.sample_patient_data["name"],
            description=self.sample_patient_data["description"],
            user_id=self.sample_patient_data["user_id"],
            is_active=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.mock_patient_repository.get_deleted.return_value = [patient_entity]

        use_case = GetDeletedPatientsUseCase(patient_repository=self.mock_patient_repository)

        # Act
        result = use_case.execute()

        # Assert
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, 1)
        self.mock_patient_repository.get_deleted.assert_called_once()