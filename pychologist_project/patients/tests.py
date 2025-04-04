from django.test import TestCase

import pytest
from datetime import datetime, timedelta
from django.db import IntegrityError
from unittest.mock import Mock
from .core.application.domain.entities.patient_entitiy import Patient as PatientEntity
from .core.infrastructure.repositories.django_patient_repository import DjangoPatientRepository
from .models import Patient as PatientModel

@pytest.fixture
def repository():
    return DjangoPatientRepository()

@pytest.mark.django_db
def test_create_patient(repository):
    patient_data = PatientEntity(
        name="John Doe",
        description="Test patient",
        first_therapy=datetime.now(),
        last_therapy=datetime.now(),
        is_active=True,
        user_id=1
    )
    created_patient = repository.create(patient_data)
    
    model = PatientModel.objects.get(id=created_patient.id)
    assert model.name == "John Doe"
    assert created_patient.user_id == 1

@pytest.mark.django_db
def test_update_patient(repository):
    patient = PatientEntity(name="Original", description="Original desc")
    created = repository.create(patient)
    
    created.name = "Updated"
    updated_patient = repository.update(created)
    
    model = PatientModel.objects.get(id=created.id)
    assert model.name == "Updated"
    assert updated_patient.description == "Original desc"

@pytest.mark.django_db
def test_get_by_id_existing(repository):
    patient = PatientEntity(name="Test")
    created = repository.create(patient)
    
    retrieved = repository.get_by_id(created.id)
    assert retrieved.id == created.id

@pytest.mark.django_db
def test_get_by_id_not_found(repository):
    with pytest.raises(ValueError, match="Paciente no encontrado"):
        repository.get_by_id(999)

@pytest.mark.django_db
def test_search_by_name(repository):
    patient1 = PatientEntity(name="John Doe")
    patient2 = PatientEntity(name="Jane Smith")
    repository.create(patient1)
    repository.create(patient2)
    
    results = repository.search({"name": "John"})
    assert len(results) == 1
    assert results[0].name == "John Doe"

@pytest.mark.django_db
def test_search_by_is_active(repository):
    patient1 = PatientEntity(name="Active", is_active=True)
    patient2 = PatientEntity(name="Inactive", is_active=False)
    repository.create(patient1)
    repository.create(patient2)
    
    results = repository.search({"is_active": True})
    assert len(results) == 1
    assert results[0].name == "Active"

@pytest.mark.django_db
def test_search_date_filters(repository):
    now = datetime.now()
    patient1 = PatientEntity(name="Old", created_at=now)
    patient2 = PatientEntity(name="New", created_at=now + timedelta(days=1))
    repository.create(patient1)
    repository.create(patient2)
    
    results = repository.search({"created_after": now.strftime('%Y-%m-%d')})
    assert len(results) == 1
    assert results[0].name == "New"

@pytest.mark.django_db
def test_search_term(repository):
    patient1 = PatientEntity(name="John", description="Doe")
    patient2 = PatientEntity(name="Jane", description="John")
    repository.create(patient1)
    repository.create(patient2)
    
    results = repository.search({"search_term": "John"})
    assert len(results) == 2

@pytest.mark.django_db
def test_get_deleted(repository):
    patient = PatientEntity(name="Delete Me")
    created = repository.create(patient)
    repository.delete(created.id)
    
    deleted_patients = repository.get_deleted()
    assert len(deleted_patients) == 1
    assert deleted_patients[0].id == created.id

@pytest.mark.django_db
def test_delete(repository):
    patient = PatientEntity(name="Delete Me")
    created = repository.create(patient)
    repository.delete(created.id)
    
    with pytest.raises(ValueError):
        repository.get_by_id(created.id)
    
    model = PatientModel.objects.get(id=created.id)
    assert model.deleted_at is not None

@pytest.mark.django_db
def test_deactivate_activate(repository):
    patient = PatientEntity(name="Toggle", is_active=True)
    created = repository.create(patient)
    
    repository.deactivate(created.id)
    deactivated = repository.get_by_id(created.id)
    assert not deactivated.is_active
    
    repository.activate(created.id)
    activated = repository.get_by_id(created.id)
    assert activated.is_active
