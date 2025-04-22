from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from ..models import Payment
from therapists.models import Therapist
from patients.models import Patient
from unittest.mock import MagicMock, patch
from ..core.infrastructure.repository.django_payment_repository import DjangoPaymentRepository as PaymentRepository
from ..core.domain.entities.payment import PaymentEntity
from core.pagination.page_helper import PaginationInput, PaginatedResponse, PaginationMetadata
from core.exceptions.custom_exceptions import EntityNotFoundError
from django.utils import timezone
from datetime import timedelta
from core.mappers.payment.payment_mappers import PaymentMapper

class TestPaymentRepository(TestCase):
    def setUp(self):
        self.repository = PaymentRepository()
        self.User = get_user_model()
        self.mock_cache = MagicMock()
        self.repository.cache_manager = self.mock_cache

    def create_user(self, email):
        return self.User.objects.create_user(password="password", email=email)
    
    def create_payment(self, therapist=None, patient=None, amount=0, date=None) -> Payment:
        if date is None:
            date = timezone.now()
        return Payment.objects.create(paid_to=therapist, patient=patient, amount=amount, paid_at=date)
    
    def create_therapist(self, name, license_number) -> Therapist:
        return Therapist.objects.create(name=name, license_number=license_number, specialization='Test')

    def create_patient(self, name) -> Patient:
        return Patient.objects.create(name=name, description='Test')
    
    def get_test_payment_entity(self, id=None, therapist_id=None, patient_id=None, amount=0, paid_at=None):
        return PaymentEntity(
            id=id,
            patient_id=patient_id,
            paid_to_id=therapist_id,
            amount=amount,
            payment_type='TRANSFER',
            receipt_number='1234',
            paid_at=paid_at,
        )
    
    def test_save_new_payment_all_fields(self):
        # Arrange
        yesterday = timezone.now() - timedelta(days=1)
        therapist_model = self.create_therapist('John Doe', '1111111')
        patient = self.create_patient('Mary Doe')
        payment_entity = self.get_test_payment_entity(therapist_id=therapist_model.id, patient_id=patient.id, amount=150.00, paid_at=yesterday)
        
        # Act
        result = self.repository.save(payment_entity)

        # Assert
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.id)
        self.assertIsNotNone(result.updated_at)
        self.assertIsNotNone(result.created_at)
        self.assertEqual(result.amount, payment_entity.amount)
        self.assertEqual(result.paid_to_id, payment_entity.paid_to_id)
        self.assertEqual(result.patient_id, payment_entity.patient_id)

        self.mock_cache.set.assert_called_once()

    def test_save_new_payment_only_obligatory_fields(self):
        # Arrange
        payment_entity = self.get_test_payment_entity(amount=150.00, paid_at=None)

        # Act
        result = self.repository.save(payment_entity)

        # Assert
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.id)
        self.assertIsNotNone(result.updated_at)
        self.assertIsNotNone(result.created_at)
        self.assertEqual(result.amount, payment_entity.amount)
        self.assertIsNone(result.paid_to_id)
        self.assertIsNone(result.paid_at)
        self.assertIsNone(result.patient_id)

        self.mock_cache.set.assert_called_once()

    def test_save_existing_payment(self):
        # Arrange
        therapist = self.create_therapist('John Doe', '1111111')
        patient = self.create_patient('Mary Doe')
        payment = self.create_payment(therapist=therapist, patient=patient, amount=150.00)
        
        payment_entity = PaymentMapper.to_entity(payment)
        payment_entity.amount = 200.00
        
        # Act
        updated_entity = self.repository.save(payment_entity)
        
        # Assert
        self.assertEqual(updated_entity.amount, 200.00)
        self.assertEqual(updated_entity.id, payment.id)
        
        # Assert Cache
        cache_key = self.mock_cache.get_cache_key.return_value
        self.mock_cache.delete.assert_called_once_with(cache_key)
        self.mock_cache.set.assert_called_once_with(cache_key, updated_entity)
        
        # Assert DB
        refreshed_payment = Payment.objects.get(id=payment.id)
        self.assertEqual(refreshed_payment.amount, 200.00)

    def test_get_by_id_from_cache(self):
        # Arange
        payment_id = 1
        cache_key = "payment_1"
        expected_payment = self.get_test_payment_entity(id=payment_id, amount=150.00)

        self.mock_cache.get_cache_key.return_value = cache_key
        self.mock_cache.get.return_value = expected_payment

        # Act
        result = self.repository.get_by_id(payment_id)
        
        self.assertEqual(result, expected_payment)
        self.mock_cache.get_cache_key.assert_called_once_with(payment_id)
        self.mock_cache.get.assert_called_once_with(cache_key)

    def test_get_by_id_from_db(self):
        # Arrange
        payment_id = 1
        cache_key = "payment_1"
        
        # Crear un pago real en la base de datos
        therapist = self.create_therapist('John Doe', '1111111')
        patient = self.create_patient('Mary Doe')
        payment = self.create_payment(therapist=therapist, patient=patient, amount=150.00)
        payment_id = payment.id
        
        # Mock del cache_manager para que devuelva None (no hay en caché)
        self.mock_cache.get_cache_key.return_value = cache_key
        self.mock_cache.get.return_value = None
        
        # Espiamos el método _get_payment para verificar que se llama
        with patch.object(self.repository, '_get_payment', wraps=self.repository._get_payment) as spy_get_payment:
            # Act
            result = self.repository.get_by_id(payment_id)
            
            # Assert
            self.assertIsNotNone(result)
            self.assertEqual(result.amount, payment.amount)
            self.assertEqual(result.paid_to_id, therapist.id)
            self.assertEqual(result.patient_id, patient.id)
            
            # Verificar que se intentó buscar en caché pero no se encontró
            self.mock_cache.get_cache_key.assert_called_once_with(payment_id)
            self.mock_cache.get.assert_called_once_with(cache_key)
            
            # Verificar que se buscó en la base de datos
            spy_get_payment.assert_called_once_with(payment_id)

    def test_get_by_id_not_found(self):
        # Arrange
        payment_id = 99999  
        cache_key = "payment_99999"
        
        self.mock_cache.get_cache_key.return_value = cache_key
        self.mock_cache.get.return_value = None
        
        # Act/Assert
        with self.assertRaises(EntityNotFoundError):
            self.repository.get_by_id(payment_id)
            
        self.mock_cache.get_cache_key.assert_called_once_with(payment_id)
        self.mock_cache.get.assert_called_once_with(cache_key)

    def test_delete_payment_soft(self):
        # Arrange
        therapist = self.create_therapist('John Doe', '1111111')
        patient = self.create_patient('Mary Doe')
        payment = self.create_payment(therapist=therapist, patient=patient, amount=150.00)
        payment_id = payment.id
        
        with patch.object(Payment, 'set_as_deleted') as mock_set_as_deleted:
            # Act
            self.repository.delete(payment_id, soft_delete=True)
            
            # Assert
            mock_set_as_deleted.assert_called_once()
            cache_key = self.mock_cache.get_cache_key.return_value
            self.mock_cache.delete.assert_called_once_with(cache_key)

    def test_delete_payment_hard(self):
        # Arrange
        therapist = self.create_therapist('John Doe', '1111111')
        patient = self.create_patient('Mary Doe')
        payment = self.create_payment(therapist=therapist, patient=patient, amount=150.00)
        payment_id = payment.id
        
        # Act
        self.repository.delete(payment_id, soft_delete=False)
        
        # Assert
        with self.assertRaises(Payment.DoesNotExist):
            Payment.objects.get(id=payment_id)
        
        cache_key = self.mock_cache.get_cache_key.return_value
        self.mock_cache.delete.assert_called_once_with(cache_key)

    def test_get_pageable_by_therapist_id_from_cache(self):
        # Arrange
        therapist_id = 1
        pagination_input = PaginationInput(page_number=1, page_size=10)
        
        # Mock de respuesta en caché
        expected_response = PaginatedResponse(
            items=[self.get_test_payment_entity(amount=150.00)],
            metadata=PaginationMetadata(
                total_items=1,
                total_pages=1,
                current_page=1,
                page_size=10,
                has_next=False,
                has_previous=False
            )
        )
        
        cache_key = "therapist_payments_1_1_10"
        self.mock_cache.generate_search_key.return_value = cache_key
        self.mock_cache.get.return_value = expected_response
        
        # Act
        result = self.repository.get_pageable_by_therapist_id(therapist_id, pagination_input)
        
        # Assert
        self.assertEqual(result, expected_response)
        self.mock_cache.generate_search_key.assert_called_once()
        self.mock_cache.get.assert_called_once_with(cache_key)

    def test_get_pageable_by_therapist_id_from_db(self):
        # Arrange
        therapist = self.create_therapist('John Doe', '1111111')
        patient = self.create_patient('Mary Doe')
        
        # Crear varios pagos para este terapeuta
        self.create_payment(therapist=therapist, patient=patient, amount=100.00)
        self.create_payment(therapist=therapist, patient=patient, amount=200.00)
        
        pagination_input = PaginationInput(page_number=1, page_size=10)
        
        # Mock del caché para que devuelva None
        cache_key = "therapist_payments_key"
        self.mock_cache.generate_search_key.return_value = cache_key
        self.mock_cache.get.return_value = None
        
        # Act
        result = self.repository.get_pageable_by_therapist_id(therapist.id, pagination_input)
        
        # Assert
        self.assertEqual(len(result.items), 2)
        self.assertEqual(result.metadata.total_items, 2)
        
        # Verificar que se guardó en caché
        self.mock_cache.set.assert_called_once_with(cache_key, result)

    def test_get_pageable_by_patient_id_from_cache(self):
        # Arrange
        patient_id = 1
        pagination_input = PaginationInput(page_number=1, page_size=10)
        
        # Mock de respuesta en caché
        expected_response = PaginatedResponse(
            items=[self.get_test_payment_entity(amount=150.00)],
            metadata=PaginationMetadata(
                total_items=1,
                total_pages=1,
                current_page=1,
                page_size=10,
                has_next=False,
                has_previous=False
            )
        )
        
        cache_key = "patient_payments_1_1_10"
        self.mock_cache.generate_search_key.return_value = cache_key
        self.mock_cache.get.return_value = expected_response
        
        # Act
        result = self.repository.get_pageable_by_patient_id(patient_id, pagination_input)
        
        # Assert
        self.assertEqual(result, expected_response)
        self.mock_cache.generate_search_key.assert_called_once()
        self.mock_cache.get.assert_called_once_with(cache_key)

    def test_get_pageable_by_patient_id_from_db(self):
        # Arrange
        therapist = self.create_therapist('John Doe', '1111111')
        patient = self.create_patient('Mary Doe')
        
        # Crear varios pagos para este paciente
        self.create_payment(therapist=therapist, patient=patient, amount=100.00)
        self.create_payment(therapist=therapist, patient=patient, amount=200.00)
        
        pagination_input = PaginationInput(page_number=1, page_size=10)
        
        # Mock del caché para que devuelva None
        cache_key = "patient_payments_key"
        self.mock_cache.generate_search_key.return_value = cache_key
        self.mock_cache.get.return_value = None
        
        # Act
        result = self.repository.get_pageable_by_patient_id(patient.id, pagination_input)
        
        # Assert
        self.assertEqual(len(result.items), 2)
        self.assertEqual(result.metadata.total_items, 2)
        
        # Verificar que se guardó en caché
        self.mock_cache.set.assert_called_once_with(cache_key, result)