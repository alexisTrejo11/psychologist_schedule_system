from django.test import TestCase
from unittest.mock import MagicMock, patch
from datetime import datetime
from rest_framework.test import APIRequestFactory, Request
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from ..core.infrastructure.api.views.views import PatientViewSet
from ..core.application.domain.entities.patient_entitiy import Patient

class PatientViewSetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Set up data for all tests."""
        cls.sample_patient_data = {
            "id": 1,
            "name": "John Doe",
            "description": "Test patient",
            "user_id": 1,
            "first_therapy": None,
            "last_therapy": None,
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "deleted_at": None,
        }

        cls.patient_entity = Patient(**cls.sample_patient_data)
        cls.mock_patient_repository = MagicMock()

        # Create a PatientViewSet with mock repository
        cls.patient_viewset = PatientViewSet()
        cls.patient_viewset.create_patient_use_case = MagicMock()
        cls.patient_viewset.update_patient_use_case = MagicMock()
        cls.patient_viewset.get_patient_use_case = MagicMock()
        cls.patient_viewset.search_patients_use_case = MagicMock()
        cls.patient_viewset.delete_patient_use_case = MagicMock()
        cls.patient_viewset.deactivate_patient_use_case = MagicMock()
        cls.patient_viewset.activate_patient_use_case = MagicMock()
        cls.patient_viewset.get_deleted_patients_use_case = MagicMock()

        cls.api_request_factory = APIRequestFactory()

    def test_create_endpoint(self):
        """
        Test the create endpoint of the PatientViewSet.
        Ensures that the request is processed correctly and returns a 201 response.
        """
        # Arrange
        data = {
            "name": self.sample_patient_data["name"],
            "description": self.sample_patient_data["description"],
            "user_id": self.sample_patient_data["user_id"],
        }
        request = self.api_request_factory.post("/patients/", data=data, format="json")
        drf_request = Request(request, parsers=[JSONParser()])
        self.patient_viewset.format_kwarg = None

        with patch('rest_framework.serializers.Serializer.is_valid', return_value=True):
            with patch('rest_framework.serializers.Serializer.validated_data', new_callable=MagicMock, return_value=data):
                with patch('rest_framework.serializers.Serializer.data', new_callable=MagicMock, return_value=self.sample_patient_data):
                    self.patient_viewset.create_patient_use_case.execute.return_value = self.patient_entity
                    response = self.patient_viewset.create(drf_request)

        # Assert
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, self.sample_patient_data)
        self.patient_viewset.create_patient_use_case.execute.assert_called_once()

    def test_update_endpoint(self):
        """
        Test the update endpoint of the PatientViewSet.
        Ensures that the request is processed correctly and returns a 200 response.
        """
        # Arrange
        pk = 1
        data = {
            "name": "Updated Name",
            "description": "Updated description",
        }
        updated_patient_data = {**self.sample_patient_data, "name": "Updated Name", "description": "Updated description"}
        updated_patient = Patient(**updated_patient_data)
        request = self.api_request_factory.put(f"/patients/{pk}/", data=data, format="json")
        drf_request = Request(request, parsers=[JSONParser()])
        self.patient_viewset.format_kwarg = None

        with patch('rest_framework.serializers.Serializer.is_valid', return_value=True):
            with patch('rest_framework.serializers.Serializer.validated_data', new_callable=lambda: data):
                with patch('rest_framework.serializers.Serializer.data', new_callable=lambda: updated_patient_data):
                    self.patient_viewset.update_patient_use_case.execute.return_value = updated_patient
                    response = self.patient_viewset.update(drf_request, pk=pk)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, updated_patient_data)
        self.patient_viewset.update_patient_use_case.execute.assert_called_once_with(pk, data)

    def test_retrieve_endpoint(self):
        """
        Test the retrieve endpoint of the PatientViewSet.
        Ensures that the request is processed correctly and returns a 200 response.
        """
        # Arrange
        pk = 1
        request = self.api_request_factory.get(f"/patients/{pk}/")
        drf_request = Request(request)
        self.patient_viewset.format_kwarg = None

        with patch('rest_framework.serializers.Serializer.data', new_callable=MagicMock, return_value=self.sample_patient_data):
            self.patient_viewset.get_patient_use_case.execute.return_value = self.patient_entity
            response = self.patient_viewset.retrieve(drf_request, pk=pk)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, self.sample_patient_data)
        self.patient_viewset.get_patient_use_case.execute.assert_called_once_with(pk)

    def test_list_endpoint(self):
        """
        Test the list endpoint of the PatientViewSet.
        Ensures that the request is processed correctly and returns a 200 response.
        """
        # Arrange
        request = self.api_request_factory.get("/patients/?name=John&is_active=True")
        drf_request = Request(request)
        self.patient_viewset.format_kwarg = None

        with patch('rest_framework.serializers.ListSerializer.data', new_callable=lambda: [self.sample_patient_data]):
            self.patient_viewset.search_patients_use_case.execute.return_value = [self.patient_entity]
            response = self.patient_viewset.list(drf_request)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0], self.sample_patient_data)

    def test_delete_action(self):
        """
        Test the delete action of the PatientViewSet.
        Ensures that the request is processed correctly and returns a 204 response.
        """
        # Arrange
        pk = 1
        request = self.api_request_factory.post(f"/patients/{pk}/delete/")
        drf_request = Request(request)
        self.patient_viewset.format_kwarg = None

        response = self.patient_viewset.delete(drf_request, pk=pk)

        # Assert
        self.assertEqual(response.status_code, 204)
        self.patient_viewset.delete_patient_use_case.execute.assert_called_once_with(pk)

    def test_deactivate_action(self):
        """
        Test the deactivate action of the PatientViewSet.
        Ensures that the request is processed correctly and returns a 204 response.
        """
        # Arrange
        pk = 1
        request = self.api_request_factory.post(f"/patients/{pk}/deactivate/")
        drf_request = Request(request)
        self.patient_viewset.format_kwarg = None

        response = self.patient_viewset.deactivate(drf_request, pk=pk)

        # Assert
        self.assertEqual(response.status_code, 204)
        self.patient_viewset.deactivate_patient_use_case.execute.assert_called_once_with(pk)

    def test_activate_action(self):
        """
        Test the activate action of the PatientViewSet.
        Ensures that the request is processed correctly and returns a 204 response.
        """
        # Arrange
        pk = 1
        request = self.api_request_factory.post(f"/patients/{pk}/activate/")
        drf_request = Request(request)
        self.patient_viewset.format_kwarg = None

        response = self.patient_viewset.activate(drf_request, pk=pk)

        # Assert
        self.assertEqual(response.status_code, 204)
        self.patient_viewset.activate_patient_use_case.execute.assert_called_once_with(pk)

    def test_deleted_action(self):
        """
        Test the deleted action of the PatientViewSet.
        Ensures that the request is processed correctly and returns a 200 response.
        """
        # Arrange
        request = self.api_request_factory.get("/patients/deleted/")
        drf_request = Request(request)
        self.patient_viewset.format_kwarg = None

        with patch('rest_framework.serializers.ListSerializer.data', new_callable=MagicMock, return_value=[self.sample_patient_data]):
            self.patient_viewset.get_deleted_patients_use_case.execute.return_value = [self.patient_entity]
            response = self.patient_viewset.deleted(drf_request)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0], self.sample_patient_data)
        self.patient_viewset.get_deleted_patients_use_case.execute.assert_called_once()