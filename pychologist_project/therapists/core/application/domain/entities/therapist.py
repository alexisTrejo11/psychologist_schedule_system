class TherapistEntity:
    def __init__(self, id=None, user_id=None, name="", license_number="", specialization="", created_at=None, updated_at=None):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.license_number = license_number
        self.specialization = specialization
        self.created_at = created_at
        self.updated_at = updated_at

