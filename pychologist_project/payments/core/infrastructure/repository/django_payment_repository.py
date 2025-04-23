from typing import List, Tuple, Optional
from core.cache.cache_manager import CacheManager
from payments.core.domain.entities.payment import PaymentEntity
from payments.core.domain.repository.payment_repository import PaymentRepository
from ....models import Payment                      
from ..filters.django_payment_search_filters import PaymentSearchFilters
from core.mappers.payment.payment_mappers import PaymentMapper
from core.exceptions.custom_exceptions import EntityNotFoundError
from core.pagination.page_helper import PaginationHelper, PaginationInput, PaginatedResponse

CACHE_PREFIX = 'payment_'

class DjangoPaymentRepository(PaymentRepository):
    def __init__(self):
        self.cache_manager = CacheManager(CACHE_PREFIX)
        super().__init__()

    def get_by_id(self, payment_id: int) -> Optional[PaymentEntity]:
        cache_key = self.cache_manager.get_cache_key(payment_id)
        
        payment_cache = self.cache_manager.get(cache_key)
        if payment_cache:
            return payment_cache

        payment = self._get_payment(payment_id) 

        return PaymentMapper.to_entity(payment) if payment else None


    def get_by_id_and_therapist_id(self, payment_id: int, therapist_id: int) -> Optional[PaymentEntity]:
        cache_key = self.cache_manager.get_cache_key(f"{payment_id}_therapist_{therapist_id}")
        
        payment_cache = self.cache_manager.get(cache_key)
        if payment_cache:
            return payment_cache

        payment = self._get_payment(payment_id)
        if payment and payment.paid_to_id == therapist_id:
            payment_entity = PaymentMapper.to_entity(payment)
            self.cache_manager.set(cache_key, payment_entity)
            return payment_entity

        return None

    def get_by_id_and_patient_id(self, payment_id: int, patient_id: int) -> Optional[PaymentEntity]:
        cache_key = self.cache_manager.get_cache_key(f"{payment_id}_patient_{patient_id}")
        
        payment_cache = self.cache_manager.get(cache_key)
        if payment_cache:
            return payment_cache

        payment = self._get_payment(payment_id)
        if payment and payment.patient_id == patient_id:
            payment_entity = PaymentMapper.to_entity(payment)
            self.cache_manager.set(cache_key, payment_entity)
            return payment_entity

        return None
    
    def search(self, payment_filters: dict, pagination_input : PaginationInput) -> PaginatedResponse[PaymentEntity]:
        filters = PaymentSearchFilters(
            amount_min=payment_filters.get('amount_min'),
            amount_max=payment_filters.get('amount_max'),
            payment_type=payment_filters.get('payment_type'),
            receipt_number=payment_filters.get('receipt_number'),
            paid_after=payment_filters.get('paid_after'),
            paid_before=payment_filters.get('paid_before'),
            therapist_id=payment_filters.get('therapist_id'),
            patient_id=payment_filters.get('patient_id'),
        )

        payments = Payment.objects.filter(filters.to_query()).order_by('-paid_at')
        
        return PaginationHelper.get_paginated_response(
            pagination_input,
            payments, 
            PaymentMapper.to_entity)

    def get_pageable_by_therapist_id(self, therapist_id: int, pagination_input : PaginationInput) -> PaginatedResponse[PaymentEntity]:            
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
            pagination_input,
            queryset, 
            PaymentMapper.to_entity)

        self.cache_manager.set(cache_key, paginated_response)

        return paginated_response

    def get_pageable_by_patient_id(self, patient_id: int,  pagination_input : PaginationInput) -> PaginatedResponse[PaymentEntity]:
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
            pagination_input,
            queryset, 
            PaymentMapper.to_entity)
    
        self.cache_manager.set(cache_key, paginated_response)

        return paginated_response

    def save(self, payment_entity: PaymentEntity) -> Optional[PaymentEntity]:
        if not payment_entity.id:
            return self._create(payment_entity)
        
        return self._update(payment_entity)

    def _create(self, payment_entity: PaymentEntity) -> Optional[PaymentEntity]:
        payment_model = PaymentMapper.to_model(payment_entity)
        
        payment_model.save()
        
        payment_entity = PaymentMapper.to_entity(payment_model)

        cache_key = self.cache_manager.get_cache_key(payment_model.id)
        self.cache_manager.set(cache_key, payment_entity)

        return payment_entity

    def _update(self, payment_entity: PaymentEntity) -> Optional[PaymentEntity]:
        payment_model = PaymentMapper.to_model(payment_entity)
        
        payment_model.save()

        payment_entity = PaymentMapper.to_entity(payment_model)

        cache_key = self.cache_manager.get_cache_key(payment_model.id)
        self.cache_manager.delete(cache_key)
        self.cache_manager.set(cache_key, payment_entity)

        return payment_entity

    def delete(self, payment_id: int , soft_delete=True) -> None:
        payment_model = self._get_payment(payment_id)
        if not payment_model:
            return

        if soft_delete:
            payment_model.set_as_deleted()
            payment_model.save()
        else:
            payment_model.delete()

        payment_cache_key = self.cache_manager.get_cache_key(payment_model.id)
        self.cache_manager.delete(payment_cache_key)
        
    def _get_payment(self, payment_id) -> Optional[Payment]:
        try:
            return Payment.objects.get(id=payment_id)
        except Payment.DoesNotExist:
           return None

