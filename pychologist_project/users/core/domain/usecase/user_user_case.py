class UpdateProfileUseCase:
    def __init__(self, user_repository):
        self.user_repository = user_repository
    
    def execute(self, user_id, data):
        user = self.user_repository.get_by_id(user_id)
        
        if not user:
            raise ValueError("Usuario no encontrado")
        
        email = data.get('email')
        if email and email != user.email:
            if self.user_repository.exists_by_email(email):
                raise ValueError("Este email ya está en uso")
            user.email = email
        

        phone = data.get('phone')
        if phone and phone != user.phone:
            if self.user_repository.exists_by_phone(phone):
                raise ValueError("Este teléfono ya está en uso")
            user.phone = phone
        
        name = data.get('name')
        if name:
            user.name = name
        
        profile_picture = data.get('profile_picture')
        if profile_picture:
            user.profile_picture = profile_picture
        
        self.user_repository.update(user)
        
        return user

class GetUserHomeDataUseCase:
    def __init__(self, user_repository, therapist_repository, patient_repository):
        self.user_repository = user_repository
        self.therapist_repository = therapist_repository
        self.patient_repository = patient_repository
    
    def execute(self, user_id):
        user = self.user_repository.get_by_id(user_id)
        
        if not user:
            raise ValueError("Usuario no encontrado")
        
        if user.role == 'ADMIN':
            return {"type": "ADMIN", "data": {}}
        elif user.role == 'THERAPIST':
            return self.therapist_repository.get_home_data(user)
        elif user.role == 'PATIENT':
            return self.patient_repository.get_home_data(user)
        else:
            raise ValueError('Rol no soportado')