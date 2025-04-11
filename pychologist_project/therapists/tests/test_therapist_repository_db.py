from django.test import TestCase
from unittest.mock import MagicMock
from django.utils import timezone
from datetime import timedelta
from ..core.application.domain.entities.therapist import TherapistEntity
from users.models import User
from therapists.models import Therapist
from therapy.models import TherapySession
from ..core.infrastructure.repositories.django_therapist_repository import DjangoTherapistRepository
from core.exceptions.custom_exceptions import EntityNotFoundError

class DjangoTherapistRepositoryTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Set up data for all tests."""
        cls.repository = DjangoTherapistRepository()
        cls.mock_cache = MagicMock()
        cls.repository.cache_manager = cls.mock_cache

        # Create sample user and therapist
        cls.user = User.objects.create_user(username="therapist_user", password="password")
        cls.therapist_model = Therapist.objects.create(
            user=cls.user,
            name="Dr. Smith",
            license_number="L12345",
            specialization="Psychology"
        )

    def test_get_by_user_id_with_cache(self):
        """
        Test retrieving a therapist by user ID with caching.
        Simulates both cache miss and cache hit scenarios.
        """
        # Arrange
        cache_key = f"therapist_{self.user.id}"
        self.mock_cache.get.return_value = None  # Cache miss
        self.mock_cache.set.return_value = None

        # Act: First call (cache miss)
        result = self.repository.get_by_user_id(self.user.id)

        # Assert: Data fetched from DB and cached
        self.assertEqual(result.name, "Dr. Smith")
        self.mock_cache.get.assert_called_once_with(cache_key)
        self.mock_cache.set.assert_called_once_with(cache_key, result)

        # Reset mocks for second call
        self.mock_cache.reset_mock()
        self.mock_cache.get.return_value = result  # Cache hit

        # Act: Second call (cache hit)
        result = self.repository.get_by_user_id(self.user.id)

        # Assert: Data retrieved from cache
        self.assertEqual(result.name, "Dr. Smith")
        self.mock_cache.get.assert_called_once_with(cache_key)
        self.mock_cache.set.assert_not_called()

    def test_get_unique_patient_count_with_cache(self):
        """
        Test retrieving the count of unique patients with caching.
        Simulates both cache miss and cache hit scenarios.
        """
        # Arrange
        cache_key = f"unique_patient_count_{self.therapist_model.id}"
        self.mock_cache.get.return_value = None  # Cache miss
        self.mock_cache.set.return_value = None

        # Create sample therapy sessions
        TherapySession.objects.create(
            therapist=self.therapist_model,
            start_date=timezone.now(),
            status="SCHEDULED"
        )
        TherapySession.objects.create(
            therapist=self.therapist_model,
            start_date=timezone.now(),
            status="COMPLETED"
        )

        # Act: First call (cache miss)
        result = self.repository.get_unique_patient_count(self.therapist_model.id)

        # Assert: Data fetched from DB and cached
        self.assertEqual(result, 0)  # No patients associated yet
        self.mock_cache.get.assert_called_once_with(cache_key)
        self.mock_cache.set.assert_called_once_with(cache_key, result)

        # Reset mocks for second call
        self.mock_cache.reset_mock()
        self.mock_cache.get.return_value = result  # Cache hit

        # Act: Second call (cache hit)
        result = self.repository.get_unique_patient_count(self.therapist_model.id)

        # Assert: Data retrieved from cache
        self.assertEqual(result, 0)
        self.mock_cache.get.assert_called_once_with(cache_key)
        self.mock_cache.set.assert_not_called()

    def test_get_incoming_session_count_with_cache(self):
        """
        Test retrieving the count of incoming sessions with caching.
        Simulates both cache miss and cache hit scenarios.
        """
        # Arrange
        cache_key = f"incoming_session_count_{self.therapist_model.id}"
        self.mock_cache.get.return_value = None  # Cache miss
        self.mock_cache.set.return_value = None

        # Create sample therapy sessions
        TherapySession.objects.create(
            therapist=self.therapist_model,
            start_date=timezone.now() + timedelta(hours=1),
            status="SCHEDULED"
        )
        TherapySession.objects.create(
            therapist=self.therapist_model,
            start_date=timezone.now() - timedelta(hours=1),
            status="COMPLETED"
        )

        # Act: First call (cache miss)
        result = self.repository.get_incoming_session_count(self.therapist_model.id)

        # Assert: Data fetched from DB and cached
        self.assertEqual(result, 1)  # Only one session is scheduled and in the future
        self.mock_cache.get.assert_called_once_with(cache_key)
        self.mock_cache.set.assert_called_once_with(cache_key, result)

        # Reset mocks for second call
        self.mock_cache.reset_mock()
        self.mock_cache.get.return_value = result  # Cache hit

        # Act: Second call (cache hit)
        result = self.repository.get_incoming_session_count(self.therapist_model.id)

        # Assert: Data retrieved from cache
        self.assertEqual(result, 1)
        self.mock_cache.get.assert_called_once_with(cache_key)
        self.mock_cache.set.assert_not_called()

    def test_create_therapist(self):
        """
        Test creating a new therapist and caching the result.
        """
        # Arrange
        therapist_data = {
            "user_id": self.user.id,
            "name": "Dr. New",
            "license_number": "L67890",
            "specialization": "Neurology"
        }

        # Act
        created_therapist = self.repository.create(therapist_data)

        # Assert
        self.assertEqual(created_therapist.name, "Dr. New")
        self.assertEqual(created_therapist.license_number, "L67890")
        self.mock_cache.set.assert_called_once()

    def test_update_therapist(self):
        """
        Test updating an existing therapist and refreshing the cache.
        """
        # Arrange
        update_data = {"name": "Dr. Updated", "specialization": "Counseling"}
        cache_key = f"therapist_{self.therapist_model.id}"

        # Act
        updated_therapist = self.repository.update(update_data, self.therapist_model)

        # Assert
        self.assertEqual(updated_therapist.name, "Dr. Updated")
        self.assertEqual(updated_therapist.specialization, "Counseling")
        self.mock_cache.set.assert_called_once_with(cache_key, updated_therapist)

    def test_delete_therapist(self):
        """
        Test deleting a therapist and removing them from the cache.
        """
        # Arrange
        cache_key = f"therapist_{self.therapist_model.id}"

        # Act
        self.repository.delete(self.therapist_model.id)

        # Assert
        self.assertFalse(Therapist.objects.filter(id=self.therapist_model.id).exists())
        self.mock_cache.delete.assert_called_once_with(cache_key)

    def test_get_by_user_id_not_found(self):
        """
        Test retrieving a therapist by user ID when no therapist exists.
        """
        # Arrange
        non_existent_user_id = 999

        # Act & Assert
        with self.assertRaises(EntityNotFoundError) as context:
            self.repository.get_by_user_id(non_existent_user_id)

        self.assertIn("Therapist", str(context.exception))
        self.assertIn(str(non_existent_user_id), str(context.exception))

    def test_delete_non_existent_therapist(self):
        """
        Test deleting a therapist when no therapist exists.
        """
        # Arrange
        non_existent_therapist_id = 999

        # Act & Assert
        with self.assertRaises(EntityNotFoundError) as context:
            self.repository.delete(non_existent_therapist_id)

        self.assertIn("Therapist", str(context.exception))
        self.assertIn(str(non_existent_therapist_id), str(context.exception))