from django.test import TestCase
from unittest.mock import MagicMock
from django.utils import timezone
from ..core.application.domain.entities.patient_entitiy import Patient as PatientEntity
from ..core.infrastructure.repositories.django_patient_repository import DjangoPatientRepository
from ..models import Patient

class PatientRepositoryCacheTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Set up data for all tests."""
        cls.repository = DjangoPatientRepository()
        cls.mock_cache = MagicMock()
        cls.repository.cache_manager = cls.mock_cache

    def test_get_by_id_with_cache(self):
        """
        Test retrieving a patient by ID with caching.
        Simulates both cache miss and cache hit scenarios.
        """
        # Arrange
        self.repository.cache_manager.get_cache_key = MagicMock(return_value="patient_1")
        now = timezone.now()
        patient_model = Patient.objects.create(
            name="John Doe",
            description="Test patient",
            is_active=True,
            created_at=now,
            updated_at=now
        )
        patient_entity = PatientEntity(
            id=patient_model.id,
            name=patient_model.name,
            description=patient_model.description,
            is_active=patient_model.is_active,
            created_at=patient_model.created_at,
            updated_at=patient_model.updated_at
        )

        # Simulate cache miss
        self.mock_cache.get.return_value = None  # Cache miss
        self.mock_cache.set.return_value = None  # Simulate successful cache set

        # Act: First call (cache miss)
        result = self.repository.get_by_id(patient_model.id)

        # Assert: Data fetched from DB and cached
        self.assertEqual(result, patient_entity)
        self.mock_cache.get.assert_called_once_with("patient_1")  # Verify the correct key was used
        self.mock_cache.set.assert_called_once_with("patient_1", patient_entity)  # Verify data was cached

        # Reset mocks for second call
        self.mock_cache.reset_mock()
        self.mock_cache.get.return_value = patient_entity  # Simulate cache hit

        # Act: Second call (cache hit)
        result = self.repository.get_by_id(patient_model.id)

        # Assert: Data retrieved from cache
        self.assertEqual(result, patient_entity)
        self.mock_cache.get.assert_called_once_with("patient_1")  # Verify the correct key was used
        self.mock_cache.set.assert_not_called()  # Cache should not be updated

    def test_create_with_cache(self):
        """
        Test creating a patient with caching.
        Ensures that the patient is created and cached correctly.
        """
        # Arrange
        now = timezone.now()
        patient_entity = PatientEntity(
            name="Jane Doe",
            description="New patient",
            is_active=True,
            created_at=now,
            updated_at=now
        )

        # Mock the get_cache_key method to return a predictable key
        self.repository.cache_manager.get_cache_key = MagicMock(return_value="patient_1")
        self.mock_cache.set.return_value = None

        # Act
        created_patient = self.repository.create(patient_entity)

        # Assert: Patient is created and cached
        self.assertEqual(created_patient.name, patient_entity.name)
        self.mock_cache.set.assert_called_once_with("patient_1", created_patient)

    def test_update_with_cache(self):
        """
        Test updating a patient with caching.
        Ensures that the patient is updated and the cache is refreshed.
        """
        # Arrange
        now = timezone.now()
        patient_model = Patient.objects.create(
            name="John Doe",
            description="Test patient",
            is_active=True,
            created_at=now,
            updated_at=now
        )

        updated_entity = PatientEntity(
            id=patient_model.id,
            name="Updated Name",
            description="Updated description",
            is_active=False,
            created_at=patient_model.created_at,
            updated_at=timezone.now()
        )

        # Mock the get_cache_key method to return a predictable key
        self.repository.cache_manager.get_cache_key = MagicMock(return_value="patient_1")
        self.mock_cache.set.return_value = None

        # Act
        updated_patient = self.repository.update(updated_entity)

        # Assert: Patient is updated and cache is refreshed
        self.assertEqual(updated_patient.name, "Updated Name")
        self.mock_cache.set.assert_called_once_with("patient_1", updated_patient)

    def test_delete_with_cache(self):
        """
        Test deleting a patient with caching.
        Ensures that the cache entry is deleted and the patient is marked as deleted in the database.
        """
        # Arrange
        now = timezone.now()
        patient_model = Patient.objects.create(
            name="John Doe",
            description="Test patient",
            is_active=True,
            created_at=now,
            updated_at=now
        )

        # Create a valid PatientEntity object
        patient_entity = PatientEntity(
            id=patient_model.id,
            name=patient_model.name,
            description=patient_model.description,
            is_active=patient_model.is_active,
            created_at=patient_model.created_at,
            updated_at=patient_model.updated_at
        )

        # Mock the get_cache_key method to return a predictable key
        self.repository.cache_manager.get_cache_key = MagicMock(return_value="patient_1")

        # Simulate cache hit with a valid PatientEntity object
        self.mock_cache.get.return_value = patient_entity
        self.mock_cache.delete.return_value = None

        # Act
        self.repository.delete(patient_model.id)

        # Assert: Cache entry is deleted
        self.mock_cache.delete.assert_called_once_with("patient_1")

        # Verify the patient is marked as deleted in the database
        deleted_patient = Patient.objects.get(id=patient_model.id)
        self.assertIsNotNone(deleted_patient.deleted_at)

    def test_search_with_cache(self):
        """
        Test searching patients with caching.
        Simulates both cache miss and cache hit scenarios.
        """
        # Arrange
        now = timezone.now()
        Patient.objects.create(
            name="John Doe",
            description="Test patient",
            is_active=True,
            created_at=now,
            updated_at=now
        )

        filters = {"name": "John"}
        cache_key = "search_key_for_name_John"  # Simulate a predictable search key
        self.repository.cache_manager.generate_search_key = MagicMock(return_value=cache_key)

        self.mock_cache.get.return_value = None  # Simulate cache miss
        self.mock_cache.set.return_value = None  # Simulate successful cache set

        # Act: First call (cache miss)
        results = self.repository.search(filters)

        # Assert: Data fetched from DB and cached
        self.assertEqual(len(results), 1)
        self.mock_cache.get.assert_called_once_with(cache_key)
        self.mock_cache.set.assert_called_once_with(cache_key, results)

        # Reset mocks for second call
        self.mock_cache.reset_mock()
        self.mock_cache.get.return_value = results  # Simulate cache hit

        # Act: Second call (cache hit)
        results = self.repository.search(filters)

        # Assert: Data retrieved from cache
        self.assertEqual(len(results), 1)
        self.mock_cache.get.assert_called_once_with(cache_key)
        self.mock_cache.set.assert_not_called()  # Cache should not be updated