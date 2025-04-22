from datetime import datetime
from typing import Optional
from payments.core.domain.entities.payment import PaymentEntity
from payments.models import Payment      

class PaymentMapper:
    @staticmethod
    def to_entity(payment_model: Payment) -> PaymentEntity:
        """
        Convierte un objeto Payment (modelo de Django) en un objeto PaymentEntity.
        """
        return PaymentEntity(
            id=payment_model.id,
            patient_id=payment_model.patient.id if payment_model.patient else None,
            paid_to_id=payment_model.paid_to.id if payment_model.paid_to else None,
            amount=float(payment_model.amount),
            payment_type=payment_model.payment_type,
            paid_at=payment_model.paid_at,
            receipt_number=payment_model.receipt_number,
            created_at=payment_model.created_at,
            updated_at=payment_model.updated_at
        )

    @staticmethod
    def to_model(payment_entity: PaymentEntity) -> Payment:
        """
        Convierte un objeto PaymentEntity en un objeto Payment (modelo de Django).
        """
        from patients.models import Patient
        from therapists.models import Therapist
        patient = Patient.objects.get(id=payment_entity.patient_id) if payment_entity.patient_id else None
        paid_to = Therapist.objects.get(id=payment_entity.paid_to_id) if payment_entity.patient_id else None

        return Payment(
            id=payment_entity.id,
            patient=patient,
            paid_to=paid_to,
            amount=payment_entity.amount,
            payment_type=payment_entity.payment_type,
            paid_at=payment_entity.paid_at,
            receipt_number=payment_entity.receipt_number,
            created_at=payment_entity.created_at or datetime.now(),
            updated_at=payment_entity.updated_at or datetime.now()
        )