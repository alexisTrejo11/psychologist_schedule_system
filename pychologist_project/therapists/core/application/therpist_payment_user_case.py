
class GetTherapistPaymentsUseCase:
    def __init__(self, payment_repository):
        self.payment_repository = payment_repository
    
    def execute(self, therapist):
        return self.payment_repository.get_by_therapist(therapist)

class GetTherapistPaymentUseCase:
    def __init__(self, payment_repository):
        self.payment_repository = payment_repository
    
    def execute(self, therapist, payment_id):
        return self.payment_repository.get_by_therapist_and_id(therapist, payment_id)


class CreateTherapistPaymentUseCase:
    def __init__(self, payment_service):
        self.payment_service = payment_service
    
    def execute(self, payment_data):
        return self.payment_service.create(payment_data)


class UpdateTherapistPaymentUseCase:
    def __init__(self, payment_service, payment_repository):
        self.payment_service = payment_service
        self.payment_repository = payment_repository
    
    def execute(self, payment_id, therapist, payment_data):
        existing_payment = self.payment_repository.get_by_therapist_and_id(therapist, payment_id)

        return self.payment_service.update_payment(payment_data, existing_payment)


class DeleteTherapistPaymentUseCase:
    def __init__(self, payment_service):
        self.payment_service = payment_service
    
    def execute(self, therapist, payment_id):
        self.payment_service.delete_payment(therapist, payment_id)
