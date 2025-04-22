from typing import Dict, List
from ...domain.repository.payment_repository import PaymentRepository
from ...domain.entities.payment import PaymentEntity
from ..stripe_services import StripeServiceInterface
from ....models import Payment as PaymentModel
from core.pagination.page_helper import PaginatedResponse
from core.mappers.payment.payment_mappers import PaymentMapper
from core.pagination.page_helper import PaginationInput
from ....models import PAYMENT_TYPES
from core.exceptions.custom_exceptions import EntityNotFoundError


# Map?
class GetPaymentUseCase:
    def __init__(self, payment_repository: PaymentRepository):
        self.repository = payment_repository

    def execute(self, payment_id: int) -> PaymentModel:
        payment_model = self.repository.get_by_id(payment_id)
        return PaymentMapper.to_model(payment_model)


class SearchPaymentsUseCase:
    def __init__(self, payment_repository: PaymentRepository):
        self.repository = payment_repository

    def execute(self, payment_filters: Dict, page_input : PaginationInput) -> PaginatedResponse[PaymentModel]:
        self._validate_payment_params(payment_filters)

        paginated_data = self.repository.search(payment_filters, page_input)
        if len(paginated_data.items) > 0:    
            itemsMapped = [PaymentMapper.to_model(payment_entity) for payment_entity in paginated_data.items] 
            paginated_data.items = itemsMapped
    
        return paginated_data

    #TODO: Move
    def _validate_payment_params(self, payment_filters: dict) -> None:
        """
        Valida que los filtros sean correctos
        
        Args:
            payment_filters: Diccionario con las propiedades, las cuales serán sometidas a validación 
            
        Raises:
            ValueError: Si algún filtro no es válido
        """
        if not payment_filters:
            return
        # Validar amount_min
        amount_min = payment_filters.get('amount_min')
        if amount_min is not None:
            if not isinstance(amount_min, (int, float)):
                raise ValueError("El monto mínimo debe ser un número")
            if amount_min < 0:
                raise ValueError("El monto mínimo no puede ser negativo")

        # Validar amount_max
        amount_max = payment_filters.get('amount_max')
        if amount_max is not None:
            if not isinstance(amount_max, (int, float)):
                raise ValueError("El monto máximo debe ser un número")
            if amount_max < 0:
                raise ValueError("El monto máximo no puede ser negativo")

        # Validar relación entre amount_min y amount_max
        if amount_min is not None and amount_max is not None:
            if amount_min > amount_max:
                raise ValueError("El monto mínimo no puede ser mayor al máximo")

        # Validar payment_type
        payment_type = payment_filters.get('payment_type')
        if payment_type is not None:
            if payment_type not in PAYMENT_TYPES:
                raise ValueError(f"Tipo de pago inválido. Válidos: {list(PAYMENT_TYPES.keys())}")

        # Validar paid_after y paid_before
        paid_after = payment_filters.get('paid_after')
        paid_before = payment_filters.get('paid_before')
        if paid_after is not None and paid_before is not None:
            if paid_after > paid_before:
                raise ValueError("La fecha 'después' no puede ser mayor a la fecha 'antes'")


class CreatePaymentUseCase:
    def __init__(self, payment_repository: PaymentRepository):
        self.repository = payment_repository

    def execute(self, payment_data: Dict) -> PaymentModel:
        payment = PaymentEntity(**payment_data)
        payment_model = self.repository.save(payment)
        return PaymentMapper.to_model(payment_model)


class UpdatePaymentUseCase:
    def __init__(self, payment_repository: PaymentRepository):
        self.repository = payment_repository

    def execute(self, payment_id: int, update_data: Dict) -> PaymentModel:
        existing_payment = self.repository.get_by_id(payment_id)
        if not existing_payment:
            raise EntityNotFoundError(f"Payment with id {payment_id} not found")

        public_attributes = {
            "id": existing_payment.id,
            "patient_id": existing_payment.patient_id,
            "paid_to_id": existing_payment.paid_to_id,
            "amount": existing_payment.amount,
            "payment_type": existing_payment.payment_type,
            "paid_at": existing_payment.paid_at,
            "receipt_number": existing_payment.receipt_number,
            "created_at": existing_payment.created_at,
            "updated_at": existing_payment.updated_at,
        }

        updated_attributes = {**public_attributes, **update_data}

        updated_payment = PaymentEntity(**updated_attributes)

        payment_model = self.repository.save(updated_payment)
        
        return PaymentMapper.to_model(payment_model)


class SoftDeletePaymentUseCase:
    def __init__(self, payment_repository: PaymentRepository):
        self.repository = payment_repository

    def execute(self, payment_id: int) -> None:
        self.repository.soft_delete(payment_id)


class ProcessStripePaymentUseCase:
    def __init__(self, stripe_service: StripeServiceInterface):
        self.stripe_service = stripe_service

    def execute(self, amount: float, currency: str = "usd") -> Dict:
        return self.stripe_service.create_payment_intent(amount, currency)


class ConfirmStripePaymentUseCase:
    def __init__(self, stripe_service: StripeServiceInterface):
        self.stripe_service = stripe_service

    def execute(self, payment_intent_id: str) -> bool:
        return self.stripe_service.confirm_payment(payment_intent_id)


class CreateStripeProductUseCase:
    def __init__(self, stripe_service: StripeServiceInterface):
        self.stripe_service = stripe_service

    def execute(self, name: str, price: float) -> Dict:
        return self.stripe_service.create_product(name, price)