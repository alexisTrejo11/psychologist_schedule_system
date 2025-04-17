from typing import List, Tuple
from core.cache.cache_manager import CacheManager
from payments.core.domain.entities.payment import PaymentEntity
from payments.core.domain.repository.payment_repository import PaymentRepository
from ....models import Payment                      
from core.mappers.payment.payment_mappers import PaymentMapper
from core.exceptions.custom_exceptions import EntityNotFoundError
from core.pagination.page_helper import PaginationHelper, PaginationInput, PaginatedResponse
from ..filters.django_payment_search_filters import PaymentSearchFilters

CACHE_PREFIX = 'payment_'

class DjangoPaymentRepository(PaymentRepository):
    def __init__(self):
        self.cache_manager = CacheManager(CACHE_PREFIX)
        super().__init__()

    def get_by_id(self, payment_id: int) -> PaymentEntity:
        cache_key = self.cache_manager.get_cache_key(payment_id)
        payment_cache = self.cache_manager.get(cache_key)
        if payment_cache:
            return payment_cache

        payment = self._get_payment(payment_id)

        return PaymentMapper.to_entity(payment)
    
    def search(self, payment_filters: dict, pagination_input : PaginationInput) -> PaginatedResponse[PaymentEntity]:
        query = PaymentSearchFilters(
            amount_max=payment_filters['amount_max'],
            amount_min=payment_filters['amount_min'],
            paid_before=payment_filters['paid_before'],
            paid_after=payment_filters['paid_after'],
            patient_id=payment_filters['patient_id'],
            therapist_id=payment_filters['therapist_id'],
            receipt_number=payment_filters['receipt_number'],
            payment_type=payment_filters['payment_type'],
        )

        payments = Payment.objects.filter(query).order_by('-paid-at')
        
        return PaginationHelper.get_paginated_response(
            payments, 
            pagination_input,
            PaymentMapper.to_entity)

    def get_paginated_by_therapist_id(self, therapist_id: int, pagination_input : PaginationInput) -> PaginatedResponse[PaymentEntity]:            
        queryset = Payment.objects.filter(
            paid_to_id=therapist_id
        ).order_by('-paid_at')

        cache_key = self.cache_manager.generate_search_key({
        "therapist_id": therapist_id,
        "page_number": pagination_input.page_number,
        "page_size": pagination_input.page_size
        })

        cached_response = self.cache_manager.get(cache_key)
        if cached_response:
            return cached_response

        paginated_response = PaginationHelper.get_paginated_response(
            queryset, 
            pagination_input,
            PaymentMapper.to_entity)

        self.cache_manager.set(cache_key, paginated_response)

        return paginated_response

    def get_by_patient_id_pageable(self, patient_id: int,  pagination_input : PaginationInput) -> PaginationHelper[PaymentEntity]:
        queryset = Payment.objects.filter(
            patient_id=patient_id
        ).order_by('-paid_at')
        
        cache_key = self.cache_manager.generate_search_key({
            "therapist_id": patient_id,
            "page_number": pagination_input.page_number,
            "page_size": pagination_input.page_size
            })

        cached_response = self.cache_manager.get(cache_key)
        if cached_response:
            return cached_response

        paginated_response = PaginationHelper.get_paginated_response(
            queryset, 
            pagination_input,
            PaymentMapper.to_entity)
    
        self.cache_manager.set(cache_key, paginated_response)

        return paginated_response

    def save(self, payment_entity: PaymentEntity) -> PaymentEntity:
        if not payment_entity.id:
            return self._create(payment_entity)
        
        return self._update(payment_entity)

    def _create(self, payment_entity: PaymentEntity) -> PaymentEntity:
        payment_model = PaymentMapper.to_model(payment_entity)
        
        payment_model.save()
        
        payment_entity = PaymentMapper.to_entity(payment_model)

        cache_key = self.cache_manager.get_cache_key(payment_model.id)
        self.cache_manager.set(cache_key, payment_entity)

        return payment_entity

    def _update(self, payment_entity: PaymentEntity) -> PaymentEntity:
        payment_model = PaymentMapper.to_model(payment_entity)
        
        payment_model.save()

        payment_entity = PaymentMapper.to_entity(payment_model)

        cache_key = self.cache_manager.get_cache_key(payment_model.id)
        self.cache_manager.delete(cache_key)
        self.cache_manager.set(cache_key, payment_entity)

        return payment_entity

    def delete(self, payment_id: int , soft_delete=True) -> None:
        payment_model = self._get_payment(payment_id)
        
        if soft_delete:
            payment_model.set_as_deleted()
            payment_model.save()
        else:
            payment_model.delete()

        payment_cache_key = self.cache_manager.get_cache_key(payment_model.id)
        self.cache_manager.delete(payment_cache_key)
        
    def _get_payment(self, payment_id):
        try:
            return Payment.objects.get(id=payment_id)
        except Payment.DoesNotExist:
            raise EntityNotFoundError('payment', payment_id)
