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
        paid_to_id: Optional[int] = None,
        amount: float = 0.0,
        payment_type: str = "",
        paid_at: Optional[datetime] = None,
        receipt_number: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self._id = id
        self._patient_id = patient_id
        self._paid_to_id = paid_to_id
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

    @id.setter
    def id(self, value: Optional[int]):
        if value is not None and not isinstance(value, int):
            raise DomainError("ID must be an integer or None.")
        self._id = value

    @property
    def patient_id(self) -> Optional[int]:
        return self._patient_id

    @patient_id.setter
    def patient_id(self, value: Optional[int]):
        if value is not None and not isinstance(value, int):
            raise DomainError("Patient ID must be an integer or None.")
        self._patient_id = value

    @property
    def paid_to_id(self) -> Optional[int]:
        return self._paid_to_id

    @paid_to_id.setter
    def paid_to_id(self, value: Optional[int]):
        if value is not None and not isinstance(value, int):
            raise DomainError("Paid To ID must be an integer or None.")
        self._paid_to_id = value

    @property
    def amount(self) -> float:
        return self._amount

    @amount.setter
    def amount(self, value: float):
        if not isinstance(value, (int, float)):
            raise DomainError("Amount must be a number.")
        self._amount = value
        self._validate_amount()

    @property
    def payment_type(self) -> str:
        return self._payment_type

    @payment_type.setter
    def payment_type(self, value: str):
        if not isinstance(value, str):
            raise DomainError("Payment type must be a string.")
        self._payment_type = value

    @property
    def paid_at(self) -> Optional[datetime]:
        return self._paid_at

    @paid_at.setter
    def paid_at(self, value: Optional[datetime]):
        if value is not None and not isinstance(value, datetime):
            raise DomainError("Paid At must be a datetime object or None.")
        self._paid_at = value

    @property
    def receipt_number(self) -> Optional[str]:
        return self._receipt_number

    @receipt_number.setter
    def receipt_number(self, value: Optional[str]):
        if value is not None and not isinstance(value, str):
            raise DomainError("Receipt number must be a string or None.")
        self._receipt_number = value

    @property
    def created_at(self) -> Optional[datetime]:
        return self._created_at

    @created_at.setter
    def created_at(self, value: Optional[datetime]):
        if value is not None and not isinstance(value, datetime):
            raise DomainError("Created At must be a datetime object or None.")
        self._created_at = value

    @property
    def updated_at(self) -> Optional[datetime]:
        return self._updated_at

    @updated_at.setter
    def updated_at(self, value: Optional[datetime]):
        if value is not None and not isinstance(value, datetime):
            raise DomainError("Updated At must be a datetime object or None.")
        self._updated_at = value