import pytest
from datetime import timedelta
from django.utils import timezone
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from ..core.application.domain.entities.patient_entitiy import Patient as PatientEntity
from ..core.infrastructure.repositories.django_patient_repository import DjangoPatientRepository
from ..models import Patient

@pytest.fixture
def create_user():
    """Fixture para crear usuarios únicos."""
    def _create_user(username):
        User = get_user_model()
        return User.objects.create_user(username=username, password="password")
    return _create_user

@pytest.fixture
def repository():
    return DjangoPatientRepository()

@pytest.mark.django_db
def test_create_patient(create_user, repository):
    user = create_user("testuser_unique")
    patient_data = PatientEntity(
        name="John Doe",
        description="Test patient",
        first_therapy=timezone.now(),
        last_therapy=timezone.now(),
        is_active=True,
        user_id=user.id
    )
    created_patient = repository.create(patient_data)
    model = repository.get_by_id(created_patient.id)
    assert model.name == "John Doe"
    assert created_patient.user_id == user.id

@pytest.mark.django_db
def test_update_patient(create_user, repository):
    user = create_user("update_user_unique")
    patient = PatientEntity(name="Original", description="Original desc", user_id=user.id)
    created = repository.create(patient)
    
    created.name = "Updated"
    updated_patient = repository.update(created)
    
    model = repository.get_by_id(created.id)
    assert model.name == "Updated"
    assert updated_patient.description == "Original desc"

@pytest.mark.django_db
def test_get_by_id_existing(create_user, repository):
    user = create_user("get_by_id_user_unique")
    patient = PatientEntity(name="Test", user_id=user.id)
    created = repository.create(patient)
    
    retrieved = repository.get_by_id(created.id)
    assert retrieved.id == created.id

@pytest.mark.django_db
def test_get_by_id_not_found(repository):
    with pytest.raises(ValueError, match="Patient with ID 999 not found."):
        repository.get_by_id(999)

@pytest.mark.django_db
def test_search_by_name(create_user, repository):
    user1 = create_user("user1_unique")
    user2 = create_user("user2_unique")
    
    patient1 = PatientEntity(name="John Doe", user_id=user1.id)
    patient2 = PatientEntity(name="Jane Smith", user_id=user2.id)
    repository.create(patient1)
    repository.create(patient2)
    
    results = repository.search({"name": "John"})
    assert len(results) == 1
    assert results[0].name == "John Doe"

@pytest.mark.django_db
def test_search_by_is_active(create_user, repository):
    user1 = create_user("user3_unique")
    user2 = create_user("user4_unique")
    
    patient1 = PatientEntity(name="Active", is_active=True, user_id=user1.id)
    patient2 = PatientEntity(name="Inactive", is_active=False, user_id=user2.id)
    repository.create(patient1)
    repository.create(patient2)
    
    results = repository.search({"is_active": True})
    assert len(results) == 1
    assert results[0].name == "Active"


@pytest.mark.django_db
def test_search_term(create_user, repository):
    user1 = create_user("user7_unique")
    user2 = create_user("user8_unique")
    
    patient1 = PatientEntity(name="John", description="Doe", user_id=user1.id)
    patient2 = PatientEntity(name="Jane", description="John", user_id=user2.id)
    repository.create(patient1)
    repository.create(patient2)
    
    results = repository.search({"search_term": "John"})
    assert len(results) == 2

@pytest.mark.django_db
def test_get_deleted(create_user, repository):
    user = create_user("delete_user_unique")
    patient = PatientEntity(name="Delete Me", user_id=user.id)
    created = repository.create(patient)
    repository.delete(created.id)
    
    deleted_patients = repository.get_deleted()
    assert len(deleted_patients) == 1
    assert deleted_patients[0].id == created.id

@pytest.mark.django_db
def test_delete(create_user, repository):
    user = create_user("delete_test_user_unique")
    patient = PatientEntity(name="Delete Me", user_id=user.id)
    created = repository.create(patient)
    repository.delete(created.id)
    
    with pytest.raises(ValueError):
        repository.get_by_id(created.id)
    
    model = Patient.objects.get(id=created.id)
    assert model.deleted_at is not None

@pytest.mark.django_db
def test_deactivate_activate(create_user, repository):
    user = create_user("deactivate_user_unique")
    
    patient = PatientEntity(name="Toggle", is_active=True, user_id=user.id)
    created = repository.create(patient)
    
    repository.deactivate(created.id)
    deactivated = repository.get_by_id(created.id)
    assert not deactivated.is_active
    
    repository.activate(created.id)
    activated = repository.get_by_id(created.id)
    assert activated.is_active


