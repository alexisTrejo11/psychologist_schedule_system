from django.test import TestCase
from unittest.mock import MagicMock, patch
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from ..models import Payment
from  django.utils import timezone
from datetime import timedelta
from core.pagination.page_helper import PaginationMetadata
from core.exceptions.custom_exceptions import EntityNotFoundError

class PaymentManagerViewSetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.admin_user = User.objects.create_superuser(
                password='adminpass',
                email='admin@example.com'
            )
        cls.regular_user = User.objects.create_user(
                password='regularpass',
                email='regular@example.com'
            )

        now = timezone.now()
        yesterday = now - timedelta(days=1)
        cls.payment = Payment.objects.create(
            id=1,
            receipt_number='12345',
            amount=150.00,
            payment_type='CASH',
            paid_at=yesterday,
            created_at=now,
            updated_at=now,
        )

        cls.payment2 = Payment.objects.create(
            receipt_number='12346',
            amount=200.00,
            payment_type='CARD',
            paid_at=yesterday - timedelta(days=1),
            created_at=now,
            updated_at=now,
        )
        
        cls.payment3 = Payment.objects.create(
            receipt_number='12347',
            amount=300.00,
            payment_type='TRANSFER',
            paid_at=yesterday - timedelta(days=2),
            created_at=now,
            updated_at=now,
        )

        cls.api_client = APIClient()

    def setUp(self):
        self.access_token = AccessToken.for_user(self.admin_user)
        self.api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    

    def test_get_payment_by_id(self):
        response = self.api_client.get(f'/payments/1/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], "Payments Successfully Retrieved")
        
        therapist_data = response.data['data']
        self.assertEqual(therapist_data['id'], self.payment.id)
        self.assertEqual(therapist_data['amount'], '150.00')
        self.assertEqual(therapist_data['payment_type'], self.payment.payment_type)


    def test_get_payment_by_id_not_found(self):
        invalid_id = 9999

        response = self.api_client.get(f'/payments/{invalid_id}/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['success'])
        self.assertIn('payment not found con id: 9999', response.data['message'].lower())


    def test_retrieve_therapist_unauthenticated(self):
        # Arange
        self.api_client.credentials(HTTP_AUTHORIZATION=f'Bearer')

        # Act
        response = self.api_client.get(f'/payments/{self.payment.id}/')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('payments.core.infrastructure.api.views.payment_manager_view.SearchPaymentsUseCase')
    def test_list_payments(self, mock_search_use_case):
        mock_items = [
            Payment(
                id=1,
                receipt_number='12345',
                amount=150.00,
                payment_type='CASH',
                paid_at=timezone.now(),
                created_at=timezone.now(),
                updated_at=timezone.now(),
                deleted_at=None
            ),
            Payment(
                id=2,
                receipt_number='12346',
                amount=200.00,
                payment_type='CARD',
                paid_at=timezone.now(),
                created_at=timezone.now(),
                updated_at=timezone.now(),
                deleted_at=None
            ),
            Payment(
                id=3,
                receipt_number='12347',
                amount=300.00,
                payment_type='TRANSFER',
                paid_at=timezone.now(),
                created_at=timezone.now(),
                updated_at=timezone.now(),
                deleted_at=None
            )
        ]

        mock_metadata = PaginationMetadata(
            total_items=3,
            current_page=1,
            page_size=10,
            total_pages=1,
            has_next=False,
            has_previous=False,
        )

        # Mockear el resultado del caso de uso
        mock_result = MagicMock()
        mock_result.items = mock_items
        mock_result.metadata = mock_metadata  # Asignar la dataclass simulada

        mock_instance = mock_search_use_case.return_value
        mock_instance.execute.return_value = mock_result

        # Realizar la solicitud GET
        response = self.api_client.get('/payments/')

        # Validar la respuesta
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], "Payments Successfully Retrieved")

        # Verificar que se devuelvan todos los pagos
        payments_data = response.data['data']['items']
        self.assertEqual(len(payments_data), 3)

        # Verificar metadata de paginación
        metadata = response.data['data']['metadata']
        self.assertEqual(metadata['total_items'], 3)
        self.assertEqual(metadata['current_page'], 1)
        self.assertEqual(metadata['page_size'], 10)
        self.assertEqual(metadata['total_pages'], 1)


    def test_list_payments_unauthenticated(self):
        self.api_client.credentials(HTTP_AUTHORIZATION=f'Bearer')
        response = self.api_client.get('/payments/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    @patch('payments.core.infrastructure.api.views.payment_manager_view.CreatePaymentUseCase')
    def test_create_payment(self, mock_create_use_case):
        payment_result = MagicMock()
        payment_result.id = 4
        payment_result.receipt_number = '67890'
        payment_result.amount = '500.00'
        payment_result.payment_type = 'TRANSFER'
        payment_result.paid_at = timezone.now().isoformat()
        payment_result.created_at = timezone.now().isoformat()
        payment_result.updated_at = timezone.now().isoformat()
        payment_result.deleted_at = None
        
        mock_instance = mock_create_use_case.return_value
        mock_instance.execute.return_value = payment_result
        
        payment_data = {
            'receipt_number': '67890',
            'amount': 500.00,
            'payment_type': 'TRANSFER',
            'paid_at': timezone.now().isoformat()
        }
        
        response = self.api_client.post('/payments/', data=payment_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], "Payments Successfully Retrieved")
        
        created_payment = response.data['data']
        self.assertEqual(created_payment['receipt_number'], '67890')
        self.assertEqual(created_payment['amount'], '500.00')
        self.assertEqual(created_payment['payment_type'], 'TRANSFER')


    @patch('payments.core.infrastructure.api.views.payment_manager_view.CreatePaymentUseCase')
    def test_create_payment_with_invalid_data(self, mock_create_use_case):
        """
        Test that the view returns a 400 Bad Request when invalid data is provided.
        """
        invalid_data = {
            'receipt_number': '12345',  # Número de recibo duplicado
            'amount': -50,  # Monto inválido
            'payment_type': 'INVALID_TYPE',  # Tipo de pago inválido
            'paid_at': timezone.now().isoformat()
        }

        response = self.api_client.post('/payments/', data=invalid_data, format='json')

        # Validar la respuesta
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('errors', response.data['data'])  # Buscar 'errors' dentro de 'data'

        # Verificar los errores específicos
        errors = response.data['data']['errors']  # Acceder a los errores dentro de 'data'
        self.assertIn('amount', errors)
        self.assertEqual(errors['amount'][0], "Amount must be greater than 0")

        self.assertIn('payment_type', errors)
        self.assertIn("is not a valid choice", errors['payment_type'][0])

        self.assertIn('receipt_number', errors)
        self.assertEqual(errors['receipt_number'][0], "Receipt number already exists")

