from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from ..core.application.domain.entities.therapist import TherapistEntity
from ..core.infrastructure.repositories.django_therapist_repository import DjangoTherapistRepository
from ..models import Therapist
from unittest.mock import MagicMock, patch

class TherapistRepositoryTestDB(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        cls.repository = DjangoTherapistRepository()
        cls.mock_cache = MagicMock()
        cls.repository.cache_manager = cls.mock_cache
    
    def create_user(self, email):
        return self.User.objects.create_user(password="password", email=email)
    
    def get_test_therapist_entity(self, therapist_model, user=None):
        return TherapistEntity(
            id=therapist_model.id,
            name=therapist_model.name,
            specialization=therapist_model.specialization,
            license_number=therapist_model.license_number,
            created_at=therapist_model.created_at,
            updated_at=therapist_model.updated_at,
            user_id=user.id if user else None,
        )
    
    def get_test_therapist_model(self, user=None):
        return Therapist.objects.create(
            name='Test Name',
            license_number='123456789', 
            specialization='Clinic',
            user=user
        )

    def test_save_create_new_therapist(self):
        user = self.create_user('new_therapist_user@test.com')
        new_entity = TherapistEntity(
            user_id=user.id,
            name='New Therapist',
            license_number='NEW123',
            specialization='New Spec'
        )

        self.mock_cache.get_cache_key.return_value = "therapist_new"
        self.mock_cache.set.return_value = None

        saved_entity = self.repository.save(new_entity)

        self.assertIsNotNone(saved_entity.id)
        self.assertEqual(saved_entity.name, 'New Therapist')
        self.assertEqual(saved_entity.user_id, user.id)
        self.mock_cache.set.assert_called_once()

    def test_save_update_existing_therapist(self):
        user = self.create_user('existing_therapist_user@test.com')
        therapist_model = self.get_test_therapist_model(user)
        existing_entity = self.get_test_therapist_entity(therapist_model, user)
        
        updated_entity = TherapistEntity(
            id=existing_entity.id,
            user_id=user.id,
            name='Updated Name',
            license_number='UPDATED123',
            specialization='Updated Spec',
            created_at=existing_entity.created_at
        )

        self.mock_cache.get_cache_key.return_value = f"therapist_{existing_entity.id}"
        self.mock_cache.set.return_value = None

        saved_entity = self.repository.save(updated_entity)

        self.assertEqual(saved_entity.id, existing_entity.id)
        self.assertEqual(saved_entity.name, 'Updated Name')
        self.assertNotEqual(saved_entity.updated_at, existing_entity.updated_at)
        self.mock_cache.set.assert_called_once()

    def test_save_without_user(self):
        new_entity = TherapistEntity(
            name='No User Therapist',
            license_number='NOUSER123',
            specialization='No User Spec'
        )

        saved_entity = self.repository.save(new_entity)

        self.assertIsNotNone(saved_entity.id)
        self.assertEqual(saved_entity.name, 'No User Therapist')
        self.assertIsNone(saved_entity.user_id)

    def test_get_by_user_id_db(self):
        user = self.create_user('get_user_test@test.com')
        therapist_model = self.get_test_therapist_model(user)
        
        self.mock_cache.get.return_value = None
        self.mock_cache.get_cache_key.return_value = f"therapist_{user.id}"

        result = self.repository.get_by_user_id(user.id)

        self.assertEqual(result.id, therapist_model.id)
        self.mock_cache.set.assert_called_once()
