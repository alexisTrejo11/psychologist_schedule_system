from django.db import models
from django.forms import ValidationError
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from phonenumber_field.modelfields import PhoneNumberField

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'ADMIN')
        extra_fields['is_staff'] = True
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser):
    ROLE_CHOICES = [
        ('THERAPIST', 'Terapeuta'),
        ('PATIENT', 'Paciente'),
        ('ADMIN', 'Administrador'),
    ]
    
    email = models.EmailField(unique=True)
    phone = PhoneNumberField(blank=True)
    role = models.CharField(max_length=15, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    
    @property
    def roles(self):
        return self._get_jwt_roles()

    def _get_jwt_roles(self):
        return getattr(self, '_roles', [])


class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile', null=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    first_therapy = models.DateTimeField(null=True, blank=True)
    last_therapy = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def set_as_deleted(self):
        if self.deleted_at != None:
            raise ValueError("Patient Already Deleted")
        
        self.deleted_at = timezone.now()
    

    def set_as_inactive(self):
        if self.is_active is True:
            raise ValueError("Patient Is Already Inactive")
        
        self.is_active = True
        self.updated_at = timezone.now()

    def __str__(self):
        return self.name

class Therapist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='therapist_profile', null=True)
    name = models.CharField(max_length=100, default='')
    license_number = models.CharField(max_length=50, unique=True)
    specialization = models.CharField(max_length=100)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dr(a). {self.user.email}"

