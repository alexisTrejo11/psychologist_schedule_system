from django.test import TestCase
from unittest.mock import MagicMock, patch
from datetime import datetime
from ..core.domain.entities.payment import PaymentEntity
from ..core.app.use_cases.payment_use_cases import GetPaymentUseCase, CreatePaymentUseCase, SoftDeletePaymentUseCase, UpdatePaymentUseCase
from  django.utils import timezone
from datetime import timedelta


class PaymentUseCaseTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.payment_repository = MagicMock()
        cls.patient_repository = MagicMock()

        now = timezone.now()
        yesterday = now - timedelta(days=1)
        cls.existing_payment_entity = PaymentEntity(
            id=1,
            patient_id=1,
            paid_to_id=1,
            receipt_number='12345',
            amount=150.00,
            payment_type='CASH',
            paid_at=yesterday,
            created_at=now,
            updated_at=now,
        )


    @patch('core.mappers.payment.payment_mappers.PaymentMapper.to_model')
    def test_get_payment_use_case(self, mock_to_model):
        # Arrange
        use_case = GetPaymentUseCase(payment_repository=self.payment_repository)
        self.payment_repository.get_by_id.return_value = self.existing_payment_entity
        
        mock_to_model.return_value = self.existing_payment_entity
        
        # Act
        result = use_case.execute(self.existing_payment_entity.id)
        
        # Assert
        expected_payment = self.existing_payment_entity
        self.assertIsNotNone(result)
        self.assertEqual(result, expected_payment)
        self.payment_repository.get_by_id.assert_called_once_with(self.existing_payment_entity.id)
        mock_to_model.assert_called_once_with(self.existing_payment_entity)

    @patch('core.mappers.payment.payment_mappers.PaymentMapper.to_model')
    def test_create_payment_use_case(self, mock_to_model):
        # Arrange
        use_case = CreatePaymentUseCase(payment_repository=self.payment_repository)

        now = timezone.now()
        yesterday = now - timedelta(days=1)
        incoming_new_payment = {
            'patient_id': 1,
            'paid_to_id': 1,
            'receipt_number': '54321',  
            'amount': 200.00,
            'payment_type': 'CASH',
            'paid_at': yesterday,
            'created_at': now,
            'updated_at': now,
        }

        self.payment_repository.save.return_value = self.existing_payment_entity
        mock_to_model.return_value = self.existing_payment_entity

        # Act
        result = use_case.execute(incoming_new_payment)

        # Assert
        expected_payment = self.existing_payment_entity
        self.assertIsNotNone(result)
        self.assertEqual(result.amount, expected_payment.amount)
        self.payment_repository.save.assert_called_once()
        mock_to_model.assert_called_once_with(self.existing_payment_entity)
            
    @patch('core.mappers.payment.payment_mappers.PaymentMapper.to_model')
    def test_soft_delete_payment_use_case(self, mock_to_model):
        # Arrange
        use_case = SoftDeletePaymentUseCase(payment_repository=self.payment_repository)
        payment_id = self.existing_payment_entity.id

        # Act
        use_case.execute(payment_id)

        # Assert
        self.payment_repository.soft_delete.assert_called_once_with(payment_id)            


    @patch('core.mappers.payment.payment_mappers.PaymentMapper.to_model')
    def test_update_payment_use_case(self, mock_to_model):
        # Arrange
        use_case = UpdatePaymentUseCase(payment_repository=self.payment_repository)
        payment_id = self.existing_payment_entity.id

        update_data = {
            'amount': 300.00,
            'payment_type': 'CARD'
        }

        updated_payment_entity = PaymentEntity(
            id=self.existing_payment_entity.id,
            patient_id=self.existing_payment_entity.patient_id,
            paid_to_id=self.existing_payment_entity.paid_to_id,
            receipt_number=self.existing_payment_entity.receipt_number,
            amount=update_data['amount'],
            payment_type=update_data['payment_type'],
            paid_at=self.existing_payment_entity.paid_at,
            created_at=self.existing_payment_entity.created_at,
            updated_at=self.existing_payment_entity.updated_at,
        )

        self.payment_repository.get_by_id.return_value = self.existing_payment_entity
        self.payment_repository.save.return_value = updated_payment_entity
        mock_to_model.return_value = updated_payment_entity

        # Act
        result = use_case.execute(payment_id, update_data)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.amount, update_data['amount'])
        self.assertEqual(result.payment_type, update_data['payment_type'])
        self.payment_repository.get_by_id.assert_called_once_with(payment_id)
        self.payment_repository.save.assert_called_once()
        mock_to_model.assert_called_once_with(updated_payment_entity)