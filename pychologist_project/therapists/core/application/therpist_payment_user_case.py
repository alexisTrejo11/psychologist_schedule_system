from payments.core.domain.repository.payment_repository import PaymentRepository
from payments.models import Payment
from core.exceptions.custom_exceptions import EntityNotFoundError
from core.mappers.payment.payment_mappers import PaymentMapper
from core.pagination.page_helper import PaginatedResponse, PaginationInput
from ...models import Therapist

class GetTherapistPaymentsListUseCase:
    def __init__(self, payment_repository : PaymentRepository):
        self.payment_repository = payment_repository
    
    def execute(self, therapist : Therapist, page_input : PaginationInput) -> PaginatedResponse[Payment]:
        pageable_payments = self.payment_repository.get_pageable_by_therapist_id(therapist.id, page_input)
        if len(pageable_payments.items) > 0:
            return pageable_payments

        items_mapped = [PaymentMapper.to_model(payment_entity) for payment_entity in pageable_payments.items]
        pageable_payments.items = items_mapped
        
        return pageable_payments


class GetTherapistPaymentUseCase:
    def __init__(self, payment_repository : PaymentRepository):
        self.payment_repository = payment_repository
    
    def execute(self, therapist, payment_id) -> Payment:
        payment = self.payment_repository.get_pageable_by_therapist_id(therapist.id, payment_id)
        if not payment:
            raise EntityNotFoundError('payment')

        return PaymentMapper.to_model(payment)
