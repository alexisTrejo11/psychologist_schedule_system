from typing import List, Optional
from django.db import transaction
from .models import Payment
from django.db.models import Q

class PaymentService:
    """
    Servicio para manejar operaciones relacionadas con los pagos.
    """

    @staticmethod
    def get_payment_by_id(payment_id: int) -> Payment:
        """
        Obtiene un pago por su ID.
        Lanza una excepción si el pago no existe.
        """
        try:
            return Payment.objects.get(id=payment_id)
        except Payment.DoesNotExist:
            raise ValueError("Pago no encontrado")

    @staticmethod
    def get_payments_by_type(payment_type: str) -> List[Payment]:
        """
        Obtiene todos los pagos de un tipo específico.
        """
        if payment_type not in dict(Payment.PAYMENT_TYPES):
            raise ValueError("Tipo de pago inválido")
        return Payment.objects.filter(payment_type=payment_type)

    @staticmethod
    def search_payments(
        amount_min: Optional[float] = None,
        amount_max: Optional[float] = None,
        payment_type: Optional[str] = None,
        receipt_number: Optional[str] = None,
        paid_after: Optional[str] = None,  # Fecha en formato YYYY-MM-DD
        paid_before: Optional[str] = None  # Fecha en formato YYYY-MM-DD
    ) -> List[Payment]:
        """
        Realiza una búsqueda dinámica de pagos basada en filtros opcionales.
        Si no se proporcionan filtros, retorna todos los pagos.
        """
        query = Q() 
        if amount_min is not None:
            query &= Q(amount__gte=amount_min)

        if amount_max is not None:
            query &= Q(amount__lte=amount_max)

        if payment_type:
            if payment_type not in dict(Payment.PAYMENT_TYPES):
                raise ValueError("Tipo de pago inválido")
            query &= Q(payment_type=payment_type)

        if receipt_number:
            query &= Q(receipt_number=receipt_number)

        if paid_after:
            query &= Q(paid_at__date__gte=paid_after)

        if paid_before:
            query &= Q(paid_at__date__lte=paid_before)

        return Payment.objects.filter(query).order_by('-paid_at')


    @staticmethod
    def create_payment(amount: float, payment_type: str, receipt_number: str = None) -> Payment:
        """
        Crea un nuevo pago.
        Validaciones:
        - El monto debe ser mayor a 0.
        - El tipo de pago debe ser válido.
        - El número de recibo debe ser único si se proporciona.
        """
        if amount <= 0:
            raise ValueError("El monto debe ser mayor a 0")
        
        if payment_type not in dict(Payment.PAYMENT_TYPES):
            raise ValueError("Tipo de pago inválido")
        
        if receipt_number:
            if Payment.objects.filter(receipt_number=receipt_number).exists():
                raise ValueError("El número de recibo ya existe")
        
        with transaction.atomic():
            payment = Payment.objects.create(
                amount=amount,
                payment_type=payment_type,
                receipt_number=receipt_number
            )
            return payment

    @staticmethod
    def update_payment(payment_id: int, **kwargs) -> Payment:
        """
        Actualiza un pago existente.
        Parámetros permitidos: amount, payment_type, receipt_number.
        """
        try:
            payment = Payment.objects.get(id=payment_id)
        except Payment.DoesNotExist:
            raise ValueError("Pago no encontrado")
        
        with transaction.atomic():
            if 'amount' in kwargs and kwargs['amount'] <= 0:
                raise ValueError("El monto debe ser mayor a 0")
            
            if 'payment_type' in kwargs and kwargs['payment_type'] not in dict(Payment.PAYMENT_TYPES):
                raise ValueError("Tipo de pago inválido")
            
            if 'receipt_number' in kwargs and kwargs['receipt_number']:
                if Payment.objects.filter(receipt_number=kwargs['receipt_number']).exclude(id=payment_id).exists():
                    raise ValueError("El número de recibo ya existe")
            
            for key, value in kwargs.items():
                setattr(payment, key, value)
            payment.save()
            return payment

    @staticmethod
    def delete_payment(payment_id: int):
        """
        Elimina un pago existente.
        """
        try:
            payment = Payment.objects.get(id=payment_id)
        except Payment.DoesNotExist:
            raise ValueError("Pago no encontrado")
        
        with transaction.atomic():
            payment.delete()


import stripe
from django.conf import settings
from .models import Payment, StripeProduct
class StripeService:
    @staticmethod
    def create_payment_intent(amount: float, currency: str = "usd") -> dict:
        """
        Crea un PaymentIntent en Stripe.
        Retorna el client_secret para procesar el pago.
        """
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Stripe maneja cantidades en centavos
                currency=currency,
                payment_method_types=["card"],
            )
            return {
                "client_secret": intent.client_secret,
                "payment_intent_id": intent.id,
            }
        except stripe.error.StripeError as e:
            raise ValueError(f"Error al crear el pago: {str(e)}")

    @staticmethod
    def confirm_payment(payment_intent_id: str) -> bool:
        """
        Confirma un pago en Stripe.
        """
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            if intent.status == "succeeded":
                # Actualiza el estado en tu base de datos
                Payment.objects.filter(stripe_payment_intent_id=payment_intent_id).update(
                    status="COMPLETED"
                )
                return True
            return False
        except stripe.error.StripeError as e:
            raise ValueError(f"Error al confirmar el pago: {str(e)}")

    @staticmethod
    def create_stripe_product(name: str, price: float) -> StripeProduct:
        """
        Crea un producto en Stripe y lo vincula a tu base de datos.
        """
        try:
            product = stripe.Product.create(name=name)
            price = stripe.Price.create(
                product=product.id,
                unit_amount=int(price * 100),
                currency="usd",
            )
            return StripeProduct.objects.create(
                name=name,
                stripe_product_id=product.id,
                price=price.unit_amount_decimal / 100,
            )
        except stripe.error.StripeError as e:
            raise ValueError(f"Error al crear el producto en Stripe: {str(e)}")