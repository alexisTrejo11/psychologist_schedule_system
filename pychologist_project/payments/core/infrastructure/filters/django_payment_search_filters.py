from typing import Optional
from datetime import datetime
from dataclasses import dataclass
from django.db.models import Q

@dataclass
class PaymentSearchFilters:
    amount_min: Optional[float] = None
    amount_max: Optional[float] = None
    payment_type: Optional[str] = None
    receipt_number: Optional[str] = None
    paid_after: Optional[datetime] = None
    paid_before: Optional[datetime] = None
    therapist_id: Optional[int] = None
    patient_id: Optional[int] = None

    def to_query(self) -> Q:
        """
        Convierte los filtros a un objeto Q de Django para consultas
        
        Returns:
            Q: Objeto Q con los filtros aplicados
        """
        query = Q()
        
        if self.amount_min is not None:
            query &= Q(amount__gte=self.amount_min)
            
        if self.amount_max is not None:
            query &= Q(amount__lte=self.amount_max)
            
        if self.payment_type:
            query &= Q(payment_type=self.payment_type)
            
        if self.receipt_number:
            query &= Q(receipt_number__icontains=self.receipt_number)
            
        if self.paid_after:
            query &= Q(paid_at__gte=self.paid_after)
            
        if self.paid_before:
            query &= Q(paid_at__lte=self.paid_before)
            
        if self.therapist_id:
            query &= Q(paid_to_id=self.therapist_id)
            
        if self.patient_id:
            query &= Q(patient_id=self.patient_id)
            
        return query