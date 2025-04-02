class UserEntity:
    def __init__(self, id=None, email=None, phone=None, role=None, is_active=True, profile_picture=None, name=None):
        self.id = id
        self.email = email
        self.phone = phone
        self.role = role
        self.is_active = is_active
        self.profile_picture = profile_picture
        self.name = name