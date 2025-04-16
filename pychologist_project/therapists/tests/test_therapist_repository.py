from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from ..core.application.domain.entities.therapist import TherapistEntity
from ..core.infrastructure.repositories.django_therapist_repository import DjangoTherapistRepository
from ..models import Therapist
from unittest.mock import MagicMock


class PatientRepositoryTestDB(TestCase):
    @classmethod
    def setUpTestData(self):
        self.User = get_user_model()
        self.repository = DjangoTherapistRepository()
        self.mock_cache = MagicMock()
        self.repository.cache_manager = self.mock_cache
    
    def create_user(self, email):
        """Helper to create a user."""
        return self.User.objects.create_user(password="password", email=email)
    
    def get_test_therapist_entity(self, therapist_model, user):
        now = timezone.now()
        return TherapistEntity(
            id=therapist_model.id,
            name=therapist_model.name,
            specialization=therapist_model.specialization,
            license_number=therapist_model.license_number,
            created_at=now,
            updated_at=now,
            user_id=user.id,
        )
    
    def get_test_therapist_model(self, user=None):
        return Therapist.objects.create(
            name='Test Name',
            license_number='123456789', 
            specialization='Clinic',
            user = user
        )

    def test_get_by_user_id_db(self):
        # Arrange
        user = self.create_user('create_therapist_user')
        therapist_model = self.get_test_therapist_model(user)
        therapist_entity = self.get_test_therapist_entity(therapist_model, user)

        # Mock el método get_cache_key
        self.mock_cache.get_cache_key.return_value = f"therapist_{therapist_model.user.id}"

        # Simulate cache miss
        self.mock_cache.get.return_value = None
        self.mock_cache.set.return_value = None

        # Act
        result = self.repository.get_by_user_id(therapist_model.user.id)

        # Assert
        self.assertEqual(result.id, therapist_entity.id)
        self.assertEqual(result.name, therapist_entity.name)
        self.mock_cache.get.assert_called_once_with(f"therapist_{therapist_model.user.id}")
        self.mock_cache.set.assert_called_once_with(f"therapist_{therapist_model.user.id}", therapist_entity)
        
    def test_get_by_user_id_cache(self):
        # Arrange
        user = self.create_user('create_therapist_user_1@gmail.com')
        therapist_model = self.get_test_therapist_model(user)
        therapist_entity = self.get_test_therapist_entity(therapist_model, user)

        # Mock el método get_cache_key
        self.mock_cache.get_cache_key.return_value = f"therapist_{therapist_model.user.id}"

        # Simulate cache hit
        self.mock_cache.get.return_value = therapist_entity

        # Act: Second call (cache hit)
        result = self.repository.get_by_user_id(therapist_model.user.id)

        # Assert: Data retrieved from cache
        self.assertEqual(result.id, therapist_entity.id)
        self.assertEqual(result.name, therapist_entity.name)
        self.mock_cache.get.assert_called_once_with(f"therapist_{therapist_model.user.id}")
        self.mock_cache.set.assert_not_called()  

    def test_create_therapist_with_user(self):
        # Arrange
        user = self.create_user('create_therapist_user_db@gmail.com')
        entity = TherapistEntity(user_id=user.id, name='John Doe', license_number='12345678', specialization='Clinic')

        # Mock the cache manager
        self.repository.cache_manager.get_cache_key = MagicMock(return_value="therapist_1")
        self.repository.cache_manager.set = MagicMock()

        # Act
        entity_created = self.repository.create(entity)

        # Assert
        self.assertIsNotNone(entity_created.id)
        self.assertIsNotNone(entity_created.created_at)
        self.assertIsNotNone(entity_created.updated_at)
        self.assertEqual(entity_created.name, 'John Doe')
        self.assertEqual(entity_created.user_id, user.id)

        # Verify cache behavior
        self.repository.cache_manager.set.assert_called_once_with("therapist_1", entity_created)

    def test_create_therapist_without_user(self):
        # Arrange
        entity = TherapistEntity(name='John Doe', license_number='12345678', specialization='Clinic')

        # Mock the cache manager
        self.repository.cache_manager.get_cache_key = MagicMock(return_value="therapist_1")
        self.repository.cache_manager.set = MagicMock()

        # Act
        entity_created = self.repository.create(entity)

        # Assert
        self.assertIsNotNone(entity_created.id)
        self.assertIsNotNone(entity_created.created_at)
        self.assertIsNotNone(entity_created.updated_at)
        self.assertEqual(entity_created.name, 'John Doe')
        self.assertIsNone(entity_created.user_id)

        # Verify cache behavior
        self.repository.cache_manager.set.assert_called_once_with("therapist_1", entity_created)


    def test_update_therapist(self):
        # Arrange
        entity_created = self.repository.create(TherapistEntity(name='John Doe', license_number='12345678', specialization='Clinic'))

        # Mock the cache manager
        self.repository.cache_manager.get_cache_key = MagicMock(return_value="therapist_1")
        self.repository.cache_manager.set = MagicMock()

        # Act
        entity_updated = self.repository.update({"name": 'Test123'}, entity_created)

        # Assert
        self.assertEqual(entity_updated.name, 'Test123')
        self.assertNotEqual(entity_updated.updated_at, entity_created.updated_at)

        # Verify cache behavior
        self.repository.cache_manager.set.assert_called_once_with("therapist_1", entity_updated)
    

    def test_delete_therapist_whithout_cache(self):
        # Arrange
        therapist_model = self.get_test_therapist_model()
        
        # Mock the get_cache_key method to return a predictable key
        self.repository.cache_manager.get_cache_key = MagicMock(return_value="therapist_1")
        self.repository.cache_manager.delete = MagicMock()

        # Act
        self.repository.delete(therapist_model.id)
        
        # Assert
        self.repository.cache_manager.delete.assert_called_once_with("therapist_1")
        with self.assertRaises(Therapist.DoesNotExist):
            Therapist.objects.get(id=therapist_model.id)


    def test_delete_therapist_with_cache(self):
        # Arrange
        therapist_model = self.get_test_therapist_model()
        therapist_model.id = 1

        # Mock the cache manager
        self.repository.cache_manager.get_cache_key = MagicMock(return_value="therapist_1")
        self.repository.cache_manager.delete = MagicMock()

        # Act
        self.repository.delete(therapist_model.id)

        # Assert
        self.repository.cache_manager.delete.assert_called_once_with("therapist_1")
        with self.assertRaises(Therapist.DoesNotExist):
            Therapist.objects.get(id=therapist_model.id)


