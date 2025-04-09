import pytest
from unittest.mock import MagicMock
from datetime import datetime
from ..core.application.domain.entities.patient_entitiy import Patient
from ..core.application.use_cases.patient_use_cases import (
    CreatePatientUseCase,
    UpdatePatientUseCase,
    GetPatientUseCase,
    SearchPatientsUseCase,
    DeletePatientUseCase,
    DeactivatePatientUseCase,
    ActivatePatientUseCase,
    GetDeletedPatientsUseCase,
)

@pytest.fixture
def mock_patient_repository():
    return MagicMock()

@pytest.fixture
def sample_patient_data():
    return {
        "name": "John Doe",
        "description": "Test patient",
        "user_id": 1,
        "is_active": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }


def test_create_patient_use_case(mock_patient_repository, sample_patient_data):
    # Arrange
    use_case = CreatePatientUseCase(patient_repository=mock_patient_repository)
    mock_patient_repository.create.return_value = Patient(
        id=1,
        name=sample_patient_data["name"],
        description=sample_patient_data["description"],
        user_id=sample_patient_data["user_id"],
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    # Act
    result = use_case.execute(sample_patient_data)

    # Assert
    assert result.id == 1
    assert result.name == sample_patient_data["name"]
    mock_patient_repository.create.assert_called_once()


def test_update_patient_use_case(mock_patient_repository, sample_patient_data):
    # Arrange
    patient_id = 1
    update_data = {"name": "Updated Name", "description": "Updated description"}
    existing_patient = Patient(
        id=patient_id,
        name=sample_patient_data["name"],
        description=sample_patient_data["description"],
        user_id=sample_patient_data["user_id"],
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    mock_patient_repository.get_by_id.return_value = existing_patient

    # Mock the update method to return an updated Patient object
    updated_patient = Patient(
        id=patient_id,
        name=update_data["name"],
        description=update_data["description"],
        user_id=sample_patient_data["user_id"],
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    mock_patient_repository.update.return_value = updated_patient

    use_case = UpdatePatientUseCase(patient_repository=mock_patient_repository)

    # Act
    result = use_case.execute(patient_id, update_data)

    # Assert
    assert result.name == update_data["name"]
    assert result.description == update_data["description"]
    mock_patient_repository.get_by_id.assert_called_once_with(patient_id)
    mock_patient_repository.update.assert_called_once()


def test_get_patient_use_case(mock_patient_repository, sample_patient_data):
    # Arrange
    patient_id = 1
    patient_entity = Patient(
        id=patient_id,
        name=sample_patient_data["name"],
        description=sample_patient_data["description"],
        user_id=sample_patient_data["user_id"],
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    mock_patient_repository.get_by_id.return_value = patient_entity

    use_case = GetPatientUseCase(patient_repository=mock_patient_repository)

    # Act
    result = use_case.execute(patient_id)

    # Assert
    assert result.id == patient_id
    assert result.name == sample_patient_data["name"]
    mock_patient_repository.get_by_id.assert_called_once_with(patient_id)


def test_search_patients_use_case(mock_patient_repository, sample_patient_data):
    # Arrange
    filters = {"name": "John"}
    patient_entity = Patient(
        id=1,
        name=sample_patient_data["name"],
        description=sample_patient_data["description"],
        user_id=sample_patient_data["user_id"],
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    mock_patient_repository.search.return_value = [patient_entity]

    use_case = SearchPatientsUseCase(patient_repository=mock_patient_repository)

    # Act
    result = use_case.execute(filters)

    # Assert
    assert len(result) == 1
    assert result[0].name == sample_patient_data["name"]
    mock_patient_repository.search.assert_called_once_with(filters)


def test_delete_patient_use_case(mock_patient_repository):
    # Arrange
    patient_id = 1
    use_case = DeletePatientUseCase(patient_repository=mock_patient_repository)

    # Act
    use_case.execute(patient_id)

    # Assert
    mock_patient_repository.delete.assert_called_once_with(patient_id)


def test_deactivate_patient_use_case(mock_patient_repository):
    # Arrange
    patient_id = 1
    use_case = DeactivatePatientUseCase(patient_repository=mock_patient_repository)

    # Act
    use_case.execute(patient_id)

    # Assert
    mock_patient_repository.deactivate.assert_called_once_with(patient_id)


def test_activate_patient_use_case(mock_patient_repository):
    # Arrange
    patient_id = 1
    use_case = ActivatePatientUseCase(patient_repository=mock_patient_repository)

    # Act
    use_case.execute(patient_id)

    # Assert
    mock_patient_repository.activate.assert_called_once_with(patient_id)


def test_get_deleted_patients_use_case(mock_patient_repository, sample_patient_data):
    # Arrange
    patient_entity = Patient(
        id=1,
        name=sample_patient_data["name"],
        description=sample_patient_data["description"],
        user_id=sample_patient_data["user_id"],
        is_active=False,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    mock_patient_repository.get_deleted.return_value = [patient_entity]

    use_case = GetDeletedPatientsUseCase(patient_repository=mock_patient_repository)

    # Act
    result = use_case.execute()

    # Assert
    assert len(result) == 1
    assert result[0].id == 1
    mock_patient_repository.get_deleted.assert_called_once()