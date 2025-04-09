import pytest
from unittest.mock import MagicMock
from django.utils import timezone
from ..core.application.domain.entities.patient_entitiy import Patient as PatientEntity
from ..core.infrastructure.repositories.django_patient_repository import DjangoPatientRepository
from ..models import Patient

@pytest.mark.django_db
def test_get_by_id_with_cache():
    # Arrange
    mock_cache = MagicMock()
    repository = DjangoPatientRepository()
    repository.cache_manager = mock_cache

    # Mock the get_cache_key method to return a predictable key
    repository.cache_manager.get_cache_key = MagicMock(return_value="patient_1")

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
    mock_cache.get.return_value = None  # Cache miss
    mock_cache.set.return_value = None  # Simulate successful cache set

    # Act: First call (cache miss)
    result = repository.get_by_id(patient_model.id)

    # Assert: Data fetched from DB and cached
    assert result == patient_entity
    mock_cache.get.assert_called_once_with("patient_1")  # Verify the correct key was used
    mock_cache.set.assert_called_once_with("patient_1", patient_entity)  # Verify data was cached

    # Reset mocks for second call
    mock_cache.reset_mock()
    mock_cache.get.return_value = patient_entity  # Simulate cache hit

    # Act: Second call (cache hit)
    result = repository.get_by_id(patient_model.id)

    # Assert: Data retrieved from cache
    assert result == patient_entity
    mock_cache.get.assert_called_once_with("patient_1")  # Verify the correct key was used
    mock_cache.set.assert_not_called()  # Cache should not be updated


@pytest.mark.django_db
def test_create_with_cache():
    # Arrange
    mock_cache = MagicMock()
    repository = DjangoPatientRepository()
    repository.cache_manager = mock_cache

    now = timezone.now()
    patient_entity = PatientEntity(
        name="Jane Doe",
        description="New patient",
        is_active=True,
        created_at=now,
        updated_at=now
    )

    # Mock the get_cache_key method to return a predictable key
    repository.cache_manager.get_cache_key = MagicMock(return_value="patient_1")
    mock_cache.set.return_value = None

    # Act
    created_patient = repository.create(patient_entity)

    # Assert: Patient is created and cached
    assert created_patient.name == patient_entity.name
    mock_cache.set.assert_called_once_with("patient_1", created_patient)


@pytest.mark.django_db
def test_update_with_cache():
    # Arrange
    mock_cache = MagicMock()
    repository = DjangoPatientRepository()
    repository.cache_manager = mock_cache

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
    repository.cache_manager.get_cache_key = MagicMock(return_value="patient_1")
    mock_cache.set.return_value = None

    # Act
    updated_patient = repository.update(updated_entity)

    # Assert: Patient is updated and cache is refreshed
    assert updated_patient.name == "Updated Name"
    mock_cache.set.assert_called_once_with("patient_1", updated_patient)


@pytest.mark.django_db
def test_delete_with_cache():
    # Arrange
    mock_cache = MagicMock()
    repository = DjangoPatientRepository()
    repository.cache_manager = mock_cache

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
    repository.cache_manager.get_cache_key = MagicMock(return_value="patient_1")

    # Simulate cache hit with a valid PatientEntity object
    mock_cache.get.return_value = patient_entity
    mock_cache.delete.return_value = None

    # Act
    repository.delete(patient_model.id)

    # Assert: Cache entry is deleted
    mock_cache.delete.assert_called_once_with("patient_1")

    # Verify the patient is marked as deleted in the database
    deleted_patient = Patient.objects.get(id=patient_model.id)
    assert deleted_patient.deleted_at is not None


@pytest.mark.django_db
def test_search_with_cache():
    # Arrange
    mock_cache = MagicMock()
    repository = DjangoPatientRepository()
    repository.cache_manager = mock_cache

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
    repository.cache_manager.generate_search_key = MagicMock(return_value=cache_key)

    mock_cache.get.return_value = None  # Simulate cache miss
    mock_cache.set.return_value = None  # Simulate successful cache set

    # Act: First call (cache miss)
    results = repository.search(filters)

    # Assert: Data fetched from DB and cached
    assert len(results) == 1
    mock_cache.get.assert_called_once_with(cache_key)
    mock_cache.set.assert_called_once_with(cache_key, results)

    # Reset mocks for second call
    mock_cache.reset_mock()
    mock_cache.get.return_value = results  # Simulate cache hit

    # Act: Second call (cache hit)
    results = repository.search(filters)

    # Assert: Data retrieved from cache
    assert len(results) == 1
    mock_cache.get.assert_called_once_with(cache_key)
    mock_cache.set.assert_not_called()  # Cache should not be updated