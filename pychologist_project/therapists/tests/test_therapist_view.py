from django.test import TestCase
from unittest.mock import MagicMock, patch
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from ..models import Therapist

class TherapistManagerViewSetCreateTest(TestCase):
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
        
        cls.sample_therapist_input_data = {
            "user": cls.regular_user.id, 
            "name": "Sigmund Freud",
            "license_number": "123456789",
            "specialization": "Psychoanalyst",
        }

        cls.invalid_input_data = {
            "user": cls.regular_user.id, 
            "license_number": "123456789",
            "specialization": "Psychoanalyst",
        }

        cls.sample_therapist_input_data_updated = {
            "user": cls.regular_user.id, 
            "name": "Jean Piaget",
            "license_number": "987654321",
            "specialization": "Conductism",
        }

        cls.sample_therapist_output_data = {
            'id': 1,
            "user": {
                "id": cls.regular_user.id,
                "email": cls.regular_user.email
            },
            "name": "Sigmund Freud",
            "license_number": "123456789",
            "specialization": "Psychoanalyst",
        }

        cls.sample_therapist_updated_data = Therapist(
                id = 1,
                user = cls.regular_user,
                name = "Jean Piaget",
                license_number = "987654321",
                specialization = "Conductism",
            )

        cls.api_client = APIClient()

    def setUp(self):
        self.access_token = AccessToken.for_user(self.admin_user)
        self.api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    

    @patch('therapists.core.infrastructure.adapters.views.therapist_manager_views.TherapistSerializer')
    @patch('therapists.core.application.therapist_use_case.CreateTherapistUseCase')
    def test_create_endpoint_success(self, mock_use_case, mock_serializer):
        # Arange 
        mock_serializer_instance = mock_serializer.return_value
        mock_serializer_instance.is_valid.return_value = True
        mock_serializer_instance.validated_data = self.sample_therapist_input_data
        mock_serializer_instance.data = self.sample_therapist_output_data
            
        mock_instance = mock_use_case.return_value
        mock_instance.execute.return_value = Therapist(
            id=1,
            user=self.regular_user,
            name="Sigmund Freud",
            license_number="123456789",
            specialization="Psychoanalyst"
        )

        # Acy
        response = self.api_client.post(
            '/therapists/',
            data=self.sample_therapist_input_data,
            format='json'
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        response_data = response.data['data']
        self.assertEqual(response_data['name'], "Sigmund Freud")
        self.assertEqual(response_data['license_number'], "123456789")
        self.assertEqual(response_data['specialization'], "Psychoanalyst")
        
        # User

        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], "Therapist created successfully.")



    @patch('therapists.core.infrastructure.adapters.views.therapist_manager_views.TherapistSerializer')
    @patch('therapists.core.application.therapist_use_case.CreateTherapistUseCase')
    def test_create_endpoint_invalid_input(self, mock_use_case, mock_serializer):
        from rest_framework.exceptions import ValidationError

        mock_serializer_instance = mock_serializer.return_value
        mock_serializer_instance.is_valid.side_effect = ValidationError({
            'name': ['This field is required']
        })
        
        # Realizar petición
        response = self.api_client.post(
            '/therapists/',  
            data=self.invalid_input_data,
            format='json'
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIsNotNone(str(response.data['message']))  



    @patch('therapists.core.infrastructure.adapters.views.therapist_manager_views.TherapistViewSet.get_object')
    @patch('therapists.core.infrastructure.adapters.views.therapist_manager_views.TherapistSerializer')
    @patch('therapists.core.application.therapist_use_case.UpdateTherapistUseCase')
    def test_update_endpoint_success(self, mock_use_case, mock_serializer, mock_get_object):
        # Arrange
        therapist_id = 1
        mock_serializer_instance = mock_serializer.return_value
        mock_serializer_instance.is_valid.return_value = True
        mock_serializer_instance.validated_data = self.sample_therapist_input_data_updated
        mock_serializer_instance.data = self.sample_therapist_updated_data
        mock_get_object.return_value = self.sample_therapist_output_data

        mock_instance = mock_use_case.return_value
        mock_instance.execute.return_value = self.sample_therapist_updated_data

        # Act
        url = f'/therapists/{therapist_id}/'
        response = self.api_client.put(url, self.sample_therapist_input_data_updated, format='json')
        
        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response_data = response.data['data']
        self.assertIsNotNone(response_data)
        
        self.assertEqual(response_data['name'], self.sample_therapist_updated_data['name'])
        self.assertEqual(response_data['specialization'], self.sample_therapist_updated_data['specialization'])
        self.assertEqual(response_data['license_number'], self.sample_therapist_updated_data['license_number'])

        self.assertTrue(response.data['success'])        
        self.assertIn('update', response.data['message'].lower())      


class TherapistViewSetRetieveTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.user = User.objects.create_user(
            password='testpass',
            email='test@example.com')     
        
        cls.admin_user = User.objects.create_superuser(
            password='adminpass',
            email='admin@example.com'
        )

        cls.therapist = Therapist.objects.create(
            user=cls.user,
            name='Dr. Smith',
            license_number='123456',
            specialization='Clinical Psychology'
        )

        cls.api_client = APIClient()


    def setUp(self):
        self.access_token = AccessToken.for_user(self.admin_user)
        self.api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        return super().setUp()
    
    def test_retreive_therapist_not_found(self):
        # Arange
        invalid_id = 9999
        
        # Act
        response = self.api_client.get(f'/therapists/{invalid_id}/')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['success'])
        self.assertIn('no therapist matches the given query.', response.data['message'].lower())


    def test_retrieve_therapist_success(self):
        response = self.api_client.get(f'/therapists/{self.therapist.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], "Therapist retrieved successfully.")
        
        # Verificar datos del terapeuta
        therapist_data = response.data['data']
        self.assertEqual(therapist_data['id'], self.therapist.id)
        self.assertEqual(therapist_data['name'], 'Dr. Smith')
        self.assertEqual(therapist_data['license_number'], '123456')
        self.assertEqual(therapist_data['specialization'], 'Clinical Psychology')

    def test_retrieve_therapist_unauthenticated(self):
        # Arange
        self.api_client.credentials(HTTP_AUTHORIZATION=f'Bearer')

        # Act
        response = self.api_client.get(f'/therapists/{self.therapist.id}/')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


