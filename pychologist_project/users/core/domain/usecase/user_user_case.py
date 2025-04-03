from core.exceptions.custom_exceptions import EntityNotFoundError, InvalidOperationError, BusinessLogicError

class GetUserHomeDataUseCase:
    def __init__(self, user_repository, therapist_repository, patient_repository):
        self.user_repository = user_repository
        self.therapist_repository = therapist_repository
        self.patient_repository = patient_repository
    
    def execute(self, user):
        
        if user.role == 'ADMIN':
            return {"type": "ADMIN", "data": {}}
        elif user.role == 'THERAPIST':
            return self.therapist_repository.get_home_data(user)
        elif user.role == 'PATIENT':
            return self.patient_repository.get_home_data(user)
        else:
            raise InvalidOperationError('Rol no soportado')


class CreateUserUseCase:
    def __init__(self, user_repository):
        self.user_repository = user_repository
    
    def execute(self, data):
        if self.user_repository.exists_by_email(data.get('email')):
            raise ValueError("El email ya está registrado")
        
        if 'phone' in data and data['phone'] and self.user_repository.exists_by_phone(data.get('phone')):
            raise ValueError("El teléfono ya está registrado")
        
        self._validate_password(data.get('password'))
        
        from ....core.domain.entities import UserEntity
        user_entity = UserEntity(
            email=data.get('email'),
            phone=data.get('phone', ''),
            role=data.get('role', 'USER'),
            name=data.get('name'),
            profile_picture=data.get('profile_picture')
        )
        
        return self.user_repository.create(user_entity, data.get('password'))
    
    def _validate_password(self, password):
        import re
        password_regex = r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$"
        if not re.match(password_regex, password):
            raise InvalidOperationError(
                "La contraseña debe tener al menos 8 caracteres, incluir al menos una letra y un número."
            )


class GetUserUseCase:
    def __init__(self, user_repository):
        self.user_repository = user_repository
    
    def execute(self, user_id):
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise EntityNotFoundError(f"Usuario con ID {user_id} no encontrado")
        return user


class GetAllUsersUseCase:
    def __init__(self, user_repository):
        self.user_repository = user_repository
    
    def execute(self, filters=None, page=1, page_size=20):
        return self.user_repository.get_all(filters, page, page_size)


class UpdateUserUseCase:
    def __init__(self, user_repository):
        self.user_repository = user_repository
    
    def execute(self, user_id, data):
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise EntityNotFoundError(f"Usuario con ID {user_id} no encontrado")
        
        email = data.get('email')
        if email and email != user.email:
            if self.user_repository.exists_by_email(email):
                raise InvalidOperationError("Este email ya está en uso")
            user.email = email
        
        phone = data.get('phone')
        if phone and phone != user.phone:
            if self.user_repository.exists_by_phone(phone):
                raise InvalidOperationError("Este teléfono ya está en uso")
            user.phone = phone
        
        if 'name' in data:
            user.name = data.get('name')
        
        if 'profile_picture' in data:
            user.profile_picture = data.get('profile_picture')
        
        if 'role' in data:
            user.role = data.get('role')
        
        if 'is_active' in data:
            user.is_active = data.get('is_active')
        
        return self.user_repository.update(user)


class DeleteUserUseCase:
    def __init__(self, user_repository):
        self.user_repository = user_repository
    
    def execute(self, user_id):
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise EntityNotFoundError(f"Usuario con ID {user_id} no encontrado")
        
        self.user_repository.delete(user_id)
        return True


class ChangePasswordUseCase:
    def __init__(self, user_repository, auth_service):
        self.user_repository = user_repository
        self.auth_service = auth_service
    
    def execute(self, user_id, current_password, new_password):
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise EntityNotFoundError(f"Usuario con ID {user_id} no encontrado")
        
        if not self.auth_service.verify_password(user_id, current_password):
            raise InvalidOperationError("Contraseña actual incorrecta")
        
        self._validate_password(new_password)
        
        self.user_repository.change_password(user_id, new_password)
        return True
    
    def _validate_password(self, password):
        import re
        password_regex = r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$"
        if not re.match(password_regex, password):
            raise BusinessLogicError(
                "La contraseña debe tener al menos 8 caracteres, incluir al menos una letra y un número."
            )


class UpdateProfileUseCase:
    def __init__(self, user_repository):
        self.user_repository = user_repository
    
    def execute(self, user_id, data):
        user = self.user_repository.get_by_id(user_id)
        
        if not user:
            raise EntityNotFoundError("Usuario no encontrado")
        
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
