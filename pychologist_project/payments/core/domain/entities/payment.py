from datetime import datetime
from typing import Optional
from core.exceptions.custom_exceptions import DomainError

class PaymentEntity:
    MAX_AMOUNT_LIMIT = 10000
    MIN_AMOUNT_LIMIT = 10

    def __init__(
        self,
        id: Optional[int] = None,
        patient_id: Optional[int] = None,
        amount: float = 0.0,
        payment_type: str = "",
        paid_at: Optional[datetime] = None,
        receipt_number: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self._id = id
        self._patient_id = patient_id
        self._amount = amount
        self._payment_type = payment_type
        self._paid_at = paid_at
        self._receipt_number = receipt_number
        self._created_at = created_at
        self._updated_at = updated_at

        self._validate_amount()

    def _validate_amount(self):
        if not self.MIN_AMOUNT_LIMIT <= self._amount <= self.MAX_AMOUNT_LIMIT:
            raise DomainError(
                f"Invalid amount. The allowed range is between {self.MIN_AMOUNT_LIMIT} and {self.MAX_AMOUNT_LIMIT}"
            )

    @property
    def id(self) -> Optional[int]:
        return self._id

    @property
    def patient_id(self) -> Optional[int]:
        return self._patient_id

    @property
    def amount(self) -> float:
        return self._amount

    @property
    def payment_type(self) -> str:
        return self._payment_type

    @property
    def paid_at(self) -> Optional[datetime]:
        return self._paid_at

    @property
    def receipt_number(self) -> Optional[str]:
        return self._receipt_number

    @property
    def created_at(self) -> Optional[datetime]:
        return self._created_at

    @property
    def updated_at(self) -> Optional[datetime]:
        return self._updated_at