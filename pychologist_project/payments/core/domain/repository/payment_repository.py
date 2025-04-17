from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from payments.core.domain.entities.payment import PaymentEntity
from core.pagination.page_helper import PaginatedResponse, PaginationInput

class PaymentRepository(ABC):
    @abstractmethod
    def get_by_id(self, payment_id: int) -> PaymentEntity:
        """Retrieves a payment by its ID."""
        pass

    @abstractmethod
    def search(self, filters: dict,  page_input : PaginationInput) -> PaginatedResponse[PaymentEntity]:
        """Search payments using dinamic filters"""
        pass

    @abstractmethod
    def get_pageable_by_therapist_id(self, therapist_id: int,  page_input : PaginationInput) -> PaginatedResponse[PaymentEntity]:
        """Retieves payments by therapist id using pagination search pattern"""
        pass

    @abstractmethod
    def get_pageable_by_patient_id(self, patient_id: int,  page_input : PaginationInput) -> PaginatedResponse[PaymentEntity]:
        """Retieves payments by patient id using pagination search pattern"""
        pass


    @abstractmethod
    def save(self, payment_entity: PaymentEntity) -> PaymentEntity:
        """Save an existing payment."""
        pass

    @abstractmethod
    def delete(self, payment_id: int, soft_delete=True) -> None:
        """Delete an existing payment. Delete is by default as soft. Could be change to hard delete adding False on the parameter"""
        pass

