class StripeServiceInterface(ABC):
    @abstractmethod
    def create_payment_intent(self, amount: float, currency: str) -> Dict:
        pass

    @abstractmethod
    def confirm_payment(self, payment_intent_id: str) -> bool:
        pass

    @abstractmethod
    def create_product(self, name: str, price: float) -> Dict:
        pass