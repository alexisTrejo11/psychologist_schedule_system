import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from rest_framework.test import APIRequestFactory, force_authenticate
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.request import Request
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from ..core.infrastructure.api.views.views import PatientViewSet
from ..core.application.domain.entities.patient_entitiy import Patient

@pytest.fixture
def sample_patient_data():
    """Sample patient data for tests"""
    return {
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

@pytest.fixture
def api_request_factory():
    """API request factory for tests"""
    return APIRequestFactory()

@pytest.fixture
def patient_entity(sample_patient_data):
    """Patient domain entity instance"""
    return Patient(**sample_patient_data)

@pytest.fixture
def mock_patient_repository():
    """Create a mock patient repository"""
    return MagicMock()

@pytest.fixture
def patient_viewset(mock_patient_repository):
    """Create a PatientViewSet with mock repository"""
    viewset = PatientViewSet()
    
    # Mock the use cases with the repository
    viewset.create_patient_use_case = MagicMock()
    viewset.update_patient_use_case = MagicMock()
    viewset.get_patient_use_case = MagicMock()
    viewset.search_patients_use_case = MagicMock()
    viewset.delete_patient_use_case = MagicMock()
    viewset.deactivate_patient_use_case = MagicMock()
    viewset.activate_patient_use_case = MagicMock()
    viewset.get_deleted_patients_use_case = MagicMock()
    
    return viewset

def test_create_endpoint(api_request_factory, sample_patient_data, patient_entity, patient_viewset):
    # Arrange
    data = {
        "name": sample_patient_data["name"],
        "description": sample_patient_data["description"],
        "user_id": sample_patient_data["user_id"],
    }
    
    # Create a properly formatted request
    request = api_request_factory.post("/patients/", data=data, format="json")
    
    # Set up the view with proper DRF context
    patient_viewset.format_kwarg = None
    
    # Important: Parse the request body and add it as request.data
    drf_request = Request(request, parsers=[JSONParser()])
    
    # Mock the serializer validation and creation
    with patch('rest_framework.serializers.Serializer.is_valid', return_value=True):
        with patch('rest_framework.serializers.Serializer.validated_data', new_callable=MagicMock, return_value=data):
            with patch('rest_framework.serializers.Serializer.data', new_callable=MagicMock, return_value=sample_patient_data):
                # Mock the use case to return our patient entity
                patient_viewset.create_patient_use_case.execute.return_value = patient_entity
                
                # Call the method directly with our prepared request
                response = patient_viewset.create(drf_request)
    
    # Assert
    assert response.status_code == 201
    assert response.data == sample_patient_data
    patient_viewset.create_patient_use_case.execute.assert_called_once()

def test_update_endpoint(api_request_factory, sample_patient_data, patient_entity, patient_viewset):
    # Arrange
    pk = 1
    data = {
        "name": "Updated Name",
        "description": "Updated description",
    }
    updated_patient_data = {**sample_patient_data, "name": "Updated Name", "description": "Updated description"}
    updated_patient = Patient(**updated_patient_data)

    # Create a properly formatted request
    request = api_request_factory.put(f"/patients/{pk}/", data=data, format="json")

    # Set up the view with proper DRF context
    patient_viewset.format_kwarg = None

    # Important: Parse the request body and add it as request.data
    drf_request = Request(request, parsers=[JSONParser()])

    # Mock the serializer validation and update
    with patch('rest_framework.serializers.Serializer.is_valid', return_value=True):
        with patch('rest_framework.serializers.Serializer.validated_data', new_callable=lambda: data):
            with patch('rest_framework.serializers.Serializer.data', new_callable=lambda: updated_patient_data):
                # Mock the use case to return our updated patient entity
                patient_viewset.update_patient_use_case.execute.return_value = updated_patient

                # Call the method directly with our prepared request
                response = patient_viewset.update(drf_request, pk=pk)

    # Assert
    assert response.status_code == 200
    assert response.data == updated_patient_data
    patient_viewset.update_patient_use_case.execute.assert_called_once_with(pk, data)
 
def test_retrieve_endpoint(api_request_factory, sample_patient_data, patient_entity, patient_viewset):
    # Arrange
    pk = 1
    request = api_request_factory.get(f"/patients/{pk}/")
    
    # Set up the view with proper DRF context
    patient_viewset.format_kwarg = None
    
    # Create proper DRF request
    drf_request = Request(request)
    
    # Mock the serializer response
    with patch('rest_framework.serializers.Serializer.data', new_callable=MagicMock, return_value=sample_patient_data):
        # Mock the use case to return our patient entity
        patient_viewset.get_patient_use_case.execute.return_value = patient_entity
        
        # Call the method directly with our prepared request
        response = patient_viewset.retrieve(drf_request, pk=pk)
    
    # Assert
    assert response.status_code == 200
    assert response.data == sample_patient_data
    patient_viewset.get_patient_use_case.execute.assert_called_once_with(pk)

def test_list_endpoint(api_request_factory, sample_patient_data, patient_entity, patient_viewset):
    # Arrange
    # Create a GET request with query parameters
    request = api_request_factory.get("/patients/?name=John&is_active=True")

    # Set up the view with proper DRF context
    patient_viewset.format_kwarg = None

    # Create a proper DRF request (query_params will be parsed automatically)
    drf_request = Request(request)

    # Mock the serializer response for a list
    with patch('rest_framework.serializers.ListSerializer.data', new_callable=lambda: [sample_patient_data]):
        # Mock the use case to return a list containing our patient entity
        patient_viewset.search_patients_use_case.execute.return_value = [patient_entity]

        # Call the method directly with our prepared request
        response = patient_viewset.list(drf_request)

    # Assert
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0] == sample_patient_data


def test_delete_action(api_request_factory, patient_viewset):
    # Arrange
    pk = 1
    request = api_request_factory.post(f"/patients/{pk}/delete/")
    
    # Create proper DRF request
    drf_request = Request(request)
    
    # Call the method directly
    response = patient_viewset.delete(drf_request, pk=pk)
    
    # Assert
    assert response.status_code == 204
    patient_viewset.delete_patient_use_case.execute.assert_called_once_with(pk)

def test_deactivate_action(api_request_factory, patient_viewset):
    # Arrange
    pk = 1
    request = api_request_factory.post(f"/patients/{pk}/deactivate/")
    
    # Create proper DRF request
    drf_request = Request(request)
    
    # Call the method directly
    response = patient_viewset.deactivate(drf_request, pk=pk)
    
    # Assert
    assert response.status_code == 204
    patient_viewset.deactivate_patient_use_case.execute.assert_called_once_with(pk)

def test_activate_action(api_request_factory, patient_viewset):
    # Arrange
    pk = 1
    request = api_request_factory.post(f"/patients/{pk}/activate/")
    
    # Create proper DRF request
    drf_request = Request(request)
    
    # Call the method directly
    response = patient_viewset.activate(drf_request, pk=pk)
    
    # Assert
    assert response.status_code == 204
    patient_viewset.activate_patient_use_case.execute.assert_called_once_with(pk)

def test_deleted_action(api_request_factory, sample_patient_data, patient_entity, patient_viewset):
    # Arrange
    request = api_request_factory.get("/patients/deleted/")
    
    # Set up the view with proper DRF context
    patient_viewset.format_kwarg = None
    
    # Create proper DRF request
    drf_request = Request(request)
    
    # Mock the serializer response for a list
    with patch('rest_framework.serializers.ListSerializer.data', new_callable=MagicMock, return_value=[sample_patient_data]):
        # Mock the use case to return a list containing our patient entity
        patient_viewset.get_deleted_patients_use_case.execute.return_value = [patient_entity]
        
        # Call the method directly with our prepared request
        response = patient_viewset.deleted(drf_request)
    
    # Assert
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0] == sample_patient_data
    patient_viewset.get_deleted_patients_use_case.execute.assert_called_once()